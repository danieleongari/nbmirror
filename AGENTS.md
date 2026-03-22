# Build `nbmirror`: Python package + hook for notebook-to-HTML mirrors

You are building a complete, publishable Python repository from scratch.

## Objective

Create a Python package named **`nbmirror`** for repositories with this structure:

* `index.html` at repo root
* `notebooks/` containing Jupyter notebooks

The package must create HTML mirror pages for notebooks under `notebooks_html/`, so those pages can be linked manually from `index.html` and browsed on GitHub Pages or any static host.

This is for **Python notebooks** and must preserve rich outputs such as:

* pandas tables
* Plotly interactive charts

Do **not** depend on nbviewer, Voilà, Quarto, or any server-side runtime.

---

## Required behavior

When a notebook in `notebooks/` is committed or passed to the CLI, generate/update:

* `notebooks_html/{relative_path_from_notebooks_without_suffix}.html`

Examples:

* `notebooks/eda.ipynb` -> `notebooks_html/eda.html`
* `notebooks/sales/q1.ipynb` -> `notebooks_html/sales/q1.html`

### HTML page requirements

Each generated HTML page must:

1. Render all **Markdown cells**
2. Render all **stored outputs**
3. Hide **all code inputs by default**
4. Provide a **small per-cell toggle button** to reveal/hide that cell’s code
5. Place the toggle button on the **right side**, visually associated with the corresponding output/code cell area
6. Support notebooks with outputs and notebooks without outputs
7. Include a **Home** button at the **top** and **bottom**
8. Make Home link back to the repo root `index.html` with the correct relative path
9. Work as a **static HTML page** without a Python server
10. Preserve **Plotly interactivity**
11. Preserve **pandas table rendering**

### Important behavior details

* Use the notebook’s **already stored outputs**
* Do **not execute notebooks by default**
* The generated report should look clean, simple, and notebook-like
* Use minimal inline JS/CSS where needed
* Toggling code must be **per cell**, not global
* Buttons should be accessible with `aria-expanded`

---

## Packaging and installation requirements

Implement this as a proper Python package named **`nbmirror`**.

### Must support two hook modes

#### 1. Plain Git hook installer

Provide a CLI command:

```bash
nbmirror install-hook
```

This installs a Git `pre-commit` hook into `.git/hooks/pre-commit` for the current repo.

#### 2. `pre-commit` framework integration

Ship:

* `.pre-commit-hooks.yaml`

and document usage from `.pre-commit-config.yaml`.

### Important note on commit-time file generation

Because hooks may modify tracked files, implement behavior that works cleanly in practice and document it clearly. If a framework-managed hook modifies files and causes a nonzero exit requiring re-stage/re-commit, document that honestly in the README.

---

## CLI requirements

Expose a console script named **`nbmirror`**.

Implement these subcommands:

```bash
nbmirror build NOTEBOOK.ipynb
nbmirror build-many NOTEBOOK1.ipynb NOTEBOOK2.ipynb ...
nbmirror install-hook
```

Support these options where relevant:

* `--repo-root`
* `--notebooks-dir` (default: `notebooks`)
* `--output-dir` (default: `notebooks_html`)
* `--home-target` (default: `index.html`)
* `--verbose`

### CLI semantics

* `build` builds one notebook
* `build-many` builds only the notebooks explicitly passed
* Hook mode should rebuild only the notebooks received from Git / pre-commit
* Ignore non-notebook files safely
* Create output directories as needed

---

## Technical implementation requirements

Use:

* `nbformat`
* `nbconvert`
* custom Jinja template and/or robust HTML post-processing
* Python packaging with `pyproject.toml`

Strong preference:

* export via **`nbconvert`**
* customize HTML output to inject:

  * hidden code blocks
  * per-cell toggle buttons
  * top/bottom Home buttons
* avoid fragile hacks if a cleaner template-based approach is possible

Do **not** hand-roll notebook rendering from raw notebook JSON unless necessary.

Use **vanilla JavaScript** and **minimal CSS**.

Do not use browser automation.

---

## Repository structure to create

Create a full repo using `src/` layout, with at least:

