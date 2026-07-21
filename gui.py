import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from main import sync_playlist

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

MIN_DURATION = 1
MAX_DURATION = 180
DEFAULT_DURATION = 15

if DND_AVAILABLE:
    class AppRoot(ctk.CTk, TkinterDnD.DnDWrapper):
        # CTk root with the tkdnd Tcl package loaded, so any widget in the
        # window can register as a drop target.
        def __init__(self):
            super().__init__()
            self.TkdndVersion = TkinterDnD._require(self)
else:
    AppRoot = ctk.CTk


class PlaylistApp:

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Sync")
        self.root.geometry("720x700")
        self.root.minsize(640, 620)

        self.build_ui()

    def build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(4, weight=1)

        # ---- Header: title + theme switcher ----
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="🎵  YouTube Playlist Sync",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Build and sync playlists from a plain-text track list",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).grid(row=1, column=0, sticky="w")

        self.theme_switcher = ctk.CTkSegmentedButton(
            header, values=["System", "Light", "Dark"],
            command=self.change_theme
        )
        self.theme_switcher.set("System")
        self.theme_switcher.grid(row=0, column=1, rowspan=2, sticky="e")

        # ---- Card: playlist source ----
        source_card = ctk.CTkFrame(self.root, corner_radius=12)
        source_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        source_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            source_card, text="Playlist Source",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4))

        file_hint = "Playlist file (.txt)"
        if DND_AVAILABLE:
            file_hint += " — or drag & drop it here"
        self.file_entry = ctk.CTkEntry(
            source_card, placeholder_text=file_hint, height=36
        )
        self.file_entry.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=4)

        self.browse_button = ctk.CTkButton(
            source_card, text="Browse", width=100, height=36,
            command=self.select_file
        )
        self.browse_button.grid(row=1, column=1, sticky="e", padx=(0, 16), pady=4)

        if DND_AVAILABLE:
            self.file_entry.drop_target_register(DND_FILES)
            self.file_entry.dnd_bind("<<Drop>>", self.handle_drop)

        self.title_entry = ctk.CTkEntry(
            source_card, placeholder_text="Playlist title (optional — defaults to the file name)",
            height=36
        )
        self.title_entry.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(4, 14)
        )

        # ---- Card: sync options ----
        options_card = ctk.CTkFrame(self.root, corner_radius=12)
        options_card.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        options_card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            options_card, text="Sync Options",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(options_card, text="Privacy").grid(
            row=1, column=0, sticky="w", padx=16
        )
        self.privacy_var = tk.StringVar(value="private")
        self.privacy_menu = ctk.CTkOptionMenu(
            options_card, variable=self.privacy_var,
            values=["private", "unlisted", "public"], width=140
        )
        self.privacy_menu.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 14))

        ctk.CTkLabel(options_card, text="Max video length (minutes)").grid(
            row=1, column=1, sticky="w", padx=8
        )
        spin_frame = ctk.CTkFrame(options_card, fg_color="transparent")
        spin_frame.grid(row=2, column=1, sticky="w", padx=8, pady=(2, 14))

        self.duration_down = ctk.CTkButton(
            spin_frame, text="−", width=32, command=lambda: self.step_duration(-1)
        )
        self.duration_down.pack(side="left")
        self.duration_entry = ctk.CTkEntry(spin_frame, width=56, justify="center")
        self.duration_entry.insert(0, str(DEFAULT_DURATION))
        self.duration_entry.pack(side="left", padx=6)
        self.duration_up = ctk.CTkButton(
            spin_frame, text="+", width=32, command=lambda: self.step_duration(1)
        )
        self.duration_up.pack(side="left")

        self.live_var = tk.BooleanVar(value=False)
        self.live_checkbox = ctk.CTkCheckBox(
            options_card, text="Allow live tracks", variable=self.live_var
        )
        self.live_checkbox.grid(row=2, column=2, sticky="w", padx=16, pady=(2, 14))

        # ---- Sync button + progress ----
        action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=8)
        action_frame.grid_columnconfigure(0, weight=1)

        self.sync_button = ctk.CTkButton(
            action_frame, text="Sync Playlist", height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.run_sync
        )
        self.sync_button.grid(row=0, column=0, sticky="ew")

        self.progress = ctk.CTkProgressBar(action_frame, height=10)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        # ---- Card: activity log ----
        log_card = ctk.CTkFrame(self.root, corner_radius=12)
        log_card.grid(row=4, column=0, sticky="nsew", padx=20, pady=(8, 16))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_card, text="Activity Log",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.log_text = ctk.CTkTextbox(
            log_card, font=ctk.CTkFont(family="Courier", size=12), wrap="word"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 14))

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice.lower())

    def step_duration(self, delta):
        try:
            value = int(self.duration_entry.get())
        except ValueError:
            value = DEFAULT_DURATION
        value = max(MIN_DURATION, min(MAX_DURATION, value + delta))
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, str(value))

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
            self.progress.set(current / total)
        else:
            self.progress.set(0)

    def run_sync(self):
        file_path = self.file_entry.get()
        title = self.title_entry.get()
        privacy = self.privacy_var.get()

        # Read the customized duration value safely
        try:
            max_duration = int(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Please provide a valid integer for maximum video length.")
            return

        allow_live = self.live_var.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a playlist file.")
            return

        self.sync_button.configure(state="disabled")
        self.progress.set(0)
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
                self.root.after(0, lambda: self.sync_button.configure(state="normal"))

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    root = AppRoot()
    app = PlaylistApp(root)
    root.mainloop()
