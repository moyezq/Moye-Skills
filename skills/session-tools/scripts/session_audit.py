# -*- coding: utf-8 -*-
"""
会话自检：从 DSH 的事件流出三份报告——操作、token、skill 加载。

干什么：读一个会话的事件流，按轮列出工具调用次数、真失败分类、重复调用与探针写删抖动；
        再读它的 token 与上下文占用；最后看每个 skill 的**正文**有没有真的进过上下文。
停在哪：只读、只打印。不评价代码质量、不跑测试、不动会话文件。
不干什么：不替你判断「哪些跑红是有意的」——那要人读。报告里把非 0 退出单列，就是为了让你自己剔。

怎么跑（本文件入口）
  职责：定位会话 → 载入事件 → 依次打印三份报告 → 退出。
  入口步骤（这一套编号是「打开本文件从哪进」，与事件流里的 turn / step 不是同一套）：
    1. find_session      — 定位 session.v3.jsonl.zstd；SESSION_ID 为空则取最近改动的那个。
    2. load_events       — 解压 zstd 并逐行解析成事件列表。
    3. report_operations — 第一份：按轮的操作、真失败、非 0 退出、重复调用、探针写删抖动。
    4. report_tokens     — 第二份：token 与上下文占用（在 projcache 里，不在事件流里）。
    5. report_skill_loads— 第三份：每个 skill 的正文首次进上下文的 turn/seq 与方式。
  输入：下面的 SESSION_ID / TURN 两个常量（改常量定范围，不用命令行参数）。
  前置：zstandard。跑前先 `python -c "import zstandard"` 确认这份解释器装了它。
  产出：全部打到 stdout，不落盘；已把 stdout 强制成 UTF-8，Windows 控制台不再出乱码。
  对外：无（脚本，跑完即退）。
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import zstandard

DSH_ROOT = Path.home() / ".dsh"
SESSIONS_DIR = DSH_ROOT / "sessions"
CACHE_DIR = DSH_ROOT / "storages" / "session_projcache" / "sessions"
SKILLS_DIR = DSH_ROOT / "skills"

# 跑这个脚本本身会产生一段含失败标签的报告文本，它会被下一次统计扫成「新失败」。
# 靠这个标记把自身的运行排除掉，否则每跑一次就自己涨一次失败数。
SELF_MARKER = "session_audit.py"

SESSION_ID = ""   # 空 = 取最近改动的会话；填 "session-xxxx-..." 或 "xxxx-..." 都认
TURN = 0          # 0 = 全部轮次；填 1 就只看第 1 轮
TOP_CONTEXT = 10  # 第二份报告里列几个最占上下文的节点

# 真失败的判定标记：都取自工具结果的确定性文本，不猜意图。
# 第三项是「只在哪些工具的调用里算」——沙箱/EPERM 只可能来自 pwsh；不限工具的话，
# 编辑一个正文里含 spawn EPERM 的文件也会被算成一次失败。
# 已知残留误报：pwsh 只要**打印出**该字样就中招（回读/grep 一份含它的文档，
# 或本脚本自己的报告被再扫一遍）。文本匹配区分不了「打印」与「真失败」，靠人剔。
FAILURE_PATTERNS = (
    ("read 目标不存在", r"^Error: cannot read .*: not found", None),
    ("edit 未先 read", r"file has not been read", None),
    ("edit old_string 未命中", r"old_string was not found", None),
    ("grep / glob 参数不合法", r"^Error: include must be one glob", None),
    ("Python 抛异常", r"Traceback \(most recent call last\)", None),
    ("沙箱拒绝 / EPERM", r"sandbox: file access denied|spawn EPERM", {"pwsh"}),
)
EXIT_CODE = re.compile(r"\[exit code: (\d+)\]")


def force_utf8_stdout() -> None:
    """把 stdout 换成 UTF-8：Windows 控制台默认 GBK，中文报告会变成乱码。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def find_session(session_id: str) -> Path:
    """
    定位一个会话的事件流文件。

    功能：给定 id（可带可不带 `session-` 前缀）就在 <dsh>/sessions/*/ 下找它；给定空串就取最近改动的。
    应用场景：report_* 之前的第一步；不同 DSH 版本的会话事件流文件名不一样
              （v3 与 v4 的差别之一就在这里），所以按 `session.v[34].jsonl.zstd` 一起找。
    输入：session_id — 会话 id，空串表示「最近的那个」。
    输出：事件流文件路径。
    异常：找不到时 SystemExit，并列出可用的工作区目录。
    """
    candidates = list(SESSIONS_DIR.glob("*/*/session.v[34].jsonl.zstd"))
    if not candidates:
        raise SystemExit(f"没找到任何会话事件流：{SESSIONS_DIR}")
    if not session_id:
        newest = max(candidates, key=lambda path: path.stat().st_mtime)
        print(f"[范围] 未指定会话，取最近改动的：{newest.parent.name}")
        return newest
    wanted = session_id if session_id.startswith("session-") else f"session-{session_id}"
    for path in candidates:
        if path.parent.name == wanted:
            return path
    raise SystemExit(f"没找到会话 {wanted}；可用的是：\n  " + "\n  ".join(sorted(p.parent.name for p in candidates)))


