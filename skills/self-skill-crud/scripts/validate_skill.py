# -*- coding: utf-8 -*-
"""
校验一个 skill 目录：SKILL.md 存在、frontmatter 合法、name 与目录名/命令尾巴一致、正文相对指针可达。

原理（按系统流程）
  一个 skill 被装载的链路是：扫描根顶层发现 <name>/SKILL.md → 解 frontmatter（name 就是 skill 名，
  `/名字` 手势按这个名字精确查表）→ agent 读正文里的指针 → 按指针去够 references/ 等文件。
  本脚本每条目录只走到「读文件 + 静态判」就结束，立刻判，再下一条。不装载、不跑 skill、不改仓库任何文件。

  一条目录逐步发生什么：
    1. 读 <目录>/SKILL.md 全文，切出 frontmatter 块（首尾 `---`）与正文行。
    2. 解 frontmatter 的 name / description；值可能被单双引号包住、可能很长、可能折行续写。
    3. 拿 name 比目录名与 kebab-case；再找 frontmatter 里的 `命令：/<名字> —— …` 尾巴与 name 比。
    4. 围栏代码块里的路径不参与判定；剩下反引号内整段是 `references/…` 这类路径的、
      以及 [说明](./xxx.md) 链接，先按本 skill 目录解析，找不到再按兄弟 skill 各试一次。
    5. 正文非空行超 500 行只提醒，不算不过。

  判据差别（为什么 `scripts/` 只提醒）
    `references/`、`agents/`、`assets/` 是本 skill 自己要读的材料，指针断了 agent 就够不到，必须不过。
    `scripts/` 常出现在散文里当「另一个项目的布局示例」（本仓 self-python-project 的正文就那么写），
    它描述的不是本 skill 的资源，断了不影响本 skill 能不能跑，所以两处都找不到时只提醒。
    三类都先按本 skill 目录找，找不到再按父目录（`skills/` 根）下每个兄弟目录各试一次
    `<兄弟目录>/<相对路径>`：本仓 ADR-0006 说「其它 skill 可以指向这些独立 skill」，
    所以 `references/writing.md` 落在兄弟 skill 里不算断链。

  一次实测（输入就是命令行参数；换目录结果会变。fixture 用完即删，不留在仓里）
    在临时目录里建一个 `bad-skill`（四坑同踩）→ 期望四项都报 → 实测 4 项不过、退出码 1：缺 description、
      name `bad-skill-name` 与目录名不符、命令尾巴 /other-skill 与 name 不符、`references/nope.md` 不存在
      （这个路径在任何兄弟 skill 里都没有，跨 skill 兜底放不过它）。
    `skills/self-skill-crud` → 期望全过 → 实测 0 项不过、退出码 0。
    `skills/self-python-project` → `scripts/ingest.py` 是别的项目布局示例 → 实测 1 项提醒、0 项不过、退出码 0。

怎么跑（本文件入口；编号和上面「一条目录」不是同一套）
  职责：给一个 skill 目录，逐项打印 `文件:行号: 说明`，末行给汇总，按有没有不过项定退出码。
  入口步骤：
    1. step0_load_skill_md — 读 <目录>/SKILL.md；文件不在就只报这一项。
    2. step1_parse_frontmatter — 切 frontmatter、解 name / description（把原理 1～2 步跑完）。
    3. step2_check_name — name 与目录名一致、且 kebab-case。
    4. step3_check_command_tail — 命令尾巴的 /名字 与 name 一致（原理第 3 步）。
    5. step4_check_referenced_paths — 正文相对路径与链接：本 skill → 兄弟 skill 兜底 → 按前缀定不过还是提醒。
    6. step5_check_body_length — 正文行数提醒（原理第 5 步）。
  输入：命令行第一个参数 = skill 目录。这一个是任务定死的对外入口，所以只在 __main__ 读一次 sys.argv。
  产出：stdout 的逐行问题 + 汇总行；退出码 0 = 通过，1 = 有问题。
"""

import re
import sys
from pathlib import Path

# 正文里允许被当指针的目录前缀，与 references/style.md 的 skill 目录结构一致
POINTER_DIRS = ("references", "scripts", "agents", "assets")

# 反引号内整段就是一个路径：`references/xxx.md`
INLINE_CODE = re.compile(r"`([^`\n]+)`")

