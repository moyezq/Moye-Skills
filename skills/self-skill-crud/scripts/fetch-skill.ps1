#Requires -Version 5.1
# 本文件必须存成 UTF-8 with BOM。Windows PowerShell 5.1 读无 BOM 的 UTF-8 会按 ANSI(cp936) 解，
# 中文字符串乱码后直接破坏解析（`powershell -File` 会报一串 Missing expression after ','）。
# pwsh 7 无此问题；setup.ps1 没 BOM 也活着，只因为它的中文全在注释里。改动本文件后确认 BOM 还在。
<#
职责：把 skills.sh 上找到的 skill 从 GitHub 取回本仓 preinstall/，只落盘、不安装。

原理（编号对应实现）：
  1) 落点从本仓 .env 的 PREINSTALL_SKILLS 读；相对值按仓库根解析，缺省 preinstall。
  2) 整份 clone 太贵：用 git 偏克隆（--filter=blob:none）+ 稀疏检出，只把目标 skill
     那一个目录的 blob 拉下来。位置先在树里定位（ls-tree 不需要 blob），再检出。
  3) 只认 SKILL.md 定界：目录名与 skill 名一致是惯例，先按目录名匹配；不中再读
     frontmatter 的 name 兜底。都不中就把候选全列出来报错，不猜。
  4) 落在 preinstall/<skill>/。同名目录已存在就停下（除非 -Force）——这个目录是给人审的，
     静默覆盖会把上次没看完的东西冲掉。
  5) 追加一行 SOURCES.md 记来源仓与 commit sha，收编时才知道取的是哪一版。
  6) 临时克隆放在落点目录的 .tmp-*/ 里，finally 里删掉；preinstall/ 已 gitignore。
  7) GitHub 时通时不通是常态，不是故障：每档克隆重试两次、带低速超时（卡住会自己断，
     不会无限等）；两档都不通就打印页面与仓库地址、exit 2，交人手动下载——
     而不是含糊地报成「取源失败」。

例：
  powershell -ExecutionPolicy Bypass -File .\scripts\fetch-skill.ps1 vercel-labs/agent-skills@vercel-react-best-practices
  powershell -ExecutionPolicy Bypass -File .\scripts\fetch-skill.ps1 https://skills.sh/obra/superpowers/brainstorming
  powershell -ExecutionPolicy Bypass -File .\scripts\fetch-skill.ps1 vercel-labs/agent-skills -Skill pr-review
  # 只读审查：拉出来读完就删，preinstall/ 与 skills/ 都不动
  powershell -ExecutionPolicy Bypass -File .\scripts\fetch-skill.ps1 anthropics/skills@frontend-design -PreinstallDir <一次性目录>
#>
[CmdletBinding()]
param(
    # owner/repo@skill | https://skills.sh/<owner>/<repo>/<skill> | https://github.com/<owner>/<repo>
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Source,

    # $Source 不带 @skill 时用；仓库里只有一个 skill 时可省。
    [string]$Skill,

    # 覆盖 .env 的 PREINSTALL_SKILLS：只读审查或试跑时指到一次性目录。
    [string]$PreinstallDir,

    # 覆盖已存在的同名目录。
    [switch]$Force,

    # 留着临时克隆目录，排错用。
    [switch]$KeepTemp
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

# 从脚本位置往上找带 setup.ps1 的目录，这样 skill 目录在 backup/ 还是 skills/ 都一样。
function Get-RepoRoot {
    $dir = Get-Item -LiteralPath $PSScriptRoot
    while ($null -ne $dir) {
        if (Test-Path -LiteralPath (Join-Path $dir.FullName 'setup.ps1')) { return $dir.FullName }
        $dir = $dir.Parent
    }
    throw "找不到仓库根：从 $PSScriptRoot 往上没有 setup.ps1。"
}

# 与 setup.ps1 同一套解析：键=值，跳过空行与 # 注释，展开 %VAR%。
function Read-DotEnv([string]$Path) {
    $map = @{}
    if (-not (Test-Path -LiteralPath $Path)) { return $map }
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq '' -or $line.StartsWith('#')) { return }
        $eq = $line.IndexOf('=')
        if ($eq -lt 1) { return }
        $map[$line.Substring(0, $eq).Trim()] =
            [Environment]::ExpandEnvironmentVariables($line.Substring($eq + 1).Trim())
    }
    return $map
}

