from __future__ import annotations

import os
from pathlib import Path


def is_notebook_file(path: Path | str) -> bool:
    return Path(path).suffix.lower() == ".ipynb"


def mirror_output_path(
    notebook_path: Path | str,
    repo_root: Path | str,
    notebooks_dir: Path | str = "notebooks",
    output_dir: Path | str = "notebooks_html",
) -> Path:
    """Map notebooks/<rel>.ipynb to notebooks_html/<rel>.html."""
    notebook = Path(notebook_path)
    root = Path(repo_root)
    notebooks_root = root / Path(notebooks_dir)
    output_root = root / Path(output_dir)

    notebook_abs = notebook if notebook.is_absolute() else (root / notebook)
    notebook_abs = notebook_abs.resolve()
    notebooks_root = notebooks_root.resolve()

    if notebook_abs.suffix.lower() != ".ipynb":
        raise ValueError(f"Not a notebook file: {notebook_path}")

    try:
        rel = notebook_abs.relative_to(notebooks_root)
    except ValueError as exc:
        raise ValueError(
            f"Notebook must be inside {notebooks_root}: {notebook_abs}"
        ) from exc

    return (output_root / rel).with_suffix(".html")


def home_link_for_output(
    output_html_path: Path | str,
    repo_root: Path | str,
    home_target: Path | str = "index.html",
) -> str:
    """Compute relative href from generated html file to the home target at repo root."""
    output_path = Path(output_html_path)
    root = Path(repo_root)
    home = root / Path(home_target)

    output_parent = output_path.parent.resolve()
    home_abs = home.resolve()
    # Use os-independent relpath, then normalize to URL style separators.
    rel_path = Path(os.path.relpath(str(home_abs), str(output_parent)))
    return rel_path.as_posix()
