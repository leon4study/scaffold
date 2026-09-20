# HANDOFF — scaffold 인수인계

> **처음 이 프로젝트를 보는 AI(클로드·커서·제미나이 무엇이든)를 위한 온보딩 문서.**
> 규칙 레퍼런스 = [CLAUDE.md](CLAUDE.md) · 사용법(WHAT) = [README.md](README.md) · 설계 결정의 이유(WHY) = [docs/design-decisions.md](docs/design-decisions.md)
> 작성: 2026-09-20 (계정 전환 대비 · 이 저장소에 기존 handoff 류 파일은 없었다)

---

## 1. 한 줄 요약

범용 Python 프로젝트 스캐폴더. **단일 파일 `setup_project.py`(약 2,200줄, 표준 라이브러리만)** 가 전부이고,
사용자는 `~/.zshrc` 의 `newpy <name>` 함수로 어느 디렉토리에서든 호출해 `~/GitStudy/<name>/` 에
프로덕션 수준 골격(pyproject · CI · src-layout · 테스트 · 문서)을 만든다.

저장소는 600KB 대(대부분 `.git`)로 작지만 **사용자가 앞으로 만드는 모든 Python 프로젝트의 시작점**이다 —
여기서의 변경은 하류 프로젝트 전체의 출발 모양을 바꾼다.

## 2. 현재 상태

**출처: `git log`(10개 커밋 전수) · `git status` · 이번 세션의 스모크 테스트.** 이 저장소에는
STATUS.md·work-log 류가 없어서 git log 와 문서 본문이 사실상 유일한 출처다.

