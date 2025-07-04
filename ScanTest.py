#!/usr/bin/env python3

import os
import sys
import time
import threading
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
classic_scanning = False
ble_scanning = False
classic_thread = None
ble_thread = None
scanned_classic = []
scanned_ble = []
log_file = "zerosync_scanlog.txt"

def get_bt_interfaces():
    try:
        output = subprocess.check_output("hciconfig | grep hci", shell=True).decode()
        interfaces = [line.split(":")[0] for line in output.strip().split("\n")]
        return interfaces
    except:
        return []

def scan_classic_bt(interface="hci0"):
    global classic_scanning, scanned_classic
    classic_scanning = True
    scanned_classic.clear()
    console.print(f"[bold yellow]Scanning Classic Bluetooth on {interface}...[/bold yellow]")
    os.system(f"hciconfig {interface} up")
    proc = subprocess.Popen(["hcitool", "-i", interface, "scan"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for line in iter(proc.stdout.readline, b''):
        if not classic_scanning:
            break
        if b"	" in line:
            parts = line.decode().strip().split("\t")
            if len(parts) == 2:
                addr, name = parts
                if addr not in [x[0] for x in scanned_classic]:
                    scanned_classic.append((addr, name))
                    console.print(f"[green][+] {addr} - {name}[/green]")
                    with open(log_file, "a") as log:
                        log.write(f"[Classic] {addr} - {name}\n")
    proc.terminate()

def scan_ble(interface="hci0"):
    global ble_scanning, scanned_ble
    ble_scanning = True
    scanned_ble.clear()
    console.print(f"[bold cyan]Scanning BLE Devices on {interface}...[/bold cyan]")
    os.system(f"hciconfig {interface} up")
    proc = subprocess.Popen(["hcitool", "-i", interface, "lescan"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for line in iter(proc.stdout.readline, b''):
        if not ble_scanning:
            break
        if b" " in line:
            parts = line.decode().strip().split(" ", 1)
            if len(parts) == 2:
                addr, name = parts
                if addr not in [x[0] for x in scanned_ble]:
                    scanned_ble.append((addr, name))
                    console.print(f"[blue][BLE] {addr} - {name}[/blue]")
                    with open(log_file, "a") as log:
                        log.write(f"[BLE] {addr} - {name}\n")
    proc.terminate()

def start_bt_scans():
    global classic_thread, ble_thread, classic_scanning, ble_scanning
    interfaces = get_bt_interfaces()
    if not interfaces:
        console.print("[red]No Bluetooth interfaces detected.[/red]")
        return
    iface = Prompt.ask("[bold cyan]Select Interface[/bold cyan]", choices=interfaces, default=interfaces[0])
    stop_bt_scans()
    classic_thread = threading.Thread(target=scan_classic_bt, args=(iface,), daemon=True)
    ble_thread = threading.Thread(target=scan_ble, args=(iface,), daemon=True)
    classic_thread.start()
    ble_thread.start()
    console.print("[green]Scan started. Use 'Stop Scanning' to cancel.[/green]")

def stop_bt_scans():
    global classic_scanning, ble_scanning
    classic_scanning = False
    ble_scanning = False
    console.print("[bold red]Scan stopped.[/bold red]")

def show_scanned_devices():
    table = Table(title="Discovered Bluetooth Devices")
    table.add_column("Type", style="cyan")
    table.add_column("Address", style="green")
    table.add_column("Name", style="magenta")
    if not scanned_classic and not scanned_ble:
        console.print("[bold red]No devices scanned yet.[/bold red]")
        return
    for addr, name in scanned_classic:
        table.add_row("Classic", addr, name)
    for addr, name in scanned_ble:
        table.add_row("BLE", addr, name)
    console.print(table)

def banner():
    panel = Panel.fit(
        "[bold magenta]ZeroSync v4.8[/bold magenta]\n[green]Bluetooth Scanner: Classic + BLE[/green]\n[yellow]Created by Null_Lyfe[/yellow]",
        title="🧿 ZeroSync",
        border_style="bright_blue"
    )
    console.print(panel)

def main_menu():
    while True:
        banner()
        table = Table(title="Scan Options")
        table.add_column("Option", style="bold green")
        table.add_column("Action", style="bold yellow")
        table.add_row("1", "🔍 Start Scanning (Classic + BLE)")
        table.add_row("2", "🛑 Stop Scanning")
        table.add_row("3", "📜 Show Scanned Devices")
        table.add_row("0", "❌ Exit")
        console.print(table)
        try:
            choice = Prompt.ask("[bold cyan]Select Option[/bold cyan]")
            if choice == "1":
                start_bt_scans()
            elif choice == "2":
                stop_bt_scans()
            elif choice == "3":
                show_scanned_devices()
            elif choice == "0":
                stop_bt_scans()
                console.print("[bold red]Exiting...[/bold red]")
                break
            else:
                console.print("[red]Invalid option[/red]")
        except KeyboardInterrupt:
            stop_bt_scans()
            break

if __name__ == "__main__":
    main_menu()
