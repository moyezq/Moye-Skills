# -*- coding: utf-8 -*-
"""
列出本机 conda 环境名，写入环境卡。

================================================================================
使用前注意事项
================================================================================
1. 固定 `conda run -n base python` 调用本文件。
2. 读 `conda info --json` 的 envs 与 root_prefix，不要把原始 JSON 打到 stdout。
3. stdout 只有 conda_date 与 conda_envs。本脚本不算为任务跑 Python。
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from env_card import load_env_card, print_card_slice, save_env_card, today_iso_date

CONDA_INFO_TIMEOUT_SEC = 30


def list_conda_env_names() -> list:
    """
    从 conda info --json 取出环境名。

    功能：root_prefix 对应 base，其余用路径最后一段。
    应用场景：conda 日探测。
    输入：无。
    输出：环境名列表，base 在前。
    异常：找不到 conda → FileNotFoundError；非 0 或超时 → RuntimeError。
    """
    conda_exe = shutil.which("conda")
    if conda_exe is None:
        raise FileNotFoundError("conda not found on PATH")
    try:
        proc = subprocess.run(
            [conda_exe, "info", "--json"],
            capture_output=True,
            text=True,
            timeout=CONDA_INFO_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("conda info --json timed out") from exc
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "conda info --json failed")
    info = json.loads(proc.stdout)
    root_prefix = Path(info["root_prefix"]).resolve()
    names = []
    seen = set()
    for prefix in info["envs"]:
        prefix_path = Path(prefix).resolve()
        # base 与 root 是同一环境，其它环境名取目录名
        name = "base" if prefix_path == root_prefix else prefix_path.name
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def detect_and_save_conda_envs() -> dict:
    """
    探测 conda 环境名并更新环境卡的 conda 字段。

    功能：写入 conda_date、conda_envs，保留命令字段。
    应用场景：第一次为任务跑 Python 且 conda_date 不是今天。
    输入：无。
    输出：更新后的环境卡 dict；同时向 stdout 打印 conda 切片。
    """
    card = load_env_card()
    card["conda_date"] = today_iso_date()
    card["conda_envs"] = list_conda_env_names()
    save_env_card(card)
    print_card_slice(card, ["conda_date", "conda_envs"])
    return card


if __name__ == "__main__":
    detect_and_save_conda_envs()