def load_events(session_path: Path) -> list:
    """
    解压并解析事件流。

    功能：zstd 解压后按行 json.loads；解析不了的行直接跳过（不因一行坏掉丢掉整份报告）。
    应用场景：三份报告的共同输入。
    输入：session_path — session.v3.jsonl.zstd 的路径。
    输出：事件 dict 列表。
    """
    with session_path.open("rb") as handle:
        raw = zstandard.ZstdDecompressor().stream_reader(handle).read()
    events = []
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def has_error_flag(event: dict) -> bool:
    """这条 tool/result 是否被标成错误。

    读取比文本模式可靠得多：编译失败、类型检查失败这类「命令本身跑完了、但内容是错误」
    的调用，只有这个字段能认出来。三份报告的第一份用它兜底，避免把这类失败算成成功。
    """
    message = (event.get("data") or {}).get("message") or {}
    return bool(message.get("isError"))


def result_text(event: dict) -> str:
    """取一条 tool/result 事件里的纯文本。

    文本块在不同事件流版本里嵌套层数不同：v4 是 content[].text，更早的是
    content[].content[].text。两种都要认——只按两层取时，在 v4 上恒为空串，
    于是失败判定、非 0 退出、skill 加载三样一起读空，报告出「0 次失败、全部 skill
    从未加载」这种假结论。
    """
    chunks = []
    for block in event["data"]["message"].get("content", []):
        if block.get("type") == "text":
            chunks.append(block.get("text") or "")
            continue
        for piece in block.get("content", []) or []:
            if isinstance(piece, dict) and piece.get("type") == "text":
                chunks.append(piece.get("text") or "")
    return "\n".join(chunks)


def in_scope(event_turn, turn: int) -> bool:
    """这个事件算不算在本次报告范围内：turn 为 0 时全要，否则只留指定轮。"""
    return turn == 0 or event_turn == turn


