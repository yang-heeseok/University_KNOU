# Project: KNOU CS & DS Learning Hub 구축

## 1. 페르소나 (Persona)

*   **소속**: 한국방송통신대학교
*   **전공**: 컴퓨터과학과 (주전공), 통계-데이터과학과 (복수전공)
*   **학년**: 3학년 2학기
*   **수강 과목 (6과목)**:
    *   **교양**: 경제학의이해, 심리학에게묻다
    *   **전공**: 데이터과학개론, 파이썬과R, 파이썬데이터처리, 파이썬컴퓨팅

## 2. 핵심 목표 (Core Objectives)

1.  **지식의 중앙화**: 모든 학습 자료(노트, 코드, 요약, 과제)를 단일 저장소(Single Source of Truth)에서 체계적으로 관리한다.
2.  **효율적 학습 사이클 구축**: '사전학습 → 본수업 → 복습/정리 → 실습'의 학습 사이클을 정립하고, 각 단계별 활동을 시스템화한다.
3.  **콘텐츠의 재사용성 극대화**: 한번 학습하고 정리한 내용은 시험 준비, 프로젝트, 기술 블로그 포스팅 등 다양한 목적으로 쉽게 재활용할 수 있는 구조를 만든다.
4.  **공유 가능한 지식 자산화**: 학습 결과물을 공개(Public)하여 타 학생들에게 도움을 주고, 잠재적인 동료 학습자/리뷰어와 상호작용할 수 있는 기반을 마련한다.
5.  **학습 과정 자동화**: 단순 반복적인 작업을 자동화하여 핵심적인 '학습' 활동에만 집중할 수 있는 환경을 구축한다. (DevOps for Learning)

## 3. 방법론 및 핵심 전략 (Methodology & Key Strategies)

### 3.1. 지식 중앙화: Git & GitHub

*   모든 학습 산출물은 GitHub Private Repository에서 관리 시작. (필요시 Public으로 전환)
*   Markdown(.md) 파일을 기본 문서 포맷으로 사용하여 가독성과 이식성을 높인다.
*   Jupyter Notebook(.ipynb)은 코드, 설명, 실행 결과를 통합하여 관리하는 데 사용한다.
*   의미 있는 단위로 `commit`하여 학습 이력을 추적하고, `branch` 전략을 활용해 과제나 특정 주제 심화 학습을 관리한다.

### 3.2. 구조화된 학습 프로세스

*   **사전 학습**: 강의 계획에 따라 관련 키워드를 LLM에게 질문하여 기본 개념을 익히고, 질문 목록을 생성한다.
*   **수업 중**: 핵심 내용을 마크다운으로 실시간 정리. 이해가 어려운 부분은 별도 표시(`[TODO]`, `[QUESTION]`).
*   **복습 및 정리**: 수업 후 노트를 완성하고, LLM을 활용해 핵심 내용을 3줄로 요약하거나, 복잡한 개념을 더 쉽게 풀어 설명하도록 요청한다.
*   **실습 및 적용**:
    *   배운 내용을 바탕으로 예제 코드를 작성하고 Jupyter Notebook에 기록한다.
    *   LLM에게 학습한 개념에 대한 연습문제나 미니 프로젝트 아이디어를 요청하여 해결해본다.

### 3.3. 자동화 파이프라인 (Automation Pipeline)

*   **GitHub Actions 활용**:
    *   **CI (Continuous Integration)**: Python/R 코드 push 시, 자동으로 Linting(코드 스타일 검사) 및 간단한 테스트를 수행하여 코드 품질을 유지한다.
    *   **CD (Continuous Deployment)**: `main` 브랜치에 노트(Markdown)가 업데이트되면, Jekyll 또는 MkDocs를 통해 자동으로 GitHub Pages 블로그에 배포한다.
    *   **Notification**: 특정 작업(예: 배포 완료, 테스트 실패) 완료 시 Slack 또는 Discord로 알림을 보낸다.

### 3.4. LLM 적극 활용 (AI-Powered Learning)

