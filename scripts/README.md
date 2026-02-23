# Video Downloader (yt-dlp)

yt-dlp 기반 동영상 다운로더. YouTube, Vimeo, X(Twitter), Instagram, Twitch, Naver TV 등 **1800+ 사이트**를 지원합니다.

CLI와 GUI 두 가지 인터페이스를 제공합니다.

## 파일 구조

| 파일 | 설명 |
|------|------|
| `yt_downloader.py` | CLI 다운로더 (메인 모듈) |
| `yt_downloader_gui.py` | tkinter GUI 래퍼 |
| `requirements.txt` | Python 의존성 |

## 설치

### 필수

```bash
pip install yt-dlp
```

### 선택 (MP3 변환, 자막 임베드, 썸네일 임베드, 영상+오디오 병합 시 필요)

```bash
# Windows (winget)
winget install Gyan.FFmpeg

# macOS (Homebrew)
brew install ffmpeg

# Linux (apt)
sudo apt install ffmpeg
```

## CLI 사용법

### 기본 다운로드

```bash
# 단일 영상 (최고화질)
python yt_downloader.py "https://www.youtube.com/watch?v=xxxxx"
python yt_downloader.py "https://vimeo.com/123456789"
python yt_downloader.py "https://x.com/user/status/123456"

# 재생목록 전체
python yt_downloader.py "https://www.youtube.com/playlist?list=xxxxx"
```

### 옵션

```bash
# MP3 변환 (ffmpeg 필요)
python yt_downloader.py "URL" --mp3
python yt_downloader.py "URL" --mp3 --audio-quality 320

# 화질 지정
python yt_downloader.py "URL" --quality 720

# 자막 포함 (한국어/영어)
python yt_downloader.py "URL" --subs

# 썸네일 저장
python yt_downloader.py "URL" --thumbnail

# 메타데이터 임베드
python yt_downloader.py "URL" --metadata

# 저장 경로 변경
python yt_downloader.py "URL" --output ./lectures

# 복합 사용
python yt_downloader.py "URL" --mp3 --output ./lectures --subs --thumbnail
```

### 배치 다운로드

URL 목록을 텍스트 파일로 일괄 다운로드합니다. 사이트를 혼합해서 사용할 수 있습니다.

```bash
python yt_downloader.py --batch urls.txt --mp3 --output ./music
```

`urls.txt` 형식:
```
# 주석은 #으로 시작
https://www.youtube.com/watch?v=aaa
https://vimeo.com/123456
https://x.com/user/status/789
```

### 채널 전체 백업

채널의 모든 영상을 **업로드 날짜별 폴더**(`YYYY-MM/`)로 정리하여 백업합니다.

```bash
python yt_downloader.py "https://www.youtube.com/@채널명" --channel
```

출력 구조:
```
downloads/
└── 채널명/
    ├── channel_info.json
    ├── 2024-01/
    │   ├── 영상제목1.mp4
    │   └── 영상제목2.mp4
    └── 2024-02/
        └── 영상제목3.mp4
```

- `channel_info.json`에 채널 메타데이터가 저장됩니다
- `.yt_archive` 파일로 중복 다운로드를 방지하며, 중단 후 이어받기가 가능합니다

### 로그인 필요 사이트 (브라우저 쿠키)

로그인이 필요한 사이트는 브라우저의 쿠키를 활용하여 인증할 수 있습니다.

```bash
python yt_downloader.py "URL" --cookies-from-browser chrome
python yt_downloader.py "URL" -c edge
python yt_downloader.py "URL" -c firefox
```

### 영상 정보 조회

다운로드 없이 영상 정보만 확인합니다.

```bash
python yt_downloader.py "URL" --info
```

출력 예시:
```
🔍 영상 정보 조회
  🌐 사이트: Youtube
  📹 제목: 영상 제목
  채널: 채널명
  길이: 12:34
  조회수: 1,234,567
  업로드: 20240101
  가용 화질: 2160p, 1080p, 720p, 480p, 360p
```

### CLI 옵션 전체

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `url` | | 동영상 URL | |
| `--batch` | `-b` | URL 목록 텍스트 파일 | |
| `--output` | `-o` | 저장 경로 | `./downloads` |
| `--mp3` | | MP3로 변환 | `false` |
| `--audio-quality` | | MP3 비트레이트 (kbps) | `192` |
| `--quality` | `-q` | 영상 화질 (best/2160/1080/720/480/360) | `best` |
| `--subs` | `-s` | 자막 다운로드 (ko/en) | `false` |
| `--thumbnail` | `-t` | 썸네일 저장 | `false` |
| `--metadata` | `-m` | 메타데이터 임베드 | `false` |
| `--channel` | | 채널 전체 백업 모드 | `false` |
| `--cookies-from-browser` | `-c` | 브라우저 쿠키 인증 (chrome/edge/firefox/safari) | |
| `--info` | | 다운로드 없이 정보만 출력 | `false` |

