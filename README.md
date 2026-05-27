# scaffold

Universal Python project scaffolder (uv-first, 2026 edition).
A single-file generator that creates a production-grade Python project skeleton.

## Quick start

```bash
# Default — uv mode. Creates folder, git inits, runs `uv sync`.
python setup_project.py myproject

# With ML pipeline submodules
python setup_project.py collision_detection --modules detection,tracking,risk,ui

# Plain venv + pip (no uv)
python setup_project.py myproject --no-uv

# Just write files (no install, no git)
python setup_project.py myproject --no-git --no-venv
```

> The script itself uses only stdlib, so **no venv activation is required to run it**.
> If `uv` is installed, the script auto-calls `uv lock` + `uv sync` for the generated project.

## One-liner from anywhere (zsh function)

To create projects under `~/GitStudy/<name>/` from any directory without `cd`-ing first,
add this function to `~/.zshrc`:

```zsh
# --- Python project scaffolder (GitStudy/scaffold) ---
# newpy <name> [--modules a,b,c] [--no-uv] [--no-venv] [--no-git]
#   → creates ~/GitStudy/<name>/ regardless of current directory
newpy() {
  (cd ~/GitStudy && python ~/GitStudy/scaffold/setup_project.py "$@")
}
```

Install it:

```bash
cp ~/.zshrc ~/.zshrc.backup        # safety backup
cat <<'EOF' >> ~/.zshrc

# --- Python project scaffolder (GitStudy/scaffold) ---
newpy() {
  (cd ~/GitStudy && python ~/GitStudy/scaffold/setup_project.py "$@")
}
EOF
source ~/.zshrc                    # reload in current shell
type newpy                         # verify: should show the function body
```

Then from anywhere:

```bash
newpy myproject                                    # default (uv + git + MIT)
newpy myproject --modules detection,tracking,ui    # with submodules
newpy myproject --no-uv                            # pip mode
newpy myproject --no-venv --no-git                 # files only
```

Notes:
- The `( ... )` **subshell** means the `cd` doesn't affect your current terminal.
- `"$@"` forwards all flags verbatim.
- Editing `setup_project.py` takes effect immediately — only edit `~/.zshrc` if you want to change the function itself (then `source ~/.zshrc`).

## Flags

| Flag | Default | Meaning |
|---|---|---|
| `name` (positional) | required | Project folder name. Must match `[a-zA-Z][a-zA-Z0-9_-]*`. |
| `--modules a,b,c` | `""` | Comma-separated submodules under `src/<name>/`. |
| `--no-uv` | uv mode | Use plain `python -m venv` + pip instead of uv. |
| `--no-venv` | venv on | Skip `.venv` / `uv sync` creation. |
| `--no-git` | git on | Skip `git init` + first commit. |
| `--license MIT\|NONE` | `MIT` | License file to generate. |

Run `python setup_project.py --help` to see this directly.

## What gets generated

- **pyproject.toml** — PEP 621 metadata + PEP 735 dependency-groups (dev/test/lint/notebook), tool configs for ruff/black/mypy/pytest/coverage.
- **Hygiene** — `.gitignore`, `.gitattributes` (LF), `.editorconfig`, `.python-version`, `.env.example`.
- **Dev tooling** — `.pre-commit-config.yaml` (ruff, black, nbstripout, nbqa), self-documenting `Makefile`.
- **GitHub automation** — CI workflow (matrix on 3.11/3.12, Linux/Mac/Win), PR/issue templates, CODEOWNERS, dependabot.
- **src-layout package** — `src/<name>/__init__.py` (no side effects), `__main__.py`, `cli.py` (typer + loguru), `config.py` (pydantic-settings).
- **Tests** — smoke + CLI tests with shared `conftest.py`.
- **Docs** — README with badges, CHANGELOG (Keep a Changelog), `docs/architecture.md`, `docs/cross-platform.md` (Mac/Windows + CUDA), ADR template.
- **Placeholders** — `data/{raw,processed,external}/`, `models/`, `notebooks/`, `logs/`.

## After scaffolding (uv mode)

```bash
cd myproject
uv run myproject --help    # CLI is already installed
uv run pytest              # tests work out of the box
uv run jupyter lab         # notebook group is in dev deps

uv add pandas              # add a runtime dep
uv add --group test pytest-mock   # add a test-only dep
uv lock                    # regenerate lockfile
```

## Philosophy

- **src-layout** prevents accidental imports of the in-tree package vs. the installed one.
- **No import side effects** — logging is configured in the CLI callback, not `__init__.py`.
- **Publish-safe dev deps** — dev tools in `[dependency-groups]`, not `[project.optional-dependencies]`, so they don't leak into PyPI metadata.
- **Cross-platform by default** — `.gitattributes` normalizes line endings; CI matrix covers Linux/Mac/Win.
