![image](https://github.com/user-attachments/assets/a0b8af4a-1b65-43e3-8fdd-464b6c1484f1)

# ZeroSync – Bluetooth Attack Toolkit

**Author:** Null_Lyfe  
**Version:** 7.9  
**License:** For educational use only.

---

## 📡 Overview

**ZeroSync** is a comprehensive Bluetooth attack toolkit that supports both **CLI (Command Line Interface)** and **GUI (Graphical User Interface)** modes. Designed for security researchers and Bluetooth enthusiasts, it enables advanced BLE attacks, device spoofing, mesh flooding, CVE exploitation, and persistent device tracking.

---

## 🖥️ Features

- 🔍 BLE Scanning with RSSI
- 🎭 MAC Spoofing
- 📡 Broadcast Alias Loop
- ✂️ Deauthentication (BLE)
- 💌 Notification Replay Attacks
- 💣 BLE Device Crasher
- 💥 CVE-2017-0785 Exploit
- 🌐 BLE Mesh Flooding (ZeroJam)
- 💉 Bettercap BLE Recon Bridge
- 📁 Session Log Export
- 🧪 Real-time GUI Console
- 🖱️ GUI Mode or CLI Mode (user choice)

---

## ⚙️ Requirements

### ✅ Python

- Python 3.8+

### ✅ Python Modules

```bash
pip3 install bluepy rich
```
Tkinter is required for the GUI version and is included by default in most Python installations.

✅ System Dependencies
```bash
sudo apt update
sudo apt install -y bluetooth bluez rfkill l2ping rfcomm sdptool bettercap xterm
```
📦 Installation

```bash
git clone https://github.com/wickednull/ZeroSync.git
cd ZeroSync
pip3 install bluepy rich --break-system-packages #If Needed.
```

⸻

🚀 Usage
🔹 CLI Mode
```bash
sudo python3 zerosync.py
```
🔹 GUI Mode
```bash
sudo python3 zerosync_gui.py
```
Root privileges (sudo) are required for Bluetooth scanning and system-level operations.


🗂️ File Structure

```bash
zerosync/
├── zerosync.py           # CLI version
├── zerosync_gui.py       # GUI version with terminal
├── zerojam_mesh.py       # BLE mesh flood module
├── zerosync_logs/        # Directory for exported session logs
```

📁 Logs
Exported session logs are saved in:
```bash
zerosync_logs/session_<timestamp>.log
```
Each log includes MAC addresses, first seen times, and max RSSI.

⚠️ Legal Disclaimer

This tool is intended for educational and authorized testing purposes only.
Do not use ZeroSync on networks, systems, or devices you do not own or have explicit permission to test.
The author assumes no liability for any damage caused by misuse.

⸻

👨‍💻 Author

Null_Lyfe
Developed with the goal of pushing Bluetooth reconnaissance and research tools to the next level.

🙏 Credits & Special Thanks
	•	💜 Special thanks to ekomsSavior, the original creator of SpamJam, whose work inspired multiple core features and concepts now integrated into ZeroSync. Your creative BLE tooling helped shape the modern direction of Bluetooth offensive research.
	•	🧠 Additional thanks to the open-source security and Bluetooth hacking community for continuous inspiration.


⸻

💬 Feedback & Contributions

Feel free to fork, improve, and submit issues or pull requests!




