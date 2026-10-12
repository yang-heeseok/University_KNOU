# KNOU 강의 저장

`download-knou.py`는 로그인한 Chrome 창에서 강의를 재생할 때 발생하는 영상 재생목록 요청을 감지하고 MP4 파일로 저장합니다. 개발자 도구에서 영상 주소를 복사할 필요가 없습니다.

## 준비

- Windows에 Python, Google Chrome, FFmpeg가 설치되어 있어야 합니다.
- 프로젝트 루트에서 `python -m pip install -r scripts\requirements.txt`를 실행합니다. 이 PC에는 Playwright가 이미 설치되어 있습니다.
- 전사 기능을 사용하려면 `python -m pip install -r scripts\requirements-transcribe.txt`도 실행합니다.
- KNOU 계정 로그인은 스크립트가 여는 Chrome 창에서 직접 진행합니다. 계정 정보를 명령어 또는 코드에 넣지 않습니다.

## 실행

프로젝트 루트에서:

```powershell
python scripts\download-knou.py
```

현재 위치가 `scripts` 폴더라면:

```powershell
python .\download-knou.py
```

별도 Chrome 창이 열리면 로그인한 뒤 원하는 강의를 재생합니다. 기본 페이지에서 강의가 바로 열리지 않으면 **같은 창에서** 수강 메뉴를 통해 해당 강의로 이동합니다. 영상 요청이 감지되면 다운로드가 자동으로 시작됩니다. 기다리는 동안 취소하려면 PowerShell에서 `Ctrl+C`를 누릅니다. 재생목록을 찾지 못하면 30분 후 종료됩니다.

## 옵션

| 옵션 | 동작 | 예시 |
| --- | --- | --- |
| 생략 | `scripts\downloads`에 강의 제목으로 저장 | `python .\download-knou.py` |
| `--output <폴더>` | 지정한 폴더에 자동 파일명으로 저장 | `python .\download-knou.py --output 'C:\Videos'` |
| `--output <파일.mp4>` | 지정한 이름으로 저장 | `python .\download-knou.py --output 'C:\Videos\강의.mp4'` |
| `--title <제목>` | 페이지에서 제목을 찾기 어려울 때 파일명 지정 | `python .\download-knou.py --title '2강. 경영전략의 개념 2'` |
| `--page-url <주소>` | 처음 열 KNOU 학습 페이지 변경 | `python .\download-knou.py --page-url 'https://ucampus.knou.ac.kr/ekp/user/study/retrieveUSTStudy.do'` |
| `--transcribe` | 다운로드 완료 후 한국어 텍스트와 SRT 자막 생성 | `python .\download-knou.py --transcribe` |

`--page-url`은 `ucampus.knou.ac.kr` 주소만 받습니다. 다른 옵션을 확인하려면 `python .\download-knou.py --help`를 실행하세요.

## 음성 전사

다운로드와 전사를 한 번에 실행하려면:

```powershell
python .\download-knou.py --transcribe
```

이미 저장된 MP4만 전사하려면 `scripts` 폴더에서:

```powershell
python .\knou_transcribe.py '.\downloads\강의.mp4'
```

전사기는 영상과 같은 폴더에 같은 기본 이름의 UTF-8 `.txt`와 시간 정보가 있는 `.srt`를 만듭니다. 예를 들어 `강의.mp4`를 전사하면 `강의.txt`, `강의.srt`가 생깁니다. 기존 전사 파일은 덮어쓰지 않습니다. 음성이 한국어가 아니라면 독립 실행 명령에 `--language en`처럼 언어 코드를 지정할 수 있습니다.

전사는 로컬 CPU에서 실행합니다. 처음 사용하면 고정된 `Systran/faster-whisper-small` 모델을 다운로드하며, 긴 강의는 전사에 시간이 걸릴 수 있습니다. 모델 다운로드에는 인터넷 연결이 필요합니다. 기본 캐시 위치는 `%USERPROFILE%\.cache\huggingface\hub`이며, 이 PC에서 내려받은 모델 파일은 약 **464 MiB**(약 **486 MB**)입니다. 정확한 모델 경로는 실행할 때 출력됩니다. 이후 모델이 캐시에 있으면 음성 파일은 외부 전사 서비스로 전송하지 않습니다. 결과는 자동 생성 초안이므로 고유명사와 전문 용어를 확인하세요.

