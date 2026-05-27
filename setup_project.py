"""
범용 Python 프로젝트 스캐폴더 (uv 우선, 2026 에디션).

────────────────────────────────────────────────────────────────────────────
이 스크립트가 하는 일
────────────────────────────────────────────────────────────────────────────
새 폴더 안에 프로덕션 수준의 Python 프로젝트 골격을 생성합니다. 구성 요소:

  • pyproject.toml
        - PEP 621 [project] 메타데이터 (이름, 버전, 의존성 등)
        - PEP 735 [dependency-groups] (dev/test/lint/notebook) — 배포 시
          새어 나가지 않는 안전한 개발용 의존성 그룹
        - [tool.uv] / [tool.coverage] / [tool.ruff] / [tool.black] / [tool.mypy]
  • 에디터 / VCS 위생 파일
        - .gitignore, .gitattributes (LF 정규화), .editorconfig
        - .python-version (uv / pyenv 가 읽어서 Python 버전 자동 선택)
        - .env.example
  • 개발 도구
        - .pre-commit-config.yaml (ruff, black, nbstripout, nbqa, 표준 훅)
        - 자기 자신을 설명하는 `help` 타깃이 있는 Makefile
  • GitHub 자동화
        - .github/workflows/ci.yml (Python 3.11/3.12 매트릭스, 캐시 +
          동시 실행 자동 취소 포함)
        - PR 템플릿, 이슈 템플릿 (버그 / 기능 요청)
        - CODEOWNERS, dependabot.yml
  • 소스 레이아웃 (src-layout)
        - src/<name>/__init__.py    (임포트 시 사이드 이펙트 없음)
        - src/<name>/__main__.py    (`python -m <name>` 로 실행 가능)
        - src/<name>/cli.py         (typer + loguru, 로깅은 콜백에서 설정)
        - src/<name>/config.py      (pydantic-settings)
        - --modules 플래그로 파이프라인 서브모듈을 선택적으로 추가
  • 테스트
        - tests/test_smoke.py       (패키지 import / config 로드 확인)
        - tests/test_cli.py         (typer 의 CliRunner 사용)
        - tests/conftest.py         (공용 fixture)
  • 문서
        - README.md (배지 포함)
        - CHANGELOG.md (Keep a Changelog 형식)
        - docs/architecture.md
        - docs/cross-platform.md (Mac/Windows/Linux + CUDA 가이드)
        - docs/uv-cheatsheet.md (uv 명령어 + pip 와의 차이 정리)
        - docs/adr/0001-record-architecture-decisions.md
  • 데이터 / 모델 / 노트북 / Claude skills 자리잡이 폴더
        - data/{raw,processed,external}/.gitkeep, models/, notebooks/, logs/, skills/
  • 선택적 자동화:
        - git init + 첫 커밋
        - uv sync (.venv 생성 + dev 의존성 설치 + uv.lock 생성)
        - pre-commit 훅 설치

────────────────────────────────────────────────────────────────────────────
사용법
────────────────────────────────────────────────────────────────────────────
    # 기본값 (uv 모드 — 권장). 폴더 생성, git 초기화, `uv sync` 까지 자동 수행.
    python setup_project.py myproject

    # src/myproject/ 아래에 ML 파이프라인 서브모듈 같이 생성
    python setup_project.py collision_detection \\
        --modules detection,tracking,risk,ui

    # uv 미사용, 일반 venv + pip 모드. conda 환경이거나 인터넷이 막힌 환경에서 유용.
    python setup_project.py myproject --no-uv

    # 자동 설치 건너뛰기 (파일 생성 + git 초기화만).
    python setup_project.py myproject --no-venv

    # git 초기화도 건너뛰기 (파일만 생성).
    python setup_project.py myproject --no-git --no-venv

    # 라이선스 파일 없이.
    python setup_project.py myproject --license NONE

    # 프로필 선택 (기본값: script)
    # 선택 기준: 노트북을 매일 열 거면 research, 코드 파일만 만질 거면 script,
    #            마크다운 정리용이면 docs.
    python setup_project.py myproject --profile docs       # 최소 (~10 패키지)
    python setup_project.py myproject --profile script     # 기본 (~30 패키지)
    python setup_project.py myproject --profile research   # 풀세트 (~80 패키지)

    # GitHub 원격 저장소까지 자동 생성 + 푸시 (gh CLI 필요, 로그인 상태여야 함).
    python setup_project.py myproject --github private    # 비공개
    python setup_project.py myproject --github public     # 공개

    # 프로젝트 삭제 — UNIX 컨벤션 (-d 안전 / -D 강제).
    python setup_project.py myproject -d                  # 안전 삭제: 폴더 이름 재입력 필요
    python setup_project.py myproject -d --remote         # 〃 + GitHub 레포까지
    python setup_project.py myproject -D                  # 강제 삭제: 확인 생략
    python setup_project.py myproject -D --remote         # 〃 + GitHub 레포까지

────────────────────────────────────────────────────────────────────────────
플래그
────────────────────────────────────────────────────────────────────────────
    name              프로젝트 폴더 이름 (위치 인자).
                      [a-zA-Z][a-zA-Z0-9_-]* 패턴이어야 함.
    --modules X,Y,Z   src/<name>/ 아래에 만들 서브모듈을 쉼표로 구분.
    --no-uv           uv 대신 일반 `python -m venv` + pip 사용.
    --no-venv         venv / uv-sync 생성을 완전히 건너뜀.
    --no-git          `git init` + 첫 커밋을 건너뜀.
    --license MIT|NONE  생성할 라이선스 파일 (기본값: MIT).
    --profile docs|script|research
                      개발 도구 프로필 (기본값: script).
                      docs=마크다운 정리용 최소 / script=일반 코드 /
                      research=노트북·ML 풀세트.
    --github none|private|public
                      GitHub 원격 저장소 자동 생성 (기본값: none).
                      gh CLI 가 설치되고 `gh auth login` 이 끝나 있어야 함.
    -d, --delete      [안전 삭제 모드] 폴더 이름을 다시 입력해야 진행.
    -D                [강제 삭제 모드] -d --yes 와 동일 (확인 생략).
    --remote          삭제 모드에서 GitHub 레포도 함께 삭제.
    --yes             확인 프롬프트 생략 (-d 와 같이 쓰면 -D 와 동등).

────────────────────────────────────────────────────────────────────────────
스크립트 종료 후 흐름 (uv 모드 기준)
────────────────────────────────────────────────────────────────────────────
스크립트가 끝나면 다음 명령어들을 바로 사용할 수 있습니다:
    cd <name>
    uv run <name> --help    # CLI 가 이미 설치되어 있어 바로 실행 가능
    uv run pytest           # 테스트가 즉시 동작
    uv run jupyter lab      # 노트북 (notebook 그룹이 dev 의존성에 포함)

나중에 의존성을 추가할 때:
    uv add pandas                       # 런타임 의존성 추가
    uv add --group test pytest-mock     # 테스트 전용 의존성 추가

락파일 재생성:
    uv lock

────────────────────────────────────────────────────────────────────────────
설계 철학
────────────────────────────────────────────────────────────────────────────
- src-layout (코드를 src/<name>/ 아래에 둠) — 트리 안의 패키지와
  실제로 설치된 패키지가 충돌해 잘못된 쪽이 import 되는 사고를 방지.
- 임포트 시 사이드 이펙트 없음 — 패키지를 import 한다고 해서 파일시스템에
  손대지 않음. 로깅 설정은 __init__.py 가 아닌 CLI 콜백에서 수행.
- 배포 안전한 dev 의존성 — 개발 도구는 [project.optional-dependencies] 가
  아니라 [dependency-groups] 에 두기 때문에 PyPI 메타데이터로 새지 않음.
- 기본적으로 크로스 플랫폼 — .gitattributes 로 줄바꿈 정규화,
  경로는 어디서나 pathlib 사용, CI 는 Linux/macOS/Windows 매트릭스에서 실행.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 상수
# --------------------------------------------------------------------------- #

# 생성되는 프로젝트의 Python 최소 버전. .python-version 파일에도 기록되어
# uv / pyenv 가 자동으로 이 버전을 설치/선택해 줍니다.
PYTHON_VERSION = "3.11"
DEFAULT_AUTHOR_NAME = "Hyunjun"
DEFAULT_AUTHOR_EMAIL = "leo4study@gmail.com"


# --------------------------------------------------------------------------- #
# 헬퍼 — 실행 환경 감지
#   git 설정값 / 현재 연도 / uv 설치 여부를 읽되, 해당 도구가 없는 환경에서도
#   스크립트가 깨지지 않도록 모두 안전한 기본값으로 폴백합니다.
# --------------------------------------------------------------------------- #

def detect_git_user() -> tuple[str, str]:
    """`git config --global` (없으면 로컬) 에서 user.name / user.email 을 읽습니다.

    git 자체가 설치되어 있지 않거나 설정값이 비어 있으면 placeholder 문자열
    (DEFAULT_AUTHOR_NAME / DEFAULT_AUTHOR_EMAIL) 로 폴백하므로, git 이 없는
    환경에서도 스캐폴더는 정상 동작합니다.

    Returns:
        (name, email) 튜플. 둘 다 항상 문자열이 채워져 있음이 보장됩니다.
    """
    name = DEFAULT_AUTHOR_NAME
    email = DEFAULT_AUTHOR_EMAIL
    for key, _ in (("user.name", name), ("user.email", email)):
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
            # git 자체가 설치되어 있지 않은 경우 — 기본값을 그대로 사용.
            pass
    return name, email


def current_year() -> int:
    """LICENSE / copyright 줄에 박을 현재 연도를 반환.

    스크립트 안에 연도를 하드코딩하면 매년 직접 갱신해야 하므로,
    실행 시점의 연도를 항상 새로 읽어 옵니다.
    """
    return datetime.datetime.now().year


def have_uv() -> bool:
    """`uv` 실행 파일이 PATH 에 있는지 확인.

    설치 모드 결정(uv 사용 가능 여부) 과 사용자에게 안내 메시지를 보여 줄
    때 활용됩니다.
    """
    return shutil.which("uv") is not None


def have_gh() -> bool:
    """GitHub 공식 CLI (`gh`) 가 PATH 에 있는지 확인.

    `--github` 플래그를 받았을 때만 GitHub 원격 저장소를 자동 생성하는데,
    그 전에 이 함수로 `gh` 설치 여부를 확인합니다. 없으면 자동 생성을
    건너뛰고 안내 메시지만 출력합니다.
    """
    return shutil.which("gh") is not None


def gh_is_authenticated() -> bool:
    """`gh auth status` 가 성공하는지 확인 — 즉 로그인되어 있는지.

    `gh` 자체는 깔려 있어도 `gh auth login` 을 한 적이 없으면 repo 생성이
    실패하므로, 미리 한 번 검사해서 친절한 에러 메시지를 줍니다.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True, text=True, check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


