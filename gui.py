import sys
import io
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from main import sync_playlist

# Optional drag-and-drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = tk.Tk  # fallback
    DND_AVAILABLE = False

# Windows theme detection
try:
    import winreg
except ImportError:
    winreg = None

def get_system_theme():
    if platform.system() == "Windows" and winreg is not None:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            # 0 = dark, 1 = light
            return "dark" if value == 0 else "light"
        except Exception:
            return "dark"
    return "light"  # fallback for other OSes

class PlaylistApp:

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Sync")

        self.theme_var = tk.StringVar(value="system")

        self.bg_color = "#1e1e1e"
        self.fg_color = "#e6e6e6"
        self.entry_bg = "#2a2a2a"
        self.accent = "#3a7ff6"

        self.build_ui()
        self.apply_theme()  # initial theme

    def build_ui(self):
        self.root.geometry("700x550")

        # Theme controls frame
        theme_frame = tk.Frame(self.root)
        theme_frame.pack(anchor="ne", padx=10, pady=5)

        tk.Label(theme_frame, text="Theme:").pack(side="left", padx=5)

        for value in ["system", "light", "dark"]:
            tk.Radiobutton(
                theme_frame,
                text=value.capitalize(),
                variable=self.theme_var,
                value=value,
                command=self.apply_theme
            ).pack(side="left")

        # Main content frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Playlist file
        self.file_label = tk.Label(self.main_frame, text="Playlist File (.txt)")
        self.file_label.pack(pady=5)

        self.file_entry = tk.Entry(self.main_frame, width=60)
        self.file_entry.pack()

        self.browse_button = tk.Button(
            self.main_frame, text="Browse", command=self.select_file
        )
        self.browse_button.pack(pady=5)

        # Drag and drop hint
        if DND_AVAILABLE:
            self.file_entry.drop_target_register(DND_FILES)
            self.file_entry.dnd_bind("<<Drop>>", self.handle_drop)

        # Title
        self.title_label = tk.Label(self.main_frame, text="Playlist Title (optional)")
        self.title_label.pack(pady=5)

        self.title_entry = tk.Entry(self.main_frame, width=60)
        self.title_entry.pack()

        # Privacy
        self.privacy_label = tk.Label(self.main_frame, text="Privacy")
        self.privacy_label.pack(pady=5)

        self.privacy_var = tk.StringVar(value="private")
        self.privacy_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.privacy_var,
            values=["private", "unlisted", "public"],
            state="readonly"
        )
        self.privacy_dropdown.pack()

        # Sync button
        self.sync_button = tk.Button(
            self.main_frame,
            text="Sync Playlist",
            command=self.run_sync,
            width=20
        )
        self.sync_button.pack(pady=15)

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode="determinate")
        self.progress.pack(fill="x", padx=10)

        # Log label
        self.log_label = tk.Label(self.main_frame, text="Activity Log")
        self.log_label.pack(pady=5)

        # Log text
        self.log_text = tk.Text(self.main_frame, height=12)
        self.log_text.pack(fill="both", expand=True)

    # ---------- THEME -----------

    def apply_theme(self):
        # Decide mode
        theme_choice = self.theme_var.get()
        if theme_choice == "system":
            mode = get_system_theme()
        else:
            mode = theme_choice

        if mode == "dark":
            self.bg_color = "#1e1e1e"
            self.fg_color = "#e6e6e6"
            self.entry_bg = "#2a2a2a"
            self.accent = "#3a7ff6"
        else:  # light
            self.bg_color = "#f2f2f2"
            self.fg_color = "#1e1e1e"
            self.entry_bg = "#ffffff"
            self.accent = "#3a7ff6"

        # Apply to root
        self.root.configure(bg=self.bg_color)

        # Theme frame labels & radios
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label) or isinstance(sub, tk.Radiobutton):
                        sub.configure(bg=self.bg_color, fg=self.fg_color)

        # Main frame bg
        self.main_frame.configure(bg=self.bg_color)

        # Labels
        for widget in [
            self.file_label,
            self.title_label,
            self.privacy_label,
            self.log_label,
        ]:
            widget.configure(bg=self.bg_color, fg=self.fg_color)

        # Entries
        for entry in [self.file_entry, self.title_entry]:
            entry.configure(bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)

        # Buttons
        self.browse_button.configure(bg=self.accent, fg="white", activebackground=self.accent)
        self.sync_button.configure(bg=self.accent, fg="white", activebackground=self.accent)

        # Log text
        self.log_text.configure(bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)

    # ---------- FILE PICKER & DND -----------

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def handle_drop(self, event):
        path = event.data
        # On Windows, paths may come wrapped in {} when there are spaces
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, path)

    # ---------- LOGGING & PROGRESS -----------

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def update_progress(self, current, total):
        if total > 0:
            value = int((current / total) * 100)
            self.progress["value"] = value
        else:
            self.progress["value"] = 0

    # ---------- SYNC THREAD -----------

    def run_sync(self):
        file_path = self.file_entry.get()
        title = self.title_entry.get()
        privacy = self.privacy_var.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a playlist file.")
            return

        self.sync_button.config(state="disabled")
        self.progress["value"] = 0
        self.log_text.delete("1.0", tk.END)
        self.log("Starting sync...")

        def task():
            try:
                sync_playlist(
                    file_path,
                    title if title else None,
                    privacy,
                    log_callback=self.log,
                    progress_callback=self.update_progress
                )
                self.log("Finished.")
                messagebox.showinfo("Success", "Playlist synced successfully.")
            except Exception as e:
                self.log(f"Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.sync_button.config(state="normal")

        threading.Thread(target=task, daemon=True).start()

# ---------- RUN APP ----------

if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = PlaylistApp(root)
    root.mainloop()