## 파일명과 중복 처리

현재 재생 중인 강의 제목이 Chrome 페이지에 표시되고 식별 가능하면 `2강. 경영전략의 개념 2.mp4`처럼 저장합니다. 여러 강의 제목이 보이지만 현재 강의를 특정할 수 없거나 제목이 영상 화면 안에만 있는 경우, 재생목록 URL의 `.../원본이름.mp4/playlist.m3u8`에서 `원본이름.mp4`를 사용합니다. 원본 이름도 알 수 없으면 `lecture.mp4`를 사용합니다. 이 경우 `--title '2강. 경영전략의 개념 2'`로 이름을 직접 지정할 수 있습니다. `--output`에 `.mp4` 파일 경로를 지정하면 그 이름이 우선합니다.

자동 파일명이 이미 있으면 `_1`, `_2` 순서로 빈 이름을 찾습니다. 예를 들어 `2강. 경영전략의 개념 2.mp4`가 있으면 `2강. 경영전략의 개념 2_1.mp4`로 저장합니다. `--title`과 원본 이름에도 같은 규칙이 적용됩니다.

`--output`에 **파일 경로를 직접 지정**했는데 그 파일이 이미 있으면 오류를 내며 덮어쓰지 않습니다. 다운로드 중에는 같은 이름의 `.part.mp4` 임시 파일을 사용하고, 성공하면 최종 이름으로 바꿉니다. 실패하면 이번 실행에서 만든 임시 파일을 지웁니다.

## 코드 동작과 로그인 정보

1. Playwright가 설치된 Chrome을 별도 프로필로 엽니다.
2. 사용자가 로그인하고 강의를 재생하면, 스크립트가 `sdnw.knou.ac.kr`의 성공한 `playlist.m3u8` 응답을 감지합니다. 토큰에 만료 시각이 있고 이미 지났다면 건너뜁니다.
3. 해당 요청의 주소와 필요한 HTTP 헤더를 FFmpeg에 전달해 재인코딩 없이 MP4로 저장합니다.
4. 완료 또는 오류 시 스크립트가 연 Chrome 창을 닫습니다.
5. `--transcribe`를 지정했다면 저장된 MP4를 CPU에서 전사해 TXT/SRT를 만듭니다. 전사에 실패해도 MP4는 유지됩니다.

전용 프로필은 `%LOCALAPPDATA%\UniversityKNOU\ChromeProfile`에 저장됩니다. 일반 Chrome 프로필과 별개이며, 로그인 상태가 유효한 동안 다음 실행에 재사용됩니다. 같은 전용 프로필을 사용하는 다운로드 스크립트를 동시에 실행하지 마세요. 토큰과 쿠키가 포함된 영상 URL 또는 실행 중인 프로세스 인수를 공유하지 마세요.

## 문제 해결

| 현상 | 확인할 내용 |
| --- | --- |
| Chrome 창이 열리지 않음 | 이전 스크립트의 전용 Chrome 창을 닫고 다시 실행합니다. |
| 재생목록을 찾지 못함 | 스크립트가 연 창에서 로그인과 영상 재생이 실제로 이루어졌는지 확인합니다. |
| FFmpeg 실패 | 로그인 만료, 영상 형식 또는 서버의 추가 보호가 원인일 수 있습니다. 강의를 새로 열어 재생한 뒤 다시 실행합니다. |
| 파일이 이미 있음 | 자동 파일명은 다음 번호를 사용합니다. `--output`에 파일명을 직접 썼다면 다른 이름을 지정합니다. |
| 전사 패키지가 없음 | `python -m pip install -r scripts\requirements-transcribe.txt`를 실행합니다. |
| 전사 파일이 이미 있음 | 기존 TXT/SRT를 덮어쓰지 않습니다. 필요한 파일을 별도로 보관한 뒤 다시 실행합니다. |

이 구현은 현재 확인된 KNOU HLS 재생 요청 형식에 맞춰져 있습니다. 실제 계정으로 로그인한 강의를 끝까지 저장하는 검증은 아직 수행하지 않았습니다.
