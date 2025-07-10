# 📸 클립보드 이미지 저장 도구

> 클립보드의 이미지를 빠르고 편리하게 저장하는 크로스 플랫폼 도구

## 🎯 개요

이 도구는 클립보드에 복사된 이미지를 간단하게 파일로 저장할 수 있는 유틸리티입니다. 스크린샷, 복사된 이미지, 그림판에서 복사한 내용 등을 빠르게 PNG, JPG, BMP 파일로 저장할 수 있습니다.

## ✨ 주요 기능

- 📋 **자동 이미지 감지**: 클립보드의 이미지 자동 추출
- 🖼️ **다양한 형식**: PNG, JPG, BMP 포맷 지원
- 🖥️ **두 가지 모드**: GUI와 콘솔 인터페이스
- 📁 **유연한 저장**: 프로그램 폴더, 다운로드, 문서, 바탕화면, 사진 폴더
- ⚙️ **설정 저장**: JSON 파일로 사용자 환경 설정 관리
- 🔄 **자동 번호**: 파일명 중복 방지
- 🎨 **JPEG 품질**: 압축 품질 조절 (1-100)
- 🌍 **크로스 플랫폼**: Windows, macOS, Linux 지원

## 📦 설치 및 준비

### 1. **Python 사용자**
```bash
# 필수 라이브러리 설치
pip install pillow

# 저장소 복제 또는 파일 다운로드
git clone <repository-url>
cd University_KNOU/research
```

### 2. **일반 사용자 (EXE 파일)**
1. **EXE 파일 빌드**:
   ```bash
   python build_exe.py
   ```
2. **배포 패키지**: `dist` 폴더에 생성된 파일들 사용

## 🚀 사용 방법

### 기본 사용 순서
1. **이미지 복사**: 스크린샷 찍기 또는 이미지 복사 (Ctrl+C / Cmd+C)
2. **프로그램 실행**: 
   - Python: `python clipboard_saver.py`
   - EXE: 더블클릭 실행
3. **모드 선택**: GUI 또는 콘솔 모드
4. **저장 설정**: 위치, 형식, 품질 선택
5. **완료**: 이미지 파일 저장 완료!

### GUI 모드
```
🖼️ GUI 모드로 실행할까요? (Y/n): Y
```
- 📸 **이미지 정보**: 크기, 모드, 예상 파일 크기 표시
- 📁 **저장 위치**: 파일 대화상자로 경로 선택
- 🎨 **JPEG 품질**: JPG 선택 시 품질 입력 창
- ✅ **완료 알림**: 저장 성공/실패 메시지

### 콘솔 모드
```
🖼️ GUI 모드로 실행할까요? (Y/n): n

📸 클립보드 이미지 정보:
   📏 크기: (1920, 1080)
   🎨 모드: RGB
   💾 예상 크기: 6234.5 KB

⚙️ 현재 설정:
   📁 저장 위치: app_dir
   🖼️ 파일 형식: PNG
   🔢 자동 번호: 예

현재 설정으로 저장하시겠습니까? (Y/n):
```

## ⚙️ 설정 관리

### 1. **프로그램 내 설정**
클립보드에 이미지가 없을 때 설정 메뉴가 제공됩니다:
```
❌ 클립보드에 이미지가 없습니다.

설정을 변경하시겠습니까? (y/N): y

⚙️ 설정 메뉴
========================================
1. 기본 파일 형식: png
2. 기본 저장 위치: app_dir
3. JPEG 품질: 85
4. 자동 열기: 아니오
5. GUI 우선: 예
6. 자동 번호: 예
7. 설정 저장 후 종료
0. 저장하지 않고 종료
```

### 2. **설정 관리 도구**
```bash
# 대화형 설정 (권장)
python config_manager.py

# 특정 설정 변경
python config_manager.py default_format jpg
python config_manager.py auto_open true
python config_manager.py jpeg_quality 90

# 현재 설정 보기
python config_manager.py show

# 기본 설정 생성
python config_manager.py create
```

### 3. **설정 파일 직접 편집**
`clipboard_config.json` 파일을 텍스트 에디터로 편집:
```json
{
  "default_format": "png",
  "default_location": "app_dir",
  "jpeg_quality": 85,
  "auto_open": false,
  "prefer_gui": true,
  "auto_numbering": true,
  "log_enabled": true
}
```

## 📁 파일 구조