# [说明](./xxx.md) 形式的链接（同一行串两个链接时第二个会漏，够用就好）
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# 含这些字符的是占位符或通配写法，不当真实路径去解析
PLACEHOLDER_CHARS = ("<", ">", "*", "$")

# 命令尾巴：命令：/名字 —— 一句话作用（反引号包住 /名字 的写法不算，见 self-skill-crud）
COMMAND_TAIL = re.compile(r"命令：\s*/([^`\s、，,。()（）]+?)\s*——")

# name 必须是 kebab-case，与 DSH 的 SKILL_NAME 同一条规则
KEBAB_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# 正文非空行上限，超过只提醒（references/style.md：超过就把细则往下推一层）
BODY_LINE_LIMIT = 500


def read_text_lines(path: Path) -> list[str]:
    """
    按 UTF-8 读全文并切成行。

    功能：utf-8-sig 顺带吃掉 BOM，否则首行 `---` 会带 \\ufeff 而判不出 frontmatter。
    应用场景：校验链第一步读 SKILL.md。
    输入：path — 文本文件路径。
    输出：行列表，已去掉行尾换行，保留行内空格。
    """
    return path.read_text(encoding="utf-8-sig").splitlines()


def strip_quotes(raw: str) -> str:
    """
    去掉 frontmatter 值两端成对的单/双引号。

    功能：`"a: b"` 与 `'a: b'` 都还原成裸值，避免引号混进 name 比较。
    应用场景：解 `key: value` 时统一值形状。
    输入：raw — 冒号右边的原文。
    输出：去引号、去两端空白的值。
    """
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    return value


def locate_frontmatter(lines: list[str]) -> tuple[int | None, int | None]:
    """
    找 frontmatter 块的首尾 `---` 行号。

    功能：首行必须是 `---`；再往下找收尾的 `---`。
    应用场景：校验链第二步切开 frontmatter 与正文。
    输入：lines — SKILL.md 全文行。
    输出：(首行下标, 收尾行下标)，0 基；开头不对返回 (None, None)，没有收尾返回 (0, None)。
    """
    if not lines or lines[0].strip() != "---":
        return None, None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return 0, index
    return 0, None


def parse_frontmatter(block_lines: list[str], first_line_no: int) -> dict[str, tuple[str, int]]:
    """
    把 frontmatter 块解成键值表。

    功能：只认 `key: value`；值被引号包住就去引号，缩进的后续行拼进上一个键的值（折行写法）。
    应用场景：取 name 与 description；不引 PyYAML，本机没装，也不引任何第三方依赖。
    输入：block_lines — 首尾 `---` 之间的行；first_line_no — 块内第一行在文件里的行号。
    输出：{键: (值, 行号)}，行号是该键第一次出现的行。
    """
    fields: dict[str, tuple[str, int]] = {}
    current_key = ""
    for offset, line in enumerate(block_lines):
        line_no = first_line_no + offset
        match = re.match(r"^([A-Za-z0-9_.\-]+)\s*:\s*(.*)$", line)
        if match:
            current_key = match.group(1)
            fields[current_key] = (strip_quotes(match.group(2)), line_no)
            continue
        # 折行续写：缩进且有内容，且不是新的 key，就拼到上一个键
        if current_key and line[:1].isspace() and line.strip():
            value, key_line_no = fields[current_key]
            fields[current_key] = (f"{value} {line.strip()}", key_line_no)
    return fields


def looks_like_pointer(target: str) -> bool:
    """
    判断一段文本本身是不是 `<指针目录>/<文件名>`。

    功能：前缀对得上、斜杠后面还有文件名（`references/` 这种光指目录的不算）、且不是占位符。
    应用场景：从反引号内容里筛出该去解析的路径。
    输入：target — 已去两端空白的候选文本。
    输出：True 表示该按 skill 目录解析这个路径。
    """
    if any(char in target for char in PLACEHOLDER_CHARS):
        return False
    for dir_name in POINTER_DIRS:
        prefix = f"{dir_name}/"
        if target.startswith(prefix):
            rest = target[len(prefix):]
            return bool(rest) and not rest.endswith("/")
    return False