def report_operations(events: list, turn: int) -> None:
    """
    第一份报告：操作量、真失败、非 0 退出、重复调用、探针写删抖动。

    功能：把 tool/call 按工具计数；拿结果文本对 FAILURE_PATTERNS 分类；单列非 0 退出（其中
           常包含有意的红灯与管道无匹配，需人剔除）；列出同名同参数的重复调用与探针文件抖动。
    应用场景：「本轮做了多少、错在哪、哪里在重复」。
    输入：events — 事件列表；turn — 0 表示全部轮次。
    输出：无返回值，打印报告。
    """
    calls = [e["data"] for e in events if e["type"] == "tool/call" and in_scope(e["data"].get("turn"), turn)]
    results = {
        e["data"]["message"]["source"]["callId"]: e
        for e in events
        if e["type"] == "tool/result"
    }
    scope_note = "全部轮次" if turn == 0 else f"第 {turn} 轮"
    print(f"\n===== 第一份：操作（{scope_note}，{len(calls)} 次工具调用）=====")
    for name, count in Counter(c["name"] for c in calls).most_common():
        print(f"  {name:<18} {count}")

    failures = Counter()
    failure_lines = []
    exits = []
    for call in calls:
        event = results.get(call["callId"])
        text = result_text(event) if event else ""
        if SELF_MARKER in call["arguments"]:
            continue  # 本脚本自己的输出含失败标签，扫进来就是自己给自己记一笔
        matched = False
        for label, pattern, tools in FAILURE_PATTERNS:
            if tools and call["name"] not in tools:
                continue
            if re.search(pattern, text, re.M):
                failures[label] += 1
                failure_lines.append((call.get("turn"), call.get("step"), call["name"], label))
                matched = True
                # 不 break：一次调用可能同时命中多条，全都记下来
        # 兜底：工具结果被标成错误但没命中任何文本模式（编译器与类型检查器的报错
        # 就属于这类——命令跑完了，内容是错误）。只标成「工具报错」，便于人剔。
        if not matched and event is not None and has_error_flag(event):
            failures["工具报错(isError)"] += 1
            failure_lines.append((call.get("turn"), call.get("step"), call["name"], "工具报错(isError)"))
        codes = {int(code) for code in EXIT_CODE.findall(text)} - {0}
        if codes:
            exits.append((call.get("turn"), call.get("step"), call["name"], sorted(codes)))
    total = sum(failures.values())
    print(f"\n  -- 真失败 {total} 次（占 {total / len(calls) * 100:.1f}%）--" if calls else "")
    for label, count in failures.most_common():
        where = ", ".join(f"t{turn}/s{step}" for turn, step, _, lab in failure_lines if lab == label)
        print(f"  {label:<24} {count:>2}   {where}")
    print(f"\n  -- 非 0 退出 {len(exits)} 次（含**有意的红灯**与管道无匹配，要人剔）--")
    for turn, step, name, codes in exits:
        print(f"  t{turn}/s{step:<5} {name:<8} exit={codes}")

    print("\n  -- 同名同参数的重复调用（>=2 次的）--")
    repeats = [(key, count) for key, count in Counter((c["name"], c["arguments"]) for c in calls).items() if count >= 2]
    if not repeats:
        print("  无")
    for (name, arguments), count in sorted(repeats, key=lambda item: -item[1])[:TOP_CONTEXT]:
        print(f"  x{count}  {name}  {arguments[:110]}")

    probe_writes = [c for c in calls if c["name"] == "write" and "probe" in c["arguments"].lower()]
    probe_deletes = [c for c in calls if c["name"] == "pwsh" and "Remove-Item" in c["arguments"] and "probe" in c["arguments"]]
    print(f"\n  -- 探针抖动：写 {len(probe_writes)} 次、删 {len(probe_deletes)} 次 --")
    if probe_deletes:
        print("  删了又建就是纯抖动：反复要用的检查该落成仓里的一份，别每轮现写。")


def report_tokens(session_path: Path) -> None:
    """
    第二份报告：token 总量与上下文占用。

    功能：会话统计与 token 不在事件流里，去 projcache 读 rows.tokenUsage / rows.sessionStats /
           rows.contextBreakdown；算出「缓存读取 / 步数」这个每步平均上下文。
    应用场景：「这轮贵在哪」——缓存读取总量 ≈ Σ(每步上下文)，上下文单调增长，故总花费近似随步数平方。
    输入：session_path — 事件流路径，用来推出同名的 projcache 文件。
    输出：无返回值，打印报告。
    """
    cache_file = CACHE_DIR / f"{session_path.parent.name}.json"
    print("\n===== 第二份：token 与上下文 =====")
    if not cache_file.exists():
        print(f"  没有会话统计文件，跳过：{cache_file}")
        return
    rows = json.loads(cache_file.read_text(encoding="utf-8"))["record"]["rows"]
    usage = rows.get("tokenUsage", {}).get("val", {}).get("totals", {})
    stats = rows.get("sessionStats", {}).get("val", {})
    pressure = rows.get("contextPressure", {}).get("val", {})
    steps = stats.get("steps") or 0
    cached = usage.get("cacheReadTokens", 0)

    print(f"  轮次 {stats.get('turns')} ｜ 模型步 {steps} ｜ 工具耗时 {stats.get('toolMs', 0) / 1000:.0f}s ｜ LLM 耗时 {stats.get('llmMs', 0) / 1000:.0f}s")
    print(f"  未缓存输入 {usage.get('uncachedInputTokens', 0):,} ｜ 输出 {usage.get('outputTokens', 0):,} ｜ 缓存写入 {usage.get('cacheWriteTokens', 0):,}")
    print(f"  缓存读取 {cached:,}" + (f"  ← 每步平均约 {cached / steps:,.0f}" if steps else ""))
    print(f"  上下文 {pressure.get('surfaceTokens', 0):,} / 窗口 {pressure.get('contextWindow', 0):,}")
    nodes = rows.get("contextBreakdown", {}).get("val", {}).get("nodes", [])
    if nodes:
        total = sum(node["heuristicTokens"] for node in nodes)
        print(f"\n  -- 最占上下文的 {TOP_CONTEXT} 个节点（全部 {len(nodes)} 个共 {total:,}）--")
        for node in sorted(nodes, key=lambda item: -item["heuristicTokens"])[:TOP_CONTEXT]:
            print(f"  seq{node['seq']:<6} {node['heuristicTokens']:>7,} tokens  {'[system]' if node.get('system') else ''}")
    print("\n  -- 读法 --")
    print("  步数才是量级杠杆：缓存读取 = Σ(每步上下文)，上下文单调增长，所以步数减半 ≈ 总花费掉到四分之一。")


