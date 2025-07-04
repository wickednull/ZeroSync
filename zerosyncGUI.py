#!/usr/bin/env python3
"""
ZeroSync GUI v1.0 – Cyberpunk Bluetooth Attack Toolkit
Author: Null_Lyfe
"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# === Launch Functions ===
def launch_script(script_name):
    try:
        subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {script_name}"])
    except FileNotFoundError:
        try:
            subprocess.Popen(["gnome-terminal", "--", "python3", script_name])
        except:
            messagebox.showerror("Error", f"Failed to launch {script_name}")

def launch_mesh_attack():
    launch_script("zerojam_mesh.py")

def launch_cli_version():
    launch_script("zerosync.py")

# === GUI Setup ===
root = tk.Tk()
root.title("ZeroSync – Bluetooth Offensive Toolkit")
root.geometry("700x520")
root.configure(bg="#0f0f0f")

style = ttk.Style()
style.theme_use("clam")
style.configure("Cyber.TButton", font=("Consolas", 12), foreground="#00ffcc", background="#1f1f1f", padding=8)
style.map("Cyber.TButton",
          foreground=[('pressed', '#ff00ff'), ('active', '#00ffff')],
          background=[('pressed', '#222222'), ('active', '#1a1a1a')])

# === Header Frame ===
header = tk.Frame(root, bg="#0f0f0f")
header.pack(pady=20)
title = tk.Label(header, text="💀 ZeroSync GUI 💀", font=("Consolas", 20, "bold"), fg="#00ffff", bg="#0f0f0f")
title.pack()
subtitle = tk.Label(header, text="Created by Null_Lyfe", font=("Consolas", 12), fg="#ff00ff", bg="#0f0f0f")
subtitle.pack()

# === Button Frame ===
btn_frame = tk.Frame(root, bg="#0f0f0f")
btn_frame.pack(pady=10)

def create_button(text, command):
    return ttk.Button(btn_frame, text=text, command=command, style="Cyber.TButton")

# === Tool Buttons ===
buttons = [
    ("🔍 Scan Devices", lambda: launch_script("zerosync.py")),
    ("📜 View Scan History", lambda: launch_script("zerosync.py")),
    ("🎭 MAC Spoofing", lambda: launch_script("zerosync.py")),
    ("🕶️ Stealth Mode", lambda: launch_script("zerosync.py")),
    ("📡 Broadcast Aliases", lambda: launch_script("zerosync.py")),
    ("✂️ Deauth BLE Device", lambda: launch_script("zerosync.py")),
    ("💣 Crash BLE Device", lambda: launch_script("zerosync.py")),
    ("💌 Replay Notification Spam", lambda: launch_script("zerosync.py")),
    ("📶 RFCOMM Flood", lambda: launch_script("zerosync.py")),
    ("💥 L2Ping DoS", lambda: launch_script("zerosync.py")),
    ("💀 CVE-2017-0785 Exploit", lambda: launch_script("zerosync.py")),
    ("🧠 Bettercap BLE Bridge", lambda: launch_script("zerosync.py")),
    ("🛰 Mesh Attack (ZeroJam)", launch_mesh_attack),
    ("📁 Export Logs", lambda: launch_script("zerosync.py")),
    ("🧠 Launch CLI Version", launch_cli_version),
    ("❌ Exit", root.quit)
]

for idx, (label, cmd) in enumerate(buttons):
    btn = create_button(label, cmd)
    btn.grid(row=idx // 2, column=idx % 2, padx=15, pady=10, sticky="ew")

# === Footer ===
footer = tk.Label(root, text="ZeroSync v7.9 | All modules integrated", font=("Consolas", 10), fg="#4444ff", bg="#0f0f0f")
footer.pack(side="bottom", pady=10)

root.mainloop()