import sys
import io
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from main import sync_playlist

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = tk.Tk  
    DND_AVAILABLE = False

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
            return "dark" if value == 0 else "light"
        except Exception:
            return "dark"
    return "light"  

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
        self.apply_theme()  

    def build_ui(self):
        self.root.geometry("700x620") # Expanded slightly to give our new options breathing room

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

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.file_label = tk.Label(self.main_frame, text="Playlist File (.txt)")
        self.file_label.pack(pady=5)

        self.file_entry = tk.Entry(self.main_frame, width=60)
        self.file_entry.pack()

        self.browse_button = tk.Button(
            self.main_frame, text="Browse", command=self.select_file
        )
        self.browse_button.pack(pady=5)

        if DND_AVAILABLE:
            self.file_entry.drop_target_register(DND_FILES)
            self.file_entry.dnd_bind("<<Drop>>", self.handle_drop)

        self.title_label = tk.Label(self.main_frame, text="Playlist Title (optional)")
        self.title_label.pack(pady=5)

        self.title_entry = tk.Entry(self.main_frame, width=60)
        self.title_entry.pack()

        self.privacy_label = tk.Label(self.main_frame, text="Privacy")
        self.privacy_label.pack(pady=5)

        self.privacy_var = tk.StringVar(value="private")
        self.privacy_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.privacy_var,
            values=["private", "unlisted", "public"],
            state="readonly"
        )
        self.privacy_dropdown.pack(pady=5)

        # ---- NEW FILTER SELECTION ROW FRAME ----
        self.filter_frame = tk.Frame(self.main_frame)
        self.filter_frame.pack(pady=10)

        self.duration_label = tk.Label(self.filter_frame, text="Max Video Length (Minutes):")
        self.duration_label.pack(side="left", padx=5)
        
        self.duration_spinbox = tk.Spinbox(self.filter_frame, from_=1, to=180, width=5)
        self.duration_spinbox.delete(0, "end")
        self.duration_spinbox.insert(0, "15") # Match original defaults
        self.duration_spinbox.pack(side="left", padx=5)

        self.live_var = tk.BooleanVar(value=False)
        self.live_checkbox = tk.Checkbutton(
            self.filter_frame, 
            text="Allow Live Tracks", 
            variable=self.live_var
        )
        self.live_checkbox.pack(side="left", padx=15)
        # ----------------------------------------

        self.sync_button = tk.Button(
            self.main_frame,
            text="Sync Playlist",
            command=self.run_sync,
            width=20
        )
        self.sync_button.pack(pady=10)

        self.progress = ttk.Progressbar(self.main_frame, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        self.log_label = tk.Label(self.main_frame, text="Activity Log")
        self.log_label.pack(pady=5)

        self.log_text = tk.Text(self.main_frame, height=10)
        self.log_text.pack(fill="both", expand=True)

    def apply_theme(self):
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
        else:  
            self.bg_color = "#f2f2f2"
            self.fg_color = "#1e1e1e"
            self.entry_bg = "#ffffff"
            self.accent = "#3a7ff6"

        self.root.configure(bg=self.bg_color)

        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label) or isinstance(sub, tk.Radiobutton):
                        sub.configure(bg=self.bg_color, fg=self.fg_color)

        self.main_frame.configure(bg=self.bg_color)
        self.filter_frame.configure(bg=self.bg_color) # Ensure options block adapts seamlessly

        for widget in [
            self.file_label,
            self.title_label,
            self.privacy_label,
            self.duration_label,
            self.log_label,
        ]:
            widget.configure(bg=self.bg_color, fg=self.fg_color)

        for entry in [self.file_entry, self.title_entry]:
            entry.configure(bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)

        # Theme matching customization for specialized filter selectors
        self.duration_spinbox.configure(bg=self.entry_bg, fg=self.fg_color, buttonbackground=self.entry_bg, insertbackground=self.fg_color)
        self.live_checkbox.configure(bg=self.bg_color, fg=self.fg_color, selectcolor=self.entry_bg, activebackground=self.bg_color, activeforeground=self.fg_color)

        self.browse_button.configure(bg=self.accent, fg="white", activebackground=self.accent)
        self.sync_button.configure(bg=self.accent, fg="white", activebackground=self.accent)

        self.log_text.configure(bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def handle_drop(self, event):
        path = event.data
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, path)

    # Tkinter is not thread-safe: the sync worker thread must never touch
    # widgets directly, so log/progress callbacks are marshaled onto the
    # main loop with root.after.

    def log(self, message):
        self.root.after(0, self._append_log, message)

    def _append_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def update_progress(self, current, total):
        self.root.after(0, self._set_progress, current, total)

    def _set_progress(self, current, total):
        if total > 0:
            value = int((current / total) * 100)
            self.progress["value"] = value
        else:
            self.progress["value"] = 0

    def run_sync(self):
        file_path = self.file_entry.get()
        title = self.title_entry.get()
        privacy = self.privacy_var.get()
        
        # Read the customized duration value safely
        try:
            max_duration = int(self.duration_spinbox.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Please provide a valid integer for maximum video length.")
            return
            
        allow_live = self.live_var.get()

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
                    max_duration_minutes=max_duration,
                    allow_live=allow_live,
                    log_callback=self.log,
                    progress_callback=self.update_progress
                )
                self.log("Finished.")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", "Playlist synced successfully."))
            except Exception as e:
                self.log(f"Error: {e}")
                self.root.after(0, lambda message=str(e): messagebox.showerror(
                    "Error", message))
            finally:
                self.root.after(0, lambda: self.sync_button.config(state="normal"))

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = PlaylistApp(root)
    root.mainloop()
