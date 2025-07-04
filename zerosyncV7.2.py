#!/usr/bin/env python3
"""
ZeroSync v7.0 – BLE Warfare Platform
Author: Null_Lyfe
"""

import os
import sys
import time
import json
import random
import subprocess
from datetime import datetime
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, BTLEException, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()
seen_devices = {}

class BLEHandler(DefaultDelegate):
    def __init__(self):
        super().__init__()
    def handleNotification(self, cHandle, data):
        console.print(f"[yellow]📥 Notification: {data}[/yellow]")

def scan_devices():
    console.print("[cyan]🔎 Scanning for BLE devices...[/cyan]")
    scanner = Scanner()
    try:
        devices = scanner.scan(10.0)
        for idx, d in enumerate(devices):
            mac = d.addr
            rssi = d.rssi
            if mac not in seen_devices:
                seen_devices[mac] = {
                    "first_seen": datetime.now().strftime("%H:%M:%S"),
                    "max_rssi": rssi
                }
            else:
                seen_devices[mac]["max_rssi"] = max(seen_devices[mac]["max_rssi"], rssi)
            vendor = guess_vendor(mac)
            console.print(f"[magenta]{idx}[/magenta]: {mac} ({vendor}) RSSI={rssi} dB")
        return devices
    except BTLEException as e:
        console.print(f"[red]❌ Scan error: {e}[/red]")
        return []

def guess_vendor(mac):
    prefix = mac.upper()[0:8]
    vendor_table = {
        "D8:A0:1D": "FitBit Inc.",
        "00:1A:7D": "Apple Inc.",
        "B8:27:EB": "Raspberry Pi",
        "40:4E:36": "Sony Audio",
        "00:1B:DC": "CSR (Cambridge Silicon Radio)"
    }
    return vendor_table.get(prefix, "Unknown")


def export_logs():
    os.makedirs("zerosync_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"zerosync_logs/session_{timestamp}.log"
    with open(path, "w") as f:
        for mac, meta in seen_devices.items():
            vendor = "UnknownVendor"
            f.write(f"{mac} ({vendor}) | Seen: {meta['first_seen']} | Max RSSI: {meta['max_rssi']}\n")
    console.print(f"[green]📁 Logs saved to {path}[/green]")
def zerojam_mesh_attack():
    console.print("[magenta]🕸️ Launching ZeroJam Mesh Flood...[/magenta]")
    names = ["zerojam_node01", "zerojam_node02", "zerojam_node03", "zerojam_beacon"]
    try:
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)
        while True:
            for name in names:
                subprocess.run(["bluetoothctl", "system-alias", name], stdout=subprocess.DEVNULL)
                console.print(f"[cyan]🌐 Broadcasting ZeroJam mesh beacon: {name}[/cyan]")
                time.sleep(1)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 Mesh attack stopped.[/red]")

def spoof_device_profile():
    profiles = {
        "1": ("Wireless Keyboard", "HID", "00:1A:7D:DA:71:13"),
        "2": ("Game Controller", "HID", "00:1B:DC:12:34:56"),
        "3": ("Bluetooth Speaker", "AudioSink", "40:4E:36:AA:BB:CC")
    }
    console.print("[blue]🎭 Available spoof profiles:[/blue]")
    for k, (name, type_, mac) in profiles.items():
        console.print(f"[magenta]{k}[/magenta]: {name} ({type_}) - {mac}")
    selected = Prompt.ask("🧬 Select profile")
    if selected in profiles:
        _, _, mac = profiles[selected]
        os.system("sudo ifconfig hci0 down")
        os.system(f"sudo bdaddr -i hci0 {mac}")
        os.system("sudo ifconfig hci0 up")
        console.print(f"[green]✅ Spoofed MAC to emulate {profiles[selected][0]}[/green]")
    else:
        console.print("[red]Invalid selection.[/red]")

def exploit_cve_lookup():
    console.print("[cyan]📚 Loading exploit DB...[/cyan]")
    db = {
        "FitBit Inc.": ["CVE-2020-26555", "CVE-2019-12378"],
        "Apple Inc.": ["CVE-2017-0785", "CVE-2018-5383"],
        "CSR (Cambridge Silicon Radio)": ["CVE-2016-0801"]
    }
    if not seen_devices:
        console.print("[red]⚠️ No devices scanned.[/red]")
        return
    for idx, mac in enumerate(seen_devices):
        vendor = guess_vendor(mac)
        vulns = db.get(vendor, [])
        vulns_str = ", ".join(vulns) if vulns else "None found"
        console.print(f"[magenta]{idx}[/magenta]: {mac} ({vendor}) → [red]{vulns_str}[/red]")



def audio_deception():
    console.print("[blue]🎧 Faking AudioSink device profile...[/blue]")
    try:
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "system-alias", "ZeroAudio"], stdout=subprocess.DEVNULL)
        console.print("[cyan]🔊 Advertising as Bluetooth Audio Device: 'ZeroAudio'[/cyan]")
        console.print("[magenta]Press [bold]CTRL+C[/bold] to stop.[/magenta]")
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 Audio deception stopped.[/red]")


def zerojam_mesh_attack():
    console.print("[magenta]🌐 Launching ZeroJam Mesh Beacon Fuzzing...[/magenta]")
    fake_names = ["Node_X1", "Relay_42", "BLE_BOT", "⚡ZeroJam_Node", "💀ZeroSync_Mesh"]
    try:
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], stdout=subprocess.DEVNULL)
        while True:
            for name in fake_names:
                subprocess.run(["bluetoothctl", "system-alias", name], stdout=subprocess.DEVNULL)
                console.print(f"[cyan]🌐 Mesh Node Broadcast: {name}[/cyan]")
                time.sleep(1.5)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 ZeroJam mesh broadcast stopped.[/red]")

def main_menu():
    while True:
        console.print(Panel("[bold cyan]ZeroSync v7.0 – Created by Null_Lyfe[/bold cyan]", border_style="bright_magenta"))
        t = Table(title="ZeroSync Main Menu", box=box.ROUNDED)
        t.add_column("ID", style="magenta", justify="center")
        t.add_column("Action", style="white")
        t.add_row("1", "Scan for BLE Devices")
        t.add_row("2", "Export Scan Logs")
        t.add_row("3", "ZeroJam Mesh Beacon Attack")
        t.add_row("4", "Device Fingerprint + Vendor Guess")
        t.add_row("5", "Spoof Device Profile")
        t.add_row("6", "Lookup Known CVEs")
        t.add_row("7", "Fake AudioSink Device")
        t.add_row("0", "Exit")
        console.print(t)
        c = Prompt.ask("💜 Choose Option")
        if c == "1": scan_devices()
        elif c == "2": export_logs()
        elif c == "3": zerojam_mesh_attack()
        elif c == "4": scan_devices()
        elif c == "5": spoof_device_profile()
        elif c == "6": exploit_cve_lookup()
        elif c == "7": audio_deception()
        elif c == "0":
            console.print("[red]Exiting ZeroSync v7...[/red]")
            break
        else:
            console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main_menu()
