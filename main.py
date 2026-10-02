import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import struct
import os

class ActCKDEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("act.ckd Path Replacer — Just Dance 2017")
        self.root.geometry("780x640")
        self.root.configure(bg="#0a0f1a")
        self.filepath = None
        self.data = None
        self.row_entries = []
        self._build_ui()

    def _build_ui(self):
        bg       = "#0a0f1a"
        panel    = "#101826"
        entry_bg = "#0d1320"
        accent   = "#00b4ff"
        text_c   = "#e0e8f0"
        hint_c   = "#6080a0"
        btn_bg   = "#0d3a5c"
        btn_act  = "#006699"

        # --- Top bar ---
        top = tk.Frame(self.root, bg=panel, relief="flat", bd=0)
        top.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top, text="act.ckd Path Replacer", font=("Segoe UI", 16, "bold"),
                 bg=panel, fg=accent).pack(side="left", padx=(10, 0))

        self.btn_open = tk.Button(top, text="Open act.ckd", command=self.open_file,
                                  bg=btn_bg, fg=text_c, activebackground=btn_act,
                                  activeforeground="white", relief="flat",
                                  font=("Segoe UI", 10), padx=12, pady=4, cursor="hand2")
        self.btn_open.pack(side="right", padx=10, pady=8)

        self.lbl_file = tk.Label(top, text="No file loaded", bg=panel, fg=hint_c,
                                font=("Segoe UI", 9))
        self.lbl_file.pack(side="right", padx=5)

        # --- Middle ---
        mid = tk.Frame(self.root, bg=bg)
        mid.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: replacements
        left = tk.Frame(mid, bg=panel, relief="flat", bd=0)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(left, text="Replacements", font=("Segoe UI", 11, "bold"),
                 bg=panel, fg=accent).pack(anchor="w", padx=10, pady=(8, 4))

        hdr = tk.Frame(left, bg=panel)
        hdr.pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(hdr, text="Find (old path)", bg=panel, fg=hint_c,
                 font=("Segoe UI", 9), width=28, anchor="w").pack(side="left")
        tk.Label(hdr, text="Replace (new path)", bg=panel, fg=hint_c,
                 font=("Segoe UI", 9), width=28, anchor="w").pack(side="left", padx=(5, 0))

        list_container = tk.Frame(left, bg=panel)
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self.canvas = tk.Canvas(list_container, bg=panel, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical",
                                 command=self.canvas.yview, bg=panel,
                                 troughcolor=panel, activebackground=btn_act)
        self.scroll_frame = tk.Frame(self.canvas, bg=panel)
        self.scroll_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(left, text="+ Add replacement", command=self.add_row,
                  bg=btn_bg, fg=text_c, activebackground=btn_act,
                  activeforeground="white", relief="flat", font=("Segoe UI", 9),
                  padx=8, pady=3, cursor="hand2").pack(anchor="w", padx=10, pady=(0, 8))

        # Right: log
        right = tk.Frame(mid, bg=panel, relief="flat", bd=0)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="Log / Preview", font=("Segoe UI", 11, "bold"),
                 bg=panel, fg=accent).pack(anchor="w", padx=10, pady=(8, 4))

        self.log = scrolledtext.ScrolledText(right, bg=entry_bg, fg=text_c,
                                             insertbackground=text_c, font=("Consolas", 9),
                                             relief="flat", wrap="word", height=12)
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        self.log.tag_config("error",   foreground="#ff5060")
        self.log.tag_config("success", foreground="#00ff88")
        self.log.tag_config("info",    foreground="#00b4ff")

        # --- Bottom ---
        bottom = tk.Frame(self.root, bg=bg)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(bottom, text="Preview", command=self.preview,
                  bg=btn_bg, fg=text_c, activebackground=btn_act,
                  activeforeground="white", relief="flat", font=("Segoe UI", 10),
                  padx=16, pady=6, cursor="hand2").pack(side="left", padx=(10, 5))

        tk.Button(bottom, text="Apply & Save", command=self.apply_save,
                  bg=accent, fg="#0a0f1a", activebackground="#0088cc",
                  activeforeground="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=16, pady=6,
                  cursor="hand2").pack(side="left", padx=5)

        tk.Button(bottom, text="Extract all paths", command=self.extract_paths,
                  bg=btn_bg, fg=text_c, activebackground=btn_act,
                  activeforeground="white", relief="flat", font=("Segoe UI", 10),
                  padx=12, pady=6, cursor="hand2").pack(side="right", padx=(5, 10))

        self.add_row()

    # --- Row management ---
    def add_row(self, find_val="", replace_val=""):
        rf = tk.Frame(self.scroll_frame, bg="#101826")
        rf.pack(fill="x", pady=2)

        fe = tk.Entry(rf, bg="#0d1320", fg="#e0e8f0", insertbackground="#e0e8f0",
                      font=("Consolas", 9), relief="flat", width=28)
        fe.insert(0, find_val)
        fe.pack(side="left", padx=(0, 5))

        re_ = tk.Entry(rf, bg="#0d1320", fg="#e0e8f0", insertbackground="#e0e8f0",
                       font=("Consolas", 9), relief="flat", width=28)
        re_.insert(0, replace_val)
        re_.pack(side="left")

        tk.Button(rf, text="\u2715", command=lambda: self.del_row(rf),
                  bg="#3a1020", fg="#ff6080", activebackground="#5a1530",
                  activeforeground="white", relief="flat", font=("Segoe UI", 8),
                  padx=4, cursor="hand2").pack(side="left", padx=(5, 0))

        self.row_entries.append((fe, re_))

    def del_row(self, rf):
        for i, (fe, re_) in enumerate(self.row_entries):
            if fe.master is rf:
                self.row_entries.pop(i)
                break
        rf.destroy()

    # --- Logging ---
    def log_msg(self, msg, tag=None):
        self.log.insert("end", msg + "\n", tag if tag else ())
        self.log.see("end")

    # --- File I/O ---
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select act.ckd",
            filetypes=[("CKD files", "*.ckd"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.data = bytearray(f.read())
            self.filepath = path
            self.lbl_file.config(text=os.path.basename(path), fg="#00ff88")
            self.log_msg(f"Loaded: {path} ({len(self.data)} bytes)", "success")
            self.log_msg("Click 'Extract all paths' to see all string paths.", "info")
        except Exception as e:
            self.log_msg(f"Error: {e}", "error")

    # --- Scanning ---
    def find_all_strings(self):
        results = []
        i = 0
        while i < len(self.data) - 4:
            length = struct.unpack_from("<I", self.data, i)[0]
            if 1 <= length <= 300 and i + 4 + length <= len(self.data):
                raw = self.data[i + 4 : i + 4 + length]
                try:
                    s = raw.decode("utf-8")
                    if "/" in s or any(ext in s for ext in (".ckd", ".tpl", ".png", ".bik", ".wav")):
                        results.append((i, length, s))
                except UnicodeDecodeError:
                    pass
            i += 1
        return results

    def extract_paths(self):
        if self.data is None:
            self.log_msg("No file loaded!", "error")
            return
        self.log_msg("\n--- All paths found ---", "info")
        strings = self.find_all_strings()
        if not strings:
            self.log_msg("No paths found.", "error")
            return
        for offset, length, s in strings:
            self.log_msg(f"  @0x{offset:06X} [{length:3d}] \"{s}\"")
        self.log_msg(f"Total: {len(strings)} paths\n", "info")

    # --- Replacements ---
    def get_replacements(self):
        reps = []
        for fe, re_ in self.row_entries:
            f = fe.get().strip()
            r = re_.get().strip()
            if f and r:
                reps.append((f, r))
        return reps

    def apply_replacements(self, preview_only=False):
        if self.data is None:
            self.log_msg("No file loaded!", "error")
            return None
        reps = self.get_replacements()
        if not reps:
            self.log_msg("No replacements specified!", "error")
            return None

        data = bytearray(self.data)
        edits = []  # (offset, old_len, new_bytes)

        for find_str, replace_str in reps:
            fb = find_str.encode("utf-8")
            rb = replace_str.encode("utf-8")
            pattern = struct.pack("<I", len(fb)) + fb
            new_pat = struct.pack("<I", len(rb)) + rb
            pos = 0
            while True:
                idx = data.find(pattern, pos)
                if idx == -1:
                    break
                edits.append((idx, len(pattern), new_pat))
                pos = idx + len(pattern)

        if not edits:
            self.log_msg("No matching strings found!", "error")
            return None

        # Apply from end to start so offsets stay valid
        edits.sort(key=lambda x: x[0], reverse=True)
        for offset, old_len, new_bytes in edits:
            data[offset : offset + old_len] = new_bytes

        for find_str, replace_str in reps:
            rb = replace_str.encode("utf-8")
            new_pat = struct.pack("<I", len(rb)) + rb
            count = sum(1 for e in edits if e[2] == new_pat)
            self.log_msg(f"  \"{find_str}\" -> \"{replace_str}\" ({count}x)", "success")

        self.log_msg(f"Total edits: {len(edits)}", "success")

        if preview_only:
            self.log_msg(f"Preview: {len(self.data)} -> {len(data)} bytes", "info")
        else:
            self.log_msg(f"Applied: {len(self.data)} -> {len(data)} bytes", "success")

        return data

    def preview(self):
        self.log_msg("\n=== PREVIEW ===", "info")
        self.apply_replacements(preview_only=True)
        self.log_msg("================\n", "info")

    def apply_save(self):
        result = self.apply_replacements(preview_only=False)
        if result is None:
            return
        save_path = filedialog.asksaveasfilename(
            title="Save act.ckd",
            defaultextension=".ckd",
            initialfile=os.path.basename(self.filepath) if self.filepath else "act.ckd",
            filetypes=[("CKD files", "*.ckd"), ("All files", "*.*")]
        )
        if not save_path:
            self.log_msg("Save cancelled.", "info")
            return
        try:
            with open(save_path, "wb") as f:
                f.write(result)
            self.data = result
            self.filepath = save_path
            self.lbl_file.config(text=os.path.basename(save_path), fg="#00ff88")
            self.log_msg(f"Saved: {save_path} ({len(result)} bytes)", "success")
            messagebox.showinfo("Done", f"Saved:\n{save_path}\n{len(result)} bytes")
        except Exception as e:
            self.log_msg(f"Error saving: {e}", "error")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    ActCKDEditor(root)
    root.mainloop()