* `pyproject.toml`
* `README.md`
* `LICENSE`
* `.gitignore`
* `.pre-commit-hooks.yaml`
* `src/nbmirror/__init__.py`
* `src/nbmirror/cli.py`
* `src/nbmirror/builder.py`
* `src/nbmirror/paths.py`
* `src/nbmirror/hook_install.py`
* `src/nbmirror/git_hook.py`
* `src/nbmirror/templates/...`
* `tests/...`
* `examples/...`

You may add more files if useful.

---

## Path and link rules

### Mirror path mapping

Map notebook paths relative to `notebooks/` into `notebooks_html/`, replacing `.ipynb` with `.html`.

### Home link generation

The Home button must always point to repo-root `index.html` with the correct relative path from the generated page.

Examples:

* `notebooks_html/a.html` -> `../index.html`
* `notebooks_html/sub/b.html` -> `../../index.html`

Implement and test this carefully.

---

## Rendering UX requirements

### Code hiding / reveal

For each code cell:

* code input is hidden initially
* a compact toggle button is rendered near that cell’s visible output area
* clicking it expands/collapses only that code cell
* the page must remain readable even when many code cells are present

For cells with no output:

* still show a compact toggle control associated with that cell

For Markdown-only notebooks:

* still generate a valid page with Home buttons

---

## Plotly and pandas requirements

The export must preserve:

* Plotly interactive charts in the final HTML
* pandas tables rendered as notebook output

Use at least one example notebook and at least one test that verifies markers indicating those outputs are present.

Do not break JS-based interactivity during export.

---

## Testing requirements

Write automated tests covering at minimum:

1. notebook path -> HTML path mapping
2. relative Home link generation
3. output directories are created correctly
4. top and bottom Home buttons exist
5. generated HTML contains per-cell toggle buttons
6. code is hidden by default
7. Markdown is present in output HTML
8. pandas table output is preserved
9. Plotly output markers are preserved
10. CLI build command works on a fixture notebook
11. build-many processes only passed notebooks
12. hook-related file filtering behaves correctly

Use `pytest`.

Add at least one integration-style fixture notebook.

---

## README requirements

The README must be strong enough for a public GitHub repo. Include:

* what `nbmirror` is
* why it exists
* expected repo structure
* installation instructions
* CLI usage examples
* how to install the plain Git pre-commit hook
* how to use with the `pre-commit` framework
* an example `.pre-commit-config.yaml`
* behavior notes about generated files
* note that notebooks are **not executed by default**
* note that output HTML is for static hosting / GitHub Pages
* limitations and design tradeoffs

---

## Code quality requirements

* Python 3.10+ unless you need a different minimum version; choose sensibly and document it
* clear function boundaries
* type hints where appropriate
* robust path handling with `pathlib`
* clean error messages
* sensible exit codes from CLI
* avoid unnecessary dependencies
* keep the implementation publishable and maintainable

---

## Acceptance criteria

The repository is complete only if all of these are true:

1. `pip install -e .` provides a working `nbmirror` command
2. `nbmirror build notebooks/example.ipynb` creates the expected HTML mirror
3. Markdown and stored outputs render
4. Code inputs are hidden by default
5. Each code cell has its own reveal toggle
6. Plotly remains interactive
7. pandas tables display correctly
8. Home buttons exist at top and bottom
9. Home links are correct for nested paths
10. tests pass
11. README is complete
12. repo is ready to publish on GitHub

---

## Output format for your response

Return the result in this exact structure:

### 1. Repository tree

Show the full tree.

### 2. Complete file contents

Provide the full content of **every file**.

### 3. Run instructions

Show exact commands to:

* create a venv
* install the package
* run tests
* build example notebook mirrors
* install the Git hook

### 4. Design notes

Give a short explanation of the implementation choices.

Do **not** return pseudocode.
Do **not** omit file contents.
Return a complete working repository.

---

## Implementation hints

Use these only if helpful:

* subclass or configure `nbconvert.HTMLExporter`
* use a custom template to control code/input rendering
* inject compact JS handlers for per-cell expand/collapse
* ensure Plotly script/output survives export
* compute relative Home links with `os.path.relpath` or `pathlib`
* keep generated HTML deterministic where possible for testability

---

## Final instruction

Build the complete `nbmirror` repository now.