# --------------------------------------------------------------------------- #
# 파일 내용 템플릿
#   각 tpl_* 함수는 한 개 파일의 *내용*(문자열)을 반환합니다. I/O 가 전혀
#   없는 순수 함수이므로 단위 테스트하기 쉽습니다.
#
#   왜 f-string 인가: 템플릿을 코드 안에 그대로 두어 가독성이 좋습니다.
#   다만 출력 결과에 리터럴 `{` / `}` 가 들어가야 하면 `{{` / `}}` 로
#   두 번 써야 한다는 트레이드오프가 있습니다.
# --------------------------------------------------------------------------- #

def _dependency_groups_block(profile: str) -> str:
    """프로필별 [dependency-groups] 섹션 (PEP 735) 을 TOML 문자열로 반환.

    docs   : 가장 가벼움. 마크다운/지식 정리용. lint 도구 1개만.
    script : 일반 Python 코드. test + lint. 노트북/pre-commit 없음.
    research: 데이터 분석/ML. 모든 그룹 + pre-commit 포함 (가장 무거움).

    이 함수는 단일 출처(single source of truth) — 프로필별 차이는 모두
    여기서 결정됩니다.
    """
    if profile == "docs":
        return '''[dependency-groups]
# docs 프로필 — 마크다운 정리용 최소 구성. 가끔 .py 파일을 만질 가능성에
# 대비해 ruff 만 깔아 둡니다. 테스트/노트북/pre-commit 없음 (~10개 패키지).
dev = [
    "ruff>=0.8",
]
'''
    if profile == "script":
        return '''[dependency-groups]
# script 프로필 — 일반 Python 코드. 테스트와 린트는 갖추되 노트북/pre-commit
# 은 필요해지면 그때 `uv add --group notebook ...` 으로 추가 (~30개 패키지).
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-randomly>=3.15",         # 테스트 순서 랜덤화 — 숨은 결합 노출
]
lint = [
    "ruff>=0.8",                     # 고속 린터 + 포매터 (Astral)
    "black>=24.10",                  # 표준 포매터
    "mypy>=1.13",                    # 정적 타입 체커
]
dev = [
    {include-group = "test"},
    {include-group = "lint"},
]
'''
    # research (가장 풍부한 구성 — 현재 기본이었던 것)
    return '''[dependency-groups]
# research 프로필 — 데이터 분석 / ML / 노트북 기반 작업용 풀세트
# (~80개 패키지). 가장 무겁지만 기여자 1명만 추가돼도 환경 일치가 큰 이득.
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-randomly>=3.15",         # 테스트 순서 랜덤화 — 숨은 결합 노출
]
lint = [
    "ruff>=0.8",                     # 고속 린터 + 포매터 (Astral)
    "black>=24.10",                  # 표준 포매터
    "mypy>=1.13",                    # 정적 타입 체커
]
notebook = [
    # VS Code / PyCharm 에서 .ipynb 를 쓰는 것을 가정한 슬림 구성.
    # 브라우저 기반 Jupyter Lab UI 가 필요하면 `uv add --group notebook jupyter` 추가.
    "ipykernel>=6.29",               # 셀 실행 커널
    "nbqa>=1.8",                     # .ipynb 에 ruff/black 적용
    "nbstripout>=0.7",               # 커밋 전 셀 출력 자동 제거
]
dev = [
    {include-group = "test"},
    {include-group = "lint"},
    {include-group = "notebook"},
    "pre-commit>=3.7",
]
'''


