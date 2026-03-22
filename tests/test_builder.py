from pathlib import Path

import nbformat

from nbmirror.builder import BuildOptions, build_notebook


def _write_notebook(path: Path, notebook: nbformat.NotebookNode) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, path)


def _make_rich_notebook() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Heading\n\nThis is markdown."),
        nbformat.v4.new_code_cell(
            source="print('table and plot')",
            outputs=[
                nbformat.v4.new_output(
                    output_type="display_data",
                    data={
                        "text/html": "<table class='dataframe'><tr><td>1</td></tr></table>",
                        "text/plain": "table",
                    },
                    metadata={},
                )
            ],
            execution_count=1,
        ),
        nbformat.v4.new_code_cell(
            source="plotly chart",
            outputs=[
                nbformat.v4.new_output(
                    output_type="display_data",
                    data={
                        "text/html": "<div id='plotly-fixture'></div><script>Plotly.newPlot('plotly-fixture', [])</script>",
                        "application/vnd.plotly.v1+json": {"data": [], "layout": {}},
                    },
                    metadata={},
                )
            ],
            execution_count=2,
        ),
    ]
    return nb


def test_builder_creates_output_directory_and_file(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "demo.ipynb"
    _write_notebook(notebook, _make_rich_notebook())

    out = build_notebook(notebook, BuildOptions(repo_root=repo))
    assert out.exists()
    assert out == repo / "notebooks_html" / "demo.html"


def test_generated_html_contains_home_buttons_and_markdown(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "demo.ipynb"
    _write_notebook(notebook, _make_rich_notebook())

    out = build_notebook(notebook, BuildOptions(repo_root=repo))
    html = out.read_text(encoding="utf-8")

    assert html.count('class="nbm-home-btn"') >= 2
    assert "Heading" in html


def test_generated_html_contains_toggle_assets_and_hidden_code_defaults(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "demo.ipynb"
    _write_notebook(notebook, _make_rich_notebook())

    out = build_notebook(notebook, BuildOptions(repo_root=repo))
    html = out.read_text(encoding="utf-8")

    assert "nbm-toggle" in html
    assert ".cell.code_cell .input" in html
    assert "aria-expanded" in html


def test_generated_html_preserves_pandas_table_and_plotly_markers(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "demo.ipynb"
    _write_notebook(notebook, _make_rich_notebook())

    out = build_notebook(notebook, BuildOptions(repo_root=repo))
    html = out.read_text(encoding="utf-8")

    assert "dataframe" in html
    assert "Plotly.newPlot" in html


def test_markdown_only_notebook_still_builds(tmp_path: Path) -> None:
    repo = tmp_path
    notebook = repo / "notebooks" / "md_only.ipynb"
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell("Only markdown")])
    _write_notebook(notebook, nb)

    out = build_notebook(notebook, BuildOptions(repo_root=repo))
    html = out.read_text(encoding="utf-8")

    assert "Only markdown" in html
    assert html.count('class="nbm-home-btn"') >= 2


