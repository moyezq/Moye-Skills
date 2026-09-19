# Moye-Skills

个人 skill 的技能仓。本机工作树：`<本仓路径>`。

Cursor 与 dsh 的默认 skills 目录做成**目录联接**，指向这份工作树，不要再各拷一份。

## Cursor 目录联接（人做一次）

dsh 侧联接由灌仓时做好。Cursor 仍用自己的 `~\.cursor\skills` 时，关掉 Cursor 后在 **以管理员以外的普通 PowerShell** 执行：

```powershell
$cursorSkills = "$env:USERPROFILE\.cursor\skills"
$workTree = "<本仓路径>"
$backup = "$env:USERPROFILE\.cursor\skills.bak-$(Get-Date -Format yyyyMMdd)"

if (Test-Path $cursorSkills) {
    Rename-Item $cursorSkills $backup
}
cmd /c mklink /J $cursorSkills $workTree
Get-Item $cursorSkills | Format-List FullName, LinkType, Target
```

`LinkType` 应为 `Junction`，`Target` 为 `<本仓路径>`。然后重新打开 Cursor。

不要联接到 `~\.dsh\skills`（多一跳，dsh 路径坏了 Cursor 跟着挂）。目标始终是工作树。

## 验收

```powershell
cmd /c dir /AL %USERPROFILE%\.cursor\skills
cmd /c dir /AL %USERPROFILE%\.dsh\skills
git -C <本仓路径> remote -v
```

两条联接都应指向 `<本仓路径>`。`origin` 必须是 `git@github.com:moye233057/Moye-Skills.git`。
