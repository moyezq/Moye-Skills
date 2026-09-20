# Moye-Skills

个人 skill 仓库。clone 后把各产品的个人 skills 目录联接到本仓 `skills/`，不要再各拷一份。

本机路径写在 `.env`，不要写进 README。

## 使用

```powershell
git clone git@github.com:moye233057/Moye-Skills.git
cd Moye-Skills
copy .env.example .env
# 按本机改 .env；Windows 默认值一般不用动
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

改完路径后重启 Cursor / dsh。

联接目标是本仓的 `skills/`，不要指到另一个产品的 skills 目录。

## 验收

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
git remote -v
```

`setup.ps1` 对已指向 `skills/` 的联接会打印 `ok`。`origin` 用 SSH。