def tpl_pyproject(
    name: str, author_name: str, author_email: str, profile: str = "script"
) -> str:
    """pyproject.toml 의 내용을 생성합니다.

    Args:
        profile: docs | script | research. 프로필별로 [dependency-groups]
            섹션의 구성이 달라집니다. 런타임 의존성과 그 외 메타데이터는
            동일.

    주요 설계 결정:
      - 개발 도구는 [dependency-groups] (PEP 735) 에 둠 — 이렇게 하면
        wheel 의 METADATA 로 새지 않아 배포해도 안전.
        ([project.optional-dependencies] 와 결정적인 차이)
      - [project.optional-dependencies] 는 주석 처리해서 비워 둠.
        실제 사용자 대상 extras (예: gpu/cpu/plotting 백엔드 선택) 용으로 예약.
      - [tool.uv].default-groups = ["dev"] 로 설정하여 `uv sync` 만으로
        dev 의존성까지 자동으로 깔리도록 함 — 새 기여자는 명령 한 번이면 끝.
      - 도구 버전은 `>=` 최소 버전만 표기. `uv sync` 가 항상 호환되는
        최신 릴리스를 해석하도록 하고, 정확한 버전 고정은 uv.lock 에 맡김.
    """
    py_target = PYTHON_VERSION.replace(".", "")
    dependency_groups = _dependency_groups_block(profile)
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
# These NEVER end up in the published wheel. 프로필별 구성은 스캐폴더가
# 결정하므로 (docs / script / research) 아래 블록은 자동 생성됩니다.
# ────────────────────────────────────────────────────────────────────────
{dependency_groups}
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
    """표준 Python 무시 항목 + 프로젝트별 무시 항목.

    기본적으로 ML 결과물(*.pt / *.pkl / *.onnx) 과 데이터셋 디렉토리
    (data/raw, data/processed, data/external) 를 제외합니다.
    빈 디렉토리만 유지하기 위해 .gitkeep 만 예외로 추적합니다.
    """
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
    """텍스트 파일의 줄바꿈을 LF 로 강제 정규화.

    Windows 전용 스크립트(.cmd/.bat/.ps1) 만 CRLF 로 두고, 알려진 바이너리
    파일들은 명시적으로 binary 로 표시해 git 이 diff 나 줄바꿈 정규화를
    시도하지 않도록 합니다. Mac/Windows 가 섞인 팀에서 줄바꿈 차이로
    diff 가 폭주하는 사고를 막아 줍니다.
    """
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
    """에디터 비종속적인 코드 스타일 기준선 (들여쓰기, 문자셋, 줄바꿈).

    VSCode, JetBrains, Vim 등 거의 모든 주요 에디터가 이 파일을 자동으로
    읽어 적용하므로, 팀원마다 에디터 설정이 달라도 일관된 스타일이 유지됩니다.
    """
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
    """.env (gitignore 대상) 의 템플릿.

    LOG_DIR 은 기본적으로 주석 처리해 두는데, 이유는 사용자가 명시적으로
    켜기 전까지는 logs/ 폴더가 만들어지지 않게 하기 위함입니다. 비밀값을
    실수로 커밋하지 않도록 실제 .env 파일은 .gitignore 에 포함되어 있습니다.
    """
    return """# Copy this file to `.env` and fill in your values.
# `.env` is gitignored; never commit secrets.

DATA_PATH=./data
MODEL_PATH=./models
LOG_LEVEL=INFO
# LOG_DIR=./logs   # uncomment to enable file logging
"""


def tpl_python_version() -> str:
    """.python-version 파일 내용. Python 버전 한 줄만 들어갑니다.

    uv 와 pyenv 모두 이 파일을 인식해서 해당 Python 버전을 자동으로
    설치/선택해 주므로, 팀원이 Python 버전을 따로 맞춰 줄 필요가 없습니다.
    """
    return f"{PYTHON_VERSION}\n"


def tpl_readme(name: str, use_uv: bool) -> str:
    """상단 배지와 설치/사용법 안내가 포함된 README 를 생성.

    설치 모드(uv vs pip) 에 따라 표시되는 명령어 블록이 달라집니다.
    use_uv=True 면 `uv sync` / `uv run` 흐름을, False 면 `python -m venv` +
    pip 흐름을 안내합니다.
    """
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
    """감지된 작성자 이름과 현재 연도가 채워진 MIT 라이선스 본문을 생성."""
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
    """Keep a Changelog 형식의 CHANGELOG.md 를 생성.

    변경 사항이 생길 때마다 [Unreleased] 섹션에 기록하고, 릴리스 시점에
    버전 번호가 붙은 헤딩 아래로 이동시키는 흐름을 권장합니다.
    """
    return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold.
"""


def tpl_makefile(use_uv: bool, profile: str = "script") -> str:
    """자기 자신을 설명하는 Makefile 을 생성.

    `make help` 를 실행하면 grep + awk 로 `## ` 형태의 문서 주석을 스캔해
    모든 타깃 목록을 보여 줍니다. 레시피는 uv 모드면 `uv run …` 을, pip
    모드면 일반 명령(또는 venv 활성화 안내) 을 사용합니다.

    프로필 인식 — docs 는 test/format 타깃을 생략 (pytest/black 이 의존성에
    없음). lint 도 ruff 만 실행. 의도하지 않은 NameError 를 사전 차단.
    """
    is_docs = profile == "docs"
    runner = "uv run " if use_uv else ""

    # 프로필별 타깃 본문 — docs 면 ruff 만, 그 외엔 풀세트
    if is_docs:
        phony = ".PHONY: help setup install lint clean"
        targets = f"""lint:  ## Run ruff
\t{runner}ruff check src tests
"""
    else:
        phony = ".PHONY: help setup install test lint format clean"
        targets = f"""test:  ## Run tests with coverage
\t{runner}pytest

lint:  ## Run ruff + mypy
\t{runner}ruff check src tests
\t{runner}mypy src

format:  ## Format with black + ruff --fix
\t{runner}black src tests
\t{runner}ruff check --fix src tests
"""

    if use_uv:
        # research 만 pre-commit 의존성이 있으므로 setup 도 그때만 훅 설치
        setup_hook = "\n\tuv run pre-commit install" if profile == "research" else ""
        return f"""{phony}

help:  ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  %-12s %s\\n", $$1, $$2}}'

setup:  ## Sync deps{' + install pre-commit hook' if profile == 'research' else ''}
\tuv sync{setup_hook}

install:  ## Sync dependencies (idempotent)
\tuv sync

{targets}
clean:  ## Remove caches and build artifacts
\trm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {{}} +
"""
    # pip 모드 — pre-commit 훅도 research 에서만
    pip_setup_tail = " && pre-commit install" if profile == "research" else ""
    return f"""{phony}

help:  ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  %-12s %s\\n", $$1, $$2}}'

setup:  ## Create venv + install dev deps{' + pre-commit hook' if profile == 'research' else ''}
\tpython3 -m venv .venv
\t. .venv/bin/activate && pip install --upgrade pip && pip install -e . && pip install --group dev{pip_setup_tail}

install:  ## Install/refresh dependencies (in active venv)
\tpip install -e . && pip install --group dev

{targets}
clean:  ## Remove caches and build artifacts
\trm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {{}} +
"""


def tpl_precommit() -> str:
    """pre-commit 훅 설정.

    포함 내용:
      - 표준 위생 훅 (공백 제거, 파일 끝 개행, 큰 파일 차단, 충돌 마커 확인 등)
      - ruff (린트 + 포맷)
      - black (포맷터 — ruff-format 과 중복이지만 안전망)
      - nbstripout: 노트북 출력(셀 실행 결과) 을 커밋에서 자동 제거해
        diff 폭주를 방지
      - nbqa: ruff/black 을 .ipynb 의 코드 셀에도 적용해 일관성 유지
    """
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
    """Pull Request 본문 템플릿.

    GitHub 에서 PR 을 새로 생성할 때 이 템플릿이 자동으로 채워져 표시되므로,
    기여자가 변경 사항/이유/테스트 방법을 빠뜨리지 않고 적도록 유도합니다.
    """
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
    """버그 리포트용 이슈 템플릿.

    재현 방법 / 기대 결과 / 실제 결과 / 환경 정보를 모두 받도록 해서
    디버깅 첫 단계에 필요한 정보가 누락되지 않게 합니다.
    """
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
    """기능 요청용 이슈 템플릿.

    "어떤 문제를 해결하려고 하나" 를 먼저 묻도록 구성해, 해결책 자체보다
    풀고자 하는 문제 정의에 집중하도록 유도합니다.
    """
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
    """CODEOWNERS 파일.

    여기에 등록된 사용자/팀은 매칭되는 파일이 변경될 때 GitHub 가 자동으로
    리뷰어로 지정해 줍니다. 원격에 푸시하기 전에 실제 핸들로 바꿔야 동작합니다.
    """
    return """# Default reviewers for everything (edit team handles before pushing)
# *       @your-team

