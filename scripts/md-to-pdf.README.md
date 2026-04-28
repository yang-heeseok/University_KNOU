# md-to-pdf.js

Markdown 파일을 A4 PDF로 변환하는 스크립트. [md-to-pdf](https://www.npmjs.com/package/md-to-pdf) 패키지 기반이며, mermaid 다이어그램을 [@mermaid-js/mermaid-cli](https://www.npmjs.com/package/@mermaid-js/mermaid-cli)(`mmdc`)로 사전 렌더링하여 SVG로 임베드합니다.

## 사전 설치

```bash
# 필수
npm install -g md-to-pdf

# Mermaid 다이어그램이 포함된 문서를 변환할 때 필요
npm install -g @mermaid-js/mermaid-cli
```

`mmdc`가 PATH에 없으면 mermaid 블록은 코드 그대로 출력됩니다(경고 메시지 표시).

## 기본 사용법

```bash
node scripts/md-to-pdf.js <파일 또는 glob 패턴> [옵션]
```

출력 PDF는 입력 파일과 같은 디렉토리에 동일 이름(`*.pdf`)으로 생성됩니다.

### 단일 파일

```bash
node scripts/md-to-pdf.js subjects/4-2/컴퓨터보안/Submitted_Files/컴퓨터보안_중간_202334-153257.md
```

### 여러 파일 (glob 패턴)

```bash
node scripts/md-to-pdf.js "subjects/**/integrated_report.md"
```

### 출력 경로 지정 (단일 파일만 가능)

```bash
node scripts/md-to-pdf.js report.md -o output/report.pdf
```

## 옵션 전체

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--margin-top <값>` | 위 여백 | `6mm` |
| `--margin-bottom <값>` | 아래 여백 | `6mm` |
| `--margin-left <값>` | 왼쪽 여백 | `20mm` |
| `--margin-right <값>` | 오른쪽 여백 | `40mm` |
| `--image-scale <값>` | 일반 이미지 크기(CSS `width`로 적용) | 미적용 |
| `--mermaid-scale <값>` | Mermaid 다이어그램 크기 | `100%` |
| `--output, -o <경로>` | 출력 파일 경로 (단일 파일 한정) | 입력 파일명.pdf |
| `--help, -h` | 도움말 출력 | |

여백 값은 `mm`, `cm`, `in`, `px` 등 CSS 단위를 사용할 수 있습니다.

## 자주 쓰는 조합

### A. 좁은 여백 + 작은 mermaid

```bash
node scripts/md-to-pdf.js report.md \
  --margin-top 5mm --margin-bottom 5mm \
  --margin-left 15mm --margin-right 15mm \
  --mermaid-scale 70%
```

### B. 기본 여백, mermaid 80% 축소

```bash
node scripts/md-to-pdf.js report.md --mermaid-scale 80%
```

### C. 일괄 변환 (subjects 하위의 모든 통합 리포트)

```bash
node scripts/md-to-pdf.js "subjects/**/integrated_report.md" --mermaid-scale 80%
```

## Mermaid 다이어그램 처리 흐름

1. 마크다운에서 ```` ```mermaid ... ``` ```` 코드 블록을 모두 추출
2. 각 블록을 임시 디렉토리(`tmp/md-to-pdf-*/`)에 `.mmd` 파일로 저장
3. `mmdc`로 SVG 렌더링 (배경: 투명)
4. SVG의 고정 `width`/`height` 속성을 제거하고 viewBox 기반으로 변경
5. `<div style="width:<scale>; margin:0 auto; text-align:center;">` 컨테이너로 감싸 마크다운에 인라인 HTML로 삽입
6. md-to-pdf로 최종 PDF 변환
7. 임시 디렉토리 자동 정리

## 트러블슈팅

### `[오류] md-to-pdf 전역 패키지를 찾을 수 없습니다`

```bash
npm install -g md-to-pdf
```

스크립트는 다음 경로를 자동 탐색합니다:
- `npm root -g` 의 결과
- `%APPDATA%\Local\nvm\v22.21.0\node_modules\md-to-pdf`
- `%APPDATA%\npm\node_modules\md-to-pdf`
- `/usr/local/lib/node_modules/md-to-pdf`

### `[경고] mmdc 미발견 → mermaid 블록은 렌더링되지 않습니다`

```bash
npm install -g @mermaid-js/mermaid-cli
```

설치 후 `mmdc --version`으로 PATH 등록을 확인하세요.

### Mermaid가 페이지를 넘침

`--mermaid-scale` 값을 줄이세요(예: `80%` → `70%`).

### 한글이 깨지거나 잘림

페이지 폭 대비 여백 합계가 너무 클 가능성. 좌우 여백을 줄여보세요(예: `--margin-left 15mm --margin-right 15mm`).

---
```bash
node "c:/project/airtown/University_KNOU/scripts/md-to-pdf.js" "c:/project/airtown/University_KNOU/subjects/4-2/컴퓨터보안/Submitted_Files/컴퓨터보안_중간_202334-153257.md" --mermaid-scale 72% --margin-left 15mm --margin-right 15mm --margin-top 5mm --margin-bottom 5mm
```