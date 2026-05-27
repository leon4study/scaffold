# scaffold

범용 Python 프로젝트 스캐폴더 (uv 우선, 2026 에디션).
프로덕션 수준의 Python 프로젝트 골격을 생성하는 단일 파일 제너레이터입니다.

## 빠른 시작

```bash
# 기본값 — uv 모드 + script 프로필. 폴더 생성, git 초기화, `uv sync` 까지 수행.
python setup_project.py myproject

# 프로필 지정 (아래 "프로필 선택 기준" 참고)
python setup_project.py my_notes --profile docs
python setup_project.py my_pipeline --profile research --modules detection,tracking,risk,ui

# 일반 venv + pip 사용 (uv 미사용)
python setup_project.py myproject --no-uv

# 파일만 생성 (설치 없음, git 없음)
python setup_project.py myproject --no-git --no-venv
```

## 프로필 선택 기준

> **노트북을 매일 열 거면 `research`, 코드 파일만 만질 거면 `script`, 마크다운 정리용이면 `docs`.**

| 프로필 | 무엇이 들어있나 | 약 패키지 수 | 어울리는 케이스 |
|---|---|---|---|
| `docs` | ruff 만 | ~10 | 마크다운/지식 정리 레포 (예: 학습 노트, 스킬 모음집) |
| `script` (기본값) | test + lint (ruff/black/mypy/pytest) | ~30 | 일반 Python 코드 — CLI 도구, 자동화 스크립트, 라이브러리, 봇, 웹 서버 |
| `research` | 위 + notebook (ipykernel/nbqa/nbstripout) + pre-commit | ~80 | 데이터 분석, ML 실험, Jupyter 기반 작업 |

### 3단계 결정 플로우

```
1. Python 프로젝트인가?           → 아니면 이 스캐폴더 안 씀 (Next/Vite/Unity 등)
2. 노트북(.ipynb)을 주로 쓸 건가?  → 그렇다 → research
3. 유지보수할 코드인가?            → 그렇다 → script   /   아니다(메모) → docs
```

도메인 예시:
- **데이터 분석 / ML 실험** → `research`
- **FastAPI 서버 / 텔레그램 봇 / CLI 도구 / pygame 게임** → `script`
- **학습 노트 / 스킬 모음 / 회의록 정리** → `docs`
- **프론트엔드 포트폴리오 (React/Next)** → 이 스캐폴더 부적합, JS 생태계 도구 사용
- **에어비엔비 관리 같은 막연한 케이스** → 가장 큰 활동(웹 서버면 script, 데이터 분석이면 research) 기준으로

> 스크립트 자체는 표준 라이브러리만 사용하므로 **venv 활성화 없이도 실행할 수 있습니다**.
> `uv`가 설치되어 있으면 생성된 프로젝트에 대해 자동으로 `uv lock` + `uv sync`를 호출합니다.

## 어디서든 한 줄로 실행하기 (zsh 함수)

먼저 `cd` 하지 않고 어느 디렉토리에서나 `~/GitStudy/<name>/` 아래에 프로젝트를 만들려면
다음 함수를 `~/.zshrc`에 추가하세요:

```zsh
# --- Python 프로젝트 스캐폴더 (GitStudy/scaffold) ---
# newpy <name> [--modules a,b,c] [--no-uv] [--no-venv] [--no-git] [--github private|public]
# newpy <name> -D [--remote] [--yes]   # 삭제 모드
#   → 현재 디렉토리와 관계없이 ~/GitStudy/<name>/ 를 생성
newpy() {
  (cd ~/GitStudy && python3 ~/GitStudy/scaffold/setup_project.py "$@")
}
# 탭 자동완성 (옵션 정의는 setup_project.py 안에 있어 자동 동기화됨)
eval "$(python3 ~/GitStudy/scaffold/setup_project.py --print-completion zsh 2>/dev/null)"
```

> **참고**: macOS 에는 `python` 명령이 없고 `python3` 만 있어, 위 함수는
> `python3` 를 사용합니다. conda/pyenv 등으로 `python` 이 잡혀 있어도 안전.

설치 방법:

```bash
cp ~/.zshrc ~/.zshrc.backup        # 안전 백업
cat <<'EOF' >> ~/.zshrc

# --- Python 프로젝트 스캐폴더 (GitStudy/scaffold) ---
newpy() {
  (cd ~/GitStudy && python3 ~/GitStudy/scaffold/setup_project.py "$@")
}
eval "$(python3 ~/GitStudy/scaffold/setup_project.py --print-completion zsh 2>/dev/null)"
EOF
source ~/.zshrc                    # 현재 셸에서 다시 로드
type newpy                         # 확인: 함수 본문이 출력되어야 함
newpy --<TAB>                      # 확인: 옵션 목록이 떠야 함
```