# Per-area ownership examples
# /src/{name}/detection/   @teammate-a
# /src/{name}/tracking/    @teammate-b
# /docs/                   @your-username
"""


def tpl_dependabot() -> str:
    """Dependabot 설정.

    pip 의존성은 매주, GitHub Actions 워크플로 버전은 매월 점검해
    오래된 버전이 있으면 자동으로 업그레이드 PR 을 열어 줍니다.
    한 번에 열리는 PR 은 최대 5 개로 제한해 노이즈를 줄였습니다.
    """
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


def _ci_steps_block(profile: str, use_uv: bool) -> str:
    """프로필별로 CI 마지막 단계 (lint / typecheck / test) 블록을 반환.

    docs: ruff 만 (mypy/pytest 가 의존성에 없음).
    script/research: ruff + mypy + pytest.
    """
    runner = "uv run " if use_uv else ""
    ruff = f"""      - name: Lint (ruff)
        run: {runner}ruff check src tests
"""
    mypy_pytest = f"""
      - name: Type check (mypy)
        run: {runner}mypy src

      - name: Test (pytest)
        run: {runner}pytest
"""
    return ruff if profile == "docs" else ruff + mypy_pytest


def tpl_ci_workflow(use_uv: bool, profile: str = "script") -> str:
    """GitHub Actions CI 워크플로: Linux/Mac/Win 매트릭스에서 린트 (+ 타입체크 + 테스트).

    프로필 인식 — docs 는 ruff 만 실행, 그 외는 ruff + mypy + pytest 실행.
    docs 프로필에서 mypy/pytest 가 의존성에 없는데 CI 가 그것을 호출하면
    레드 빌드가 나기 때문에 단계 자체를 빼는 게 정직한 처리.

    적용된 최적화:
      - `concurrency:` — 같은 브랜치에서 새 푸시가 들어오면 진행 중이던
        이전 실행을 자동 취소해서 CI 분(분당 과금) 을 절약.
      - uv 모드에서는 astral-sh/setup-uv 액션의 내장 캐시를 사용해
        의존성 설치가 pip 대비 훨씬 빠름.
      - pre-commit 캐시를 별도로 두어 반복 실행 시간을 더 줄임.
    """
    ci_steps = _ci_steps_block(profile, use_uv)
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
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install ${{{{ matrix.python-version }}}}

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Cache pre-commit
        uses: actions/cache@v5
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{{{ runner.os }}}}-${{{{ hashFiles('.pre-commit-config.yaml') }}}}

{ci_steps}"""
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
      - uses: actions/checkout@v6

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
        uses: actions/cache@v5
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{{{ runner.os }}}}-${{{{ hashFiles('.pre-commit-config.yaml') }}}}

{ci_steps}"""


def tpl_init(name: str) -> str:
    """패키지의 __init__.py 를 생성.

    의도적으로 최소화 — 로깅 설정도, 파일시스템 접근도 하지 않습니다.
    패키지를 import 하는 것 자체가 사이드 이펙트를 가지면 안 되기 때문입니다.
    (사이드 이펙트가 있으면 테스트, REPL 검사, 다른 패키지의 import 등에서
    예상 못한 동작이 발생합니다.) 실제 로깅은 cli.py 의 콜백에서 설정합니다.
    """
    return f'''"""Top-level package for {name}."""

__version__ = "0.1.0"
'''


def tpl_main(name: str) -> str:
    """__main__.py 를 생성.

    이 파일이 있으면 `python -m {name}` 명령으로도 CLI 를 실행할 수 있습니다.
    [project.scripts] 로 등록된 콘솔 스크립트와 동등한 대체 실행 경로 역할.
    """
    return f'''"""Entry point for `python -m {name}`."""

from {name}.cli import app

if __name__ == "__main__":
    app()
'''


def tpl_config(name: str) -> str:
    """환경 변수 / .env 파일에서 값을 읽어 오는 pydantic-settings 모델을 생성.

    pydantic-settings 를 쓰는 이유:
      - 타입 검증이 자동으로 됨 (잘못된 값은 시작 시점에 즉시 실패)
      - .env 파일 지원이 내장되어 있음
      - 설정 가능한 모든 항목이 한 클래스에 모여 있어 문서화 효과
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
    """Typer 기반 CLI 를 생성.

    로깅 설정은 typer 의 @app.callback() 안에 두었습니다. 이렇게 하면
    어떤 서브커맨드를 실행하든 그보다 먼저 로깅 초기화가 일어나면서도,
    `import {name}` 만 했을 때는 절대 실행되지 않으므로 패키지 import 의
    무(無) 사이드 이펙트 원칙이 깨지지 않습니다.
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
    """스모크(smoke) 테스트 — 패키지 import 와 설정 로드가 되는지 확인.

    가장 기본적인 설치/경로 오류(예: editable install 누락, src-layout
    경로 잘못 설정) 를 가장 먼저 잡아 줍니다. 실제 비즈니스 로직 테스트는
    별도로 추가해야 합니다.
    """
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
    """typer 의 CliRunner 를 이용한 CLI 테스트.

    실제 서브프로세스를 띄우지 않고 같은 프로세스 안에서 커맨드를 호출해
    종료 코드와 출력을 검사하므로 빠르고 결정적입니다.
    """
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
    """공용 pytest fixture 를 모아 두는 conftest.py 를 생성.

    pytest 가 자동으로 발견하므로 별도 import 없이 모든 테스트에서
    사용할 수 있습니다. 예시로 들어가는 tmp_data_dir 는 파일시스템
    상태가 필요한 테스트를 위해 격리된 임시 디렉토리를 제공합니다.
    """
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
    """--modules 플래그로 지정한 각 파이프라인 서브모듈의 __init__.py 를 생성.

    한 줄짜리 docstring 만 들어가는 빈 패키지로, 사용자가 여기에 실제
    파이프라인 단계 코드를 채워 넣게 됩니다.
    """
    return f'"""{name}.{module} — pipeline stage."""\n'


def tpl_arch_doc(name: str) -> str:
    """아키텍처 개요 문서를 생성.

    플레이스홀더 다이어그램이 들어가 있으므로, 실제 설계가 잡히면 다이어그램과
    모듈 설명을 직접 갱신해야 합니다.
    """
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
    """크로스 플랫폼(Mac/Windows/Linux) 셋업 가이드를 생성.

    특히 PyTorch 의 CUDA / CPU 빌드 선택을 uv 의 extras 와 sources 기능으로
    명시적으로 분리하는 패턴을 안내합니다. 묵시적 백엔드 선택으로 인한
    "내 컴퓨터에선 되는데" 문제를 줄이는 것이 목적입니다.
    """
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


def tpl_uv_cheatsheet() -> str:
    """uv 자주 쓰는 명령어 치트시트 + pip 와의 핵심 차이 정리.

    생성된 프로젝트의 docs/uv-cheatsheet.md 로 들어갑니다. 새로 합류한
    팀원이 uv 가 처음이어도 첫 한두 시간에 필요한 것은 거의 다 여기서
    찾을 수 있도록 구성합니다.
    """
    return """# uv 치트시트

> `uv` 는 Rust 로 작성된 차세대 Python 패키지 매니저입니다. pip + venv +
> pip-tools + virtualenv 의 기능을 한 도구로 통합하고, 보통 10–100배 빠릅니다.

## 핵심: `uv add` vs `pip install`

겹치는 부분이 있지만 **핵심이 다릅니다**. `pip install` 은 *깔기만* 하고,
`uv add` 는 *프로젝트의 의존성으로 영구 등록 + 깔기 + 락 갱신* 을 한 번에 합니다.

```bash
pip install pandas
# → 현재 venv 에 pandas 만 설치하고 끝.
# → pyproject.toml 은 그대로. 다른 사람이 clone 해도 pandas 는 안 깔림.
# → 손으로 pyproject.toml 에도 추가해야 함.

uv add pandas
# → 1) pyproject.toml 의 [project.dependencies] 에 "pandas>=X.Y" 자동 추가
# → 2) .venv 에 설치
# → 3) uv.lock 에 정확한 버전 + 해시 + 의존 트리 기록
# → 다른 사람이 `uv sync` 하면 동일한 버전이 그대로 재현됨.
```

