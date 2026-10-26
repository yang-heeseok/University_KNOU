# scripts/

학습 아카이브 운영을 위한 유틸리티 스크립트 모음.

## 인덱스

| 스크립트 | 용도 | 문서 |
|---|---|---|
| [`md-to-pdf.js`](md-to-pdf.js) | Markdown → A4 PDF 변환 (Mermaid 사전 렌더링 지원) | [md-to-pdf.README.md](md-to-pdf.README.md) |
| [`yt_downloader.py`](yt_downloader.py), [`yt_downloader_gui.py`](yt_downloader_gui.py) | yt-dlp 기반 동영상 다운로더 (CLI / tkinter GUI) | [yt-downloader.README.md](yt-downloader.README.md) |
| [`download-knou.py`](download-knou.py) | 로그인한 Chrome 창에서 KNOU 강의 요청을 감지해 MP4로 저장 | [download-knou.README.md](download-knou.README.md) |
| [`knou_transcribe.py`](knou_transcribe.py) | 강의 영상 · 통화 · 인터뷰 녹음을 TXT/SRT로 전사 (모델 선택 · 화자 분리) | [download-knou.README.md](download-knou.README.md#음성-전사) |
| [`build-docs.js`](build-docs.js) | 학습 아카이브 Markdown → HTML 정적 사이트 빌드 | (별도 문서 없음) |

## 빠른 사용 예시

```bash
# Markdown → PDF (좁은 여백, mermaid 80%)
node scripts/md-to-pdf.js report.md \
  --margin-top 5mm --margin-bottom 5mm \
  --margin-left 15mm --margin-right 15mm \
  --mermaid-scale 80%

# 영상 다운로드 (MP3 변환)
python scripts/yt_downloader.py "https://www.youtube.com/watch?v=xxxxx" --mp3 -o ./downloads

# GUI 실행
python scripts/yt_downloader_gui.py
```

### 개발자 도구 없이 KNOU 강의 저장

```powershell
python -m pip install -r scripts\requirements.txt
python scripts\download-knou.py

# 원하는 파일 경로에 저장
python scripts\download-knou.py --output 'C:\Videos\강의.mp4'

# 다운로드 후 음성 전사
python scripts\download-knou.py --transcribe
```

스크립트가 별도 Chrome 창을 엽니다. 그 창에서 KNOU에 로그인하고 강의를 재생하면 자동으로 저장합니다. 자세한 사용법, 파일명 규칙, 로그인 정보 위치 및 문제 해결은 [전용 문서](download-knou.README.md)를 참고하세요.

세부 옵션과 트러블슈팅은 각 스크립트별 README를 참고하세요.

## 의존성

- **Node.js 22.x** — `md-to-pdf.js`, `build-docs.js` 실행
- **Python 3.13+** — `yt_downloader*.py` 실행 (`pip install -r requirements.txt`)
- **전역 npm 패키지**: `md-to-pdf`, `@mermaid-js/mermaid-cli`
- **선택**: `ffmpeg` (yt-downloader의 MP3 변환·자막 임베드·영상+오디오 병합 시 필요)
- **`download-knou.py`**: `playwright`와 `ffmpeg`, 설치된 Chrome 필요 (Playwright용 별도 브라우저 다운로드는 필요 없음)
- **전사 옵션 / `knou_transcribe.py`**: 선택 의존성 `requirements-transcribe.txt` 필요