```
research/
├── clipboard_saver.py          # 통합 메인 프로그램
├── clipboard_image_save.py     # 원본 기본 버전 (참고용)
├── config_manager.py           # 설정 관리 도구
├── build_exe.py               # EXE 빌드 스크립트
├── clipboard_config.json      # 설정 파일
└── README_clipboard_tool.md   # 이 문서

dist/ (빌드 후 생성)
├── ClipboardImageSaver.exe    # 실행 파일
├── clipboard_config.json      # 기본 설정
├── 사용법.txt                  # 사용자 가이드
└── README.txt                 # 간단 안내
```

## 🔧 EXE 빌드 방법

### 자동 빌드
```bash
python build_exe.py
```

### 수동 빌드
```bash
# PyInstaller 설치
pip install pyinstaller

# EXE 빌드
pyinstaller --onefile --windowed --name ClipboardImageSaver research/clipboard_saver.py

# 설정 파일 복사
copy research\clipboard_config.json dist\
```

## ⚡ 빠른 사용법

### 스크린샷 → 파일 저장
1. `Win + Shift + S` (Windows) 또는 `Cmd + Shift + 4` (macOS)로 스크린샷
2. 프로그램 실행
3. 엔터 눌러서 기본 설정으로 저장

### 웹 이미지 → 파일 저장
1. 웹브라우저에서 이미지 우클릭 → "이미지 복사"
2. 프로그램 실행
3. GUI 모드에서 저장 위치 선택

### 그림판 → 파일 저장
1. 그림판에서 작업 후 Ctrl+A, Ctrl+C
2. 프로그램 실행
3. JPG 형식 선택하여 용량 절약

## 🛠️ 문제 해결

### 프로그램이 실행되지 않을 때
```bash
# Python 버전 확인
python --version

# 필수 라이브러리 확인
pip show pillow

# 권한 문제 (Windows)
# 관리자 권한으로 실행
```

### 이미지가 저장되지 않을 때
1. **클립보드 확인**: 이미지가 올바르게 복사되었는지 확인
2. **권한 확인**: 저장 폴더의 쓰기 권한 확인
3. **로그 확인**: `clipboard_saver.log` 파일 확인

### 설정이 저장되지 않을 때
1. **파일 권한**: 프로그램 폴더의 쓰기 권한 확인
2. **읽기 전용**: `clipboard_config.json`이 읽기 전용인지 확인
3. **초기화**: 설정 파일 삭제 후 재실행

## 📊 설정 옵션 상세

| 설정 키 | 설명 | 기본값 | 가능한 값 |
|---------|------|--------|-----------|
| `default_format` | 기본 파일 형식 | `png` | `png`, `jpg`, `bmp` |
| `default_location` | 기본 저장 위치 | `app_dir` | `app_dir`, `downloads`, `documents`, `desktop`, `pictures` |
| `jpeg_quality` | JPEG 압축 품질 | `85` | `1-100` (높을수록 고품질) |
| `auto_open` | 저장 후 자동 열기 | `false` | `true`, `false` |
| `prefer_gui` | GUI 모드 우선 | `true` | `true`, `false` |
| `auto_numbering` | 자동 번호 추가 | `true` | `true`, `false` |
| `log_enabled` | 로그 기록 | `true` | `true`, `false` |

## 💡 사용 팁

### 생산성 향상
- **바탕화면 바로가기**: 자주 사용한다면 바탕화면에 바로가기 생성
- **시작 메뉴 등록**: Windows 시작 메뉴나 macOS Dock에 등록
- **핫키 연동**: 핫키 프로그램과 연동하여 키보드 단축키로 실행

### 파일 관리
- **자동 번호**: `auto_numbering`을 활성화하면 `clipboard_0001.png` 형식으로 저장
- **날짜별 폴더**: 매일 다른 폴더에 저장하려면 스크립트로 날짜별 폴더 생성
- **클라우드 동기화**: 저장 위치를 OneDrive, Google Drive 폴더로 설정

### 품질 최적화
- **PNG**: 스크린샷, 그래픽에 최적 (무손실)
- **JPG**: 사진, 복잡한 이미지에 최적 (용량 절약)
- **BMP**: 원본 품질 보존 필요 시 (용량 큼)

---

## 📞 지원 및 문의

- **로그 확인**: `clipboard_saver.log` 파일에서 오류 확인
- **설정 초기화**: `clipboard_config.json` 파일 삭제 후 재실행
- **버전 정보**: 프로그램 실행 시 상단에 표시

---

**제작**: Claude AI Assistant  
**라이선스**: MIT  
**버전**: 1.0.0 