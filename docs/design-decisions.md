# 설계 결정 (Design Decisions)

> 왜 이 스캐폴더가 지금의 모습인가에 대한 기록.
> 사용법(WHAT)은 [README](../README.md), 여기는 그 *이유*(WHY).

이 문서는 코드만 봐서는 추측할 수밖에 없는 결정들을 모아 둡니다. 다음에 같은
질문이 떠올랐을 때 다시 토론하지 않으려고 적어 두는 거예요.

---

## 1. 프로필 시스템 (docs / script / research)

### 결정
세 개의 용도 기반(use-case) 프로필을 제공한다. **기본값은 `script`**.

- `docs` — 마크다운/지식 정리. ruff 만 (~10 패키지).
- `script` — 일반 Python 코드. test + lint (~30).
- `research` — 데이터 분석 / ML / 노트북. test + lint + notebook + pre-commit (~80).

### 왜 크기 기준(`lite/full/minimal`) 이 아닌 용도 기준인가
크기 기준은 옵션이 늘어나면 의미가 흐려진다 — "medium-lite-plus" 같은 끔찍한
이름으로 진화함. 용도 기준은 새 용도가 등장하면 새 단어로 *추가* 만 하면 되고,
기존 의미는 안 흔들림. 또 사용자가 자기 프로젝트의 *정체성* 을 한 번은
명명하게 강제하는 사고 훈련 효과도 있다.

### 왜 `script` 가 기본값인가
통계적으로 가장 흔한 케이스. "노트북 안 씀 + 코드 유지보수함" 이 신규 사용자의
80%. `research` 가 기본이면 데이터 분석 안 하는 사람도 매번 80개 패키지를
받게 되고, `docs` 가 기본이면 코드 짜는 사람이 매번 `--profile script` 를
적어야 한다. 신규 사용자의 첫 경험이 가벼움 = 좋은 디폴트.

### 선택 기준 한 줄
> 노트북을 매일 열 거면 **research**, 코드 파일만 만질 거면 **script**, 마크다운 정리용이면 **docs**.

### 도메인 매핑 예시
| 도메인 | 프로필 |
|---|---|
| 데이터 분석, ML 실험, Jupyter 작업 | research |
| FastAPI 서버, 텔레그램 봇, CLI 도구, pygame 게임, 자동화 스크립트 | script |
| 학습 노트, 스킬 모음, 회의록 정리 | docs |
| **프론트엔드 (React/Next.js)** | ❌ 이 스캐폴더 부적합. JS 생태계 도구 사용 |

도메인이 결정하는 건 **프로필이 아니라 런타임 의존성**이다 — pandas, fastapi,
pygame 같은 라이브러리는 프로젝트 생성 후 `uv add` 로 채운다. 프로필은
*도구* (테스트/린트/노트북) 만 결정한다.

---

## 2. 프로필 인식의 범위

### 결정
`--profile` 은 다음 *모든* 산출물에 영향을 준다:

1. `pyproject.toml` 의 `[dependency-groups]`
2. `.github/workflows/ci.yml` 의 lint/typecheck/test 단계
3. `Makefile` 의 test/lint/format 타깃
4. `pre-commit` 훅 자동 설치 여부 (research 만)
5. 스크립트 마무리 "Next steps" 안내 메시지

### 왜
한 곳만 분기하면 *깔리지도 않은 도구를 안내하거나 호출* 해서 사용자에게 혼란
또는 실제 실패(CI 레드 빌드)를 일으킨다. 첫 구현 때 의존성 그룹만 분기하고
나머지를 잊었던 게 실제로 docs 프로필의 CI 를 깨뜨릴 뻔한 잠재 버그였음.

프로필 인식이 누락된 부분은 *반드시* 나중에 발현된다. 한 번 추가할 때
전부 일관되게 분기시키는 것이 원칙.

---

## 3. `-d` / `-D` 의미 분리 (UNIX 컨벤션)

### 결정
- `-d` / `--delete` = 안전 삭제 (폴더 이름 재입력 프롬프트 거침)
- `-D` = 강제 삭제 (`-d --yes` 와 동등, 확인 생략)

### 왜
UNIX 도구의 `-i` / `-f` 패턴 (`rm -i` 인터랙티브 / `rm -f` 강제) 과 같은
사고방식. 소문자 = 안전, 대문자 = 강제. 사용자에게 익숙한 컨벤션이고
대소문자 차이가 의도를 명확히 전달.

초기 구현에선 `-D` 하나만 두고 "destructive 동작이라 Shift 한 번 강제" 라는
약한 가드를 의도했지만, 이미 4중 안전장치(폴더 존재 / pyproject 검증 / cwd 보호 /
이름 재입력) 가 있는 상황에서 Shift 추가 1번의 실질 보호는 거의 0. 표준
컨벤션을 따라가는 게 더 가치 있다.

### 4중 안전장치 (delete_project 안)
1. 폴더가 실제로 존재
2. 폴더 안에 `pyproject.toml` 존재 (= 스캐폴드로 만든 폴더로 보임)
3. 현재 작업 디렉토리가 삭제 대상 안이면 거부 (rm -rf cwd 사고 방지)
4. 폴더 이름을 다시 입력해야 진행 (`--yes` 또는 `-D` 만 우회)

---

## 4. `--modules` 공백 허용

### 결정
다음 세 형식이 모두 동일하게 동작:
```
--modules detection,tracking,risk
--modules detection tracking risk
--modules "detection, tracking, risk"
```

