# -*- coding: utf-8 -*-
r"""
探测 PATH 高频命令：只读入口给出当天可用命令名，写入入口更新环境卡。

================================================================================
使用前注意事项
================================================================================
1. 会话只调只读入口 `list_available_commands()`；写环境卡的 `detect_and_save_commands()` 在受限沙箱下会被拒。不读 conda 环境名单。
2. 要增删命令只改 COMMANDS_TO_CHECK；每条 version 参数写死。PATH 上 which 不到时看 FALLBACK_EXES。
3. 只把探测成功的名字写入 commands；不写版本、不写失败项。
4. stdout 只有 commands_date 与 commands。本脚本不算为任务跑 Python。
"""

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from env_card import load_env_card, print_card_slice, save_env_card, today_iso_date

# 高频开发命令：名字 + 用来确认存在的 version 参数。conda / python 不在此列。
COMMANDS_TO_CHECK = [
    ("git", ["--version"]),
    ("ssh", ["-V"]),
    ("node", ["--version"]),
    ("npm", ["--version"]),
    ("pnpm", ["--version"]),
    ("npx", ["--version"]),
    ("pip", ["--version"]),
    ("playwright-cli", ["--version"]),
    ("ffmpeg", ["-version"]),
    ("whisper", ["-h"]),
    ("soffice", ["--version"]),
    ("pandoc", ["--version"]),
]

# PATH 上 which 不到时，把本机安装位置填在这里（留空表示只用 PATH）。
FALLBACK_EXES = {}

VERSION_TIMEOUT_SEC = 8


def _resolve_exe(name: str):
    """
    解析命令可执行文件：先 PATH，再 FALLBACK_EXES。

    功能：给探测提供单一入口路径。
    应用场景：which 不到但本机已装在固定目录时。
    输入：name — COMMANDS_TO_CHECK 里的命令名。
    输出：存在的 exe 路径；都没有则 None。
    """
    found = shutil.which(name)
    if found:
        return found
    fallback = FALLBACK_EXES.get(name)
    if fallback is not None and fallback.is_file():
        return str(fallback)
    return None


def _command_is_available(name: str, version_args: list) -> bool:
    """解析到 exe 后跑固定 version 参数；whisper 无独立 --version，文件在即算可用。"""
    exe = _resolve_exe(name)
    if exe is None:
        return False
    # openai-whisper 的 CLI 把 -h/--version 走转写入口，返回非 0；以文件存在为准
    if name == "whisper":
        return True
    try:
        proc = subprocess.run(
            [exe] + version_args,
            capture_output=True,
            text=True,
            # 子进程按本地代码页吐字节；固定 utf-8 + replace，避免读线程抛 UnicodeDecodeError。
            # 这里只用 returncode，替换字符不影响判定。
            encoding="utf-8",
            errors="replace",
            timeout=VERSION_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0


def list_available_commands() -> list:
    """
    按 COMMANDS_TO_CHECK 收集当前可用的命令名。

    功能：which + version，只保留成功的名字。
    应用场景：命令日探测。
    输入：无。
    输出：可用命令名列表，顺序与 COMMANDS_TO_CHECK 一致。
    """
    names = []
    for name, version_args in COMMANDS_TO_CHECK:
        if _command_is_available(name, version_args):
            names.append(name)
    return names


def detect_and_save_commands() -> dict:
    """
    探测可用命令并更新环境卡的命令字段。

    功能：写入 commands_date、commands，保留 conda 字段。
    应用场景：本对话第一次需要命令白名单（PATH 命令）且 commands_date 不是今天。
    输入：无。
    输出：更新后的环境卡 dict；同时向 stdout 打印命令切片。
    """
    card = load_env_card()
    card["commands_date"] = today_iso_date()
    card["commands"] = list_available_commands()
    save_env_card(card)
    print_card_slice(card, ["commands_date", "commands"])
    return card


if __name__ == "__main__":
    detect_and_save_commands()
