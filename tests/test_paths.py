from pathlib import Path

import pytest

from nbmirror.paths import home_link_for_output, mirror_output_path


def test_notebook_to_html_mapping(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "sales" / "q1.ipynb"
    notebook.parent.mkdir(parents=True)
    notebook.write_text("{}", encoding="utf-8")

    output = mirror_output_path(notebook, repo)
    assert output == repo / "notebooks_html" / "sales" / "q1.html"


def test_home_link_generation_simple(tmp_path: Path) -> None:
    repo = tmp_path
    output = repo / "notebooks_html" / "a.html"
    output.parent.mkdir(parents=True)
    output.write_text("", encoding="utf-8")

    href = home_link_for_output(output, repo, "index.html")
    assert href == "../index.html"


def test_home_link_generation_nested(tmp_path: Path) -> None:
    repo = tmp_path
    output = repo / "notebooks_html" / "sub" / "b.html"
    output.parent.mkdir(parents=True)
    output.write_text("", encoding="utf-8")

    href = home_link_for_output(output, repo, "index.html")
    assert href == "../../index.html"


def test_mapping_rejects_notebook_outside_dir(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "other" / "outside.ipynb"
    notebook.parent.mkdir(parents=True)
    notebook.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        mirror_output_path(notebook, repo)
