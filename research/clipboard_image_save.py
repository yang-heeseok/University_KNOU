import os
import sys
import datetime
from pathlib import Path
from PIL import ImageGrab, Image

# GUI용 tkinter
import tkinter as tk
from tkinter import filedialog, messagebox

def get_clipboard_image():
    """클립보드에서 유효한 이미지 추출"""
    image = ImageGrab.grabclipboard()
    if image is None or not isinstance(image, Image.Image):
        print("❌ 클립보드에 이미지가 없거나 유효하지 않습니다.")
        sys.exit(1)
    return image

def get_next_numbered_filename(base_dir: Path, base_name: str, ext: str) -> Path:
    """기본 폴더명_01, 폴더명_02 같은 번호 지정된 파일 경로 반환"""
    for i in range(1, 1000):
        suffix = f"{i:02}"
        filename = f"{base_name}_{suffix}.{ext}"
        path = base_dir / filename
        if not path.exists():
            return path
    raise Exception("⚠️ 파일이 너무 많습니다. 수동 저장 필요.")

def save_image(image: Image.Image, save_path: Path, format: str, auto_open: bool):
    """이미지 저장 및 조건부 열기"""
    if save_path.exists():
        overwrite = input(f"\n⚠️ 파일이 이미 존재합니다: {save_path.name}\n덮어쓰시겠습니까? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("🚫 저장을 취소했습니다.")
            sys.exit(0)

    try:
        image.save(save_path, format=format.upper())
        print(f"\n✅ 이미지 저장 완료: {save_path}")
        if auto_open:
            os.startfile(str(save_path))  # Windows 전용
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")
        sys.exit(1)

def get_user_folder(option: str) -> Path:
    """사용자가 선택한 폴더 경로 반환"""
    home = Path.home()
    if option == "downloads":
        return home / "Downloads"
    elif option == "documents":
        return home / "Documents"
    else:
        return Path.cwd()

def ask_extension() -> str:
    ext_map = {'1': 'png', '2': 'jpg', '3': 'bmp'}
    print("\n저장할 이미지 확장자를 선택하세요:")
    print("  1. PNG (기본)")
    print("  2. JPG")
    print("  3. BMP")
    choice = input("번호 입력 [1/2/3]: ").strip()
    return ext_map.get(choice, 'png')

# ----------------- GUI 모드 ------------------

def run_gui_mode(image: Image.Image):
    root = tk.Tk()
    root.withdraw()

    filetypes = [
        ("PNG", "*.png"),
        ("JPG", "*.jpg"),
        ("BMP", "*.bmp"),
    ]

    default_name = Path.cwd().name + "_01.png"
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=filetypes,
        initialfile=default_name,
        title="이미지 저장 경로 선택"
    )

    if not save_path:
        messagebox.showinfo("취소됨", "저장이 취소되었습니다.")
        sys.exit(0)

    try:
        ext = Path(save_path).suffix.lstrip('.')
        image.save(save_path, format=ext.upper())
        messagebox.showinfo("저장 완료", f"이미지가 저장되었습니다:\n{save_path}")
    except Exception as e:
        messagebox.showerror("오류", f"이미지 저장 실패: {e}")
    sys.exit(0)

# ----------------- Main ------------------

def main():
    image = get_clipboard_image()

    print("🖼️ GUI 모드로 실행할까요? (Y/n): ", end="")
    gui_choice = input().strip().lower()

    if gui_choice in ['', 'y', 'yes']:
        run_gui_mode(image)

    # ---- 콘솔 모드 진입 ----
    print("👉 기본값으로 저장하시겠습니까? (파일명=폴더명_번호, 현재폴더, PNG, 미리보기 없음)")
    use_default = input("기본값 사용? (Y/n): ").strip().lower()

    base_dir = Path.cwd()
    folder_name = base_dir.name
    ext = "png"

    if use_default in ['', 'y', 'yes']:
        save_path = get_next_numbered_filename(base_dir, folder_name, ext)
        save_image(image, save_path, ext, auto_open=False)
        return

    # 사용자 입력 경로 설정
    custom_name = input(f"저장할 파일 이름을 입력하세요 (엔터 시 기본: {folder_name}): ").strip()
    if not custom_name:
        custom_name = folder_name

    print("\n저장할 위치를 선택하세요:")
    print("  1. 현재 폴더 (기본)")
    print("  2. 다운로드 폴더")
    print("  3. 문서 폴더")
    folder_choice = input("번호 입력 [1/2/3]: ").strip()
    folder_map = {"1": "current", "2": "downloads", "3": "documents"}
    folder_option = folder_map.get(folder_choice, "current")
    save_dir = get_user_folder(folder_option)

    ext = ask_extension()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{custom_name}_{timestamp}.{ext}"
    save_path = save_dir / filename

    auto_open = input("저장 후 이미지를 바로 여시겠습니까? (y/N): ").strip().lower() == 'y'
    save_image(image, save_path, ext, auto_open)

if __name__ == "__main__":
    main()
