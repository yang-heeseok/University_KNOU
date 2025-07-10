"""
클립보드 이미지 저장 도구 설정 관리 유틸리티

일반인도 쉽게 사용할 수 있는 설정 파일 관리 도구
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def get_config_path() -> Path:
    """설정 파일 경로 반환"""
    if getattr(sys, 'frozen', False):
        # EXE 파일인 경우
        return Path(sys.executable).parent / "clipboard_config.json"
    else:
        # Python 스크립트인 경우
        return Path(__file__).parent / "clipboard_config.json"

class ConfigManager:
    """설정 관리 클래스"""
    
    def __init__(self):
        self.config_file = get_config_path()
        self.default_config = {
            "default_format": "png",
            "default_location": "app_dir",
            "jpeg_quality": 85,
            "auto_open": False,
            "prefer_gui": True,
            "auto_numbering": True,
            "log_enabled": True
        }
        
        # 설정 설명
        self.config_descriptions = {
            "default_format": "기본 파일 형식 (png, jpg, bmp)",
            "default_location": "기본 저장 위치 (app_dir, downloads, documents, desktop, pictures)",
            "jpeg_quality": "JPEG 압축 품질 (1-100, 높을수록 고품질)",
            "auto_open": "저장 후 자동으로 파일 열기 (true/false)",
            "prefer_gui": "GUI 모드 우선 사용 (true/false)",
            "auto_numbering": "파일명에 자동 번호 추가 (true/false)",
            "log_enabled": "로그 기록 활성화 (true/false)"
        }
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본 설정과 병합
                    return {**self.default_config, **config}
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
        
        return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 설정 파일 저장 완료: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False
    
    def create_default_config(self):
        """기본 설정 파일 생성"""
        if self.save_config(self.default_config):
            print("📄 기본 설정 파일이 생성되었습니다.")
            self.show_config()
        return self.default_config
    
    def show_config(self):
        """현재 설정 표시"""
        config = self.load_config()
        print(f"\n⚙️ 현재 설정 ({self.config_file})")
        print("=" * 50)
        
        for key, value in config.items():
            desc = self.config_descriptions.get(key, "")
            print(f"{key}: {value}")
            if desc:
                print(f"  → {desc}")
            print()
    
    def update_config(self, key: str, value: Any):
        """설정 값 업데이트"""
        config = self.load_config()
        
        # 값 타입 변환
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
        
        # 값 유효성 검사
        if key == "default_format" and value not in ['png', 'jpg', 'bmp']:
            print(f"❌ 잘못된 파일 형식: {value}")
            print("사용 가능한 형식: png, jpg, bmp")
            return False
        
        if key == "default_location" and value not in ['app_dir', 'downloads', 'documents', 'desktop', 'pictures']:
            print(f"❌ 잘못된 저장 위치: {value}")
            print("사용 가능한 위치: app_dir, downloads, documents, desktop, pictures")
            return False
        
        if key == "jpeg_quality" and (not isinstance(value, int) or value < 1 or value > 100):
            print(f"❌ 잘못된 JPEG 품질: {value}")
            print("JPEG 품질은 1-100 사이의 숫자여야 합니다.")
            return False
        
        config[key] = value
        
        if self.save_config(config):
            print(f"✅ 설정 업데이트: {key} = {value}")
            return True
        return False
    
    def interactive_setup(self):
        """대화형 설정"""
        print("🛠️ 클립보드 이미지 저장 도구 설정")
        print("=" * 40)
        
        config = self.load_config()
        
        # 파일 형식 설정
        print("\n1. 기본 파일 형식을 선택하세요:")
        formats = {"1": "png", "2": "jpg", "3": "bmp"}
        for num, fmt in formats.items():
            mark = "★" if config['default_format'] == fmt else " "
            print(f"  {num}. {fmt.upper()} {mark}")
        
        choice = input(f"선택 [1-3] (현재: {config['default_format']}): ").strip()
        if choice in formats:
            config['default_format'] = formats[choice]
        
        # 저장 위치 설정
        print("\n2. 기본 저장 위치를 선택하세요:")
        locations = {
            "1": ("app_dir", "프로그램 폴더"),
            "2": ("downloads", "다운로드 폴더"),
            "3": ("documents", "문서 폴더"),
            "4": ("desktop", "바탕화면"),
            "5": ("pictures", "사진 폴더")
        }
        
        for num, (key, desc) in locations.items():
            mark = "★" if config['default_location'] == key else " "
            print(f"  {num}. {desc} {mark}")
        
        choice = input(f"선택 [1-5] (현재: {config['default_location']}): ").strip()
        if choice in locations:
            config['default_location'] = locations[choice][0]
        
        # JPEG 품질 설정
        print(f"\n3. JPEG 품질 (1-100, 현재: {config['jpeg_quality']}):")
        quality_input = input("JPEG 품질 입력 (엔터=현재값 유지): ").strip()
        if quality_input:
            try:
                quality = int(quality_input)
                if 1 <= quality <= 100:
                    config['jpeg_quality'] = quality
                else:
                    print("⚠️ 1-100 사이의 값을 입력하세요.")
            except ValueError:
                print("⚠️ 숫자를 입력하세요.")
        
        # 자동 열기 설정
        current_auto_open = "예" if config['auto_open'] else "아니오"
        print(f"\n4. 저장 후 자동으로 파일을 열까요? (현재: {current_auto_open})")
        auto_open_input = input("자동 열기 (y/n): ").strip().lower()
        if auto_open_input in ['y', 'yes']:
            config['auto_open'] = True
        elif auto_open_input in ['n', 'no']:
            config['auto_open'] = False
        
        # GUI 모드 설정
        current_gui = "예" if config['prefer_gui'] else "아니오"
        print(f"\n5. GUI 모드를 우선 사용하시겠습니까? (현재: {current_gui})")
        gui_input = input("GUI 우선 (y/n): ").strip().lower()
        if gui_input in ['y', 'yes']:
            config['prefer_gui'] = True
        elif gui_input in ['n', 'no']:
            config['prefer_gui'] = False
        
        # 자동 번호 설정
        current_numbering = "예" if config['auto_numbering'] else "아니오"
        print(f"\n6. 파일명에 자동으로 번호를 추가하시겠습니까? (현재: {current_numbering})")
        numbering_input = input("자동 번호 (y/n): ").strip().lower()
        if numbering_input in ['y', 'yes']:
            config['auto_numbering'] = True
        elif numbering_input in ['n', 'no']:
            config['auto_numbering'] = False
        
        # 설정 저장
        print("\n" + "=" * 40)
        if self.save_config(config):
            print("✅ 설정이 저장되었습니다!")
            self.show_config()
        else:
            print("❌ 설정 저장에 실패했습니다.")

def main():
    """메인 함수"""
    manager = ConfigManager()
    
    if len(sys.argv) == 1:
        # 인수가 없으면 대화형 설정
        manager.interactive_setup()
    
    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()
        
        if command == "show":
            manager.show_config()
        elif command == "create":
            manager.create_default_config()
        elif command == "setup":
            manager.interactive_setup()
        else:
            print("❌ 알 수 없는 명령어입니다.")
            print_help()
    
    elif len(sys.argv) == 3:
        key, value = sys.argv[1], sys.argv[2]
        manager.update_config(key, value)
    
    else:
        print_help()

def print_help():
    """도움말 출력"""
    print("📖 클립보드 이미지 저장 도구 설정 관리")
    print("=" * 40)
    print("사용법:")
    print("  python config_manager.py                    # 대화형 설정")
    print("  python config_manager.py show               # 현재 설정 보기")
    print("  python config_manager.py create             # 기본 설정 생성")
    print("  python config_manager.py setup              # 대화형 설정")
    print("  python config_manager.py <키> <값>          # 특정 설정 변경")
    print()
    print("설정 키:")
    print("  default_format      파일 형식 (png, jpg, bmp)")
    print("  default_location    저장 위치 (app_dir, downloads, documents, desktop, pictures)")
    print("  jpeg_quality        JPEG 품질 (1-100)")
    print("  auto_open           자동 열기 (true, false)")
    print("  prefer_gui          GUI 우선 (true, false)")
    print("  auto_numbering      자동 번호 (true, false)")
    print()
    print("예시:")
    print("  python config_manager.py default_format jpg")
    print("  python config_manager.py auto_open true")
    print("  python config_manager.py jpeg_quality 90")

if __name__ == "__main__":
    main() 