def iter_pointer_targets(body_lines: list[str], first_line_no: int) -> list[tuple[str, int]]:
    """
    扫正文，取出所有要解析的相对指针。

    功能：围栏代码块（``` 围起来的部分）整段跳过——那是模板与示例；块外反引号内整段是
    `references/xxx.md` 这类路径的收下，`[说明](./xxx.md)`、`[说明](references/xxx.md)` 链接也收下（去掉 #锚点）。
    应用场景：校验链第五步，逐个按 skill 目录判定。
    输入：body_lines — 正文行；first_line_no — 正文第一行在文件里的行号。
    输出：[(相对路径, 行号)]，同一路径出现两次就记两条，方便对上线号。
    """
    targets: list[tuple[str, int]] = []
    in_fence = False
    for offset, line in enumerate(body_lines):
        line_no = first_line_no + offset
        # 围栏开合都只看行首 ``` ：块内是模板与示例，路径不参与判定
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for raw in INLINE_CODE.findall(line):
            target = raw.strip()
            if looks_like_pointer(target):
                targets.append((target, line_no))
        for raw in MARKDOWN_LINK.findall(line):
            target = raw.split("#", 1)[0].strip()
            if target.startswith(("./", "../")) or looks_like_pointer(target):
                targets.append((target, line_no))
    return targets


def find_sibling_hit(skill_dir: Path, target: str) -> str:
    """
    在兄弟 skill 目录里找同一个相对路径。

    功能：本 skill 里找不到时，按父目录（`skills/` 根）下每个兄弟目录各试一次
    `<兄弟目录>/<相对路径>`；本仓 ADR-0006 允许 skill 之间互相指向，命中就不是断链。
    应用场景：正文写 `references/writing.md` 而文件在兄弟 skill `self-notes-read` 里的那种指针。
    输入：skill_dir — 本 skill 目录；target — 已去两端空白的相对路径。
    输出：命中的兄弟目录名；一个都没命中返回空串。
    """
    parent = skill_dir.parent
    if not parent.is_dir():
        return ""
    for sibling in sorted(parent.iterdir()):
        if not sibling.is_dir() or sibling.name == skill_dir.name:
            continue
        if (sibling / target).exists():
            return sibling.name
    return ""


class Report:
    """收集逐项结果：跑了几项、哪几项不过（带文件与行号）、哪几项只是提醒。"""

    def __init__(self) -> None:
        """建一个空的结果收集器。"""
        self.total = 0
        self.failed = 0
        self.issues: list[tuple[str, int, str]] = []
        self.warns: list[tuple[str, int, str]] = []

    def passed(self) -> None:
        """记一项检查跑过且通过。"""
        self.total += 1

    def fail(self, file_path: str, line_no: int, message: str) -> None:
        """记一项不过：计入总数、计入不过数、留下文件与行号。"""
        self.total += 1
        self.failed += 1
        self.issues.append((file_path, line_no, message))

    def warn(self, file_path: str, line_no: int, message: str) -> None:
        """记一项提醒：计入总数，但不影响退出码。"""
        self.total += 1
        self.warns.append((file_path, line_no, message))