즉 **`pip install` + `pyproject.toml` 수동 편집** 의 두 단계를 한 번에 묶은 것이 `uv add` 입니다.

## 자주 쓰는 명령

### 환경 구성
```bash
uv sync                       # pyproject + uv.lock 기준으로 .venv 재구성
uv sync --all-groups          # dev / test / lint / notebook 모두 설치
uv sync --no-dev              # 런타임 의존성만 (프로덕션 배포 시)
uv lock                       # 락파일 재생성 (최신 호환 버전으로 재해석)
uv lock --upgrade             # 모든 의존성을 최신 호환 버전으로 업그레이드
uv lock --upgrade-package pandas   # 특정 패키지만 업그레이드
```

### 의존성 추가 / 제거
```bash
uv add pandas                          # 런타임 의존성 추가
uv add 'pandas>=2.2,<3'                # 버전 범위 지정
uv add --group test pytest-mock        # test 그룹에만 추가
uv add --group lint mypy               # lint 그룹에만 추가
uv add --dev ipdb                      # dev 그룹 (test+lint+notebook 의 합집합)
uv remove pandas                       # 제거 (pyproject + lock 자동 정리)
```

### 실행
```bash
uv run python script.py                # venv 활성화 없이 한 줄 실행
uv run pytest                          # 어떤 명령이든 `uv run <cmd>` 로 실행 가능
uv run myproject --help                # console_scripts 진입점도 동일하게
uv run --with httpx python -c "..."    # 일회성으로 추가 패키지 끼워 실행
```

또는 평소처럼 venv 를 활성화해도 됩니다:
```bash
source .venv/bin/activate              # macOS / Linux
# .venv\\Scripts\\activate             # Windows
pytest                                 # 이제 `uv run` 없이 직접
deactivate                             # 끝낼 때
```

### Python 자체 관리
```bash
uv python install 3.12                 # Python 3.12 설치 (uv 가 직접)
uv python list                         # 설치된 / 사용 가능한 버전 목록
uv python pin 3.12                     # 이 프로젝트의 .python-version 갱신
```

### 캐시 / 정리
```bash
uv cache clean                         # 다운로드 캐시 비우기
uv cache dir                           # 캐시 경로 확인
```

## pip 명령과의 1:1 대응표

| 하려는 일 | pip + venv | uv |
|---|---|---|
| 가상환경 만들기 | `python -m venv .venv` | `uv venv` (보통 `uv sync` 가 자동) |
| 의존성 설치 | `pip install -e . && pip install --group dev` | `uv sync` |
| 패키지 추가 | `pip install X` + pyproject 수동 편집 | `uv add X` |
| 패키지 제거 | `pip uninstall X` + pyproject 수동 편집 | `uv remove X` |
| 명령 실행 | `source .venv/bin/activate && X` | `uv run X` |
| 락파일 생성 | `pip-compile` (별도 도구 필요) | `uv lock` (내장) |
| 락파일 동기화 | `pip-sync` (별도 도구 필요) | `uv sync` |
| Python 설치 | `pyenv install 3.12` (별도 도구) | `uv python install 3.12` |

## 락파일(uv.lock) 이 뭔가요?

`pyproject.toml` 에는 **버전 범위** 만 적습니다 (예: `pandas>=2.2`).
실제로 어느 시점에 누가 깔았느냐에 따라 `2.2.0` 일 수도, `2.2.3` 일 수도 있어
"내 컴퓨터에선 되는데" 문제가 생깁니다.

`uv.lock` 은 이번 해석 결과의 **정확한 버전 + 해시** 를 모두 적어 두는
파일입니다. 다른 사람이 `uv sync` 하면 이 파일을 따라 **완전히 동일한
버전 조합** 이 설치되어 재현성이 보장됩니다.

**언제 갱신되나**:
- `uv add` / `uv remove` → 자동
- `uv sync` 도중 pyproject 가 lock 과 어긋나면 → 자동
- 명시적 `uv lock` → "지금 가능한 최신 호환 버전으로 다시 풀어 줘"

평소에는 직접 `uv lock` 을 칠 일이 거의 없습니다. **`uv.lock` 은 git 에
반드시 커밋** 하세요 — 이게 빠지면 락파일의 의미가 없어집니다.

## 의존성 그룹 ([dependency-groups], PEP 735)

`pyproject.toml` 의 `[dependency-groups]` 에 정의된 그룹들은 **배포되는
wheel 의 메타데이터에 포함되지 않습니다**. 즉 PyPI 에 올려도 ruff / pytest
같은 개발 도구가 따라 올라가지 않습니다.

이 프로젝트의 기본 그룹:
- `test` — pytest, pytest-cov, pytest-randomly
- `lint` — ruff, black, mypy
- `notebook` — jupyter, ipykernel, nbqa, nbstripout
- `dev` — 위 셋 + pre-commit (전부)

```bash
uv sync                       # default-groups = ["dev"] 이므로 dev 그룹 포함
uv sync --no-dev              # 런타임만 (프로덕션 컨테이너 등)
uv sync --group test          # test 만 추가로
uv sync --all-groups          # 모든 그룹
```

## 흔한 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `uv: command not found` | uv 미설치 | `curl -LsSf https://astral.sh/uv/install.sh \\| sh` |
| `ModuleNotFoundError: <name>` | editable 설치가 안 됨 | `uv sync` 한 번 더 |
| CI 에서 동작이 로컬과 다름 | uv.lock 이 커밋 안 됨 | `git add uv.lock && git commit` |
| 의존성을 추가했는데 다른 사람에게 안 깔림 | `pip install` 만 하고 pyproject 수정 안 함 | `uv add` 로 다시 추가 |
| 락파일이 자꾸 변함 | 버전 범위가 너무 느슨 | 범위를 더 좁히거나 lock 만 커밋 |

## 참고

- 공식 문서: https://docs.astral.sh/uv/
- PEP 735 (dependency-groups): https://peps.python.org/pep-0735/
"""


def tpl_adr_template() -> str:
    """ADR (Architecture Decision Record) 템플릿을 생성.

    Michael Nygard 의 형식을 따릅니다. 중요한 아키텍처 결정마다 docs/adr/
    아래에 번호가 매겨진 새 파일을 추가하고, 기존 결정이 뒤집힐 때는
    원본을 수정하지 않고 새 ADR 이 그것을 superseded 한다고 명시합니다.
    """
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
# 파일시스템 헬퍼
# --------------------------------------------------------------------------- #

def write_file(path: Path, content: str) -> None:
    """텍스트를 디스크에 기록. 필요한 상위 디렉토리는 자동 생성합니다.

    인코딩은 항상 UTF-8 로 고정 — Windows 의 기본 로케일 인코딩(cp949 등) 에
    걸려 한글이나 특수 문자가 깨지는 사고를 막기 위함입니다.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def touch_keep(path: Path) -> None:
    """`.gitkeep` 파일을 만들어 비어 있는 디렉토리도 git 이 추적하도록 만듦.

    git 은 파일이 없는 디렉토리를 추적하지 않으므로, data/raw 같이
    "구조만 있고 처음에는 비어 있어야 하는" 폴더를 보존하려면
    더미 파일이 하나 필요합니다.
    """
    write_file(path / ".gitkeep", "")


# --------------------------------------------------------------------------- #
# 프로젝트 생성
#   오케스트레이터 역할: 모든 템플릿 파일을 디스크에 쓰고, 선택적으로 git 을
#   초기화하며, 선택적으로 가상환경 (uv 또는 일반 python -m venv) 을 만듭니다.
# --------------------------------------------------------------------------- #

