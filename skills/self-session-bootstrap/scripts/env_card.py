# -*- coding: utf-8 -*-
"""
环境卡读写：会话索引 scripts/_meta/env_card.json。

================================================================================
使用前注意事项
================================================================================
1. 字段只有 commands_date / commands / conda_date / conda_envs；日期为 YYYY-MM-DD。
2. 文件不存在时按空卡返回；损坏的 JSON 让异常冒泡，不要静默当空卡。
3. 写入前先 load 再改自己的字段，避免命令探测与 conda 探测互相覆盖。
4. 本模块不是探测入口，不要单独跑。
"""

import json
from datetime import datetime
from pathlib import Path

_META_DIR = Path(__file__).resolve().parent / "_meta"
ENV_CARD_FILE = _META_DIR / "env_card.json"

EMPTY_CARD = {
    "commands_date": None,
    "commands": [],
    "conda_date": None,
    "conda_envs": [],
}


def today_iso_date() -> str:
    """本机日历日，格式 YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")


def load_env_card() -> dict:
    """
    读环境卡；没有文件则返回空卡副本。

    功能：加载日缓存。
    应用场景：命令探测或 conda 探测写入前。
    输入：无。
    输出：含四字段的 dict。
    异常：文件存在但不是合法 JSON → json.JSONDecodeError。
    """
    if not ENV_CARD_FILE.is_file():
        return dict(EMPTY_CARD)
    with open(ENV_CARD_FILE, encoding="utf-8") as f:
        card = json.load(f)
    # 按空卡键补齐，已有字段保持原值
    merged = dict(EMPTY_CARD)
    merged.update(card)
    return merged


def save_env_card(card: dict) -> None:
    """
    把环境卡写成一行 JSON。

    功能：覆盖写入 env_card.json。
    应用场景：探测脚本更新自己的字段之后。
    输入：card — 完整四字段 dict。
    输出：无。
    """
    _META_DIR.mkdir(parents=True, exist_ok=True)
    with open(ENV_CARD_FILE, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, separators=(",", ":"))


def print_card_slice(card: dict, keys: list) -> None:
    """
    向 stdout 打印环境卡的指定字段，紧凑 JSON。

    功能：给 agent 最小结果，不带版本、不带不可用命令。
    应用场景：探测脚本的 stdout。
    输入：card — 环境卡；keys — 要打印的键名列表。
    输出：无（打印一行）。
    """
    payload = {key: card[key] for key in keys}
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
