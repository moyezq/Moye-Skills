"""列出归纳日期为今天的笔记库 markdown 文件。

知识库根从仓库根 `.env` 的 `NOTES_ROOT` 读（本机专属值不写死在脚本里；键的说明见 `.env.example`）。
读不到就报出该键名并退出 1，不猜路径。

怎么跑（非交互 shell 里 `conda activate` 无效，用解释器绝对路径）：
    python "<skill根目录>/scripts/list_today_notes.py"
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

NOTES_KEY = "NOTES_ROOT"
DATE_RE = re.compile(r"归纳日期[：:]\s*(\d{4}-\d{2}-\d{2})")


def load_dotenv(path: Path) -> dict[str, str]:
    """读 KEY=VALUE 形式的 .env；文件不在就当空表。"""
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def scan(root: Path, today: str) -> list[Path]:
    matched = []
    for path in sorted(root.rglob("*.md")):
        head = path.read_text(encoding="utf-8", errors="replace")[:400]
        m = DATE_RE.search(head)
        if m and m.group(1) == today:
            matched.append(path)
    return matched


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    raw = load_dotenv(repo_root / ".env").get(NOTES_KEY)
    if not raw:
        sys.exit(f"{repo_root / '.env'} 缺 {NOTES_KEY}（本机知识库根；见 .env.example）")
    root = Path(raw)
    today = date.today().isoformat()
    files = scan(root, today)
    print(f"date={today} count={len(files)}")
    for path in files:
        print(path.relative_to(root).as_posix())
