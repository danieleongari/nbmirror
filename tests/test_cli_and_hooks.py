from pathlib import Path
import os

import nbformat

from nbmirror.cli import main
from nbmirror.git_hook import filter_notebooks


def _write_min_notebook(path: Path, text: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell("# Title"),
            nbformat.v4.new_code_cell(
                source=f"print('{text}')",
                outputs=[
                    nbformat.v4.new_output(
                        output_type="stream",
                        name="stdout",
                        text=f"{text}\\n",
                    )
                ],
                execution_count=1,
            ),
        ]
    )
    nbformat.write(nb, path)


def test_cli_build_command_works(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "one.ipynb"
    _write_min_notebook(notebook)

    code = main([
        "build",
        str(notebook),
        "--repo-root",
        str(repo),
    ])
    assert code == 0
    assert (repo / "notebooks_html" / "one.html").exists()


def test_cli_build_many_processes_only_passed_notebooks(tmp_path: Path) -> None:
    repo = tmp_path
    n1 = repo / "notebooks" / "one.ipynb"
    n2 = repo / "notebooks" / "two.ipynb"
    n3 = repo / "notebooks" / "three.ipynb"
    _write_min_notebook(n1, "one")
    _write_min_notebook(n2, "two")
    _write_min_notebook(n3, "three")

    code = main([
        "build-many",
        str(n1),
        str(n3),
        "--repo-root",
        str(repo),
    ])
    assert code == 0
    assert (repo / "notebooks_html" / "one.html").exists()
    assert (repo / "notebooks_html" / "three.html").exists()
    assert not (repo / "notebooks_html" / "two.html").exists()


def test_hook_filtering_ignores_non_notebooks_and_outside_notebooks_dir() -> None:
    changed = [
        "README.md",
        "notebooks/a.ipynb",
        "scripts/x.py",
        "notebooks/sub/b.ipynb",
        "other/c.ipynb",
    ]

    filtered = filter_notebooks(changed, notebooks_dir="notebooks")
    assert filtered == [Path("notebooks/a.ipynb"), Path("notebooks/sub/b.ipynb")]


def test_install_hook_command_creates_pre_commit_file(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / ".git" / "hooks").mkdir(parents=True)

    code = main([
        "install-hook",
        "--repo-root",
        str(repo),
    ])
    assert code == 0
    hook = repo / ".git" / "hooks" / "pre-commit"
    assert hook.exists()
    text = hook.read_text(encoding="utf-8")
    assert "nbmirror hook-run" in text
    assert "git add -- \"notebooks_html\"" in text


def test_integration_fixture_notebook_exists() -> None:
    fixture = Path(__file__).parent / "fixtures" / "integration_fixture.ipynb"
    assert fixture.exists()


def test_cli_build_from_subdirectory_without_repo_root(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / ".git").mkdir()
    (repo / "index.html").write_text("<html></html>", encoding="utf-8")
    notebook = repo / "notebooks" / "one.ipynb"
    _write_min_notebook(notebook)

    nested = repo / "notebooks_html"
    nested.mkdir(parents=True, exist_ok=True)

    original_cwd = Path.cwd()
    try:
        os.chdir(nested)
        code = main(["build", "notebooks/one.ipynb"])
    finally:
        os.chdir(original_cwd)

    assert code == 0
    assert (repo / "notebooks_html" / "one.html").exists()
