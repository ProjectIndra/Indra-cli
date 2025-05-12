import os
import sys
import ctypes
import subprocess
import urllib.request
import time
import psutil
import requests
import base64
import nacl.public
import nacl.encoding
import nacl.signing
from dotenv import load_dotenv

load_dotenv()

KEYS_DIR=r"C:\\Program Files\\WireGuard"
LISTEN_PORT=51820
WIREGUARD_EXE = r"C:\\Program Files\\WireGuard\\wireguard.exe"
CONFIG_PATH = r"C:\\Users\\hetar\\Documents\\WireGuard\\new-client.conf"


def is_admin():
    """Check if script is running with admin rights."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_wireguard_ui():
    """Kill WireGuard UI if it's running."""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'wireguard.exe' in proc.info['name'].lower():
            try:
                print(f"[*] Killing process {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
            except Exception as e:
                print(f"[-] Failed to kill {proc.info['name']}: {e}")

def install_wireguard_if_missing():
    wireguard_path = r"C:\Program Files\WireGuard\wireguard.exe"
    installer_url = "https://download.wireguard.com/windows-client/wireguard-installer.exe"
    installer_path = os.path.join(os.getenv('TEMP'), "wireguard-installer.exe")

    # Check if WireGuard is installed
    if os.path.isfile(wireguard_path):
        print("[+] WireGuard is already installed.")
        return

    print("[*] WireGuard not found. Downloading installer...")

    # Download the installer
    try:
        urllib.request.urlretrieve(installer_url, installer_path)
        print(f"[+] Installer downloaded to: {installer_path}")
    except Exception as e:
        print(f"[-] Failed to download installer: {e}")
        return

    # Run installer silently
    try:
        print("[*] Installing WireGuard silently...")
        subprocess.run([installer_path, "/install", "/quiet"], check=True)
        print("[+] WireGuard installed successfully.")
        
        # Give installer some time to auto-launch WireGuard UI
        time.sleep(3)

        # Kill the UI if it appeared
        kill_wireguard_ui()

    except subprocess.CalledProcessError as e:
        print(f"[-] Installation failed: {e}")
    finally:
        if os.path.exists(installer_path):
            os.remove(installer_path)
            print("[*] Installer cleaned up.")

def handle(args):
	"""Silently install WireGuard and generate keys if not already present.

	Args:
		args (_type_): _description_
	"""
	if not is_admin():
		print("[-] This script requires admin privileges. Please run as admin.")
		return

	# Check if WireGuard is installed, if not, install it
	install_wireguard_if_missing()
	print("[+] WireGuard is installed.")