def step0_load_skill_md(skill_dir: Path, report: Report) -> tuple[Path, list[str]] | None:
    """
    读 <skill 目录>/SKILL.md。

    功能：确认 SKILL.md 存在并读成行；不在就记一项不过。
    应用场景：校验链第一步，后面几步都吃这份行列表。
    输入：skill_dir — 待查目录；report — 结果收集器。
    输出：命中时 (SKILL.md 路径, 行列表)；缺文件时 None。
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.fail(str(skill_md), 0, "缺少 SKILL.md")
        return None
    report.passed()
    return skill_md, read_text_lines(skill_md)


def step1_parse_frontmatter(
    skill_md: Path,
    lines: list[str],
    report: Report,
) -> tuple[dict[str, tuple[str, int]], list[str], int, list[str], int]:
    """
    切 frontmatter 并解出 name / description。

    功能：查首尾 `---`；缺 name 或 description（或值为空）各记一项不过。
    应用场景：校验链第二步。
    输入：skill_md — 文件路径（只用于报错）；lines — 全文行；report — 结果收集器。
    输出：(字段表, 正文行, 正文首行号, frontmatter 块行, 块首行号)。
    """
    start, end = locate_frontmatter(lines)
    if start is None:
        report.fail(str(skill_md), 1, "frontmatter 必须以 --- 开头")
        return {}, [], 1, [], 1
    if end is None:
        report.fail(str(skill_md), len(lines), "frontmatter 没有收尾的 ---")
        return {}, [], len(lines) + 1, [], 1
    report.passed()

    # 块内第一行是文件第 2 行；正文从收尾 --- 的下一行开始
    block_lines = lines[start + 1:end]
    block_first_line_no = start + 2
    fields = parse_frontmatter(block_lines, block_first_line_no)
    body_lines = lines[end + 1:]
    body_first_line_no = end + 2

    for key in ("name", "description"):
        if fields.get(key, ("", 0))[0]:
            report.passed()
        else:
            report.fail(str(skill_md), start + 1, f"frontmatter 缺少 {key}")
    return fields, body_lines, body_first_line_no, block_lines, block_first_line_no


def step2_check_name(
    skill_dir: Path,
    skill_md: Path,
    fields: dict[str, tuple[str, int]],
    report: Report,
) -> str:
    """
    查 name 与目录名一致、且是 kebab-case。

    功能：name 缺失时跳过这两项（缺 name 已在 step1 报过）；不一致、不合规各记一项不过。
    应用场景：校验链第三步。
    输入：skill_dir — 目录（目录名就是 skill 该有的名字）；skill_md — 文件路径；
          fields — 字段表；report — 结果收集器。
    输出：name 值；缺失时返回空串。
    """
    name, line_no = fields.get("name", ("", 1))
    if not name:
        return ""
    if name == skill_dir.name:
        report.passed()
    else:
        report.fail(str(skill_md), line_no, f"name `{name}` 与目录名 `{skill_dir.name}` 不一致")
    if KEBAB_NAME.match(name):
        report.passed()
    else:
        report.fail(str(skill_md), line_no, f"name `{name}` 不是 kebab-case（小写字母/数字，用 - 连接）")
    return name


def step3_check_command_tail(
    skill_md: Path,
    fields: dict[str, tuple[str, int]],
    block_lines: list[str],
    block_first_line_no: int,
    name: str,
    report: Report,
) -> None:
    """
    查 description 末尾的命令尾巴 `/名字` 是否等于 name。

    功能：按行找 `命令：/<名字> —— …`；带尾巴时每个尾巴都要与 name 相等，不等记一项不过。
    应用场景：校验链第四步。DSH 的 `/名字` 手势按 skill 名精确查表，尾巴写错名字就够不到这个 skill。
    输入：skill_md — 文件路径；fields — 字段表；block_lines / block_first_line_no — frontmatter 块；
          name — 上一步解出的 name；report — 结果收集器。
    输出：无；结果都进 report。
    """
    description, description_line_no = fields.get("description", ("", 0))
    hits = [
        (line_no, match.group(1))
        for line_no, line in enumerate(block_lines, start=block_first_line_no)
        for match in COMMAND_TAIL.finditer(line)
    ]
    if not hits and description:
        # description 折行写时尾巴可能跨行，退回整段找，行号用 description 那一行
        hits = [(description_line_no, match.group(1)) for match in COMMAND_TAIL.finditer(description)]
    if not hits:
        report.passed()
        return
    for line_no, tail_name in hits:
        if tail_name == name:
            report.passed()
        else:
            report.fail(str(skill_md), line_no, f"命令尾巴 /{tail_name} 与 name `{name}` 不一致")


def step4_check_referenced_paths(
    skill_dir: Path,
    skill_md: Path,
    body_lines: list[str],
    body_first_line_no: int,
    report: Report,
) -> None:
    """
    正文里点到的相对路径逐个判定：本 skill → 兄弟 skill 兜底 → 按前缀定不过还是提醒。

    功能：先按 <skill 目录>/<相对路径> 找；找不到再按兄弟 skill 找（ADR-0006 允许互相指向），
    命中记一项提醒。两处都没有时：references/、agents/、assets/ 记不过；scripts/ 只记提醒
    ——散文里的 scripts/xxx.py 极常是另一个项目的布局示例，不是本 skill 的资源。
    应用场景：校验链第五步，挡住「指针指向一份不存在的材料」，又不误伤跨 skill 指针。
    输入：skill_dir — skill 目录；skill_md — 文件路径；body_lines / body_first_line_no — 正文；
          report — 结果收集器。
    输出：无；结果都进 report。
    """
    targets = iter_pointer_targets(body_lines, body_first_line_no)
    if not targets:
        report.passed()
        return
    for target, line_no in targets:
        if (skill_dir / target).exists():
            report.passed()
            continue
        sibling_name = find_sibling_hit(skill_dir, target)
        if sibling_name:
            report.warn(
                str(skill_md),
                line_no,
                f"正文引用的 {target} 不在本 skill 内，按兄弟 skill `{sibling_name}` 命中（跨 skill 指针）",
            )
            continue
        if target.startswith("scripts/"):
            report.warn(
                str(skill_md),
                line_no,
                f"正文引用的 {target} 在本 skill 与兄弟 skill 里都不存在（scripts/ 只提醒：这类路径多是布局示例）",
            )
            continue
        report.fail(str(skill_md), line_no, f"正文引用的相对路径不存在：{target}")


def step5_check_body_length(
    skill_md: Path,
    body_lines: list[str],
    body_first_line_no: int,
    report: Report,
) -> None:
    """
    正文行数只提醒：超过 BODY_LINE_LIMIT 非空行时就该把细则往下推一层。

    功能：数正非空行；超限记一项提醒（不算不过），没超记一项通过。
    应用场景：校验链第六步，对应 references/style.md 的 500 行建议。
    输入：skill_md — 文件路径；body_lines / body_first_line_no — 正文；report — 结果收集器。
    输出：无；结果都进 report。
    """
    line_count = len([line for line in body_lines if line.strip()])
    if line_count > BODY_LINE_LIMIT:
        report.warn(
            str(skill_md),
            body_first_line_no + BODY_LINE_LIMIT,
            f"正文非空行 {line_count} 行，超过 {BODY_LINE_LIMIT} 行，该往下推一层",
        )
    else:
        report.passed()


def print_report(report: Report) -> None:
    """
    打印报告：问题、提醒、汇总，汇总永远是最后一行。

    功能：按文件与行号排序打印 `文件:行号: 说明`，末行给「检查了几项、几项不过」。
    应用场景：校验链收尾。
    输入：report — 结果收集器。
    输出：stdout 文本，无返回值。
    """
    for file_path, line_no, message in sorted(report.issues, key=lambda item: (item[0], item[1])):
        print(f"{file_path}:{line_no}: {message}")
    for file_path, line_no, message in sorted(report.warns, key=lambda item: (item[0], item[1])):
        print(f"{file_path}:{line_no}: （提醒）{message}")
    summary = f"汇总：检查 {report.total} 项，{report.failed} 项不过"
    if report.warns:
        summary += f"，{len(report.warns)} 项提醒"
    print(summary)


if __name__ == "__main__":
    # 中文要按 UTF-8 出，命令行管道默认是 GBK（等同 Scripts/py.ps1 里的 PYTHONUTF8=1）
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("用法：python validate_skill.py <skill 目录>", file=sys.stderr)
        sys.exit(1)
    SKILL_DIR = Path(sys.argv[1])

    report = Report()
    # 阶段0：读 <目录>/SKILL.md
    loaded = step0_load_skill_md(SKILL_DIR, report)
    if loaded is not None:
        skill_md, lines = loaded
        # 阶段1：切 frontmatter、解 name / description
        fields, body_lines, body_first_line_no, block_lines, block_first_line_no = step1_parse_frontmatter(
            skill_md, lines, report
        )
        # 阶段2：name 与目录名一致、kebab-case
        name = step2_check_name(SKILL_DIR, skill_md, fields, report)
        # 阶段3：命令尾巴 /名字 与 name 一致
        step3_check_command_tail(skill_md, fields, block_lines, block_first_line_no, name, report)
        # 阶段4：正文里点到的相对路径真实存在
        step4_check_referenced_paths(SKILL_DIR, skill_md, body_lines, body_first_line_no, report)
        # 阶段5：正文行数提醒
        step5_check_body_length(skill_md, body_lines, body_first_line_no, report)

    print_report(report)
    sys.exit(1 if report.failed else 0)
