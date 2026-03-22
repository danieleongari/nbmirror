from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
import warnings

import nbformat
from nbconvert import HTMLExporter

from .paths import home_link_for_output, mirror_output_path


@dataclass(frozen=True)
class BuildOptions:
    repo_root: Path
    notebooks_dir: Path = Path("notebooks")
    output_dir: Path = Path("notebooks_html")
    home_target: Path = Path("index.html")
    verbose: bool = False


def _read_asset_text(filename: str) -> str:
    return files("nbmirror.templates").joinpath(filename).read_text(encoding="utf-8")


def _inject_shell(html: str, home_href: str, title: str) -> str:
    css = _read_asset_text("injected.css")
    js = _read_asset_text("injected.js")

    nav_top = (
        '<div class="nbm-home-wrap nbm-home-top">'
        f'<a class="nbm-home-btn" href="{home_href}">\u2190 Home</a>'
        "</div>"
    )
    nav_bottom = (
        '<div class="nbm-home-wrap nbm-home-bottom">'
        f'<a class="nbm-home-btn" href="{home_href}">\u2190 Home</a>'
        "</div>"
    )

    extra_head = f"\n<style>\n{css}\n</style>\n"
    html = html.replace("</head>", extra_head + "</head>", 1)

    top_marker = f"\n{nav_top}\n"
    bottom_marker = f"\n{nav_bottom}\n"

    if "<body" in html:
        body_open_idx = html.find(">", html.find("<body"))
        if body_open_idx != -1:
            html = html[: body_open_idx + 1] + top_marker + html[body_open_idx + 1 :]

    script = (
        "\n<script>\n"
        f"window.NBMIRROR_HOME={home_href!r};\n"
        f"window.NBMIRROR_TITLE={title!r};\n"
        f"{js}\n"
        "</script>\n"
    )

    html = html.replace("</body>", bottom_marker + script + "</body>", 1)
    return html


def build_notebook(notebook_path: Path | str, options: BuildOptions) -> Path:
    notebook = Path(notebook_path)
    repo_root = options.repo_root.resolve()

    output_path = mirror_output_path(
        notebook_path=notebook,
        repo_root=repo_root,
        notebooks_dir=options.notebooks_dir,
        output_dir=options.output_dir,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    notebook_abs = notebook if notebook.is_absolute() else (repo_root / notebook)
    notebook_abs = notebook_abs.resolve()

    nb = nbformat.read(notebook_abs, as_version=4)
    exporter = HTMLExporter(template_name="classic")
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="IPython3 lexer unavailable, falling back on Python 3",
            module="nbconvert.filters.highlight",
        )
        body, _resources = exporter.from_notebook_node(nb)

    home_href = home_link_for_output(
        output_html_path=output_path,
        repo_root=repo_root,
        home_target=options.home_target,
    )
    title = notebook_abs.stem
    rendered = _inject_shell(body, home_href=home_href, title=title)
    output_path.write_text(rendered, encoding="utf-8")

    if options.verbose:
        print(f"built: {output_path}")

    return output_path


def build_many_notebooks(notebook_paths: list[Path | str], options: BuildOptions) -> list[Path]:
    built: list[Path] = []
    for path in notebook_paths:
        path_obj = Path(path)
        if path_obj.suffix.lower() != ".ipynb":
            continue
        built.append(build_notebook(path_obj, options))
    return built
