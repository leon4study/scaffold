"""
Universal Python project scaffolder (uv-first, 2026 edition).

────────────────────────────────────────────────────────────────────────────
WHAT THIS SCRIPT DOES
────────────────────────────────────────────────────────────────────────────
Generates a production-grade Python project skeleton in a new folder, with:

  • pyproject.toml
        - PEP 621 [project] metadata (name, version, deps, etc.)
        - PEP 735 [dependency-groups] for dev/test/lint/notebook (publish-safe)
        - [tool.uv]/[tool.coverage]/[tool.ruff]/[tool.black]/[tool.mypy]
  • Editor / VCS hygiene
        - .gitignore, .gitattributes (LF normalization), .editorconfig
        - .python-version (read by uv/pyenv)
        - .env.example
  • Dev tooling
        - .pre-commit-config.yaml (ruff, black, nbstripout, nbqa, std hooks)
        - Makefile with a self-documenting `help` target
  • GitHub automation
        - .github/workflows/ci.yml (matrix on Python 3.11/3.12, with cache &
          concurrency-cancel)
        - PR template, issue templates (bug/feature)
        - CODEOWNERS, dependabot.yml
  • Source layout (src-layout)
        - src/<name>/__init__.py    (no import side-effects)
        - src/<name>/__main__.py    (so `python -m <name>` works)
        - src/<name>/cli.py         (typer + loguru, logging set in callback)
        - src/<name>/config.py      (pydantic-settings)
        - Optional pipeline submodules via --modules
  • Tests
        - tests/test_smoke.py       (package import / config load)
        - tests/test_cli.py         (typer CliRunner)
        - tests/conftest.py         (shared fixtures)
  • Docs
        - README.md (with badges)
        - CHANGELOG.md (Keep a Changelog format)
        - docs/architecture.md
        - docs/cross-platform.md (Mac/Windows/Linux + CUDA recipes)
        - docs/adr/0001-record-architecture-decisions.md
  • Data / models / notebooks placeholders
        - data/{raw,processed,external}/.gitkeep, models/, notebooks/, logs/
  • Optional automation:
        - git init + first commit
        - uv sync (creates .venv + installs dev deps + generates uv.lock)
        - pre-commit install

────────────────────────────────────────────────────────────────────────────
USAGE
────────────────────────────────────────────────────────────────────────────
    # Default (uv mode — recommended). Creates folder, git inits, runs `uv sync`.
    python setup_project.py myproject

    # Add ML pipeline submodules under src/myproject/
    python setup_project.py collision_detection \\
        --modules detection,tracking,risk,ui

    # Plain venv + pip mode (no uv). Useful in conda-only or air-gapped envs.
    python setup_project.py myproject --no-uv

    # Skip auto-install entirely (just write files + git init).
    python setup_project.py myproject --no-venv

    # Skip git init too (just write files).
    python setup_project.py myproject --no-git --no-venv

    # No license file.
    python setup_project.py myproject --license NONE

────────────────────────────────────────────────────────────────────────────
FLAGS
────────────────────────────────────────────────────────────────────────────
    name              Project folder name (positional). Validated as
                      [a-zA-Z][a-zA-Z0-9_-]*.
    --modules X,Y,Z   Comma-separated submodules under src/<name>/.
    --no-uv           Use plain `python -m venv` + pip instead of uv.
    --no-venv         Skip venv / uv-sync creation entirely.
    --no-git          Skip `git init` + first commit.
    --license MIT|NONE  License file (default: MIT).

────────────────────────────────────────────────────────────────────────────
RESULT WORKFLOW (uv mode)
────────────────────────────────────────────────────────────────────────────
After this script finishes:
    cd <name>
    uv run <name> --help    # CLI is already installed
    uv run pytest           # tests work out of the box
    uv run jupyter lab      # notebooks (notebook group is in dev deps)

To add a dependency later:
    uv add pandas           # runtime dep
    uv add --group test pytest-mock   # test-only dep

To regenerate the lockfile:
    uv lock

────────────────────────────────────────────────────────────────────────────
PHILOSOPHY
────────────────────────────────────────────────────────────────────────────
- src-layout (code under src/<name>/) — prevents accidental imports of
  the in-tree package vs the installed one.
- No import side effects — importing the package does NOT touch the
  filesystem (logging is set up in the CLI callback, not __init__.py).
- Publish-safe dev deps — dev tools live in [dependency-groups], NOT in
  [project.optional-dependencies], so they don't leak into PyPI metadata.
- Cross-platform by default — .gitattributes normalizes line endings;
  pathlib everywhere; CI runs on Linux/macOS/Windows.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

PYTHON_VERSION = "3.11"  # Pinned via .python-version; uv auto-installs this.
DEFAULT_AUTHOR_NAME = "Your Name"
DEFAULT_AUTHOR_EMAIL = "you@example.com"


# --------------------------------------------------------------------------- #
# Helpers — environment detection
#   Read git config / current year / uv presence, with safe fallbacks so the
#   scaffolder works on machines that don't have git or uv installed.
# --------------------------------------------------------------------------- #

def detect_git_user() -> tuple[str, str]:
    """Read user.name / user.email from `git config --global` (or local).

    Falls back to placeholder strings if git is missing or no config is set,
    so users can still run the scaffolder cleanly. Returns (name, email).
    """
    name = DEFAULT_AUTHOR_NAME
    email = DEFAULT_AUTHOR_EMAIL
    for key, default in (("user.name", name), ("user.email", email)):
        try:
            result = subprocess.run(
                ["git", "config", "--get", key],
                capture_output=True, text=True, check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                if key == "user.name":
                    name = result.stdout.strip()
                else:
                    email = result.stdout.strip()
        except FileNotFoundError:
            # git not installed — fall back to defaults.
            pass
    return name, email


def current_year() -> int:
    """Year for LICENSE / copyright lines (so it's never frozen)."""
    return datetime.datetime.now().year


def have_uv() -> bool:
    """Check if `uv` is on PATH. Used to decide install mode + give hints."""
    return shutil.which("uv") is not None


# --------------------------------------------------------------------------- #
# File content templates
#   Each tpl_* function returns the *content* of one file. They are pure
#   string generators — no I/O — so they are easy to unit-test.
#
#   Why f-strings: keeps templates inline and readable. The trade-off is
#   that literal `{` / `}` in the output must be doubled (`{{` / `}}`).
# --------------------------------------------------------------------------- #

def tpl_pyproject(name: str, author_name: str, author_email: str) -> str:
    """Generate pyproject.toml.

    Key choices:
      - [dependency-groups] (PEP 735) for dev tools — these don't leak into
        the published wheel's METADATA, unlike [project.optional-dependencies].
      - [project.optional-dependencies] is left commented out, reserved for
        true user-facing extras (e.g. gpu/cpu/plotting backends).
      - [tool.uv].default-groups = ["dev"] so `uv sync` picks up dev deps
        automatically — new contributors only need one command.
      - Tool versions use `>=` minimums so `uv sync` always resolves the
        latest compatible release. Pin via uv.lock for reproducibility.
    """
    py_target = PYTHON_VERSION.replace(".", "")
    return f"""[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

# ────────────────────────────────────────────────────────────────────────
# Project metadata (PEP 621 — read by every modern Python tool)
# ────────────────────────────────────────────────────────────────────────
[project]
name = "{name}"
version = "0.1.0"
description = "{name} project"
readme = "README.md"
requires-python = ">={PYTHON_VERSION}"
license = {{ text = "MIT" }}
authors = [{{ name = "{author_name}", email = "{author_email}" }}]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: MIT License",
]

# Runtime dependencies (always installed for the package's users).
# Add data/ML libraries here as the project actually needs them — keep
# the install footprint small for users who don't need everything.
dependencies = [
    "loguru>=0.7",                   # structured logging
    "pydantic-settings>=2.0",        # typed settings via .env / env vars
    "typer>=0.12",                   # CLI framework (built on click)
    # --- Data analysis (uncomment as needed) ---------------------------
    # "pandas>=2.2",
    # "numpy>=1.26",
    # "matplotlib>=3.8",
    # "seaborn>=0.13",
    # "scikit-learn>=1.4",
    # --- Deep learning (CUDA/CPU pattern: see docs/cross-platform.md) --
    # "torch>=2.2",
]

# ────────────────────────────────────────────────────────────────────────
# Optional extras for END USERS (DON'T put dev tools here — they'd leak
# into the wheel's METADATA on publish). Uncomment when you have real
# user-facing toggles like GPU support, S3 backend, etc.
# See docs/cross-platform.md for the CUDA/CPU torch pattern using uv sources.
# ────────────────────────────────────────────────────────────────────────
# [project.optional-dependencies]
# gpu = ["torch>=2.2"]
# cpu = ["torch>=2.2"]

# Project URLs surface on PyPI and GitHub. Fill the placeholders before
# publishing. Commented for now so the file is valid even with no remote.
# [project.urls]
# Homepage   = "https://github.com/<USER>/{name}"
# Repository = "https://github.com/<USER>/{name}"
# Issues     = "https://github.com/<USER>/{name}/issues"

# Console script registered on install (e.g. `make_portfolio --help`).
[project.scripts]
{name} = "{name}.cli:app"

# ────────────────────────────────────────────────────────────────────────
# Dependency groups (PEP 735 — supported by uv / pdm / hatch / pip 25.1+).
# These NEVER end up in the published wheel. `include-group` enables
# composition (dev = test + lint + notebook + extras).
# ────────────────────────────────────────────────────────────────────────
[dependency-groups]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-randomly>=3.15",         # randomize test order to surface hidden coupling
]
lint = [
    "ruff>=0.8",                     # fast linter + formatter (Astral)
    "black>=24.10",                  # canonical formatter
    "mypy>=1.13",                    # static type checker
]
notebook = [
    "jupyter>=1.0",
    "ipykernel>=6.29",
    "nbqa>=1.8",                     # run ruff/black on .ipynb files
    "nbstripout>=0.7",               # strip outputs before commit
]
dev = [
    {{include-group = "test"}},
    {{include-group = "lint"}},
    {{include-group = "notebook"}},
    "pre-commit>=3.7",
]

# uv-specific config: `uv sync` (no flags) installs the dev group by default,
# so first-time contributors only need one command.
[tool.uv]
default-groups = ["dev"]

# ────────────────────────────────────────────────────────────────────────
# Tool configurations
# ────────────────────────────────────────────────────────────────────────
[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py{py_target}"

[tool.ruff.lint]
# E/F = pycodestyle/pyflakes; I = isort; B = bugbear; UP = pyupgrade; SIM = simplify
select = ["E", "F", "I", "B", "UP", "SIM"]
ignore = ["E501"]                    # line-length is handled by formatter

[tool.black]
line-length = 100
target-version = ["py{py_target}"]

[tool.mypy]
python_version = "{PYTHON_VERSION}"
strict = false                       # Start lax; tighten as the codebase matures.
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --cov=src --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
branch = true                        # measure branch coverage too

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
show_missing = true
fail_under = 0                       # raise this once you add real tests
"""


def tpl_gitignore() -> str:
    """Standard Python + project-specific ignores. Excludes ML artifacts
    (*.pt/*.pkl/*.onnx) and dataset directories by default."""
    return """# --- Python ---------------------------------------------------------
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# --- Virtualenv -----------------------------------------------------
.venv/
venv/
env/

# --- Tooling --------------------------------------------------------
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.tox/
.ipynb_checkpoints/

# --- IDEs -----------------------------------------------------------
.vscode/
.idea/
*.swp
*.swo

# --- OS -------------------------------------------------------------
.DS_Store
Thumbs.db

# --- Project --------------------------------------------------------
.env
data/raw/*
data/processed/*
data/external/*
!data/**/.gitkeep
models/*
!models/.gitkeep
logs/
wandb/
mlruns/
*.pt
*.pkl
*.onnx
"""


def tpl_gitattributes() -> str:
    """Force LF line endings on text files; mark known binaries as binary
    so git doesn't try to diff or normalize them."""
    return """# Auto-detect text files and normalize line endings to LF
* text=auto eol=lf

# Windows-only scripts keep CRLF
*.cmd  text eol=crlf
*.bat  text eol=crlf
*.ps1  text eol=crlf

# Binary files (no diff/normalization)
*.png   binary
*.jpg   binary
*.jpeg  binary
*.gif   binary
*.ico   binary
*.pdf   binary
*.zip   binary
*.gz    binary
*.tar   binary
*.mp4   binary
*.mov   binary
*.pt    binary
*.pkl   binary
*.onnx  binary
*.h5    binary
*.parquet binary
"""


def tpl_editorconfig() -> str:
    """Editor-agnostic style baseline (indentation, charset, EOL).
    Read by VSCode, JetBrains, Vim, etc."""
    return """root = true

[*]
indent_style = space
indent_size = 4
charset = utf-8
end_of_line = lf
trim_trailing_whitespace = true
insert_final_newline = true

[*.{yml,yaml,json,md}]
indent_size = 2

[Makefile]
indent_style = tab
"""


def tpl_env_example() -> str:
    """Template for .env (gitignored). LOG_DIR is opt-in to avoid creating
    a logs/ folder by default — only when the user explicitly enables it."""
    return """# Copy this file to `.env` and fill in your values.
# `.env` is gitignored; never commit secrets.

DATA_PATH=./data
MODEL_PATH=./models
LOG_LEVEL=INFO
# LOG_DIR=./logs   # uncomment to enable file logging
"""


def tpl_python_version() -> str:
    """Pin Python version. uv reads this and auto-installs the right Python."""
    return f"{PYTHON_VERSION}\n"


def tpl_readme(name: str, use_uv: bool) -> str:
    """README with status badges and install/usage instructions appropriate
    to the chosen install mode (uv vs pip)."""
    if use_uv:
        install_block = """```bash
# 1) Install uv if not already (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh         # macOS / Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# 2) Sync (creates .venv automatically + installs dev deps + writes uv.lock)
uv sync

# 3) Install pre-commit hook
uv run pre-commit install
```"""
        run_block = f"""```bash
uv run {name} --help        # CLI
uv run pytest               # tests
uv run jupyter lab          # notebooks (notebook group is in dev deps)
```"""
    else:
        install_block = f"""```bash
# 1) Python {PYTHON_VERSION} (use pyenv if needed)
python3 --version

# 2) Virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\\Scripts\\activate          # Windows PowerShell

# 3) Install (pip 25.1+ for --group; otherwise upgrade pip first)
python -m pip install --upgrade pip
pip install -e .
pip install --group dev
pre-commit install
```"""
        run_block = f"""```bash
{name} --help
pytest
```"""

    return f"""# {name}

> One-line description goes here.

[![CI](https://github.com/<USER>/{name}/actions/workflows/ci.yml/badge.svg)](https://github.com/<USER>/{name}/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-{PYTHON_VERSION}%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000)
![Linter: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

## Setup

{install_block}

## Usage

{run_block}

## Development

```bash
make help       # list all available targets
make test       # run tests
make lint       # ruff + mypy
make format     # black + ruff --fix
```

## Cross-platform notes

See [docs/cross-platform.md](docs/cross-platform.md) for Mac/Windows compatibility and CUDA setup.

## License

MIT
"""


def tpl_license_mit(author_name: str, year: int) -> str:
    """MIT license body with detected author + current year."""
    return f"""MIT License

Copyright (c) {year} {author_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def tpl_changelog() -> str:
    """Keep a Changelog format. Update [Unreleased] as you make changes;
    move entries under a versioned heading on release."""
    return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold.
"""


def tpl_makefile(use_uv: bool) -> str:
    """Self-documenting Makefile. `make help` lists targets via grep+awk
    over `## ` doc-comments. Recipes use `uv run` (uv mode) or activate
    instructions (pip mode)."""
    if use_uv:
        return f""".PHONY: help setup install test lint format clean

help:  ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  %-12s %s\\n", $$1, $$2}}'

setup:  ## Sync deps + install pre-commit hook
\tuv sync
\tuv run pre-commit install

install:  ## Sync dependencies (idempotent)
\tuv sync

test:  ## Run tests with coverage
\tuv run pytest

lint:  ## Run ruff + mypy
\tuv run ruff check src tests
\tuv run mypy src

format:  ## Format with black + ruff --fix
\tuv run black src tests
\tuv run ruff check --fix src tests

clean:  ## Remove caches and build artifacts
\trm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {{}} +
"""
    return f""".PHONY: help setup install test lint format clean

help:  ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  %-12s %s\\n", $$1, $$2}}'

setup:  ## Create venv + install dev deps + pre-commit hook
\tpython3 -m venv .venv
\t. .venv/bin/activate && pip install --upgrade pip && pip install -e . && pip install --group dev && pre-commit install

install:  ## Install/refresh dependencies (in active venv)
\tpip install -e . && pip install --group dev

test:  ## Run tests
\tpytest

lint:  ## Run ruff + mypy
\truff check src tests
\tmypy src

format:  ## Format with black + ruff --fix
\tblack src tests
\truff check --fix src tests

clean:  ## Remove caches and build artifacts
\trm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {{}} +
"""


def tpl_precommit() -> str:
    """Pre-commit hooks: standard hygiene + ruff/black + notebook hygiene
    (nbstripout strips outputs, nbqa applies ruff/black to .ipynb cells)."""
    return """# Run on every git commit. Update with: pre-commit autoupdate
repos:
  # ── Standard hygiene ────────────────────────────────────────────────
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=10240"]
      - id: check-merge-conflict
      - id: mixed-line-ending
        args: ["--fix=lf"]

  # ── Ruff (lint + format) ────────────────────────────────────────────
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  # ── Black (formatting; redundant-but-harmless with ruff-format) ─────
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  # ── Notebook output stripping (prevents diff explosions) ────────────
  - repo: https://github.com/kynan/nbstripout
    rev: 0.8.1
    hooks:
      - id: nbstripout

  # ── Ruff/Black on notebook code cells (consistency with .py files) ──
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.9.1
    hooks:
      - id: nbqa-ruff
        args: ["--fix"]
      - id: nbqa-black
"""


def tpl_pr_template() -> str:
    """Pull-request body template, surfaced by GitHub on PR creation."""
    return """## What
<!-- 무엇이 바뀌나 (1-3줄) -->

## Why
<!-- 왜 필요한가 -->

## How to test
- [ ] ...

## Checklist
- [ ] 테스트 추가/갱신
- [ ] 문서 업데이트
- [ ] CHANGELOG.md `[Unreleased]`에 항목 추가
- [ ] Conventional Commits 형식의 커밋 메시지
"""


def tpl_issue_bug() -> str:
    """Bug report issue template."""
    return """---
name: Bug report
about: Report something that's broken
labels: bug
---

## Description
<!-- 무엇이 잘못됐나 -->

## Reproduction
1.
2.
3.

## Expected vs Actual
- Expected:
- Actual:

## Environment
- OS:
- Python version:
- Package version:
"""


def tpl_issue_feature() -> str:
    """Feature request issue template."""
    return """---
name: Feature request
about: Propose a new feature or improvement
labels: enhancement
---

## Problem
<!-- 어떤 문제를 해결하려고 하나 -->

## Proposed solution
<!-- 어떻게 해결할 것인가 -->

## Alternatives considered
"""


def tpl_codeowners() -> str:
    """CODEOWNERS makes GitHub auto-request reviews from listed handles
    when a matched file changes. Edit handles before pushing."""
    return """# Default reviewers for everything (edit team handles before pushing)
# *       @your-team

# Per-area ownership examples
# /src/{name}/detection/   @teammate-a
# /src/{name}/tracking/    @teammate-b
# /docs/                   @your-username
"""


def tpl_dependabot() -> str:
    """Dependabot watches for outdated deps and opens PRs to bump them."""
    return """version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
"""


def tpl_ci_workflow(use_uv: bool) -> str:
    """GitHub Actions CI: lint + type check + test on Linux/Mac/Win matrix.

    Optimizations:
      - `concurrency:` cancels superseded runs on the same branch (saves CI minutes).
      - uv mode uses astral-sh/setup-uv with built-in cache (much faster than pip).
      - pre-commit cache shaves seconds on repeated runs.
    """
    if use_uv:
        return f"""name: CI

on:
  push:
    branches: [main]
  pull_request:

# Cancel earlier runs on the same branch when a new one starts.
concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  lint-test:
    runs-on: ${{{{ matrix.os }}}}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["{PYTHON_VERSION}", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install ${{{{ matrix.python-version }}}}

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Cache pre-commit
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{{{ runner.os }}}}-${{{{ hashFiles('.pre-commit-config.yaml') }}}}

      - name: Lint (ruff)
        run: uv run ruff check src tests

      - name: Type check (mypy)
        run: uv run mypy src

      - name: Test (pytest)
        run: uv run pytest
"""
    return f"""name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  lint-test:
    runs-on: ${{{{ matrix.os }}}}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["{PYTHON_VERSION}", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: pip

      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install --group dev

      - name: Cache pre-commit
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{{{ runner.os }}}}-${{{{ hashFiles('.pre-commit-config.yaml') }}}}

      - name: Lint (ruff)
        run: ruff check src tests

      - name: Type check (mypy)
        run: mypy src

      - name: Test (pytest)
        run: pytest
"""


def tpl_init(name: str) -> str:
    """Package __init__.py.

    Intentionally minimal — NO logging setup, NO filesystem touches. Importing
    the package must not have side effects (otherwise tests, REPL inspection,
    and downstream importers misbehave). Logging is configured in cli.py.
    """
    return f'''"""Top-level package for {name}."""

__version__ = "0.1.0"
'''


def tpl_main(name: str) -> str:
    """__main__.py: enables `python -m {name}` as an alternative to the
    console-script entry point."""
    return f'''"""Entry point for `python -m {name}`."""

from {name}.cli import app

if __name__ == "__main__":
    app()
'''


def tpl_config(name: str) -> str:
    """Pydantic-settings model loaded from environment / .env.

    Why pydantic-settings: type validation + .env support + clear
    documentation of all configurable knobs in one place.
    """
    return f'''"""Application configuration loaded from environment / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized config. Override via environment variables or `.env` file.

    Field names map case-insensitively to env vars:
      project_name → PROJECT_NAME, log_level → LOG_LEVEL, etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    project_name: str = "{name}"
    log_level: str = "INFO"
    log_dir: Path | None = None        # set to enable file logging
    data_path: Path = Path("./data")
    model_path: Path = Path("./models")


# Singleton — import this everywhere instead of constructing Settings yourself.
settings = Settings()
'''


def tpl_cli(name: str) -> str:
    """Typer-based CLI.

    Logging is configured in a typer @app.callback() so it runs before any
    command but only when the CLI is actually invoked — keeps `import {name}`
    side-effect-free.
    """
    return f'''"""Command-line interface for {name}."""

import sys

import typer
from loguru import logger

from {name}.config import settings


def setup_logging() -> None:
    """Configure loguru sinks based on settings. Called from app callback."""
    logger.remove()                     # drop the default sink
    logger.add(
        sys.stderr,
        format=(
            "<green>{{time:YYYY-MM-DD HH:mm:ss}}</green> | "
            "<level>{{level:<8}}</level> | "
            "<cyan>{{name}}</cyan> - <level>{{message}}</level>"
        ),
        level=settings.log_level,
    )
    if settings.log_dir is not None:
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(
            settings.log_dir / "{name}_{{time:YYYY-MM-DD}}.log",
            rotation="00:00",
            retention="30 days",
            encoding="utf-8",
            level="DEBUG",
        )


app = typer.Typer(help="{name} CLI")


@app.callback()
def _bootstrap() -> None:
    """Runs before every subcommand — initialize logging here."""
    setup_logging()


@app.command()
def info() -> None:
    """Print runtime configuration."""
    logger.info(f"Project: {{settings.project_name}}")
    logger.info(f"Data path: {{settings.data_path}}")
    logger.info(f"Model path: {{settings.model_path}}")


@app.command()
def hello(name: str = "world") -> None:
    """Sanity-check entry point."""
    logger.info(f"Hello, {{name}}!")


if __name__ == "__main__":
    app()
'''


def tpl_test_smoke(name: str) -> str:
    """Smoke test — verifies the package can be imported and config loads.
    Catches the most basic install/path mistakes."""
    return f'''"""Smoke test — confirms package imports and config loads."""

from {name} import __version__
from {name}.config import settings


def test_version() -> None:
    assert __version__


def test_settings_loads() -> None:
    assert settings.project_name
    assert settings.log_level
'''


def tpl_test_cli(name: str) -> str:
    """CLI tests via typer's CliRunner — invokes commands in-process and
    inspects exit codes / output."""
    return f'''"""CLI tests using typer.testing.CliRunner."""

from typer.testing import CliRunner

from {name}.cli import app

runner = CliRunner()


def test_hello_command() -> None:
    result = runner.invoke(app, ["hello", "--name", "test"])
    assert result.exit_code == 0


def test_info_command() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
'''


def tpl_conftest() -> str:
    """Shared pytest fixtures live here. tmp_data_dir is one example
    pattern for tests that need filesystem state."""
    return '''"""Shared pytest fixtures (auto-discovered by pytest)."""

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Provide an isolated data directory for tests that need filesystem state."""
    d = tmp_path / "data"
    d.mkdir()
    return d
'''


def tpl_module_init(name: str, module: str) -> str:
    """One-liner __init__.py for each pipeline submodule (--modules flag)."""
    return f'"""{name}.{module} — pipeline stage."""\n'


def tpl_arch_doc(name: str) -> str:
    """Architecture overview — replace the diagram with the real design."""
    return f"""# Architecture

## Overview
High-level diagram of {name} (replace with your actual design).

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Input   │ ──▶ │ Pipeline │ ──▶ │  Output  │
└──────────┘     └──────────┘     └──────────┘
```

## Modules
- `src/{name}/__init__.py` — package metadata only (no side effects)
- `src/{name}/__main__.py` — enables `python -m {name}`
- `src/{name}/cli.py` — typer entry points + logging bootstrap
- `src/{name}/config.py` — pydantic-settings configuration

## Data flow
- `data/raw/` — read-only original inputs
- `data/processed/` — derived from raw via scripts in `src/`
- `data/external/` — third-party sources

## Decisions
See `docs/adr/` for Architecture Decision Records.
"""


def tpl_crossplatform_doc() -> str:
    """Cross-platform setup guide. Includes the CUDA/CPU torch pattern via
    uv extras — keeps backend choice explicit instead of silent."""
    return f"""# Cross-platform notes (Mac / Windows / Linux)

## Why this matters
Mac and Windows differ in:
- Line endings (LF vs CRLF) — handled by `.gitattributes`
- Path separators — always use `pathlib.Path`, never raw `/` or `\\`
- GPU backends — Mac=MPS, Windows/Linux=CUDA
- Python install paths

## Required one-time team setup

```bash
# Mac/Linux
git config --global core.autocrlf input

# Windows (in Git Bash or PowerShell)
git config --global core.autocrlf true
```

## Python {PYTHON_VERSION}

Pinned via `.python-version`. With **uv**:
```bash
uv sync                  # installs the right Python + all deps
```

Without uv:
- macOS: `brew install python@{PYTHON_VERSION}` or `pyenv install {PYTHON_VERSION}`
- Windows: from python.org installer, or `pyenv-win`
- Linux: `pyenv install {PYTHON_VERSION}`

## Device-agnostic PyTorch (if used)

```python
import torch

def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():  # Apple Silicon
        return torch.device("mps")
    return torch.device("cpu")
```

## PyTorch installation — two patterns

PyTorch is **not** in default deps. Pick the pattern that matches your team.

### Pattern 1 — uncomment in `pyproject.toml` (single-backend team)

```toml
dependencies = [
    "torch>=2.2",   # Mac MPS / Linux CPU
]
```

Then for CUDA users, install via the right index:
```bash
# CUDA 12.1
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU-only fallback
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Pattern 2 — multi-backend extras (Mac + CUDA mixed team)

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
cpu = ["torch>=2.2"]
gpu = ["torch>=2.2"]

[tool.uv]
conflicts = [[{{ extra = "cpu" }}, {{ extra = "gpu" }}]]

[tool.uv.sources]
torch = [
    {{ index = "pytorch-cpu",   extra = "cpu" }},
    {{ index = "pytorch-cu121", extra = "gpu" }},
]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true
```

Each contributor picks the right wheel:
```bash
uv sync --extra gpu     # CUDA build (Linux/Win with NVIDIA)
uv sync --extra cpu     # CPU/Mac build
```

## Heavy training

Mac MPS is slower than CUDA. For real training runs:
- Use a Windows/Linux teammate's NVIDIA GPU, or
- Use Google Colab / Lambda Labs / RunPod

Mac is fine for development, debugging, and inference.

## Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Diff shows every line changed | CRLF vs LF | Ensure `.gitattributes` committed; re-run `git add --renormalize .` |
| `\\r` in shell scripts | Saved as CRLF | Convert: `dos2unix script.sh` |
| `ModuleNotFoundError` after install | Editable install missing | `uv sync` (or `pip install -e .`) |
| YOLO/CUDA errors on Mac | Wrong torch wheel | Install Mac wheel (no `--index-url`) |
| `uv: command not found` | uv not installed | `curl -LsSf https://astral.sh/uv/install.sh | sh` |
"""


def tpl_adr_template() -> str:
    """ADR (Architecture Decision Record) — Michael Nygard's format. Each
    significant decision gets its own numbered file in docs/adr/."""
    return """# 1. Record architecture decisions

Date: 2026-01-01

## Status
Accepted

## Context
We need to document significant architectural decisions so future contributors
(including our future selves) understand *why* the project looks the way it does.

## Decision
We will use Architecture Decision Records (ADRs) as described by Michael Nygard.

## Consequences
- Each significant decision gets its own numbered file in `docs/adr/`.
- Older decisions are not rewritten; instead, a new ADR supersedes them.
"""


# --------------------------------------------------------------------------- #
# Filesystem helpers
# --------------------------------------------------------------------------- #

def write_file(path: Path, content: str) -> None:
    """Write text to disk, creating parent dirs as needed.
    Always UTF-8 to avoid Windows locale surprises."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def touch_keep(path: Path) -> None:
    """Create a `.gitkeep` so empty directories are tracked by git."""
    write_file(path / ".gitkeep", "")


# --------------------------------------------------------------------------- #
# Project creation
#   The orchestrator: writes every templated file, optionally inits git,
#   optionally creates a virtualenv (uv or plain python -m venv).
# --------------------------------------------------------------------------- #

def create_project(
    name: str,
    modules: list[str],
    do_git: bool,
    do_venv: bool,
    license_type: str,
    use_uv: bool,
) -> None:
    """Build the project tree and run optional automation.

    Order matters:
      1. write all files
      2. (uv mode) `uv lock` to generate uv.lock BEFORE first commit
      3. git init + commit (so uv.lock is in the initial commit)
      4. (uv mode) `uv sync` to create .venv + install + run pre-commit install
         (pip mode) `python -m venv` only — user installs manually
    """
    root = Path(name)
    if root.exists():
        print(f"\n[ERROR] '{name}' already exists. Refusing to overwrite.\n")
        sys.exit(1)

    # Fail fast if uv is required but missing — nothing has been written yet.
    if do_venv and use_uv and not have_uv():
        print("\n[ERROR] uv is not installed (default install mode).")
        print("  Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print('  Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"')
        print("  Or rerun with --no-uv to use plain venv + pip.\n")
        sys.exit(1)

    print(f"\n[setup] Creating '{name}'...")

    author_name, author_email = detect_git_user()
    year = current_year()

    # ---- core files ------------------------------------------------------
    write_file(root / "pyproject.toml", tpl_pyproject(name, author_name, author_email))
    write_file(root / ".gitignore", tpl_gitignore())
    write_file(root / ".gitattributes", tpl_gitattributes())
    write_file(root / ".editorconfig", tpl_editorconfig())
    write_file(root / ".env.example", tpl_env_example())
    write_file(root / ".python-version", tpl_python_version())
    write_file(root / "README.md", tpl_readme(name, use_uv))
    write_file(root / "CHANGELOG.md", tpl_changelog())
    write_file(root / "Makefile", tpl_makefile(use_uv))
    write_file(root / ".pre-commit-config.yaml", tpl_precommit())
    if license_type.upper() == "MIT":
        write_file(root / "LICENSE", tpl_license_mit(author_name, year))

    # ---- GitHub automation ----------------------------------------------
    write_file(root / ".github" / "PULL_REQUEST_TEMPLATE.md", tpl_pr_template())
    write_file(root / ".github" / "ISSUE_TEMPLATE" / "bug_report.md", tpl_issue_bug())
    write_file(root / ".github" / "ISSUE_TEMPLATE" / "feature_request.md", tpl_issue_feature())
    write_file(root / ".github" / "CODEOWNERS", tpl_codeowners())
    write_file(root / ".github" / "dependabot.yml", tpl_dependabot())
    write_file(root / ".github" / "workflows" / "ci.yml", tpl_ci_workflow(use_uv))

    # ---- src layout (the package itself) --------------------------------
    pkg = root / "src" / name
    write_file(pkg / "__init__.py", tpl_init(name))
    write_file(pkg / "__main__.py", tpl_main(name))
    write_file(pkg / "config.py", tpl_config(name))
    write_file(pkg / "cli.py", tpl_cli(name))

    for module in modules:
        write_file(pkg / module / "__init__.py", tpl_module_init(name, module))

    # ---- tests -----------------------------------------------------------
    write_file(root / "tests" / "__init__.py", "")
    write_file(root / "tests" / "conftest.py", tpl_conftest())
    write_file(root / "tests" / "test_smoke.py", tpl_test_smoke(name))
    write_file(root / "tests" / "test_cli.py", tpl_test_cli(name))

    # ---- docs ------------------------------------------------------------
    write_file(root / "docs" / "architecture.md", tpl_arch_doc(name))
    write_file(root / "docs" / "cross-platform.md", tpl_crossplatform_doc())
    write_file(root / "docs" / "adr" / "0001-record-architecture-decisions.md", tpl_adr_template())

    # ---- data / models / notebooks placeholders -------------------------
    for sub in ("raw", "processed", "external"):
        touch_keep(root / "data" / sub)
    touch_keep(root / "models")
    touch_keep(root / "notebooks")
    touch_keep(root / "logs")

    print("[setup] Files written.")

    # ---- uv lock (before git, so uv.lock is in initial commit) ----------
    if do_venv and use_uv:
        try:
            subprocess.run(["uv", "lock"], cwd=root, check=True, capture_output=True)
            print("[setup] uv.lock generated.")
        except subprocess.CalledProcessError as e:
            print(f"[setup] uv lock failed: {e.stderr.decode() if e.stderr else e}")

    # ---- git init + first commit ----------------------------------------
    if do_git:
        try:
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "chore: initial scaffold"],
                cwd=root, check=True, capture_output=True,
            )
            print("[setup] Git initialized + first commit.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[setup] Git init skipped: {e}")

    # ---- venv / uv sync --------------------------------------------------
    if do_venv:
        if use_uv:
            try:
                # `uv sync` reads default-groups from [tool.uv], so dev group is
                # installed automatically. Stream output so user sees progress.
                subprocess.run(["uv", "sync"], cwd=root, check=True)
                print("[setup] uv sync completed (.venv created + dev deps installed).")
                # Install pre-commit hook into .git/hooks/.
                subprocess.run(
                    ["uv", "run", "pre-commit", "install"],
                    cwd=root, check=False, capture_output=True,
                )
                print("[setup] pre-commit hook installed.")
            except subprocess.CalledProcessError as e:
                print(f"[setup] uv sync failed: {e}")
        else:
            try:
                subprocess.run(
                    [sys.executable, "-m", "venv", str(root / ".venv")],
                    check=True, capture_output=True,
                )
                print(f"[setup] venv created at {root / '.venv'}.")
            except subprocess.CalledProcessError as e:
                print(f"[setup] venv creation failed: {e}")

    # ---- summary --------------------------------------------------------
    print(f"\n[done] '{name}' created.")
    print("\nNext steps:")
    print(f"  cd {name}")
    if do_venv and use_uv:
        # uv mode: everything is already installed. Just run something.
        print(f"  uv run {name} --help          # try the CLI")
        print("  uv run pytest                 # run tests")
        print("  uv run jupyter lab            # open notebooks")
    elif do_venv and not use_uv:
        # pip mode: user must activate + install manually.
        print("  source .venv/bin/activate     # macOS/Linux")
        print("  # .venv\\Scripts\\activate    # Windows PowerShell")
        print("  python -m pip install --upgrade pip")
        print("  pip install -e .")
        print("  pip install --group dev       # requires pip 25.1+")
        print("  pre-commit install")
        print(f"  {name} --help                 # try the CLI")
    else:
        # No venv: fully manual setup.
        print("  # set up your environment, then:")
        print("  pip install -e . && pip install --group dev")
        print(f"  {name} --help")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    """Argument parser. Defaults are tuned for a happy path:
    - uv mode (modern, fast, lockfile-backed)
    - git init enabled
    - venv/uv-sync enabled
    - MIT license
    """
    p = argparse.ArgumentParser(
        description="Universal Python project scaffolder (uv-first)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("name", nargs="?", help="Project name (folder created here)")
    p.add_argument(
        "--modules",
        default="",
        help=(
            "Comma-separated pipeline submodules to scaffold under "
            "src/<name>/ (e.g. detection,tracking,risk,ui)"
        ),
    )
    p.add_argument(
        "--no-uv",
        action="store_true",
        help="Use plain `python -m venv` + pip instead of uv (default: uv).",
    )
    p.add_argument("--no-git", action="store_true", help="Skip git init + first commit")
    p.add_argument("--no-venv", action="store_true", help="Skip .venv / uv-sync creation")
    p.add_argument(
        "--license",
        default="MIT",
        choices=["MIT", "NONE"],
        help="License file to generate (default: MIT)",
    )
    return p.parse_args()


def main() -> None:
    """Validate args and dispatch to create_project()."""
    args = parse_args()
    name = args.name or input("Project name: ").strip()
    if not name:
        print("[ERROR] No project name provided.")
        sys.exit(1)
    # Project names must be safe as Python identifiers AND filesystem names.
    if not name.replace("_", "").replace("-", "").isalnum() or not name[0].isalpha():
        print(
            "[ERROR] Project name must start with a letter and contain only "
            "letters, digits, '_', or '-'."
        )
        sys.exit(1)

    modules = [m.strip() for m in args.modules.split(",") if m.strip()]

    create_project(
        name=name,
        modules=modules,
        do_git=not args.no_git,
        do_venv=not args.no_venv,
        license_type=args.license,
        use_uv=not args.no_uv,
    )


if __name__ == "__main__":
    main()
