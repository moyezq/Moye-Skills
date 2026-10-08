# 落盘后怎么查

一条：**脚本层**。指针断没断、frontmatter 合不合法、命令尾巴对不对，这些是确定性的，写完就查。

规则到底有没有用**不在这里判**：离线造的案例测不出真实价值，得看实际使用——用了几轮发现某条没被照做、或它在浪费读的人的时间，再回来改。所以这份文档不设「不过就不许发」的门禁。

## 脚本层

```
python skills/self-skill-crud/scripts/validate_skill.py <skill 目录>
```

它查六样，任一「不过」都以非零退出码报出文件与行号：

- `SKILL.md` 存在，frontmatter 有 `name` 与 `description`
- `name` 与目录名一致、kebab-case
- description 末尾的命令尾巴与 `name` 一致（带尾巴时）
- 正文点到的 `references/`、`agents/`、`assets/` 路径真实存在；本 skill 里没有就按兄弟 skill 找（ADR-0006 允许 skill 互指），两边都没有才算不过
- `scripts/` 路径找不到只**提醒**：散文里的 `scripts/x.py` 多半是别的项目的布局示例
- 正文非空行超过 500 行只**提醒**：该往下推一层

围栏代码块内的路径不参与判定（那是模板与示例）。

路径检查的常见触发场景：刚把一份参考文件搬走或改名（`references/` 与 `agents/` 都要跟着改），或正文里提过一份还没建的参考。