# 原生命令失败不抛异常，得逐个看 $LASTEXITCODE，否则会把失败当成功往下走。
# 调用期间临时放开 ErrorActionPreference：PS 5.1 下 'Stop' 配 2>&1 会把 git 的 stderr
# 当成 NativeCommandError 直接终止，警告也会误判成失败。
function Invoke-Git {
    param([string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & git @GitArgs 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prev
    }
    if ($code -ne 0) {
        # git 的 stderr 混着 PowerShell 的 ErrorRecord 格式，整段转储糊到终端上没人看。
        # 取第一条有内容的行就够——"GitHub 时通时不通"是常态，提示必须短。
        $first = @($out | ForEach-Object { "$_" } | Where-Object { $_.Trim() -ne '' }) | Select-Object -First 1
        if (-not $first) { $first = '（git 没有输出）' }
        throw "git 失败（exit $code）：$first"
    }
    return $out
}

function Resolve-Source {
    param([string]$Text, [string]$SkillName)
    $owner = $null; $repo = $null; $skill = $SkillName

    if ($Text -match '^https?://(?:www\.)?skills\.sh/([^/]+)/([^/]+)/([^/?#]+)') {
        $owner = $Matches[1]; $repo = $Matches[2]
        if (-not $skill) { $skill = $Matches[3] }
    }
    elseif ($Text -match '^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$') {
        $owner = $Matches[1]; $repo = $Matches[2]
    }
    else {
        $body = $Text
        $at = $Text.LastIndexOf('@')
        if ($at -gt 0) {
            $body = $Text.Substring(0, $at)
            if (-not $skill) { $skill = $Text.Substring($at + 1) }
        }
        $parts = $body.Trim().Trim('/').Split('/')
        if ($parts.Count -eq 2) { $owner = $parts[0]; $repo = $parts[1] }
    }

    if (-not $owner -or -not $repo) {
        throw "认不出取源：'$Text'。用 owner/repo@skill、owner/repo 配 -Skill，或 skills.sh 页面 URL。"
    }
    return [pscustomobject]@{ Owner = $owner; Repo = $repo; Skill = $skill }
}

# 列出仓库里所有含 SKILL.md 的目录；仓库根的 skill 记为空串。
function Get-SkillDirs {
    param([string]$RepoDir)
    $paths = Invoke-Git -GitArgs @('-C', $RepoDir, 'ls-tree', '-r', '--name-only', 'HEAD')
    $dirs = @()
    foreach ($p in $paths) {
        $p = "$p".Trim()
        if ($p -eq '') { continue }
        if ($p -match '^(.*)/SKILL\.md$') { $dirs += $Matches[1] }
        elseif ($p -eq 'SKILL.md') { $dirs += '' }
    }
    return $dirs
}

function Get-SkillPath {
    param([string]$Dir)
    if ($Dir -eq '') { return 'SKILL.md' }
    return "$Dir/SKILL.md"
}

# 目录名不中时的兜底：读 frontmatter 的 name。偏克隆下这会按需拉单个 blob。
function Get-FrontmatterName {
    param([string]$RepoDir, [string]$Dir)
    $head = Invoke-Git -GitArgs @('-C', $RepoDir, 'show', "HEAD:$(Get-SkillPath $Dir)")
    foreach ($line in $head) {
        if ("$line" -match '^\s*name:\s*(.+?)\s*$') {
            return $Matches[1].Trim().Trim('"', "'")
        }
    }
    return $null
}

$repoRoot = Get-RepoRoot
$cfg = Read-DotEnv (Join-Path $repoRoot '.env')
$rawDest = if ($PreinstallDir) { $PreinstallDir } else { $cfg['PREINSTALL_SKILLS'] }
if ([string]::IsNullOrWhiteSpace($rawDest)) { $rawDest = 'preinstall' }
$dest = if ([IO.Path]::IsPathRooted($rawDest)) { $rawDest } else { Join-Path $repoRoot $rawDest }
$dest = [IO.Path]::GetFullPath($dest)
if (-not (Test-Path -LiteralPath $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }

$src = Resolve-Source -Text $Source -SkillName $Skill
$url = "https://github.com/$($src.Owner)/$($src.Repo).git"
$tmp = Join-Path $dest ('.tmp-' + [guid]::NewGuid().ToString('N').Substring(0, 8))

try {
    Write-Output "取源 $($src.Owner)/$($src.Repo)$(if ($src.Skill) { "@$($src.Skill)" })"
    Write-Output "落点 $dest"

    # 2) 拉仓库。GitHub 时通时不通是常态，不是故障：每档有界重试两次，带低速超时
    #    （传输低于 1KB/s 持续 25s 就自己断），都不通就交人，不无限等。
    $env:GIT_TERMINAL_PROMPT = '0'   # 需要凭据时不要弹提示卡住，直接失败
    $net = @('-c', 'http.lowSpeedLimit=1000', '-c', 'http.lowSpeedTime=25', '-c', 'credential.helper=')
    $strategies = @(
        @{ Name = '偏克隆 + 稀疏'; Args = @('clone', '--depth', '1', '--filter=blob:none', '--sparse', '--quiet') },
        @{ Name = '浅克隆';        Args = @('clone', '--depth', '1', '--quiet') }
    )
    $cloned = $false
    foreach ($strategy in $strategies) {
        foreach ($attempt in 1..2) {
            if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
            try {
                Invoke-Git -GitArgs ($net + $strategy.Args + @($url, $tmp)) | Out-Null
                $cloned = $true
                break
            }
            catch {
                Write-Output "  $($strategy.Name) 第 $attempt 次没通：$($_.Exception.Message)"
            }
        }
        if ($cloned) { break }
    }
    if (-not $cloned) {
        $hint = if ($src.Skill) { $src.Skill } else { $src.Repo }
        $page = "https://skills.sh/$($src.Owner)/$($src.Repo)/$hint"
        $repo = "https://github.com/$($src.Owner)/$($src.Repo)"
        Write-Output ''
        Write-Output '取不回来：这次没能从 GitHub 取到（网络时通时不通是常态，重试都没中）。'
        Write-Output '请手动下载，放好即可：'
        Write-Output "  1. 仓库页 $repo → Code → Download ZIP"
        Write-Output "  2. skill 页 $page"
        Write-Output '  3. 解压后把 skill 那一层整个目录（含 SKILL.md，references/ 之类也要）放到：'
        Write-Output "     $(Join-Path $dest $hint)"
        Write-Output '  先照上面两条核对 owner/repo/skill 名字；确认没写错就是网络，手动取或过会儿再试都行。'
        exit 2
    }

    $dirs = @(Get-SkillDirs -RepoDir $tmp)
    if ($dirs.Count -eq 0) { throw "$url 里没有 SKILL.md，不是 skill 仓。" }

    # 3) 定位目标 skill。
    $pick = $null
    if ($src.Skill) {
        $pick = @($dirs | Where-Object { $_ -ne '' -and (Split-Path $_ -Leaf) -ieq $src.Skill }) | Select-Object -First 1
        if ($null -eq $pick) {
            foreach ($d in $dirs) {
                if ((Get-FrontmatterName -RepoDir $tmp -Dir $d) -ieq $src.Skill) { $pick = $d; break }
            }
        }
        # 注意用 $null 判空：仓库根的 skill 匹配到的是空串，不是没匹配到。
        if ($null -eq $pick) {
            throw "没找到 skill '$($src.Skill)'。该仓库的候选：`n$(($dirs | ForEach-Object { if ($_ -eq '') { '<仓库根>' } else { $_ } }) -join "`n")"
        }
    }
    else {
        if ($dirs.Count -ne 1) {
            throw "仓库里有 $($dirs.Count) 个 skill，得指明取哪个：`n$(($dirs | ForEach-Object { if ($_ -eq '') { '<仓库根>' } else { $_ } }) -join "`n")"
        }
        $pick = $dirs[0]
    }

    $skillName = if ($src.Skill) { $src.Skill }
                 elseif ($pick -eq '') { $src.Repo }
                 else { Split-Path $pick -Leaf }

    # 2) 定位完再检出，只拉这一个目录的 blob。根级 skill 关掉稀疏拿全树。
    if ($pick -eq '') {
        Invoke-Git -GitArgs @('-C', $tmp, 'sparse-checkout', 'disable') | Out-Null
        $from = $tmp
    }
    else {
        Invoke-Git -GitArgs @('-C', $tmp, 'sparse-checkout', 'set', $pick) | Out-Null
        $from = Join-Path $tmp ($pick -replace '/', '\')
    }
    if (-not (Test-Path -LiteralPath (Join-Path $from 'SKILL.md'))) {
        throw "检出后没看到 SKILL.md：$from"
    }

    # 4) 落盘，不覆盖。
    $target = Join-Path $dest $skillName
    if (Test-Path -LiteralPath $target) {
        if (-not $Force) { throw "$target 已存在。先人审或删掉它，或加 -Force 覆盖。" }
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    if ($pick -eq '') {
        New-Item -ItemType Directory -Path $target | Out-Null
        Get-ChildItem -LiteralPath $tmp -Force |
            Where-Object { $_.Name -ne '.git' -and $_.Name -notlike '.tmp-*' } |
            ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse }
    }
    else {
        Copy-Item -LiteralPath $from -Destination $target -Recurse
    }

    # 5) 溯源：收编时要知道取的是哪一版。
    $sha = "$(Invoke-Git -GitArgs @('-C', $tmp, 'rev-parse', 'HEAD') | Select-Object -First 1)".Trim()
    $files = @(Get-ChildItem -LiteralPath $target -Recurse -File)
    $sourcesPath = Join-Path $dest 'SOURCES.md'
    if (-not (Test-Path -LiteralPath $sourcesPath)) {
        Set-Content -LiteralPath $sourcesPath -Encoding UTF8 -Value (@(
                '# preinstall 取源记录'
                ''
                '本目录内容由 `self-skill-crud` 的 `scripts/fetch-skill.ps1` 从上游取回，未收编。'
                ''
                '| skill | 来源仓 | commit | 取回日期 |'
                '| --- | --- | --- | --- |'
            ) -join "`n")
    }
    Add-Content -LiteralPath $sourcesPath -Encoding UTF8 `
        -Value "| ``$skillName`` | $($src.Owner)/$($src.Repo) | ``$sha`` | $(Get-Date -Format 'yyyy-MM-dd') |"

    Write-Output ''
    Write-Output "取回 $($src.Owner)/$($src.Repo)@$skillName"
    Write-Output "  落点     $target"
    Write-Output "  commit   $sha"
    Write-Output "  文件     $($files.Count) 个"
    Write-Output "  页面     https://skills.sh/$($src.Owner)/$($src.Repo)/$skillName"
    Write-Output "  取源记录 $sourcesPath"
    Write-Output ''
    Write-Output '下一步：人审该目录。收编进 skills/ 由人决定，本脚本不动 skills/。'
}
catch {
    # 只给人看一句话，别把 PowerShell 的异常转储糊到终端上。
    [Console]::Error.WriteLine("取源失败：$($_.Exception.Message)")
    exit 1
}
finally {
    # 6) 临时克隆收尾；preinstall/ 已 gitignore，正常情况不会留痕。
    if (-not $KeepTemp -and (Test-Path -LiteralPath $tmp)) {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
