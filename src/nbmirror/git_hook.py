from __future__ import annotations

from pathlib import Path

from .builder import BuildOptions, build_many_notebooks


def filter_notebooks(changed_files: list[str], notebooks_dir: str = "notebooks") -> list[Path]:
    selected: list[Path] = []
    notebooks_prefix = Path(notebooks_dir)

    for item in changed_files:
        p = Path(item)
        if p.suffix.lower() != ".ipynb":
            continue
        try:
            p.relative_to(notebooks_prefix)
        except ValueError:
            continue
        selected.append(p)

    return selected


def run_hook_build(
    changed_files: list[str],
    repo_root: Path,
    notebooks_dir: str = "notebooks",
    output_dir: str = "notebooks_html",
    home_target: str = "index.html",
    verbose: bool = False,
) -> list[Path]:
    notebooks = filter_notebooks(changed_files, notebooks_dir=notebooks_dir)
    if not notebooks:
        return []

    options = BuildOptions(
        repo_root=repo_root,
        notebooks_dir=Path(notebooks_dir),
        output_dir=Path(output_dir),
        home_target=Path(home_target),
        verbose=verbose,
    )
    return build_many_notebooks(notebooks, options)