- **완성되어 그대로 쓰이고 있음.** 마지막 커밋은 `3ee2cc6`(2026-05-27 18:32,
  `docs: capture session design decisions`). 작업 트리는 깨끗하고 `origin/main`
  (https://github.com/leon4study/scaffold.git) 과 동기화돼 있었다.
- **10개 커밋 전부가 2026-05-27 하루(12:47~18:32)에 찍혀 있다.** 즉 한 세션에 만들어졌고,
  그 뒤 오늘(2026-09-20)까지 **약 4개월간 코드 변경이 없다.** 방치가 아니라 "문제가 없어서
  안 건드린" 상태로 보이나, 사용자 확인은 없다 `⟨확인 필요⟩`.
- **동작 확인(2026-09-20, 이번 세션)**: 임시 폴더에서 `python3 setup_project.py smoketest
  --no-venv --no-git` 실행 → 36개 파일 정상 생성(`skills/.gitkeep` 포함), `--help` 정상.
  uv 모드·git·GitHub 경로는 이번에 돌리지 않았다 `⟨확인 필요⟩`.
- **막혀 있는 것 없음.** 보류 중인 것은 의도적 보류다 → [design-decisions §10](docs/design-decisions.md).

**이번 세션(2026-09-20)에 추가된 미커밋 변경** — 전부 문서/주석이며 동작 변경 없음:

| 파일 | 변경 |
|---|---|
| `CLAUDE.md` | **신규** (이전엔 없었다) |
| `HANDOFF.md` | **신규** (이 파일) |
| `README.md` | "생성되는 항목"에 빠져 있던 `skills/` 추가 · 플래그 표에 `--print-completion` 행 추가 |
| `setup_project.py` | `create_project` docstring 의 **낡은 서술** 교정(§5 참조) · `detect_git_user` docstring 의 git config 우선순위 서술 교정 |

> 이 저장소에 **오래된 미완 WIP 은 없었다.** 작업 트리는 이 세션 시작 시점에 완전히 깨끗했다.

## 3. 구조 지도

파일이 5개뿐이라 표로 전부 덮인다.

| 위치 | 뭐가 있나 |
|---|---|
| `setup_project.py` | 스캐폴더 본체. 맨 위 모듈 docstring 이 사실상 매뉴얼(하는 일·사용법·플래그·설계 철학). 구조: 상수 → 환경 감지 헬퍼(`detect_git_user`/`have_uv`/`have_gh`) → `tpl_*` 순수 함수 30여 개(파일 한 개의 *내용*을 문자열로 반환) → `create_project`(오케스트레이터) → `delete_project` → `_ZSH_COMPLETION` → `parse_args`/`main` |
| `README.md` | 사용법(WHAT). 프로필 선택 기준·3단계 결정 플로우·`newpy` zsh 함수 설치법·플래그 표·생성물 목록 |
| `docs/design-decisions.md` | **이 저장소의 핵심 문서.** 10개 결정의 *이유*와 §10 "무엇을 안 만들었나", 부록의 문서 갱신 트리거 |
| `CLAUDE.md` | AI 작업 규칙(2026-09-20 신규) |
| `HANDOFF.md` | 이 파일 |

- **저장소 자체에는 `.gitignore`·테스트·CI 가 없다.** 남에게는 만들어 주지만 자기 자신에게는
  적용하지 않은 상태 — stdlib-only 단일 파일이라 의존성도 빌드도 없기 때문으로 보이나,
  의도적 결정인지는 문서에 없다 `⟨확인 필요⟩`.
- **저장소 밖 의존**: `~/.zshrc` 132~140행의 `newpy` 함수 + `eval "$(... --print-completion zsh)"`.
  새 기계로 옮기면 README "어디서든 한 줄로 실행하기" 절차를 다시 밟아야 한다.

## 4. 작업 흐름 타임라인

**출처: `git log --reverse`(시각 포함) + `~/.claude/projects/-Users-jun-GitStudy/memory/project_scaffold.md`.**
날짜가 특정되는 것만 적는다.

| 시각 | 무슨 일 | 파생된 것 |
|---|---|---|
| ~2026-05-27 이전 | `setup_project.py` 가 GitStudy 루트에 **README 없는 단일 파일**로 굴러다님. 옵션이 기억 안 나는 게 문제였음(출처: 루트 memory) | 이 시기 버전으로 SynerGNet·collision_detection 이 스캐폴드됨 |
| 05-27 12:47 | `40d4289` 초기 커밋 — 자체 저장소로 분리 + README | `setup_project.py` + `README.md` |
| 05-27 12:59 | `efa7c9b` `newpy` zsh 함수 문서화 (한 줄로 어디서든 생성) | README 의 zsh 절 |
| 05-27 14:54 | `607b823` 삭제 모드 · GitHub 자동화 · `skills/` 자리잡이 · 문서 한국어화 | `delete_project`, `--github`, 4중 안전장치 |
| 05-27 15:14 | `462cac7` notebook 그룹 슬림화(jupyter 메타패키지 제외) | [design-decisions §7](docs/design-decisions.md) |
| 05-27 15:35 | `2347d0f` zsh 자동완성 생성기 + `newpy` 를 `python3` 로 (macOS 엔 `python` 이 없음) | `--print-completion`, `_ZSH_COMPLETION` |
| 05-27 17:01 | `3fbc8d6` **`--profile {docs,script,research}`** 도입 (크기 기준이 아닌 용도 기준) | `_dependency_groups_block` |
| 05-27 17:41 | `3f62093` 프로필 인식을 CI·Makefile·next-steps 까지 확대 — **docs 프로필 CI 가 깨질 뻔한 잠재 버그를 잡음** | `_ci_steps_block`, `tpl_makefile(profile)` |
| 05-27 17:48 | `85caf60` GitHub Actions 메이저 고정(checkout v6 / setup-uv v7 / cache v5 / setup-python v5) — 신규 레포마다 dependabot PR 이 쏟아지는 노이즈 제거 | [design-decisions §9](docs/design-decisions.md) |
| 05-27 18:23 | `bc50df0` `--modules` 공백 허용 + `-d`/`-D` 분리(UNIX 컨벤션) | `nargs="*"` + 후처리, 삭제 플래그 2종 |
| 05-27 18:32 | `3ee2cc6` 그날의 결정들을 `docs/design-decisions.md` 로 박제 | 이 저장소의 핵심 문서 |
| 2026-09-20 | 계정 전환 대비 정비 — `CLAUDE.md`·`HANDOFF.md` 신규, README 2곳 보강, 낡은 docstring 2곳 교정 | (이 세션) |

**하류에서 이 도구로 만들어진 것(2026-09-20 확인, `docs/uv-cheatsheet.md` 존재로 판별)**:
`auction_road` · `make_skills` · `new_items` · `startup_beauty`.
`SynerGNet`·`collision_detection` 은 분리 이전 버전으로 만들어졌다고 루트 memory 에 적혀 있다
(현재 `~/GitStudy/SynerGNet/` 폴더는 비어 있음).

## 5. 이 프로젝트의 규칙

### 5-1. 대화(memory)에만 있고 어느 문서에도 없던 것 — **계정 전환 시 유실 위험 최상**

출처: `~/.claude/projects/-Users-jun-GitStudy-scaffold/memory/` (2개 파일) + 루트 memory 의 `project_scaffold.md`.

- **이 도구는 사용자 워크플로의 *기반*으로 확정된 것이다**(memory 원문): *"사용자가 이 도구를
  본인 워크플로의 기반으로 쓰기로 함. 앞으로 만드는 모든 Python 프로젝트가 `newpy` 로 시작 …
  즉 이 스캐폴더의 결정들이 사용자의 모든 미래 프로젝트의 시작점이 됨."*
  → 새 Python 프로젝트 얘기가 나오면 스캐폴딩 절차를 새로 유도하지 말고 **`newpy <name>` 을 권한다.**
- **스캐폴딩 로직을 고칠 땐 `~/GitStudy/scaffold/setup_project.py` 를 직접 고친다.** 다음
  `newpy` 호출에 즉시 반영된다 — 함수 자체를 바꿀 때만 `source ~/.zshrc` 가 필요하다.
- **한국어 친화 + 생성물 영문 유지**(memory 원문): *"코드 내 주석/문서 한국어 선호(단 생성될
  템플릿 안의 영문 콘텐츠는 호환성 위해 유지)."* → 이번에 [CLAUDE.md §4](CLAUDE.md) 로 옮겨 적었다.
