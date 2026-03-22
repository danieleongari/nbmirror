from __future__ import annotations

import argparse
from pathlib import Path

from .builder import BuildOptions, build_many_notebooks, build_notebook
from .git_hook import run_hook_build
from .hook_install import install_pre_commit_hook


def _add_common_build_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", default=None, help="Repository root")
    parser.add_argument("--notebooks-dir", default="notebooks", help="Notebook directory")
    parser.add_argument("--output-dir", default="notebooks_html", help="Output HTML directory")
    parser.add_argument("--home-target", default="index.html", help="Home target relative to repo root")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")


def _detect_repo_root(start: Path) -> Path:
    """Find repository root from current path by looking for .git, then index.html."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    for candidate in (current, *current.parents):
        if (candidate / "index.html").exists() and (candidate / "notebooks").exists():
            return candidate
    return current


def _resolve_repo_root(repo_root_arg: str | None) -> Path:
    if repo_root_arg:
        return Path(repo_root_arg).resolve()
    return _detect_repo_root(Path.cwd())


def _build_options_from_args(args: argparse.Namespace) -> BuildOptions:
    return BuildOptions(
        repo_root=_resolve_repo_root(args.repo_root),
        notebooks_dir=Path(args.notebooks_dir),
        output_dir=Path(args.output_dir),
        home_target=Path(args.home_target),
        verbose=bool(args.verbose),
    )


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nbmirror", description="Build notebook HTML mirrors")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build one notebook mirror")
    p_build.add_argument("notebook", help="Notebook path")
    _add_common_build_options(p_build)

    p_many = sub.add_parser("build-many", help="Build many notebook mirrors")
    p_many.add_argument("notebooks", nargs="+", help="Notebook paths")
    _add_common_build_options(p_many)

    p_install = sub.add_parser("install-hook", help="Install plain Git pre-commit hook")
    p_install.add_argument("--repo-root", default=None, help="Repository root")
    p_install.add_argument("--notebooks-dir", default="notebooks", help="Notebook directory")
    p_install.add_argument("--output-dir", default="notebooks_html", help="Output HTML directory")
    p_install.add_argument("--home-target", default="index.html", help="Home target relative to repo root")

    p_hook = sub.add_parser("hook-run", help=argparse.SUPPRESS)
    p_hook.add_argument("files", nargs="*", help="Changed files")
    _add_common_build_options(p_hook)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        options = _build_options_from_args(args)
        build_notebook(args.notebook, options)
        return 0

    if args.command == "build-many":
        options = _build_options_from_args(args)
        build_many_notebooks(args.notebooks, options)
        return 0

    if args.command == "install-hook":
        hook_path = install_pre_commit_hook(
            repo_root=_resolve_repo_root(args.repo_root),
            notebooks_dir=args.notebooks_dir,
            output_dir=args.output_dir,
            home_target=args.home_target,
        )
        print(f"installed: {hook_path}")
        return 0

    if args.command == "hook-run":
        built = run_hook_build(
            changed_files=list(args.files),
            repo_root=_resolve_repo_root(args.repo_root),
            notebooks_dir=args.notebooks_dir,
            output_dir=args.output_dir,
            home_target=args.home_target,
            verbose=bool(args.verbose),
        )
        if args.verbose and built:
            print(f"rebuilt {len(built)} notebook mirrors")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