def create_project(
    name: str,
    modules: list[str],
    do_git: bool,
    do_venv: bool,
    license_type: str,
    use_uv: bool,
    github: str,
    profile: str,
) -> None:
    """프로젝트 트리를 생성하고 선택적 자동화 단계를 실행.

    profile (docs | script | research) 는 다음을 결정합니다:
      - pyproject.toml 의 [dependency-groups] 구성
      - pre-commit 훅 자동 설치 여부 (research 만 설치)
      - (현재 단계에서는) 그 외 모든 파일은 동일하게 생성
    프로필별 차이를 늘리고 싶으면 _dependency_groups_block 과 이 함수
    안의 분기 두 곳만 손대면 됩니다.

    실행 순서가 중요합니다:
      1. 모든 파일을 디스크에 기록
      2. (uv 모드) 첫 커밋 *전에* `uv lock` 으로 uv.lock 을 생성
      3. git init + 첫 커밋 (uv.lock 도 초기 커밋에 포함되도록)
      4. (github != "none") `gh repo create` 로 GitHub 원격 저장소 생성 +
         첫 커밋 푸시. gh CLI 가 없거나 로그인 안 되어 있으면 안내만 출력.
      5. (uv 모드) `uv sync` 로 .venv 생성 + 의존성 설치 + pre-commit 훅 설치
         (pip 모드) `python -m venv` 만 수행 — 이후 설치는 사용자가 직접

    Args:
        github: "none" | "private" | "public" — GitHub 원격 저장소 생성 모드.
            "none" 이면 로컬에만 git 초기화. 그 외에는 해당 가시성으로
            `gh repo create` 호출.
    """
    root = Path(name)
    if root.exists():
        print(f"\n[ERROR] '{name}' already exists. Refusing to overwrite.\n")
        sys.exit(1)

    # uv 모드가 필요한데 uv 가 설치되어 있지 않으면 *파일을 쓰기 전에* 즉시
    # 실패시킵니다. 이렇게 해야 반쪽짜리 결과물이 남지 않습니다.
    if do_venv and use_uv and not have_uv():
        print("\n[ERROR] uv is not installed (default install mode).")
        print("  Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print('  Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"')
        print("  Or rerun with --no-uv to use plain venv + pip.\n")
        sys.exit(1)

    print(f"\n[setup] Creating '{name}'...")

    author_name, author_email = detect_git_user()
    year = current_year()

    # ---- 핵심 파일 -------------------------------------------------------
    write_file(root / "pyproject.toml", tpl_pyproject(name, author_name, author_email, profile))
    write_file(root / ".gitignore", tpl_gitignore())
    write_file(root / ".gitattributes", tpl_gitattributes())
    write_file(root / ".editorconfig", tpl_editorconfig())
    write_file(root / ".env.example", tpl_env_example())
    write_file(root / ".python-version", tpl_python_version())
    write_file(root / "README.md", tpl_readme(name, use_uv))
    write_file(root / "CHANGELOG.md", tpl_changelog())
    write_file(root / "Makefile", tpl_makefile(use_uv, profile))
    write_file(root / ".pre-commit-config.yaml", tpl_precommit())
    if license_type.upper() == "MIT":
        write_file(root / "LICENSE", tpl_license_mit(author_name, year))

    # ---- GitHub 자동화 (CI, 템플릿, dependabot 등) -----------------------
    write_file(root / ".github" / "PULL_REQUEST_TEMPLATE.md", tpl_pr_template())
    write_file(root / ".github" / "ISSUE_TEMPLATE" / "bug_report.md", tpl_issue_bug())
    write_file(root / ".github" / "ISSUE_TEMPLATE" / "feature_request.md", tpl_issue_feature())
    write_file(root / ".github" / "CODEOWNERS", tpl_codeowners())
    write_file(root / ".github" / "dependabot.yml", tpl_dependabot())
    write_file(root / ".github" / "workflows" / "ci.yml", tpl_ci_workflow(use_uv, profile))

    # ---- src 레이아웃 (실제 패키지 본체) --------------------------------
    pkg = root / "src" / name
    write_file(pkg / "__init__.py", tpl_init(name))
    write_file(pkg / "__main__.py", tpl_main(name))
    write_file(pkg / "config.py", tpl_config(name))
    write_file(pkg / "cli.py", tpl_cli(name))

    for module in modules:
        write_file(pkg / module / "__init__.py", tpl_module_init(name, module))

    # ---- 테스트 ----------------------------------------------------------
    write_file(root / "tests" / "__init__.py", "")
    write_file(root / "tests" / "conftest.py", tpl_conftest())
    write_file(root / "tests" / "test_smoke.py", tpl_test_smoke(name))
    write_file(root / "tests" / "test_cli.py", tpl_test_cli(name))

    # ---- 문서 ------------------------------------------------------------
    write_file(root / "docs" / "architecture.md", tpl_arch_doc(name))
    write_file(root / "docs" / "cross-platform.md", tpl_crossplatform_doc())
    write_file(root / "docs" / "uv-cheatsheet.md", tpl_uv_cheatsheet())
    write_file(root / "docs" / "adr" / "0001-record-architecture-decisions.md", tpl_adr_template())

    # ---- data / models / notebooks / skills 자리잡이 폴더 ---------------
    for sub in ("raw", "processed", "external"):
        touch_keep(root / "data" / sub)
    touch_keep(root / "models")
    touch_keep(root / "notebooks")
    touch_keep(root / "logs")
    # Claude Code skill 파일 (.md) 을 모아 두는 곳. 빈 폴더로 시작해도
    # 클로드가 이 폴더를 인식해서 스킬을 추가/사용할 수 있습니다.
    touch_keep(root / "skills")

    print("[setup] Files written.")

    # ---- uv lock (git 보다 먼저 실행해야 uv.lock 이 첫 커밋에 포함됨) ----
    if do_venv and use_uv:
        try:
            subprocess.run(["uv", "lock"], cwd=root, check=True, capture_output=True)
            print("[setup] uv.lock generated.")
        except subprocess.CalledProcessError as e:
            print(f"[setup] uv lock failed: {e.stderr.decode() if e.stderr else e}")

    # ---- git 초기화 + 첫 커밋 -------------------------------------------
    git_ok = False
    if do_git:
        try:
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "chore: initial scaffold"],
                cwd=root, check=True, capture_output=True,
            )
            print("[setup] Git initialized + first commit.")
            git_ok = True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[setup] Git init skipped: {e}")

    # ---- GitHub 원격 저장소 생성 + 푸시 ---------------------------------
    # 보안상 기본값은 "none" — 명시적으로 --github private|public 을 줘야
    # 외부에 코드가 올라갑니다. gh CLI 가 없거나 로그인이 안 돼 있으면
    # 친절한 안내만 출력하고 스크립트는 계속 진행합니다(치명적 오류 아님).
    if github != "none":
        if not git_ok:
            print("[setup] --github 옵션은 git init 이 성공해야 동작합니다. 건너뜀.")
        elif not have_gh():
            print("[setup] gh CLI 가 설치되어 있지 않아 GitHub 저장소 생성을 건너뜁니다.")
            print("        설치: https://cli.github.com/  (Mac: `brew install gh`)")
        elif not gh_is_authenticated():
            print("[setup] gh 가 로그인되어 있지 않아 GitHub 저장소 생성을 건너뜁니다.")
            print("        먼저 한 번 실행: `gh auth login`")
        else:
            visibility_flag = f"--{github}"  # --private 또는 --public
            try:
                # --source=. : 현재 폴더가 로컬 git 저장소
                # --remote=origin : remote 이름 origin 으로 등록
                # --push : 첫 커밋을 즉시 푸시
                subprocess.run(
                    ["gh", "repo", "create", name, visibility_flag,
                     "--source=.", "--remote=origin", "--push"],
                    cwd=root, check=True,
                )
                print(f"[setup] GitHub 저장소 생성 + 푸시 완료 ({github}).")
            except subprocess.CalledProcessError as e:
                # 흔한 실패 원인: 같은 이름 레포가 이미 존재, 권한 부족 등.
                print(f"[setup] gh repo create 실패: {e}")
                print("        로컬 저장소는 그대로 유지됩니다. 수동으로:")
                print(f"        gh repo create {name} {visibility_flag} --source=. --push")

    # ---- venv / uv sync --------------------------------------------------
    if do_venv:
        if use_uv:
            try:
                # `uv sync` 는 [tool.uv] 의 default-groups 설정을 읽어 자동으로
                # dev 그룹까지 설치합니다. capture_output 을 쓰지 않고 그대로
                # 흘려 보내, 사용자가 설치 진행 상황을 실시간으로 볼 수 있게 함.
                subprocess.run(["uv", "sync"], cwd=root, check=True)
                print("[setup] uv sync completed (.venv created + dev deps installed).")
                # pre-commit 훅은 research 프로필에서만 의존성으로 들어가므로
                # 그 외 프로필에선 설치 단계를 건너뜁니다 (실행해도 실패만 함).
                if profile == "research":
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

    # ---- 마무리 요약 -----------------------------------------------------
    print(f"\n[done] '{name}' created.")
    print("\nNext steps:")
    print(f"  cd {name}")
    if do_venv and use_uv:
        # uv 모드: 모든 의존성이 이미 설치되어 있으므로 바로 실행만 하면 됨.
        # 프로필별로 안내 라인을 다르게 — 깔리지도 않은 도구를 추천하면 사용자가 혼란.
        print(f"  uv run {name} --help          # try the CLI")
        if profile in ("script", "research"):
            print("  uv run pytest                 # run tests")
        if profile == "research":
            print("  # 노트북: notebooks/ 폴더를 VS Code/PyCharm 에서 열기")
            print("  #   브라우저 UI 가 필요하면: uv add --group notebook jupyter")
    elif do_venv and not use_uv:
        # pip 모드: venv 활성화 + 패키지 설치를 사용자가 직접 해야 함.
        print("  source .venv/bin/activate     # macOS/Linux")
        print("  # .venv\\Scripts\\activate    # Windows PowerShell")
        print("  python -m pip install --upgrade pip")
        print("  pip install -e .")
        print("  pip install --group dev       # requires pip 25.1+")
        if profile == "research":
            print("  pre-commit install")
        print(f"  {name} --help                 # try the CLI")
        if profile in ("script", "research"):
            print("  pytest                        # run tests")
    else:
        # venv 자체를 건너뛴 경우: 환경 구성부터 끝까지 모두 수동.
        print("  # set up your environment, then:")
        print("  pip install -e . && pip install --group dev")
        print(f"  {name} --help")
        if profile in ("script", "research"):
            print(f"  pytest                        # run tests")


