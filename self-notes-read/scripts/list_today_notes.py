"""列出归纳日期为今天的 笔记库 markdown 文件。"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(r"<工作目录>\笔记库")
DATE_RE = re.compile(r"归纳日期[：:]\s*(\d{4}-\d{2}-\d{2})")


def scan(root: Path, today: str) -> list[Path]:
    matched = []
    for path in sorted(root.rglob("*.md")):
        head = path.read_text(encoding="utf-8", errors="replace")[:400]
        m = DATE_RE.search(head)
        if m and m.group(1) == today:
            matched.append(path)
    return matched


if __name__ == "__main__":
    today = date.today().isoformat()
    files = scan(ROOT, today)
    print(f"date={today} count={len(files)}")
    for p in files:
        print(p.relative_to(ROOT).as_posix())
