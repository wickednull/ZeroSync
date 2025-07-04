
#!/usr/bin/env python3
import os
import subprocess
import threading
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()
scanned_devices = []
scan_thread = None
stop_flag = False

def scan_classic_bt():
    global scanned_devices
    console.print("[bold cyan]Scanning Classic Bluetooth...[/bold cyan]")
    try:
        out = subprocess.check_output("bluetoothctl devices", shell=True).decode()
        lines = out.strip().split("\n")
        for line in lines:
            if line:
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3:
                    addr, name = parts[1], parts[2]
                    scanned_devices.append((addr, name, "Classic"))
    except Exception as e:
        console.print(f"[red]Error scanning Classic BT: {e}[/red]")

def scan_ble_bettercap():
    global scanned_devices
    console.print("[bold magenta]Scanning BLE with Bettercap (10 seconds)...[/bold magenta]")
    try:
        result = subprocess.check_output("bettercap -eval 'ble.recon on; sleep 10; ble.show; ble.recon off'", shell=True, stderr=subprocess.DEVNULL).decode()
        for line in result.splitlines():
            if "[ble.device]" in line:
                parts = line.split()
                addr = parts[2]
                name = parts[-1] if len(parts) >= 4 else "Unknown"
                scanned_devices.append((addr, name, "BLE"))
    except Exception as e:
        console.print(f"[red]Error running Bettercap BLE scan: {e}[/red]")

def run_scan():
    global stop_flag, scanned_devices
    stop_flag = False
    scanned_devices.clear()
    scan_classic_bt()
    scan_ble_bettercap()
    console.print("[green]Scan complete![/green]")

def main_menu():
    while True:
        console.print(Panel.fit("[bold cyan]ZeroSync v4.9[/bold cyan]\n[green]Bluetooth Scanner: Classic + BLE[/green]\n[yellow]Created by Null_Lyfe[/yellow]", title="ZeroSync", subtitle="Scan Engine"))
        table = Table(title="Scan Options")
        table.add_column("Option", style="cyan", justify="center")
        table.add_column("Action", style="yellow")

        table.add_row("1", "🔍 Start Scanning (Classic + BLE)")
        table.add_row("2", "📋 Show Scanned Devices")
        table.add_row("0", "❌ Exit")

        console.print(table)

        choice = Prompt.ask("[blue]Select Option[/blue]", choices=["0", "1", "2"])
        if choice == "1":
            run_scan()
        elif choice == "2":
            if not scanned_devices:
                console.print("[red]No devices scanned yet.[/red]")
            else:
                dev_table = Table(title="Scanned Devices")
                dev_table.add_column("Address", style="green")
                dev_table.add_column("Name")
                dev_table.add_column("Type")
                for addr, name, dtype in scanned_devices:
                    dev_table.add_row(addr, name, dtype)
                console.print(dev_table)
        elif choice == "0":
            break

if __name__ == "__main__":
    os.system("clear")
    main_menu()
