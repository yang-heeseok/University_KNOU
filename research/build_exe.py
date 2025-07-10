"""
클립보드 이미지 저장 도구 EXE 빌드 스크립트

크로스 플랫폼 지원 및 설정 파일 연동 기능
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path

def get_platform_info():
    """플랫폼 정보 반환"""
    system = platform.system()
    arch = platform.machine()
    
    platform_map = {
        "Windows": "win",
        "Darwin": "mac",
        "Linux": "linux"
    }
    
    return platform_map.get(system, "unknown"), arch

def load_build_config():
    """빌드 설정 로드"""
    config_file = Path("research/clipboard_config.json")
    default_config = {
        "app_name": "ClipboardImageSaver",
        "version": "1.0.0",
        "description": "클립보드 이미지 저장 도구",
        "windowed": True,
        "one_file": True,
        "include_config": True,
        "icon_file": None
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 빌드 관련 설정만 추출
                build_config = {}
                for key in default_config.keys():
                    if key in user_config:
                        build_config[key] = user_config[key]
                
                # 기본값과 병합
                return {**default_config, **build_config}
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
    
    return default_config

def install_pyinstaller():
    """PyInstaller 설치"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                      check=True, capture_output=True)
        print("✅ PyInstaller 이미 설치됨")
        return True
    except subprocess.CalledProcessError:
        print("📦 PyInstaller 설치 중...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True)
            print("✅ PyInstaller 설치 완료")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller 설치 실패: {e}")
            return False

def clean_build_dirs():
    """이전 빌드 파일 정리"""
    dirs_to_clean = ["dist", "build"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"🧹 {dir_name} 폴더 정리 완료")
    
    # .spec 파일 정리
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 {spec_file.name} 파일 정리 완료")

def build_exe():
    """EXE 파일 빌드"""
    # 플랫폼 정보
    platform_name, arch = get_platform_info()
    print(f"🖥️ 플랫폼: {platform.system()} ({arch})")
    
    # 빌드 설정 로드
    config = load_build_config()
    print(f"⚙️ 빌드 설정 로드 완료")
    
    # 소스 파일 확인
    script_path = Path("research/clipboard_saver.py")
    if not script_path.exists():
        print(f"❌ 소스 파일을 찾을 수 없습니다: {script_path}")
        return False
    
    print(f"📄 소스 파일: {script_path}")
    
    # PyInstaller 설치 확인
    if not install_pyinstaller():
        return False
    
    # 이전 빌드 정리
    clean_build_dirs()
    
    # PyInstaller 명령어 구성
    cmd = [sys.executable, "-m", "pyinstaller"]
    
    # 기본 옵션
    if config['one_file']:
        cmd.append("--onefile")
    
    if config['windowed']:
        cmd.append("--windowed")
    
    # 실행 파일 이름
    exe_name = config['app_name']
    if platform.system() == "Windows":
        exe_name += ".exe"
    cmd.extend(["--name", exe_name])
    
    # 아이콘 설정
    if config['icon_file'] and Path(config['icon_file']).exists():
        cmd.extend(["--icon", config['icon_file']])
    
    # 데이터 파일 포함
    data_files = []
    
    # 설정 파일 포함
    if config['include_config']:
        config_file = Path("research/clipboard_config.json")
        if config_file.exists():
            if platform.system() == "Windows":
                data_files.append(f"{config_file};.")
            else:
                data_files.append(f"{config_file}:.")
    
    for data_file in data_files:
        cmd.extend(["--add-data", data_file])
    
    # Hidden imports
    hidden_imports = [
        "PIL._tkinter_finder",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.simpledialog"
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
    # 소스 파일 추가
    cmd.append(str(script_path))
    
    print("🏗️ EXE 파일 빌드 시작...")
    print(f"📝 명령어: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ EXE 파일 빌드 성공!")
        
        # 빌드 결과 확인
        dist_dir = Path("dist")
        exe_file = dist_dir / exe_name
        
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 생성된 파일: {exe_file}")
            print(f"📏 파일 크기: {file_size:.1f} MB")
            
            # 배포 패키지 생성
            create_distribution_package(exe_file, config)
            return True
        else:
            print("❌ EXE 파일을 찾을 수 없습니다.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE 빌드 실패: {e}")
        if e.stderr:
            print(f"오류 출력: {e.stderr}")
        return False

def create_distribution_package(exe_file: Path, config: dict):
    """배포 패키지 생성"""
    dist_dir = exe_file.parent
    
    # 설정 파일 복사
    config_source = Path("research/clipboard_config.json")
    if config_source.exists():
        config_dest = dist_dir / "clipboard_config.json"
        shutil.copy2(config_source, config_dest)
        print(f"📋 설정 파일 복사: {config_dest}")
    
    # 사용 가이드 생성
    create_user_guide(dist_dir, config)
    
    # README 생성
    create_readme(dist_dir, config)
    
    print(f"📁 배포 패키지 위치: {dist_dir.absolute()}")

def create_user_guide(dist_dir: Path, config: dict):
    """사용자 가이드 생성"""
    platform_name, _ = get_platform_info()
    exe_name = config['app_name']
    if platform.system() == "Windows":
        exe_name += ".exe"
    
    guide_path = dist_dir / "사용법.txt"
    
    guide_content = f"""
클립보드 이미지 저장 도구 사용 가이드
====================================

🎯 프로그램 정보
- 이름: {config['app_name']}
- 버전: {config['version']}
- 설명: {config['description']}
- 플랫폼: {platform.system()}

📦 파일 구성
- {exe_name}               : 메인 실행 파일
- clipboard_config.json    : 설정 파일 (자동 생성)
- clipboard_saver.log      : 로그 파일 (자동 생성)
- 사용법.txt               : 이 파일

🚀 사용 방법
1. 이미지를 클립보드에 복사 (Ctrl+C 또는 Cmd+C)
2. {exe_name} 더블클릭 실행
3. GUI 또는 콘솔 모드 선택
4. 저장 위치 및 형식 지정
5. 이미지 저장 완료!

⚙️ 설정 변경 방법
방법 1: 프로그램 실행 시 설정 메뉴 사용
- 클립보드에 이미지가 없을 때 설정 메뉴 제공

방법 2: 설정 파일 직접 편집
- clipboard_config.json 파일을 텍스트 에디터로 편집
- JSON 형식을 유지해야 함

방법 3: 명령줄 도구 사용 (고급 사용자)
- config_manager.py 스크립트 사용 (Python 필요)

📁 저장 위치 옵션
- app_dir      : 프로그램 파일과 같은 폴더
- downloads    : 다운로드 폴더
- documents    : 문서 폴더
- desktop      : 바탕화면
- pictures     : 사진 폴더

🖼️ 지원 형식
- PNG (기본)   : 무손실 압축, 투명도 지원
- JPG          : 손실 압축, 작은 파일 크기
- BMP          : 무압축, 큰 파일 크기

🔧 문제 해결
1. 프로그램이 실행되지 않을 때
   - 바이러스 백신 소프트웨어 확인
   - 관리자 권한으로 실행 시도

2. 이미지가 저장되지 않을 때
   - 클립보드에 이미지가 올바르게 복사되었는지 확인
   - 저장 위치의 쓰기 권한 확인
   - 로그 파일(clipboard_saver.log) 확인

3. 설정이 저장되지 않을 때
   - 프로그램 폴더의 쓰기 권한 확인
   - 설정 파일이 읽기 전용이 아닌지 확인

💡 사용 팁
- 자주 사용한다면 바탕화면에 바로가기 생성
- 시작 메뉴나 독(Dock)에 프로그램 등록
- 핫키 프로그램과 연동하여 빠른 실행 설정

📞 지원
- 문제 발생 시 로그 파일을 확인하세요
- 설정을 초기화하려면 clipboard_config.json 파일을 삭제하고 재실행

버전: {config['version']}
빌드 일시: {platform.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📖 사용자 가이드 생성: {guide_path}")

def create_readme(dist_dir: Path, config: dict):
    """README 파일 생성"""
    readme_path = dist_dir / "README.txt"
    
    readme_content = f"""
{config['app_name']} v{config['version']}
=======================================

클립보드의 이미지를 빠르고 편리하게 저장하는 도구입니다.

주요 기능:
- 클립보드 이미지 자동 감지
- PNG, JPG, BMP 형식 지원  
- GUI 및 콘솔 인터페이스
- 크로스 플랫폼 지원
- 설정 파일로 사용자 환경 설정

시작하기:
1. 이미지를 클립보드에 복사
2. 프로그램 실행
3. 저장 위치 선택
4. 완료!

자세한 사용법은 '사용법.txt' 파일을 참고하세요.

라이선스: MIT
제작: Claude AI Assistant
    """
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 README 생성: {readme_path}")

def main():
    """메인 함수"""
    print("🔨 클립보드 이미지 저장 도구 EXE 빌드")
    print("=" * 50)
    
    # 필수 파일 확인
    required_files = ["research/clipboard_saver.py"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("❌ 필수 파일이 없습니다:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # 빌드 실행
    success = build_exe()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ EXE 빌드 완료!")
        print("배포 준비가 완료되었습니다.")
        
        # 플랫폼별 추가 안내
        if platform.system() == "Windows":
            print("\n💡 Windows 사용자 안내:")
            print("- Windows Defender가 실행을 차단할 수 있습니다")
            print("- '자세한 정보' -> '실행'을 클릭하여 실행하세요")
        elif platform.system() == "Darwin":
            print("\n💡 macOS 사용자 안내:")
            print("- 'Gatekeeper'가 실행을 차단할 수 있습니다")
            print("- 시스템 환경설정 > 보안 및 개인정보 보호에서 허용하세요")
        
        return True
    else:
        print("\n❌ EXE 빌드 실패")
        return False

if __name__ == "__main__":
    import datetime
    
    success = main()
    
    # 종료 메시지
    if success:
        input("\n🎉 빌드가 완료되었습니다! Enter를 눌러 종료...")
    else:
        input("\n❌ 빌드에 실패했습니다. Enter를 눌러 종료...")
        sys.exit(1) 