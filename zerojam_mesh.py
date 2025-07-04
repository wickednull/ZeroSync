#!/usr/bin/env python3
"""
ZeroJam Mesh Engine – BLE Mesh Spammer
Part of the ZeroSync Toolkit
Author: Null_Lyfe
"""

import os
import subprocess
import time
import random
from rich.console import Console
from rich.panel import Panel

console = Console()

alias_list = [
    "💀ZeroSync", "NSA_Van_07", "FREE_WIFI_NOW", "👾BLE_Botnet", "💣ZeroJam_A1",
    "Bluetooth_BOMB", "💀Null_Lyfe", "💜LOVEBOMB", "xXx_Z3R0xXx", "🐉DarkSignal",
    "🚓PoliceDrone", "👽UFO_Probe", "HackTheAir", "🔥InYourWalls", "Virus_BLE"
]

def banner():
    console.print(Panel.fit("[bold magenta]ZeroJam BLE Mesh Spammer[/bold magenta]\n[cyan]Created by Null_Lyfe[/cyan]", border_style="bright_magenta"))

def start_bluetooth():
    subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"])
    subprocess.run(["sudo", "hciconfig", "hci0", "up"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)
    console.print("[green]✔ Bluetooth adapter prepared.[/green]")

def broadcast_loop():
    console.print("[yellow]🛰 Starting BLE mesh storm... Press Ctrl+C to stop[/yellow]")
    try:
        while True:
            name = random.choice(alias_list)
            subprocess.run(["bluetoothctl", "system-alias", name], stdout=subprocess.DEVNULL)
            console.print(f"[magenta]📡 Broadcasting as:[/magenta] [bold cyan]{name}[/bold cyan]")
            time.sleep(1.2)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("\n[red]🛑 Mesh broadcast stopped. Restoring alias.[/red]")

def main():
    banner()
    start_bluetooth()
    broadcast_loop()

if __name__ == "__main__":
    main()