### 왜
초기 구현은 단일 값 (`detection,tracking,risk`) 만 받았는데, 자연스러운 공백
표기를 사용하면 셸이 공백으로 토큰을 잘라 새 위치 인자로 인식되면서
조용히 실패. UX 함정. `nargs="*"` + 후처리(`split()` 으로 공백·쉼표 모두 분해) 로
세 형식 모두 흡수.

---

## 5. `setup_project.py` 는 stdlib-only

### 결정
스캐폴더 본체는 **표준 라이브러리만** 사용한다. typer, click, rich 등 외부
라이브러리 금지.

### 왜
스캐폴더의 닭-달걀 문제: 새 venv 를 만드는 도구가 venv 안에 있어야 한다면
처음 사용하는 사람이 막힌다. 어떤 환경에서도 `python3 setup_project.py myproj`
가 즉시 동작해야 한다.

이 제약은 자동완성을 typer 의 `--install-completion` 대신 **`--print-completion zsh`** 라는
자체 출력 + `eval` 패턴으로 푼 이유이기도 하다. typer 도입은 매력적이지만
stdlib-only 가치보다 작다.

---

## 6. `--print-completion` 패턴

### 결정
zsh 완성 함수를 setup_project.py 안에 문자열로 보관하고, `--print-completion zsh`
가 stdout 으로 출력. `.zshrc` 에서 `eval "$(... --print-completion zsh)"` 로 소싱.

### 왜
완성 정의가 스크립트 안에 *단일 출처* 로 존재하므로 옵션을 추가/변경해도
`.zshrc` 를 손댈 필요가 없다. 새 머신 셋업 시에도 README 의 한 블록만
복붙하면 된다. typer 의 `--install-completion` 만큼 매끄럽고, stdlib-only
도 깨지 않는다.

비용: 셸 시작 시 매번 python 한 번 호출(~100ms). 체감 안 됨. 정 거슬리면
결과를 캐시 파일로 떨굴 수 있지만 현재 필요 없음.

---

## 7. notebook 그룹은 슬림 (jupyter 제외)

### 결정
research 프로필의 `notebook` 그룹은 `ipykernel` + `nbqa` + `nbstripout` 만.
`jupyter` 패키지 자체는 포함하지 않는다.

### 왜
주된 사용자가 VS Code / PyCharm 에서 `.ipynb` 를 열어 작업. 거기에 필요한 건
**커널(`ipykernel`)** 뿐. 브라우저 Jupyter Lab UI 는 거의 안 씀.
`jupyter` 메타패키지는 jupyter-server, notebook, jupyterlab 등 약 15개를
끌고 와서 .venv 크기를 크게 늘림.

브라우저 UI 가 필요한 사람은 `uv add --group notebook jupyter` 로 명시적
opt-in 하면 된다.

---

## 8. GitHub 자동 생성 / 삭제

### 결정
- `--github private|public` 으로 *명시적 opt-in* 시에만 GitHub 레포 생성. 기본값 `none`.
- 삭제 시 `--remote` 로 GitHub 레포까지 제거. `gh auth refresh -h github.com -s delete_repo` 사전 필요.

### 왜
의도하지 않은 외부 노출은 되돌리기 어렵다 (특히 비밀 정보가 섞이면). 따라서
기본은 *로컬만*, 외부 푸시는 사용자가 직접 선택. gh CLI 누락 시에는 친절한
안내만 출력하고 로컬 진행은 그대로 유지 (치명적 오류 아님).

---

## 9. dependabot 액션 버전 고정

### 결정
`tpl_ci_workflow` 안의 GitHub Actions 들은 현재 최신 메이저로 박아 둔다
(`checkout@v6`, `setup-uv@v7`, `cache@v5`, `setup-python@v5`).

### 왜
첫 푸시 직후 dependabot 이 즉시 깨어나 옛 버전들을 자동 PR 로 올리는데,
이 노이즈가 모든 신규 프로젝트마다 반복된다. 템플릿 자체를 최신 상태로
유지하면 깨끗하게 시작 가능. 메이저 버전이 또 오르면 그때 한 번에 갱신.

---

## 10. 무엇을 *안* 만들었나 (의도적 비결정)

다음은 아직 만들지 않았고, 만들 필요가 생기면 그때 결정한다:

- **`--minimal` 프로필**: docs 가 충분히 가벼움 (10 패키지). 더 줄여 봤자 차이 미미.
- **bash 자동완성**: 현재 사용자가 zsh 전용. bash 추가는 같은 패턴 5분이면 됨.
- **도메인별 런타임 프리셋** (`--web` fastapi, `--ml` torch 등): 옵션 폭발 위험. 사용자가 `uv add` 로 직접 추가하는 게 더 명확.
- **GitHub Issue 자동 생성**: 스캐폴더의 책임 범위 밖.

---

## 부록: 이 문서의 트리거

다음 상황에서 이 문서를 갱신한다:

1. 새 프로필을 추가/제거할 때 (1번 표 갱신)
2. 새 안전장치/컨벤션을 도입할 때 (3·8번 식)
3. 외부 의존성을 도입/제거할 때 (5번 원칙 영향 검토)
4. dependabot 이 새 액션 메이저를 권장해 머지할 때 (9번 버전 박아 두기)
5. 기본값을 바꿀 때 (이유 기록 필수)

"왜 이렇게 했지?" 가 코드만으로 답이 안 나오면 여기 적어 두기.