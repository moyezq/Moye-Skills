# -*- coding: utf-8 -*-
"""一次性搭好 Vite + React + TypeScript 本栈前端。

功能：按仓根判断落点，创建 Vite 工程、安装锁死依赖、写入模板文件。每一步只跑一次，失败即退出并打印从失败步起的手搓命令。
应用场景：react-standard-coding 的「新建项目」路径；Agent 对本仓库只调用本脚本一次。
输入：--project-root 仓根；可选 --target frontend|root 覆盖自动落点。
输出：目标目录里可继续写业务的前端包；成功退出码 0，失败退出码 1。
异常：目标已是本栈、pnpm 不在 PATH、任一步命令失败 → 打印剩余命令后 SystemExit(1)。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets" / "templates"

RUNTIME_DEPS = [
    "react-router-dom",
    "zustand",
    "@tanstack/react-query",
    "react-hook-form",
    "@hookform/resolvers",
    "zod",
    "react-error-boundary",
    "lucide-react",
]
STYLE_DEPS = ["tailwindcss", "@tailwindcss/vite"]
DEV_DEPS = [
    "@types/node",
    "vitest",
    "@testing-library/react",
    "@testing-library/jest-dom",
    "@testing-library/user-event",
    "jsdom",
    "prettier",
]

SKIP_COPY_NAMES = {"index.css"}


class Step:
    def __init__(self, title: str, manual: str, run: Callable[[], None]) -> None:
        self.title = title
        self.manual = manual
        self.run = run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a Vite React TypeScript SPA once.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--target", choices=("frontend", "root"))
    return parser.parse_args()


def looks_like_python_backend(root: Path) -> bool:
    if (root / "pyproject.toml").is_file():
        return True
    if (root / "main.py").is_file() and (
        (root / "requirements.txt").is_file() or (root / "conf").is_dir()
    ):
        return True
    return False


def choose_target(root: Path, override: str | None) -> Path:
    if override == "frontend":
        return root / "frontend"
    if override == "root":
        return root
    package_json = root / "package.json"
    if package_json.is_file() and "react" in package_json.read_text(encoding="utf-8"):
        return root
    if looks_like_python_backend(root):
        return root / "frontend"
    return root


def pnpm_bin() -> str:
    found = shutil.which("pnpm")
    if found is None:
        print("PATH 里没有 pnpm。请先安装 pnpm，再手动执行下面命令。", file=sys.stderr)
        raise SystemExit(1)
    return found


def run_cmd(argv: list[str], cwd: Path) -> int:
    env = os.environ.copy()
    env.setdefault("CI", "1")
    completed = subprocess.run(argv, cwd=cwd, env=env, check=False)
    return completed.returncode


def print_remaining(steps: list[Step], start: int) -> None:
    print("\n脚手架失败。请用户从这一步起手动执行（Agent 不要再跑本脚本）：\n")
    for step in steps[start:]:
        print(f"## {step.title}")
        print(step.manual)
        print()


def ensure_ts_paths(tsconfig: Path) -> None:
    if not tsconfig.is_file():
        return
    text = tsconfig.read_text(encoding="utf-8")
    if '"@/*"' in text:
        return
    needle = '"compilerOptions": {'
    if needle not in text:
        raise RuntimeError(f"{tsconfig} 没有 compilerOptions")
    insert = '"compilerOptions": {\n    "baseUrl": ".",\n    "paths": { "@/*": ["./src/*"] },'
    tsconfig.write_text(text.replace(needle, insert, 1), encoding="utf-8")


def copy_templates(dest: Path) -> None:
    src_root = TEMPLATES
    for path in src_root.rglob("*"):
        if path.is_dir():
            continue
        if path.name in SKIP_COPY_NAMES:
            continue
        rel = path.relative_to(src_root)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def remove_vite_defaults(dest: Path) -> None:
    for rel in ("src/App.tsx", "src/App.css", "src/assets/react.svg"):
        path = dest / rel
        if path.is_file():
            path.unlink()


def build_steps(dest: Path, pnpm: str) -> list[Step]:
    dest_disp = str(dest)
    create_argv = [pnpm, "create", "vite@latest", ".", "--template", "react-ts"]

    def step_mkdir() -> None:
        dest.mkdir(parents=True, exist_ok=True)

    def step_create() -> None:
        if (dest / "package.json").is_file():
            return
        code = run_cmd(create_argv, dest)
        if code != 0:
            raise RuntimeError("create vite 失败")

    def step_style() -> None:
        code = run_cmd([pnpm, "add", *STYLE_DEPS], dest)
        if code != 0:
            raise RuntimeError("安装 Tailwind 失败")

    def step_dev() -> None:
        code = run_cmd([pnpm, "add", "-D", *DEV_DEPS], dest)
        if code != 0:
            raise RuntimeError("安装开发依赖失败")

    def step_runtime() -> None:
        code = run_cmd([pnpm, "add", *RUNTIME_DEPS], dest)
        if code != 0:
            raise RuntimeError("安装运行时依赖失败")

    def step_config() -> None:
        ensure_ts_paths(dest / "tsconfig.json")
        ensure_ts_paths(dest / "tsconfig.app.json")
        shutil.copy2(TEMPLATES / "vite.config.ts", dest / "vite.config.ts")
        css = dest / "src" / "index.css"
        css.write_text('@import "tailwindcss";\n', encoding="utf-8")

    def step_shadcn_init() -> None:
        code = run_cmd([pnpm, "dlx", "shadcn@latest", "init", "--yes"], dest)
        if code != 0:
            raise RuntimeError("shadcn init 失败")

    def step_templates() -> None:
        copy_templates(dest)
        shutil.copy2(TEMPLATES / "vite.config.ts", dest / "vite.config.ts")
        remove_vite_defaults(dest)

    def step_button() -> None:
        code = run_cmd([pnpm, "dlx", "shadcn@latest", "add", "button", "--yes"], dest)
        if code != 0:
            raise RuntimeError("shadcn add button 失败")

    return [
        Step("创建目录", f"mkdir {dest_disp}", step_mkdir),
        Step(
            "create vite",
            " ".join(create_argv) + f"\n  （cwd: {dest_disp}）",
            step_create,
        ),
        Step("安装 Tailwind", f"cd {dest_disp}\npnpm add " + " ".join(STYLE_DEPS), step_style),
        Step("安装开发依赖", f"cd {dest_disp}\npnpm add -D " + " ".join(DEV_DEPS), step_dev),
        Step(
            "写 Vite / TS 别名 / index.css",
            f"把 skill 里 assets/templates/vite.config.ts 拷到 {dest_disp}/vite.config.ts，tsconfig 加 @/*，src/index.css 写成 @import \"tailwindcss\";",
            step_config,
        ),
        Step("shadcn init", f"cd {dest_disp}\npnpm dlx shadcn@latest init --yes", step_shadcn_init),
        Step("安装运行时依赖", f"cd {dest_disp}\npnpm add " + " ".join(RUNTIME_DEPS), step_runtime),
        Step(
            "写入本栈模板",
            f"把 skill assets/templates 下文件拷到 {dest_disp}（不要覆盖 shadcn 改过的 src/index.css），删掉 src/App.tsx",
            step_templates,
        ),
        Step("shadcn button", f"cd {dest_disp}\npnpm dlx shadcn@latest add button --yes", step_button),
    ]


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    dest = choose_target(root, args.target)
    if (dest / "src" / "app" / "router.tsx").is_file():
        print(f"已经是本栈前端：{dest / 'src' / 'app' / 'router.tsx'} 存在。不要重跑脚手架。")
        raise SystemExit(1)

    pnpm = pnpm_bin()
    steps = build_steps(dest, pnpm)
    for index, step in enumerate(steps):
        try:
            step.run()
        except Exception as exc:
            print(f"{step.title}：{exc}", file=sys.stderr)
            print_remaining(steps, index)
            raise SystemExit(1) from None
    print(f"脚手架完成：{dest}")


if __name__ == "__main__":
    main()
