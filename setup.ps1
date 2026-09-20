#Requires -Version 5.1
# 读取仓库根目录 .env，把各产品的个人 skills 目录联接到本仓 skills/。

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot
$skillsDir = Join-Path $repoRoot "skills"
$envFile = Join-Path $repoRoot ".env"

if (-not (Test-Path $skillsDir)) {
    throw "missing skills directory: $skillsDir"
}
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $repoRoot ".env.example") $envFile
    throw "created .env from .env.example; fill the paths and rerun"
}

function Read-DotEnv([string]$path) {
    $map = @{}
    Get-Content $path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $key = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        $map[$key] = [Environment]::ExpandEnvironmentVariables($value)
    }
    return $map
}

function Set-SkillsJunction([string]$linkPath, [string]$target) {
    if ([string]::IsNullOrWhiteSpace($linkPath)) { return }
    $target = (Resolve-Path $target).Path
    if (Test-Path $linkPath) {
        $item = Get-Item $linkPath
        if ($item.LinkType -eq "Junction") {
            $current = [string]$item.Target
            if ($current.TrimEnd("\") -eq $target.TrimEnd("\")) {
                Write-Output "ok $linkPath -> $target"
                return
            }
            cmd /c rmdir $linkPath
        } else {
            $backup = "$linkPath.bak-$(Get-Date -Format yyyyMMdd)"
            if (Test-Path $backup) {
                throw "backup already exists: $backup"
            }
            Rename-Item $linkPath $backup
            Write-Output "backup $backup"
        }
    }
    $parent = Split-Path $linkPath -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    cmd /c mklink /J $linkPath $target
    if ($LASTEXITCODE -ne 0) {
        throw "mklink failed: $linkPath -> $target"
    }
    Write-Output "link $linkPath -> $target"
}

$cfg = Read-DotEnv $envFile
Set-SkillsJunction $cfg["CURSOR_SKILLS"] $skillsDir
Set-SkillsJunction $cfg["DSH_SKILLS"] $skillsDir
