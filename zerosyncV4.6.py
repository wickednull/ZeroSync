#!/usr/bin/env python3

import os
import sys
import time
import threading
import subprocess
from bluetooth import discover_devices, BluetoothError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
scanned = []
scanning = False
scan_thread = None
log_file = "zerosync_scanlog.txt"

def scan_devices():
    global scanned, scanning
    scanning = True
    scanned.clear()
    console.print("[bold yellow]Scanning for Bluetooth devices... (Use Stop to cancel)[/bold yellow]")
    while scanning:
        try:
            nearby_devices = discover_devices(duration=8, lookup_names=True)
            for addr, name in nearby_devices:
                if addr not in [x[0] for x in scanned]:
                    scanned.append((addr, name))
                    console.print(f"[green][+] {addr} - {name}[/green]")
                    with open(log_file, "a") as log:
                        log.write(f"{addr} - {name}\n")
            time.sleep(3)
        except BluetoothError as e:
            console.print(f"[red]Bluetooth Error:[/red] {e}")
            break
        except Exception as ex:
            console.print(f"[red]Unknown Scan Error:[/red] {ex}")
            break

def start_scan_thread():
    global scan_thread, scanning
    if not scanning:
        scan_thread = threading.Thread(target=scan_devices, daemon=True)
        scan_thread.start()
    else:
        console.print("[yellow]Scan already in progress.[/yellow]")

def stop_scan():
    global scanning
    if scanning:
        scanning = False
        console.print("[bold red]Scanning stopped.[/bold red]")
    else:
        console.print("[cyan]No scan running.[/cyan]")

def show_scanned_devices():
    if not scanned:
        console.print("[bold red]No devices found.[/bold red]")
        return
    table = Table(title="Scanned Devices")
    table.add_column("Address", style="cyan")
    table.add_column("Name", style="magenta")
    for addr, name in scanned:
        table.add_row(addr, name)
    console.print(table)

def banner():
    panel = Panel.fit(
        "[bold magenta]ZeroSync v4.6[/bold magenta]\n[green]Bluetooth Attack Toolkit[/green]\n[yellow]Created by Null_Lyfe[/yellow]",
        title="🧿 ZeroSync",
        border_style="bright_blue"
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
        table.add_row("4", "❌ Exit")
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
                stop_scan()
                console.print("[bold red]Exiting...[/bold red]")
                break
            else:
                console.print("[red]Invalid choice[/red]")
        except KeyboardInterrupt:
            stop_scan()
            break

if __name__ == "__main__":
    main_menu()
