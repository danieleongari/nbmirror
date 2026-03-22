# nbmirror

nbmirror builds static HTML mirror pages for Jupyter notebooks in repositories that use a simple structure:

- `index.html` at repository root
- notebooks under `notebooks/`
- generated mirrors under `notebooks_html/`

It is designed for static hosting such as GitHub Pages. It does not run a Python server, and it does not execute notebooks by default.

## Why

Notebook links in static sites are awkward to maintain when you want rendered pages with rich outputs. nbmirror converts stored notebook outputs into browsable HTML pages that can be linked from your root `index.html`.

In the past I used [nbviewer](https://nbviewer.org/) a for this purpose, but recently it very often gives `503 Error: Service Unavailable / GitHub API rate limit exceeded. Try Again Later`.

Also, I prefer to have the possibility to hide the code of the notebooks, for a lean reading experience.

## Expected repository layout

```text
.
├─ index.html
├─ notebooks/
│  └─ ... .ipynb
└─ notebooks_html/
   └─ ... .html (generated)
```

## Features

- Maps notebook paths to stable mirror paths:
  - `notebooks/eda.ipynb` -> `notebooks_html/eda.html`
  - `notebooks/sales/q1.ipynb` -> `notebooks_html/sales/q1.html`
- Preserves markdown cells and stored outputs
- Keeps code hidden by default
- Adds per-cell code toggle controls with `aria-expanded`
- Adds Home buttons at top and bottom of each page
- Computes correct relative Home links back to root `index.html`
- Preserves rich outputs such as pandas HTML tables and Plotly output content

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

## CLI usage

```bash
nbmirror build notebooks/nb_example.ipynb
nbmirror build-many notebooks/a.ipynb notebooks/sub/b.ipynb
nbmirror install-hook
```

Options (where relevant):

- `--repo-root` (default: `.`)
- `--notebooks-dir` (default: `notebooks`)
- `--output-dir` (default: `notebooks_html`)
- `--home-target` (default: `index.html`)
- `--verbose`

Examples:

```bash
nbmirror build notebooks/sales/q1.ipynb --verbose
nbmirror build-many notebooks/a.ipynb notebooks/b.ipynb --output-dir notebooks_html
```

## Plain Git hook installation

Install a pre-commit hook directly into `.git/hooks/pre-commit`:

```bash
nbmirror install-hook
```

Behavior:

- The hook rebuilds mirrors only for staged notebook paths.
- If generated mirror files are updated, the hook auto-stages `notebooks_html/` changes and exits nonzero.
- Re-run the same commit command once; the second attempt should pass with staged mirror updates included.

## pre-commit framework integration

This repository ships `.pre-commit-hooks.yaml` with hook id `nbmirror`.

Example `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/your-org/nbmirror
    rev: v0.1.0
    hooks:
      - id: nbmirror
        args: ["--repo-root", "."]
```

Note on generated files:

- Framework-managed hooks that modify files generally require re-stage/re-commit. That is expected.

## Static hosting notes

Generated HTML pages are static files suitable for GitHub Pages and similar hosts.

## Limitations and tradeoffs

- Notebooks are not executed. Only stored outputs are rendered.
- Deleted notebooks do not automatically remove stale mirror HTML files.
- Layout and toggle behavior are intentionally minimal to keep generated pages deterministic and maintainable.

## Development

```bash
pytest
```