# --------------------------------------------------------------------------- #
# 프로젝트 삭제
#   -D / --delete 플래그가 주어졌을 때 호출됩니다. 실수로 잘못된 폴더를 날리지
#   않도록 여러 단계의 안전장치를 거칩니다:
#     1. 폴더가 실제로 존재해야 함
#     2. 폴더 안에 pyproject.toml 이 있어야 함 (= 스캐폴드로 만든 폴더로 보임)
#     3. 현재 작업 디렉토리가 삭제 대상 안에 있으면 거부 (rm-rf cwd 사고 방지)
#     4. --yes 가 없으면 사용자가 폴더 이름을 다시 타이핑해야 진행
# --------------------------------------------------------------------------- #

def delete_project(name: str, delete_remote: bool, skip_confirm: bool) -> None:
    """로컬 프로젝트 폴더 (및 선택적으로 동명의 GitHub 레포) 를 삭제.

    Args:
        name: 삭제할 폴더 이름. 현재 작업 디렉토리 기준 상대 경로로 해석.
        delete_remote: True 면 `gh repo delete <name>` 도 함께 호출.
        skip_confirm: True 면 확인 프롬프트 생략 (자동화/스크립트 용).
    """
    root = Path(name).resolve()

    # 안전장치 1 — 폴더가 실제로 존재
    if not root.exists():
        print(f"\n[ERROR] '{root}' 가 존재하지 않습니다.\n")
        sys.exit(1)

    # 안전장치 2 — 스캐폴드로 만든 폴더로 보여야 함 (pyproject.toml 존재)
    # 이게 가장 중요한 가드: ~/ 같은 일반 디렉토리를 실수로 지정해도 안 지워짐.
    if not (root / "pyproject.toml").exists():
        print(f"\n[ERROR] '{root}' 안에 pyproject.toml 이 없습니다. 삭제를 거부합니다.")
        print("        (잘못된 폴더를 실수로 날리는 사고를 막기 위한 안전장치)\n")
        sys.exit(1)

    # 안전장치 3 — 현재 작업 디렉토리가 삭제 대상 안이면 거부
    try:
        cwd = Path.cwd().resolve()
        if cwd == root or root in cwd.parents:
            print(f"\n[ERROR] 현재 작업 디렉토리({cwd}) 가 삭제 대상 안에 있습니다.")
            print("        다른 폴더로 이동한 뒤 다시 실행하세요.\n")
            sys.exit(1)
    except OSError:
        # cwd 가 이미 삭제된 등 비정상 상태 — 안전하게 계속 진행.
        pass

    # 사용자에게 무엇이 일어날지 명확히 보여 줌
    print(f"\n[delete] 삭제 예정 경로: {root}")
    if delete_remote:
        print(f"[delete] GitHub 레포 '{name}' 도 함께 삭제됩니다 (gh repo delete).")
    print()

    # 안전장치 4 — 폴더 이름을 다시 타이핑해야 진행 (오타 한 글자도 거부)
    if not skip_confirm:
        try:
            typed = input(
                f"정말 삭제하려면 폴더 이름을 그대로 다시 입력하세요 [{name}]: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[delete] 취소되었습니다.")
            sys.exit(1)
        if typed != name:
            print("[delete] 이름이 일치하지 않아 취소되었습니다.")
            sys.exit(1)

    # ---- 로컬 폴더 삭제 -------------------------------------------------
    try:
        shutil.rmtree(root)
        print(f"[delete] 로컬 폴더 삭제 완료: {root}")
    except OSError as e:
        print(f"[ERROR] 폴더 삭제 실패: {e}")
        sys.exit(1)

    # ---- GitHub 레포 삭제 (선택) ----------------------------------------
    if not delete_remote:
        print("\n[done] 로컬 삭제 완료. (GitHub 레포는 그대로)")
        return

    if not have_gh():
        print("[delete] gh CLI 가 설치되어 있지 않아 GitHub 레포 삭제를 건너뜁니다.")
        print("        설치: https://cli.github.com/  (Mac: `brew install gh`)")
        print(f"        또는 웹에서 직접 삭제: github.com/<USER>/{name}/settings")
        return

    if not gh_is_authenticated():
        print("[delete] gh 로그인되지 않아 GitHub 레포 삭제를 건너뜁니다.")
        print("        먼저 한 번 실행: `gh auth login`")
        return

    try:
        # gh repo delete 는 기본적으로 현재 로그인 사용자의 레포를 대상으로 함.
        # --yes 는 gh 자체의 추가 확인 프롬프트를 건너뛰는 옵션 (우리 쪽
        # 안전장치 4 를 이미 통과했으므로 중복 확인 불필요).
        subprocess.run(
            ["gh", "repo", "delete", name, "--yes"],
            check=True, capture_output=True, text=True,
        )
        print(f"[delete] GitHub 레포 삭제 완료: {name}")
        print("\n[done] 로컬 + 원격 삭제 완료.")
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "") if isinstance(e.stderr, str) else ""
        # 가장 흔한 실패: delete_repo 권한 스코프 누락.
        if "delete_repo" in stderr or "scope" in stderr.lower():
            print("[ERROR] gh 에 delete_repo 권한이 없습니다. 한 번 갱신하면 됩니다:")
            print("        gh auth refresh -h github.com -s delete_repo")
        else:
            print(f"[ERROR] GitHub 레포 삭제 실패: {stderr or e}")
        print("        로컬 폴더는 이미 삭제되었습니다.")