이후 어디서든:

```bash
newpy myproject                                    # 기본값 (uv + git + MIT)
newpy myproject --modules detection,tracking,ui    # 서브모듈 포함
newpy myproject --no-uv                            # pip 모드
newpy myproject --no-venv --no-git                 # 파일만 생성
```

참고:
- `( ... )` **서브셸** 덕분에 `cd`가 현재 터미널에 영향을 주지 않습니다.
- `"$@"`는 모든 플래그를 그대로 전달합니다.
- `setup_project.py` 수정은 즉시 반영됩니다 — 함수 자체를 바꾸고 싶을 때만 `~/.zshrc`를 편집한 뒤 `source ~/.zshrc` 하면 됩니다.

## 플래그

| 플래그 | 기본값 | 의미 |
|---|---|---|
| `name` (위치 인자) | 필수 | 프로젝트 폴더 이름. `[a-zA-Z][a-zA-Z0-9_-]*` 패턴을 따라야 합니다. |
| `--profile docs\|script\|research` | `script` | 개발 도구 프로필 (위 "프로필 선택 기준" 참고). |
| `--modules a,b,c` | `""` | `src/<name>/` 아래에 만들 서브모듈을 쉼표로 구분하여 지정. |
| `--no-uv` | uv 모드 | uv 대신 일반 `python -m venv` + pip 사용. |
| `--no-venv` | venv 켜짐 | `.venv` / `uv sync` 생성을 건너뜀. |
| `--no-git` | git 켜짐 | `git init` + 첫 커밋을 건너뜀. |
| `--license MIT\|NONE` | `MIT` | 생성할 라이선스 파일. |
| `--github none\|private\|public` | `none` | GitHub 원격 저장소 자동 생성 (gh CLI 필요). |
| `-D` / `--delete` | off | 삭제 모드 (폴더 이름 재입력 필요). |
| `--remote` | off | 삭제 모드에서 GitHub 레포도 함께 삭제. |
| `--yes` | off | 삭제 모드에서 확인 프롬프트 생략. |

`python setup_project.py --help`를 실행하면 직접 확인할 수 있습니다.

## 생성되는 항목

- **pyproject.toml** — PEP 621 메타데이터 + PEP 735 dependency-groups (dev/test/lint/notebook), ruff/black/mypy/pytest/coverage 도구 설정.
- **정리용 파일** — `.gitignore`, `.gitattributes` (LF), `.editorconfig`, `.python-version`, `.env.example`.
- **개발 도구** — `.pre-commit-config.yaml` (ruff, black, nbstripout, nbqa), 자기 문서화 `Makefile`.
- **GitHub 자동화** — CI 워크플로 (Python 3.11/3.12 × Linux/Mac/Win 매트릭스), PR/이슈 템플릿, CODEOWNERS, dependabot.
- **src-layout 패키지** — `src/<name>/__init__.py` (사이드 이펙트 없음), `__main__.py`, `cli.py` (typer + loguru), `config.py` (pydantic-settings).
- **테스트** — 공용 `conftest.py`와 함께 동작하는 smoke + CLI 테스트.
- **문서** — 배지가 포함된 README, CHANGELOG (Keep a Changelog), `docs/architecture.md`, `docs/cross-platform.md` (Mac/Windows + CUDA), `docs/uv-cheatsheet.md` (uv 명령어 + pip 와의 차이), ADR 템플릿.
- **플레이스홀더** — `data/{raw,processed,external}/`, `models/`, `notebooks/`, `logs/`.

## 스캐폴딩 이후 (uv 모드)

```bash
cd myproject
uv run myproject --help    # CLI이 이미 설치되어 있음
uv run pytest              # 테스트가 바로 동작
uv run jupyter lab         # notebook 그룹이 dev deps에 포함됨

uv add pandas              # 런타임 의존성 추가
uv add --group test pytest-mock   # 테스트 전용 의존성 추가
uv lock                    # 락파일 재생성
```

## 철학

- **src-layout**은 인-트리 패키지와 설치된 패키지의 우발적 임포트 충돌을 방지합니다.
- **임포트 시 사이드 이펙트 없음** — 로깅은 `__init__.py`가 아닌 CLI 콜백에서 설정합니다.
- **배포 안전한 dev 의존성** — 개발 도구는 `[project.optional-dependencies]`가 아니라 `[dependency-groups]`에 두어 PyPI 메타데이터로 새어나가지 않게 합니다.
- **기본적으로 크로스 플랫폼** — `.gitattributes`로 줄바꿈을 정규화하고, CI 매트릭스가 Linux/Mac/Win을 커버합니다.
