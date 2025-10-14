import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class CustomScrollableDialog(tk.Toplevel):
    def __init__(self, parent, title, message, items):
        super().__init__(parent)
        self.title(title)
        self.result = False  # Default to False (No)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.geometry("600x400") # Set a default size

        tk.Label(self, text=message, justify=tk.LEFT).pack(padx=10, pady=10, anchor='w')

        text_frame = tk.Frame(self, borderwidth=1, relief="sunken")
        text_frame.pack(padx=10, pady=5, expand=True, fill='both')

        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, height=15, width=70)
        text_area.pack(expand=True, fill='both')
        
        text_area.insert(tk.INSERT, "\n".join(items))
        text_area.configure(state='disabled')

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Yes", command=self.on_yes, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="No", command=self.on_no, width=10).pack(side=tk.LEFT, padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_no) # Handle closing the window
        self.wait_window(self)

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()

def find_empty_folders(path):
    empty_folders = []
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if not dirnames and not filenames:
            empty_folders.append(dirpath)
    return empty_folders

def get_max_depth(path):
    max_d = 0
    base_path = os.path.normpath(path)
    base_depth = base_path.count(os.sep)
    for dirpath, _, _ in os.walk(path):
        current_path = os.path.normpath(dirpath)
        depth = current_path.count(os.sep) - base_depth
        if depth > max_d:
            max_d = depth
    return max_d + 1

def main():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select a folder to clean up")
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    print(f"Selected folder: {folder_path}")

    max_depth = get_max_depth(folder_path)
    proceed_with_depth = messagebox.askyesno(
        "Confirm Process",
        f"The maximum folder depth is {max_depth}.\n\n"
        f"The process will repeat up to {max_depth} times to ensure all nested empty folders are removed.\n\n"
        "Do you want to proceed?"
    )

    if not proceed_with_depth:
        print("Operation cancelled by user.")
        return

    deleted_folders_all_sessions = []
    for i in range(max_depth):
        print(f"--- Running pass {i+1} of {max_depth} ---")
        empty_folders_abs = find_empty_folders(folder_path)

        if not empty_folders_abs:
            print("No more empty folders found. Stopping process.")
            messagebox.showinfo("Info", "No more empty folders found. The process will now stop.")
            break

        relative_folders = sorted([os.path.relpath(p, folder_path) for p in empty_folders_abs])
        
        dialog = CustomScrollableDialog(
            root,
            "Confirm Deletion",
            f"Pass {i+1}/{max_depth}: Found {len(empty_folders_abs)} empty folders. Delete them?",
            relative_folders
        )
        proceed = dialog.result

        if proceed:
            deleted_in_this_session = []
            for folder in empty_folders_abs:
                try:
                    os.rmdir(folder)
                    rel_path = os.path.relpath(folder, folder_path)
                    deleted_in_this_session.append(rel_path)
                    print(f"Deleted: {rel_path}")
                except OSError as e:
                    print(f"Error deleting {folder}: {e}")
            
            if deleted_in_this_session:
                deleted_folders_all_sessions.extend(deleted_in_this_session)
                messagebox.showinfo("Pass Complete", f"Pass {i+1}/{max_depth} complete. Deleted {len(deleted_in_this_session)} folders.")
        else:
            print("Deletion cancelled by user.")
            messagebox.showinfo("Cancelled", f"Pass {i+1}/{max_depth}: Deletion cancelled.")
            break

    print("\n--- Operation Complete ---")
    if not deleted_folders_all_sessions:
        messagebox.showinfo("Complete", "Operation complete. No folders were deleted in total.")
        print("No folders were deleted.")
    else:
        # Sort the final list for cleaner reporting
        deleted_folders_all_sessions.sort()
        print(f"Total folders deleted: {len(deleted_folders_all_sessions)}")
        for folder in deleted_folders_all_sessions:
            print(folder)
        
        CustomScrollableDialog(
            root,
            "Deletion Report",
            f"Total folders deleted: {len(deleted_folders_all_sessions)}",
            deleted_folders_all_sessions
        )

if __name__ == "__main__":
    main()