# --------------------------------------------------------------------------- #
# 셸 자동완성 생성기
#   `--print-completion zsh` 로 호출하면 newpy 용 zsh 완성 함수를 stdout 에
#   출력합니다. .zshrc 에서 `eval "$(... --print-completion zsh)"` 형태로
#   소싱하면 옵션 탭 완성이 동작합니다.
#
#   이 스크립트가 완성 정의의 단일 출처(single source of truth)가 되므로
#   옵션이 늘어나거나 바뀌어도 .zshrc 를 손댈 필요가 없습니다.
# --------------------------------------------------------------------------- #

_ZSH_COMPLETION = r"""# newpy zsh completion (generated by setup_project.py --print-completion zsh)
_newpy() {
  _arguments \
    '*--modules[서브모듈 — 공백/쉼표 모두 허용]:modules' \
    '--no-uv[uv 대신 pip 사용]' \
    '--no-git[git init 건너뜀]' \
    '--no-venv[venv 생성 건너뜀]' \
    '--license[라이선스]:license:(MIT NONE)' \
    '--profile[프로필]:profile:(docs script research)' \
    '--github[GitHub 레포]:visibility:(none private public)' \
    '-d[안전 삭제 모드 — 이름 재입력 필요]' \
    '--delete[안전 삭제 모드]' \
    '-D[강제 삭제 모드 — 확인 생략]' \
    '--remote[GitHub 레포도 삭제]' \
    '--yes[확인 생략 (-d 와 함께 쓰면 -D 와 동등)]' \
    '--print-completion[자동완성 스크립트 출력]:shell:(zsh)' \
    '--help[도움말]' \
    '-h[도움말]'
}
compdef _newpy newpy
"""


def print_completion(shell: str) -> None:
    """주어진 셸용 자동완성 스크립트를 stdout 으로 출력.

    현재는 zsh 만 지원. 셸 시작 시점에 `eval "$(... --print-completion zsh)"`
    로 소싱되도록 설계됐으므로 출력은 순수 셸 코드여야 하고, 에러는 stderr
    로만 내보냅니다.
    """
    if shell == "zsh":
        print(_ZSH_COMPLETION)
        return
    print(
        f"[ERROR] '{shell}' 셸은 아직 지원하지 않습니다. 현재는 zsh 만 가능.",
        file=sys.stderr,
    )
    sys.exit(1)


# --------------------------------------------------------------------------- #
# CLI 진입점
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파서.

    기본값들은 "행복한 경로(happy path)" 에 맞춰 두었습니다:
      - uv 모드 (현대적이고 빠르며 락파일 기반으로 재현 가능)
      - git 초기화 켜짐
      - venv / uv sync 켜짐
      - MIT 라이선스
    각 플래그는 이 기본값을 *끄는* 용도로 동작합니다.
    """
    p = argparse.ArgumentParser(
        description="Universal Python project scaffolder (uv-first)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("name", nargs="?", help="Project name (folder created here)")
    p.add_argument(
        "--modules",
        nargs="*",
        default=[],
        help=(
            "src/<name>/ 아래에 만들 서브모듈. 공백/쉼표/혼합 모두 허용 — "
            "예: `--modules detection,tracking` 또는 `--modules detection tracking` "
            "또는 `--modules \"detection, tracking, risk, ui\"`."
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
    p.add_argument(
        "--profile",
        default="script",
        choices=["docs", "script", "research"],
        help=(
            "프로젝트 프로필 (기본값: script). "
            "docs=마크다운 정리용 최소 구성 / "
            "script=일반 코드 (test+lint) / "
            "research=데이터·ML (test+lint+notebook+pre-commit). "
            "선택 기준: 노트북을 매일 열 거면 research, "
            "코드 파일만 만질 거면 script, 마크다운 정리용이면 docs."
        ),
    )
    p.add_argument(
        "--github",
        default="none",
        choices=["none", "private", "public"],
        help=(
            "GitHub 원격 저장소 자동 생성 + 푸시. 기본값 'none' (생성 안 함). "
            "'private' 또는 'public' 을 지정하면 gh CLI 로 해당 가시성의 "
            "원격 저장소를 만들고 첫 커밋을 푸시합니다. gh 설치/로그인 필요."
        ),
    )
    # ── 삭제 모드 플래그 ────────────────────────────────────────────────
    # UNIX 컨벤션을 따라 -d 와 -D 를 의미적으로 분리:
    #   -d / --delete  = 안전 삭제 (폴더 이름 재입력 프롬프트 거침)
    #   -D             = 강제 삭제 (-d --yes 와 동일, 확인 생략)
    # --remote 와 조합하여 GitHub 레포까지 같이 처리.
    p.add_argument(
        "-d", "--delete",
        action="store_true",
        help=(
            "[안전 삭제 모드] name 으로 지정한 로컬 폴더를 삭제. "
            "폴더 이름을 다시 입력해야 진행됩니다. --remote 면 GitHub 레포도 같이."
        ),
    )
    p.add_argument(
        "-D",
        action="store_true",
        dest="delete_force",
        help="[강제 삭제 모드] -d --yes 와 동일. 확인 프롬프트를 건너뜀.",
    )
    p.add_argument(
        "--remote",
        action="store_true",
        help="삭제 모드에서 GitHub 레포도 함께 삭제 (gh 설치/로그인 필요).",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="삭제 모드에서 확인 프롬프트를 건너뜀 (자동화 용도).",
    )
    # ── 셸 자동완성 출력 모드 ───────────────────────────────────────────
    # name 보다 먼저 처리되어야 하므로 main() 에서 별도 분기로 다룹니다.
    p.add_argument(
        "--print-completion",
        choices=["zsh"],
        default=None,
        metavar="SHELL",
        help=(
            "지정한 셸용 자동완성 스크립트를 stdout 으로 출력하고 종료. "
            "사용 예: `eval \"$(setup_project.py --print-completion zsh)\"` "
            "(현재 zsh 만 지원)."
        ),
    )
    return p.parse_args()


def main() -> None:
    """인자를 검증하고 create_project() 로 위임.

    인자가 비어 있으면 표준 입력으로 직접 묻습니다(스크립트를 인자 없이
    더블클릭/실행해도 동작하도록).
    """
    args = parse_args()

    # 자동완성 출력 모드는 name 검증보다 먼저 처리하고 즉시 종료.
    if args.print_completion:
        print_completion(args.print_completion)
        return

    name = args.name or input("Project name: ").strip()
    if not name:
        print("[ERROR] No project name provided.")
        sys.exit(1)
    # 프로젝트 이름은 Python 식별자로도, 파일시스템 이름으로도 모두 안전해야
    # 합니다. 첫 글자는 알파벳, 나머지는 알파벳/숫자/언더스코어/하이픈만 허용.
    if not name.replace("_", "").replace("-", "").isalnum() or not name[0].isalpha():
        print(
            "[ERROR] Project name must start with a letter and contain only "
            "letters, digits, '_', or '-'."
        )
        sys.exit(1)

    # 삭제 모드면 분기 — 생성 관련 인자들은 모두 무시.
    # -D (force) 는 -d + --yes 와 동일 의미. 둘 중 하나라도 켜져 있으면 삭제.
    if args.delete or args.delete_force:
        skip_confirm = args.yes or args.delete_force
        delete_project(name, delete_remote=args.remote, skip_confirm=skip_confirm)
        return

    # --modules 는 nargs="*" 라 리스트로 들어옴. 토큰을 공백 + 쉼표 모두로
    # 분해해 사용자가 어떤 형식으로 입력하든 동일하게 동작하도록.
    # 예: ["detection,tracking,risk"] / ["a","b","c"] / ["detection,", "tracking,", "risk"]
    modules = " ".join(args.modules).replace(",", " ").split()

    create_project(
        name=name,
        modules=modules,
        do_git=not args.no_git,
        do_venv=not args.no_venv,
        license_type=args.license,
        use_uv=not args.no_uv,
        github=args.github,
        profile=args.profile,
    )


if __name__ == "__main__":
    main()