*   **개념 학습**: "너는 [과목명] 교수님이야. [개념]에 대해 중학생도 이해할 수 있게 설명해줘."
*   **콘텐츠 생성**: "지금까지 정리한 [주제] 노트를 기반으로 예상 시험 문제 5개와 정답을 만들어줘."
*   **코드 리뷰 및 리팩토링**: "이 Python 코드는 [기능]을 구현한 거야. 더 효율적이고 가독성 좋게 리팩토링해줘."
*   **에러 디버깅**: "이 코드 실행 시 [에러 메시지]가 발생했어. 원인과 해결 방법을 알려줘."
*   **자동 요약**: "아래 마크다운으로 정리된 수업 내용을 핵심만 요약해서 블로그 포스트 초안을 작성해줘."

## 4. 제안 디렉토리 구조 (Proposed Directory Structure)

```
KNOU-CS-DS-Learning-Hub/
├── .github/
│   └── workflows/          # GitHub Actions 워크플로우 (자동화)
│       ├── deploy-notes.yml
│       └── python-ci.yml
├── courses/
│   ├── 1_economics/        # 경제학의이해
│   ├── 2_psychology/       # 심리학에게묻다
│   ├── 3_intro_to_ds/      # 데이터과학개론
│   ├── 4_python_and_r/     # 파이썬과R
│   ├── 5_python_data/      # 파이썬데이터처리
│   └── 6_python_compute/   # 파이썬컴퓨팅
│       ├── notes/          # 강의 노트 (Markdown)
│       ├── code/           # 실습 코드 (py, R, ipynb)
│       ├── assignments/    # 과제
│       └── resources/      # 관련 자료, 논문, 링크
├── blog/                   # GitHub Pages로 배포될 블로그 소스 (Jekyll/MkDocs)
├── scripts/                # 자동화에 사용될 셔ㅣㄹ 스크립트
└── README.md               # 프로젝트 개요 및 진행 상황
```

## 5. 기술 스택 (Technology Stack)

*   **Version Control**: Git, GitHub
*   **Documentation**: Markdown
*   **IDE/Editor**: VS Code
*   **Coding**: Python, R, Jupyter Notebook
*   **Automation**: GitHub Actions
*   **Publishing**: GitHub Pages, Jekyll (or MkDocs)
*   **Communication**: Slack (or Discord) for notifications
*   **AI Assistant**: Gemini, ChatGPT 등 LLM
```

### 추가 참고 자료

이러한 학습 방식을 실천하는 데 도움이 될 만한 자료들입니다.

*   **GitHub Pages 공식 문서**: [https://pages.github.com/](https://pages.github.com/)
    *   정리한 노트를 웹사이트로 쉽게 만들 수 있습니다.
*   **MkDocs (문서 사이트 생성기)**: [https://www.mkdocs.org/](https://www.mkdocs.org/)
    *   마크다운 파일로 전문적인 문서 사이트를 쉽게 구축할 수 있는 도구입니다. Jekyll보다 간단할 수 있습니다.
*   **GitHub Actions 공식 문서**: [https://docs.github.com/ko/actions](https://docs.github.com/ko/actions)
    *   자동화 파이프라인을 구축하기 위한 핵심 자료입니다.
*   **"Learning in Public" 개념**: [https://www.swyx.io/learn-in-public](https://www.swyx.io/learn-in-public)
    *   학습 과정을 공개적으로 공유하는 것의 가치에 대해 설명하는 유명한 글입니다. 프로젝트의 '공유' 목표와 일맥상통합니다.

이 `context.md` 파일이 앞으로의 학습 여정에 훌륭한 나침반이 되기를 바랍니다. 성공적인 학기 보내세요!

<!--
[PROMPT_SUGGESTION]위 `context.md`의 `제안 디렉토리 구조`를 실제로 생성하는 쉘 스크립트를 작성해줘.[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]GitHub Actions를 사용해서 `courses` 폴더의 마크다운 파일이 변경되면 MkDocs를 이용해 GitHub Pages에 자동으로 배포하는 `deploy-notes.yml` 워크플로우 파일을 작성해줘.[/PROMPT_SUGGESTION]