- **결정을 제시하는 방식**: *"장기적/근본 해법 선호 — 임시방편이 아니라 근본적으로 필요한 쪽으로.
  단순 답보다 왜 그런 선택을 했는지 선택 기준과 과정을 알려 달라"*, *"학습 위주 — 정답만 주지 말기"*
  (시나리오 퀴즈식으로 스스로 풀고 채점받는 흐름이 잘 맞았다는 기록).
  → 프로젝트를 넘어 적용되므로 포터블 사본을 만들어 뒀다:
  `/Users/jun/GitStudy/ai_handoff/rules/scaffold_decisions_with_tradeoffs.md`.
- **git 작업은 복붙**(memory 원문): *"커밋 푸시 내가 직접할 수 있게 복붙할 수 있게 줘"* —
  `git add`/`commit`/`push` 를 코드 블록 3개로 나눠 주고 AI 가 직접 실행하지 않는다.
  이건 이미 허브에 있는 규칙(`startup_beauty_manual_git_mode.md`, 2026-08-01)과 같은 내용인데,
  **여기 기록이 2026-05-27 로 더 이르다** — 즉 한 프로젝트 특유의 요구가 아니라 원래부터의 습관.
  중복 사본은 만들지 않았다.
- **사용자가 말한 다음 작업 후보**(2026-05-27 시점): ① 첫 스킬 만들 때 도움 요청
  (`~/GitStudy/make_skills/skills/`) ② bash 자동완성 추가 ③ 도메인별 런타임 프리셋(신중).
  이후 진행 여부는 `⟨확인 필요⟩`.
- **루트 memory 의 낡은 조각**: `~/.claude/projects/-Users-jun-GitStudy/memory/project_scaffold.md`
  의 `newpy` 스니펫은 `python` 으로 적혀 있는데, **실제 `~/.zshrc` 와 README 는 `python3`** 다
  (2026-05-27 15:35 `2347d0f` 에서 바뀜 — macOS 엔 `python` 이 없다). 그 memory 파일을 근거로
  `.zshrc` 를 고치지 말 것. (memory 원본은 이번에 수정하지 않았다.)

### 5-2. 문서에 이미 있는 하드룰 (요약하지 않고 링크만)

- 작업 규칙 전반(stdlib-only · 프로필 5곳 동시 수정 · 언어 정책 · 커밋 · 설명 방식) → [CLAUDE.md](CLAUDE.md)
- 결정 10개의 이유 + 의도적 비결정 + 문서 갱신 트리거 → [docs/design-decisions.md](docs/design-decisions.md)
- 플래그·프로필 선택 기준·`newpy` 설치법 → [README.md](README.md)
- 스크립트가 하는 일 전체 목록 → `setup_project.py` 최상단 모듈 docstring

## 6. 주의사항

- **민감 파일 없음.** 이 저장소에는 `.env`·키·토큰 파일이 존재하지 않는다. 코드 안의
  `.env.example` 은 *생성될 파일의 내용을 만드는 템플릿 문자열*(`tpl_env_example`)일 뿐 실제
  자격증명이 아니다.
