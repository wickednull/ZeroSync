#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import queue

class ZeroSyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZeroSync – Bluetooth Offensive Toolkit")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f0f0f")

        self.cmd_queue = queue.Queue()
        self.setup_style()
        self.build_layout()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cyber.TButton", font=("Consolas", 10), foreground="#00ffcc",
                        background="#1f1f1f", padding=6)
        style.map("Cyber.TButton",
                  foreground=[('pressed', '#ff00ff'), ('active', '#00ffff')],
                  background=[('pressed', '#222222'), ('active', '#1a1a1a')])

    def build_layout(self):
        header = tk.Frame(self.root, bg="#0f0f0f")
        header.pack(pady=10)
        title = tk.Label(header, text="💀 ZeroSync GUI 💀", font=("Consolas", 16, "bold"),
                         fg="#00ffff", bg="#0f0f0f")
        title.pack()
        subtitle = tk.Label(header, text="Created by Null_Lyfe", font=("Consolas", 10),
                            fg="#ff00ff", bg="#0f0f0f")
        subtitle.pack()

        body = tk.Frame(self.root, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        # Button panel
        btn_frame = tk.Frame(body, bg="#0f0f0f")
        btn_frame.pack(side="left", padx=10, pady=10, fill="y")

        tools = [
            ("Scan Devices", "python3 zerosync.py"),
            ("Broadcast", "python3 zerosync.py"),
            ("Crash", "python3 zerosync.py"),
            ("Deauth", "python3 zerosync.py"),
            ("Replay", "python3 zerosync.py"),
            ("RFCOMM", "python3 zerosync.py"),
            ("CVE", "python3 zerosync.py"),
            ("Bettercap", "python3 zerosync.py"),
            ("Mesh (ZeroJam)", "python3 zerojam_mesh.py"),
            ("Export Logs", "python3 zerosync.py"),
        ]

        for label, cmd in tools:
            ttk.Button(btn_frame, text=label, style="Cyber.TButton",
                       command=lambda c=cmd: self.run_command(c)).pack(pady=4, fill="x")

        ttk.Button(btn_frame, text="Exit", style="Cyber.TButton", command=self.root.quit).pack(
            pady=10, fill="x")

        # Terminal output box
        self.output_box = tk.Text(body, bg="black", fg="lime", insertbackground="lime",
                                  font=("Consolas", 10), wrap="word")
        self.output_box.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.output_box.insert("end", "[ZeroSync Terminal Initialized]\n")

        self.root.after(100, self.update_output)

    def run_command(self, cmd):
        def target():
            try:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    self.cmd_queue.put(line)
            except Exception as e:
                self.cmd_queue.put(f"[ERROR] {e}\n")
        threading.Thread(target=target, daemon=True).start()

    def update_output(self):
        try:
            while not self.cmd_queue.empty():
                line = self.cmd_queue.get_nowait()
                self.output_box.insert("end", line)
                self.output_box.see("end")
        finally:
            self.root.after(100, self.update_output)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZeroSyncGUI(root)
    root.mainloop()