## GUI 사용법

```bash
python yt_downloader_gui.py
```

### GUI 기능

- **URL 입력**: 클립보드 붙여넣기 버튼 지원
- **옵션 설정**: MP3 변환, 자막, 썸네일, 메타데이터, 화질 선택, 브라우저 쿠키 선택
- **저장 경로**: 폴더 탐색기로 선택
- **배치 모드**: 여러 URL 입력 또는 텍스트 파일 불러오기
- **채널 백업**: 채널 URL 입력 후 채널 백업 버튼으로 전체 백업
- **실시간 진행률**: 프로그레스 바, 속도, ETA 표시
- **다운로드 로그**: 스크롤 가능한 로그 영역
- **중지 기능**: 진행 중인 다운로드를 안전하게 중단

### GUI 레이아웃

```
┌─ URL 입력 ──────────────────────────────────┐
│ [URL 입력창          ] [붙여넣기] [초기화]    │
├─ 옵션 ─────────────────────────────────────┤
│ ☐ MP3  ☐ 자막  ☐ 썸네일  ☐ 메타데이터      │
│ 화질: [best ▼]   쿠키: [없음 ▼]             │
├─ 저장 경로 ────────────────────────────────┤
│ [./downloads                 ] [찾아보기]   │
├─ 배치 모드 ────────────────────────────────┤
│ [여러 URL 입력               ] [파일 불러오기]│
├─ 실행 ─────────────────────────────────────┤
│ [▶ 다운로드]  [📂 채널 백업]  [⏹ 중지]      │
├─ 진행률 ───────────────────────────────────┤
│ [████████████░░░░░░░░] 60%  2.3MB/s  ETA 30s│
├─ 로그 ─────────────────────────────────────┤
│ (스크롤 가능 텍스트 영역)                    │
└─────────────────────────────────────────────┘
```

## 주요 기능

### 한글 제목 보정
- **NFC 정규화**: macOS에서 발생하는 한글 자모 분리 현상 방지
- **Mojibake 복구**: latin-1로 잘못 디코딩된 UTF-8 한글 자동 복원
- **Windows 파일명 호환**: 금지 문자(`<>:"/\|?*`) 자동 제거

### 중복 다운로드 방지
- `.yt_archive` 파일에 다운로드 완료된 영상 ID를 기록
- 동일 영상의 재다운로드를 자동으로 스킵
- 중단 후 재실행 시 이어받기 가능

### 다운로드 결과 로그
- 완료 후 `download_log_YYYYMMDD_HHMMSS.json` 파일로 결과 저장
- 성공/실패 건수 요약 및 실패 목록 출력

## 아키텍처 (GUI)

```
메인 스레드 (tkinter 이벤트 루프)
    ├─ 워커 스레드 → YTDownloader 실행
    │      ├─ QueueWriter: sys.stdout 대체, ANSI 코드 제거 후 Queue 전달
    │      └─ GUIProgressHook: 구조화된 진행률 데이터를 Queue 전달
    └─ root.after(100ms)로 Queue 폴링 → UI 위젯 업데이트
```

- **QueueWriter**: 워커 스레드의 print 출력을 가로채서 ANSI 이스케이프 코드를 제거한 뒤 Queue에 전달
- **GUIProgressHook**: yt-dlp의 progress_hooks에 등록되어 다운로드 진행률(퍼센트, 속도, ETA)을 구조화된 딕셔너리로 Queue에 전달
- **threading.Event**: 중지 버튼 클릭 시 cancel_event를 설정하여 워커 스레드에 안전한 종료 신호 전달

## 지원 사이트 (일부)

| 사이트 | URL 예시 |
|--------|----------|
| YouTube | `https://www.youtube.com/watch?v=...` |
| YouTube 재생목록 | `https://www.youtube.com/playlist?list=...` |
| YouTube 채널 | `https://www.youtube.com/@채널명` |
| Vimeo | `https://vimeo.com/123456` |
| X (Twitter) | `https://x.com/user/status/123` |
| Instagram | `https://www.instagram.com/p/...` |
| Twitch | `https://www.twitch.tv/videos/...` |
| Naver TV | `https://tv.naver.com/v/...` |
| Kakao TV | `https://tv.kakao.com/channel/.../cliplink/...` |

전체 지원 사이트 목록: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
