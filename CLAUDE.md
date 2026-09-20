# CLAUDE.md — scaffold 작업 규칙

> 이 저장소에서 AI가 지킬 규칙만 적는다.
> **왜 지금의 모습인가(설계 결정의 이유)** = [docs/design-decisions.md](docs/design-decisions.md) ·
> **사용법(WHAT)** = [README.md](README.md) · **지금까지의 이력과 다음 할 일** = [HANDOFF.md](HANDOFF.md).

## 0. 이 저장소가 뭔지 (한 줄)

범용 Python 프로젝트 스캐폴더. 단일 파일 `setup_project.py`(약 2,200줄, stdlib-only) 하나가 전부이고,
사용자는 `~/.zshrc` 의 `newpy <name>` 함수로 어디서든 호출해 `~/GitStudy/<name>/` 을 만든다.
**사용자가 앞으로 만드는 모든 Python 프로젝트의 시작점**이라 여기서의 변경은 하류로 번진다.

## 1. `setup_project.py` 는 stdlib-only — 외부 의존성 금지

typer·click·rich·jinja 등 **어떤 서드파티도 import 하지 않는다.** 새 venv 를 만드는 도구가
venv 안에 있어야 한다면 첫 사용자가 막히기 때문이다(닭-달걀). 어떤 환경에서도
`python3 setup_project.py myproj` 가 즉시 동작해야 한다.
→ 근거·파생 결정(`--print-completion` 패턴이 왜 이렇게 생겼는지) = [design-decisions §5·§6](docs/design-decisions.md).

이 제약을 깨야 할 상황이 오면, 깨는 것 자체를 **새 결정으로 design-decisions.md 에 기록**한다.

## 2. `--profile` 을 건드리면 다섯 곳을 전부 같이 고친다

프로필(`docs` / `script` / `research`)은 다음 다섯 군데에 영향을 준다:

| # | 산출물 | 코드 |
|---|---|---|
| 1 | `pyproject.toml` 의 `[dependency-groups]` | `_dependency_groups_block` |
| 2 | `.github/workflows/ci.yml` 의 lint/typecheck/test 단계 | `_ci_steps_block` |
| 3 | `Makefile` 의 test/lint/format 타깃 | `tpl_makefile` |
| 4 | pre-commit 훅 자동 설치 여부 (research 만) | `create_project` |
| 5 | 마무리 "Next steps" 안내 문구 | `create_project` 끝부분 |

한 곳만 분기하면 **깔리지도 않은 도구를 CI 가 호출해 레드 빌드**가 난다(실제로 docs 프로필에서
날 뻔했던 버그). → [design-decisions §2](docs/design-decisions.md).

## 3. 결정은 코드가 아니라 design-decisions.md 에 남긴다

"왜 이렇게 했지?" 가 코드만으로 답이 안 나오면 [docs/design-decisions.md](docs/design-decisions.md) 에 적는다.
그 문서가 스스로 정한 갱신 트리거(부록):

1. 프로필 추가/제거 2. 새 안전장치·컨벤션 도입 3. 외부 의존성 도입/제거(§5 원칙 영향 검토)
4. dependabot 이 액션 메이저를 올려 머지할 때(§9) 5. 기본값 변경(이유 기록 필수)

§10 "무엇을 *안* 만들었나" 에 적힌 것들(`--minimal` 프로필, bash 자동완성, `--web`/`--ml` 같은
도메인 프리셋, GitHub Issue 자동 생성)은 **의도적으로 보류된 것**이다. 다시 제안할 때는
§10 의 보류 사유를 먼저 반박한다.

## 4. 언어 — 스크립트는 한국어 주석, 생성되는 템플릿 안은 영문 유지

- `setup_project.py` 의 주석·docstring, README, docs 는 **한국어**.
- 그러나 `tpl_*` 함수가 **뱉어내는 내용**(생성될 프로젝트의 README·CI·PR 템플릿·CODEOWNERS 등)의
  영문 문구는 호환성을 위해 **그대로 유지**한다. 하류 프로젝트가 공개 저장소가 될 수 있고,
  GitHub 도구들이 영문 관례를 전제하기 때문.
- 예외적으로 이미 한국어인 출력(삭제 확인 프롬프트, 일부 `[setup]` 안내)은 그대로 둔다.

## 5. 이 저장소를 고칠 때의 안전 수칙

- 하류 프로젝트에 **소급 적용은 없다.** 이미 생성된 프로젝트(auction_road · make_skills ·
  new_items · startup_beauty 등)는 생성 시점의 템플릿으로 굳어 있다. "스캐폴더를 고쳤으니
  기존 프로젝트도 고쳐졌다"고 가정하지 않는다.
- 삭제 모드(`-d` / `-D`)의 4중 안전장치(폴더 존재 / `pyproject.toml` 존재 / cwd 보호 /
  이름 재입력)는 **줄이지 않는다.** → [design-decisions §3](docs/design-decisions.md).
- `--github` 기본값은 `none` 이다. 외부 공개는 사용자가 명시적으로 opt-in 하는 것이지
  편의를 위해 기본값을 바꾸지 않는다. → [design-decisions §8](docs/design-decisions.md).
- 수정한 뒤에는 임시 이름으로 한 번 생성해 눈으로 확인하고 지운다
  *(기존 문서에 명문화된 규칙은 아니고, 테스트가 없는 단일 파일 도구라서 권장하는 확인 절차)*:
  ```bash
  # 프로젝트 이름은 반드시 영문자로 시작해야 한다(`_smoke` 같은 이름은 거부됨)
  cd /tmp && python3 ~/GitStudy/scaffold/setup_project.py smoketest --no-venv --no-git \
    && find smoketest -type f | sort && rm -rf smoketest
  ```

## 6. 커밋·git

- **AI 가 직접 커밋/푸시하지 않는다.** 변경만 해 두고 `git add` / `git commit` / `git push` 를
  복붙 가능한 블록으로 나눠서 건넨다. 사용자가 직접 친다. (사용자 명시 요청)
- 메시지는 기존 로그 형식대로 **conventional prefix + 간결한 한 줄**
  (예: `feat: --modules 공백 허용 + -d/-D 의미 분리 (UNIX 컨벤션)`). 영문·한국어 혼용 그대로 둔다.
- 커밋 메시지·PR 본문에 **AI 협업 언급(Co-Authored-By 트레일러, "AI와 함께 작업했다" 류 문장)을
  넣지 않는다.** → `/Users/jun/GitStudy/ai_handoff/rules/no_coauthored_by.md`
  (scaffold 는 독립 git 저장소라 저장소 안에서는 링크가 닿지 않는다 — 절대경로로 표기).

## 7. 설명 방식 (사용자 선호)

- **임시방편 말고 근본 해법.** 사용자가 명시적으로 "임시방편이 아니라 근본적으로 필요한 쪽으로
  수정하고 싶다"고 했다.
- 새 기능·옵션·기본값을 제안할 땐 **(1) 추천 (2) 근거 (3) 트레이드오프 (4) 대안**을 같이 낸다.
  정답만 던지지 말 것 — 사용자는 *왜 그게 맞는지*를 이해해야 다음에 스스로 적용한다.
- 길게 써도 된다(표·플로우·근거 환영). 단 군더더기는 뺀다.