- **하드코딩된 작성자 폴백**: `DEFAULT_AUTHOR_NAME = "Hyunjun"` / `DEFAULT_AUTHOR_EMAIL =
  "leo4study@gmail.com"`(파일 상단 상수). git config 를 못 읽을 때만 쓰인다. 2026-09-20 실측
  기준 실제 생성물에는 전역 git config 값(`leon` / 같은 이메일)이 들어갔다. 이름은 폴백 상수와
  다르므로, 폴백을 그대로 둘지 갱신할지는 사용자 판단 `⟨확인 필요⟩`.
- **`detect_git_user()` 는 `--global` 을 쓰지 않는다** → 실행 위치의 *로컬* git 설정이 이기고,
  그 값이 생성물의 `LICENSE`·`pyproject authors` 에 박힌다. 회사/타인 명의 설정이 걸린 저장소
  안에서 실행하면 그대로 새 나간다는 뜻. (docstring 은 이번에 사실에 맞게 고쳤다.)
- **하류 프로젝트에 소급 적용은 없다.** 이미 생성된 프로젝트는 생성 시점 템플릿으로 굳어 있다.
  스캐폴더를 고쳤다고 기존 프로젝트가 따라 바뀌지 않는다.
- **삭제 모드는 진짜로 지운다.** `-D` 는 확인 없이 `rm -rf` 다. 테스트할 땐 반드시 임시 디렉토리에서.
- **`~/.zshrc` 는 사용자 영역** — 함수 정의를 바꿔야 하면 직접 편집하지 말고 복붙 블록으로 건넨다
  (§5-1 git 복붙 선호와 같은 맥락).
- **프로젝트 이름 규칙**: 영문자로 시작 + 영숫자/`_`/`-` 만. `_smoke` 처럼 밑줄로 시작하면 거부된다
  (스모크 테스트하다 실제로 막힌 부분).
- **저장소 밖 관찰 — 건드리지 않았음**: `~/GitStudy/.git/` 이 `info/`·`objects/` 만 있는 **깨진 stub**
  이라 `git rev-parse` 가 "not a git repository" 로 실패한다. scaffold 자체와는 무관하지만,
  `newpy` 가 `cd ~/GitStudy` 후 실행되므로 "GitStudy 루트의 로컬 git 설정" 같은 건 현재 존재하지
  않는다는 뜻이다. 이 stub 의 정체·처리 여부는 사용자 확인 `⟨확인 필요⟩`.

## 7. 다음 AI가 할 일

1. **[docs/design-decisions.md](docs/design-decisions.md) 를 먼저 읽는다.** scaffold 관련 질문의
   90%는 여기 답이 있고, 새 제안은 여기 원칙(stdlib-only · 프로필 5곳 일관 분기)을 깨는지부터 확인한다.
2. **§10 "무엇을 안 만들었나" 를 확인한 뒤 제안한다.** `--minimal`·bash 자동완성·`--web`/`--ml`
   프리셋·Issue 자동 생성은 이미 보류 사유가 적혀 있다 — 다시 제안하려면 그 사유를 먼저 반박할 것.
3. 코드를 고쳤으면 [CLAUDE.md §5](CLAUDE.md) 의 스모크 명령으로 한 번 생성해 보고 지운다(테스트 없음).
4. 사용자가 새 Python 프로젝트를 시작한다고 하면 절차를 새로 설명하지 말고 `newpy <name> --profile X`
   한 줄을 준다.

### 열려 있는 질문

- 2026-05-27 이후 4개월간 변경이 없는데, 그 사이 `newpy` 로 만든 프로젝트에서 불편했던 점이
  있는가? (있다면 그게 다음 작업 목록이다) `⟨확인 필요⟩`
- GitHub Actions 메이저 버전(§9: checkout v6 / setup-uv v7 / cache v5 / setup-python v5)이
  그동안 또 올랐는가? 템플릿을 최신으로 유지하는 게 §9 결정의 전제다 `⟨확인 필요⟩`
- bash 자동완성·첫 스킬 작성 지원(2026-05-27 에 사용자가 꼽은 후보)은 여전히 하고 싶은가? `⟨확인 필요⟩`
- `DEFAULT_AUTHOR_NAME = "Hyunjun"` 폴백을 실제 git 이름(`leon`)에 맞출 것인가, 그대로 둘 것인가? `⟨확인 필요⟩`
