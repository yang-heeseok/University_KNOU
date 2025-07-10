"""
클립보드 이미지 저장 도구 - 통합 최종 버전

기능:
- 크로스 플랫폼 지원 (Windows, macOS, Linux)
- GUI/콘솔 모드 지원
- 설정 파일 관리 (JSON)
- EXE 배포 최적화
- 로깅 시스템
- 파일명 검증
- JPEG 품질 조절
"""

import os
import sys
import json
import logging
import platform
import subprocess
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import ImageGrab, Image

# GUI용 tkinter
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def get_executable_dir() -> Path:
    """실행 파일의 디렉토리 경로 반환 (EXE/스크립트 자동 감지)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller EXE 파일인 경우
        return Path(sys.executable).parent
    else:
        # 일반 Python 스크립트인 경우
        return Path(__file__).parent

class ClipboardImageSaver:
    """클립보드 이미지 저장 클래스"""
    
    def __init__(self):
        # 실행 환경에 따른 경로 설정
        self.app_dir = get_executable_dir()
        self.config_file = self.app_dir / "clipboard_config.json"
        self.log_file = self.app_dir / "clipboard_saver.log"
        
        # 기본 설정
        self.default_config = {
            "default_format": "png",
            "default_location": "app_dir",
            "jpeg_quality": 85,
            "auto_open": False,
            "prefer_gui": True if GUI_AVAILABLE else False,
            "auto_numbering": True,
            "log_enabled": True
        }
        
        # 로깅 설정
        self.setup_logging()
        
        # 설정 로드
        self.config = self.load_config()
        
        logger.info(f"클립보드 이미지 저장 도구 시작 - 위치: {self.app_dir}")
    
    def setup_logging(self):
        """로깅 설정"""
        global logger
        
        # 기존 핸들러 제거
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # 새 로깅 설정
        handlers = [logging.StreamHandler()]
        
        # 로그 파일 추가 (실패해도 계속 진행)
        try:
            handlers.append(logging.FileHandler(str(self.log_file), encoding='utf-8'))
        except Exception:
            pass
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True
        )
        logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    merged_config = {**self.default_config, **config}
                    logger.info(f"설정 파일 로드: {self.config_file}")
                    return merged_config
        except Exception as e:
            logger.warning(f"설정 파일 로드 실패: {e}")
        
        # 기본 설정으로 새 파일 생성
        logger.info("기본 설정 파일 생성")
        self.save_config_to_file(self.default_config)
        return self.default_config.copy()
    
    def save_config(self):
        """현재 설정을 파일에 저장"""
        self.save_config_to_file(self.config)
    
    def save_config_to_file(self, config: Dict[str, Any]):
        """설정을 파일에 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("설정 파일 저장 완료")
            print(f"✅ 설정 저장: {self.config_file}")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            print(f"❌ 설정 저장 실패: {e}")
    
    def get_clipboard_image(self) -> Optional[Image.Image]:
        """클립보드에서 이미지 추출"""
        try:
            image = ImageGrab.grabclipboard()
            if image is None or not isinstance(image, Image.Image):
                return None
            logger.info(f"클립보드 이미지 추출: {image.size}")
            return image
        except Exception as e:
            logger.error(f"클립보드 이미지 추출 실패: {e}")
            return None
    
    def validate_filename(self, filename: str) -> str:
        """파일명 유효성 검사"""
        # 금지 문자 제거
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 길이 제한
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()
    
    def get_next_numbered_filename(self, base_dir: Path, base_name: str, ext: str) -> Path:
        """번호가 매겨진 파일명 생성"""
        base_name = self.validate_filename(base_name)
        for i in range(1, 10000):
            suffix = f"{i:04d}"
            filename = f"{base_name}_{suffix}.{ext}"
            path = base_dir / filename
            if not path.exists():
                return path
        raise ValueError("사용 가능한 파일명을 찾을 수 없습니다.")
    
    def get_save_directory(self, option: str) -> Path:
        """저장 위치 결정"""
        if option == "app_dir":
            return self.app_dir
        
        home = Path.home()
        if option == "downloads":
            return home / "Downloads"
        elif option == "documents":
            return home / "Documents"
        elif option == "desktop":
            return home / "Desktop"
        elif option == "pictures":
            return home / "Pictures"
        else:
            return Path.cwd()
    
    def open_file_cross_platform(self, file_path: Path):
        """크로스 플랫폼 파일 열기"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(file_path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path)])
            logger.info(f"파일 열기: {file_path}")
        except Exception as e:
            logger.error(f"파일 열기 실패: {e}")
            print(f"⚠️ 파일을 열 수 없습니다: {e}")
    
    def save_image(self, image: Image.Image, save_path: Path, format_type: str, 
                   quality: int = 85, auto_open: bool = False) -> bool:
        """이미지 저장"""
        try:
            # 디렉토리 생성
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 존재 확인
            if save_path.exists():
                if GUI_AVAILABLE:
                    try:
                        root = tk.Tk()
                        root.withdraw()
                        overwrite = messagebox.askyesno(
                            "파일 덮어쓰기", 
                            f"파일이 이미 존재합니다:\n{save_path.name}\n\n덮어쓰시겠습니까?"
                        )
                        root.destroy()
                    except:
                        overwrite = input(f"\n⚠️ 파일이 이미 존재합니다: {save_path.name}\n덮어쓰시겠습니까? (y/N): ").strip().lower() == 'y'
                else:
                    overwrite = input(f"\n⚠️ 파일이 이미 존재합니다: {save_path.name}\n덮어쓰시겠습니까? (y/N): ").strip().lower() == 'y'
                
                if not overwrite:
                    print("🚫 저장을 취소했습니다.")
                    return False
            
            # 저장 옵션 설정
            save_kwargs = {"format": format_type.upper()}
            if format_type.lower() in ['jpg', 'jpeg']:
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            
            # 이미지 저장
            image.save(save_path, **save_kwargs)
            logger.info(f"이미지 저장: {save_path}")
            
            # 정보 출력
            file_size = save_path.stat().st_size / 1024
            print(f"\n✅ 이미지 저장 완료!")
            print(f"   📁 경로: {save_path}")
            print(f"   📏 크기: {image.size}")
            print(f"   📦 파일 크기: {file_size:.1f} KB")
            
            # 자동 열기
            if auto_open:
                self.open_file_cross_platform(save_path)
            
            return True
            
        except Exception as e:
            logger.error(f"이미지 저장 실패: {e}")
            print(f"❌ 이미지 저장 실패: {e}")
            return False
    
    def run_gui_mode(self, image: Image.Image) -> bool:
        """GUI 모드 실행"""
        if not GUI_AVAILABLE:
            print("❌ GUI를 사용할 수 없습니다.")
            return False
        
        try:
            root = tk.Tk()
            root.title("클립보드 이미지 저장")
            root.withdraw()
            
            # 이미지 정보 표시
            file_size = len(image.tobytes()) / 1024
            info_msg = f"📸 클립보드 이미지 정보\n\n크기: {image.size}\n모드: {image.mode}\n예상 크기: {file_size:.1f} KB"
            messagebox.showinfo("이미지 정보", info_msg)
            
            # 저장 경로 선택
            filetypes = [
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
            
            # 기본 저장 위치
            if self.config['default_location'] == 'app_dir':
                initial_dir = str(self.app_dir)
            else:
                initial_dir = str(self.get_save_directory(self.config['default_location']))
            
            default_name = f"clipboard_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.config['default_format']}"
            save_path = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                defaultextension=f".{self.config['default_format']}",
                filetypes=filetypes,
                initialfile=default_name,
                title="이미지 저장 위치 선택"
            )
            
            if not save_path:
                messagebox.showinfo("취소됨", "저장이 취소되었습니다.")
                return False
            
            save_path = Path(save_path)
            ext = save_path.suffix.lstrip('.').lower()
            
            # JPEG 품질 설정
            quality = self.config['jpeg_quality']
            if ext in ['jpg', 'jpeg']:
                quality_str = simpledialog.askstring(
                    "JPEG 품질",
                    f"JPEG 품질을 입력하세요 (1-100):",
                    initialvalue=str(quality)
                )
                if quality_str:
                    try:
                        quality = max(1, min(100, int(quality_str)))
                    except ValueError:
                        quality = self.config['jpeg_quality']
            
            # 이미지 저장
            success = self.save_image(image, save_path, ext, quality, auto_open=self.config['auto_open'])
            
            if success:
                messagebox.showinfo("완료", "이미지 저장이 완료되었습니다!")
            else:
                messagebox.showerror("오류", "이미지 저장에 실패했습니다.")
            
            root.destroy()
            return success
            
        except Exception as e:
            logger.error(f"GUI 모드 실행 실패: {e}")
            print(f"❌ GUI 모드 실행 실패: {e}")
            return False
    
    def run_console_mode(self, image: Image.Image) -> bool:
        """콘솔 모드 실행"""
        print(f"\n📸 클립보드 이미지 정보:")
        print(f"   📏 크기: {image.size}")
        print(f"   🎨 모드: {image.mode}")
        print(f"   💾 예상 크기: {len(image.tobytes()) / 1024:.1f} KB")
        
        # 현재 설정 표시
        print(f"\n⚙️ 현재 설정:")
        print(f"   📁 저장 위치: {self.config['default_location']}")
        print(f"   🖼️ 파일 형식: {self.config['default_format'].upper()}")
        print(f"   🔢 자동 번호: {'예' if self.config['auto_numbering'] else '아니오'}")
        
        use_default = input("\n현재 설정으로 저장하시겠습니까? (Y/n): ").strip().lower()
        
        if use_default in ['', 'y', 'yes']:
            return self.save_with_default_settings(image)
        else:
            return self.save_with_custom_settings(image)
    
    def save_with_default_settings(self, image: Image.Image) -> bool:
        """기본 설정으로 저장"""
        base_dir = self.get_save_directory(self.config['default_location'])
        base_name = "clipboard"
        ext = self.config['default_format']
        
        if self.config['auto_numbering']:
            save_path = self.get_next_numbered_filename(base_dir, base_name, ext)
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_name}_{timestamp}.{ext}"
            save_path = base_dir / filename
        
        return self.save_image(
            image, save_path, ext, 
            self.config['jpeg_quality'], 
            self.config['auto_open']
        )
    
    def save_with_custom_settings(self, image: Image.Image) -> bool:
        """사용자 정의 설정으로 저장"""
        # 파일명 입력
        default_name = "clipboard"
        custom_name = input(f"\n파일 이름 (엔터=기본값): ").strip()
        if not custom_name:
            custom_name = default_name
        
        # 저장 위치 선택
        print("\n저장 위치 선택:")
        locations = {
            "1": ("app_dir", f"프로그램 폴더 ({self.app_dir})"),
            "2": ("downloads", "다운로드 폴더"),
            "3": ("documents", "문서 폴더"),
            "4": ("desktop", "바탕화면"),
            "5": ("pictures", "사진 폴더")
        }
        
        for key, (_, desc) in locations.items():
            print(f"  {key}. {desc}")
        
        location_choice = input("선택 [1-5]: ").strip()
        location_key = locations.get(location_choice, ("app_dir", "프로그램 폴더"))[0]
        save_dir = self.get_save_directory(location_key)
        
        # 파일 형식 선택
        print("\n파일 형식 선택:")
        formats = {"1": "png", "2": "jpg", "3": "bmp"}
        
        for key, format_type in formats.items():
            print(f"  {key}. {format_type.upper()}")
        
        format_choice = input("선택 [1-3]: ").strip()
        ext = formats.get(format_choice, "png")
        
        # JPEG 품질 설정
        quality = self.config['jpeg_quality']
        if ext in ['jpg', 'jpeg']:
            quality_input = input(f"JPEG 품질 (1-100, 기본={quality}): ").strip()
            if quality_input:
                try:
                    quality = max(1, min(100, int(quality_input)))
                except ValueError:
                    print("⚠️ 잘못된 입력. 기본값 사용.")
        
        # 파일명 생성
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{custom_name}_{timestamp}.{ext}"
        save_path = save_dir / filename
        
        # 자동 열기 설정
        auto_open = input("저장 후 파일을 열까요? (y/N): ").strip().lower() == 'y'
        
        return self.save_image(image, save_path, ext, quality, auto_open)
    
    def show_settings_menu(self):
        """설정 메뉴"""
        while True:
            print(f"\n⚙️ 설정 메뉴")
            print("=" * 40)
            print(f"1. 기본 파일 형식: {self.config['default_format']}")
            print(f"2. 기본 저장 위치: {self.config['default_location']}")
            print(f"3. JPEG 품질: {self.config['jpeg_quality']}")
            print(f"4. 자동 열기: {'예' if self.config['auto_open'] else '아니오'}")
            print(f"5. GUI 우선: {'예' if self.config['prefer_gui'] else '아니오'}")
            print(f"6. 자동 번호: {'예' if self.config['auto_numbering'] else '아니오'}")
            print("7. 설정 저장 후 종료")
            print("0. 저장하지 않고 종료")
            
            choice = input("\n선택 [0-7]: ").strip()
            
            if choice == "1":
                new_format = input("파일 형식 (png/jpg/bmp): ").strip().lower()
                if new_format in ['png', 'jpg', 'bmp']:
                    self.config['default_format'] = new_format
                    print(f"✅ 설정 변경: {new_format}")
            
            elif choice == "2":
                print("저장 위치: app_dir, downloads, documents, desktop, pictures")
                new_location = input("저장 위치: ").strip().lower()
                if new_location in ['app_dir', 'downloads', 'documents', 'desktop', 'pictures']:
                    self.config['default_location'] = new_location
                    print(f"✅ 설정 변경: {new_location}")
            
            elif choice == "3":
                try:
                    new_quality = int(input("JPEG 품질 (1-100): ").strip())
                    if 1 <= new_quality <= 100:
                        self.config['jpeg_quality'] = new_quality
                        print(f"✅ 설정 변경: {new_quality}")
                except ValueError:
                    print("❌ 잘못된 입력")
            
            elif choice in ["4", "5", "6"]:
                key_map = {"4": "auto_open", "5": "prefer_gui", "6": "auto_numbering"}
                key = key_map[choice]
                self.config[key] = not self.config[key]
                print(f"✅ 설정 변경: {'예' if self.config[key] else '아니오'}")
            
            elif choice == "7":
                self.save_config()
                print("✅ 설정이 저장되었습니다.")
                break
            
            elif choice == "0":
                print("❌ 변경사항이 저장되지 않았습니다.")
                break
    
    def run(self):
        """메인 실행 함수"""
        try:
            # 클립보드 이미지 확인
            image = self.get_clipboard_image()
            if image is None:
                print("❌ 클립보드에 이미지가 없습니다.")
                config_choice = input("\n설정을 변경하시겠습니까? (y/N): ").strip().lower()
                if config_choice == 'y':
                    self.show_settings_menu()
                return False
            
            # 실행 모드 선택
            if GUI_AVAILABLE and self.config.get('prefer_gui', True):
                mode_choice = input("🖼️ GUI 모드로 실행할까요? (Y/n): ").strip().lower()
                if mode_choice in ['', 'y', 'yes']:
                    return self.run_gui_mode(image)
            
            # 콘솔 모드 실행
            return self.run_console_mode(image)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 사용자 중단")
            return False
        except Exception as e:
            logger.error(f"예기치 않은 오류: {e}")
            print(f"❌ 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    print("🖼️ 클립보드 이미지 저장 도구")
    print("=" * 40)
    
    saver = ClipboardImageSaver()
    
    # 실행 환경 정보
    if getattr(sys, 'frozen', False):
        print(f"📦 EXE 모드")
    else:
        print(f"🐍 Python 모드")
    
    print(f"📁 설정 파일: {saver.config_file}")
    
    success = saver.run()
    
    if success:
        print("\n✅ 완료!")
    else:
        print("\n❌ 실패")
    
    # EXE 모드에서는 종료 대기
    if getattr(sys, 'frozen', False):
        input("\n종료하려면 Enter를 누르세요...")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 