def report_skill_loads(events: list) -> None:
    """
    第三份报告：每个 skill 的**正文**有没有真的进上下文。

    功能：区分「只出现在目录摘要里」与「正文真的加载了」。正文进入有两种方式——
           skill 工具返回的 <skill_content name="X">，或直接 read 了它的 SKILL.md
           （read 的工具调用参数里出现该 skill 目录名）。两者都找不到就是从未加载。
    应用场景：回答「这份 skill 到底生效了吗」。目录摘要在每个会话开头都有，不算生效。
    输入：events — 事件列表。
    输出：无返回值，打印报告。
    """
    loaded = []
    for event in events:
        if event["type"] == "tool/result":
            text = result_text(event)
            for match in re.finditer(r'<skill_content name="([^"]+)">', text):
                loaded.append((match.group(1), "skill 工具", event["data"].get("turn"), event.get("seq")))
        elif event["type"] == "tool/call" and event["data"].get("name") == "read":
            # 解析 JSON 取 file_path，不拿正则去啃转义过的原始文本（那种写法在真实数据上很脆）
            try:
                file_path = json.loads(event["data"].get("arguments") or "{}").get("file_path", "")
            except (json.JSONDecodeError, AttributeError):
                continue
            parts = Path(file_path).parts
            if len(parts) >= 2 and parts[-1] == "SKILL.md" and "skills" in parts:
                loaded.append((parts[-2], "read 文件", event["data"].get("turn"), event.get("seq")))

    names = sorted(
        path.parent.name
        for path in SKILLS_DIR.glob("*/SKILL.md")
        if not path.parent.name.startswith(".")
    )
    print(f"\n===== 第三份：skill 正文有没有进上下文（本机 {len(names)} 个 skill）=====")
    for name in names:
        hits = [item for item in loaded if item[0] == name]
        if not hits:
            print(f"  {name:<26} 从未加载（只在目录摘要里出现过 = 没生效）")
            continue
        first = min(hits, key=lambda item: (item[3] is None, item[3]))
        print(f"  {name:<26} {first[1]:<10} 首次 turn={first[2]} seq={first[3]}（共 {len(hits)} 次）")


if __name__ == "__main__":
    force_utf8_stdout()
    # 范围：常量区决定；空 SESSION_ID = 取最近改动的会话，TURN=0 = 全部轮次
    session = find_session(SESSION_ID)
    events = load_events(session)
    print(f"[范围] {session.parent.parent.name} / {session.parent.name} ｜ 事件 {len(events)} 条")
    # 第一份：操作量、真失败、重复调用、探针抖动
    report_operations(events, TURN)
    # 第二份：token 与上下文（在 projcache 里，不在事件流里）
    report_tokens(session)
    # 第三份：每个 skill 的正文有没有真的进上下文
    report_skill_loads(events)
