import os
import subprocess
import requests
import base64
import nacl.public
from dotenv import load_dotenv
import time
import socket
import ctypes
import sys
import platform


# load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))

LISTEN_PORT = os.getenv("LISTEN_PORT")
WIREGUARD_EXE = os.getenv("WIREGUARD_EXE")
CONFIG_PATH = os.getenv("CONFIG_PATH")
CONFIG_NAME = os.getenv("CONFIG_NAME")


def generate_wireguard_keys():
    # Generate a new private key (32 random bytes)
    private_key = nacl.public.PrivateKey.generate()

    # Private key bytes
    private_key_bytes = private_key.encode()

    # Corresponding public key
    public_key_bytes = private_key.public_key.encode()

    # Base64 encode like wg expects
    private_key_b64 = base64.standard_b64encode(private_key_bytes).decode('ascii')
    public_key_b64 = base64.standard_b64encode(public_key_bytes).decode('ascii')

    return private_key_b64, public_key_b64


def create_conf_file(private_key, address, peer_public_key, allowed_ips, vm_peer_address, endpoint, config_path):
    config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
ListenPort = {LISTEN_PORT}

[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {allowed_ips},{vm_peer_address}
Endpoint = {endpoint}
PersistentKeepalive = 5
"""
    print(config_path)
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"Configuration file created at {config_path}")


def uninstall_tunnel(config_name):
    if platform.system() == "Windows":
        try:
            subprocess.run([WIREGUARD_EXE, '/uninstalltunnelservice', config_name], check=True)
            print(f"Tunnel '{config_name}' stopped and uninstalled.")
        except subprocess.CalledProcessError:
            print(f"No existing tunnel service '{config_name}' to uninstall.")
    else:
        try:
            subprocess.run(["wg-quick", "down", CONFIG_PATH], check=True)
            print(f"WireGuard interface '{CONFIG_PATH}' brought down.")
        except subprocess.CalledProcessError:
            print("No existing WireGuard interface to bring down.")


def install_tunnel(config_path, config_name):
    uninstall_tunnel(config_name)
    time.sleep(1)
    if platform.system() == "Windows":
        try:
            subprocess.run([WIREGUARD_EXE, '/installtunnelservice', config_path], check=True)
            print(f"Tunnel '{config_name}' installed and started.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install tunnel: {e}")
    else:
        try:
            subprocess.run(["wg-quick", "up", CONFIG_PATH], check=True)
            print(f"WireGuard interface '{CONFIG_PATH}' brought up.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to bring up WireGuard interface: {e}")


def open_shell_with_ssh(username, wireguard_ip):
    print(f"Opening SSH to {username}@{wireguard_ip}")
    
    wireguard_ip = wireguard_ip.split("/")[0]

    if platform.system() == "Windows":
        subprocess.Popen(["start", "powershell", "-NoExit", "-Command", f"ssh {username}@{wireguard_ip}"], shell=True)
    else:
        try:
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ssh {username}@{wireguard_ip}; exec bash"])
        except FileNotFoundError:
            try:
                subprocess.Popen(["x-terminal-emulator", "-e", f"ssh {username}@{wireguard_ip}"])
            except FileNotFoundError:
                print(f"[!] Could not open a new terminal window. Please run: ssh {username}@{wireguard_ip}")


def is_admin():
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except AttributeError:
            return False
    else:
        return os.geteuid() == 0


def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("CKART_SESSION")
    url = base_url + "/cli/wg/connect"

    payload = {
        "vm_name": args.connect,
    }

    try:
        response = requests.post(url, json=payload, headers={"Authorization": f"BearerCLI {token}"})
    except requests.exceptions.RequestException as e:
        print(f"[-] Error connecting to server: {e}")
        return

    data = response.json()
    if data.get("error"):
        print("[-]", data["error"])
        return
    
    wireguard_ip = data.get('vm_peer_address')
    vm_public_key = data.get('interface_public_key')
    allowed_ips = data.get('interface_allowed_ips')
    username = data.get('username','avinash')
    private_key = data.get('client_peer_private_key')
    address = data.get('client_peer_address')
    endpoint = data.get('interface_endpoint')
    vm_peer_address = data.get('vm_peer_address')


    if not vm_public_key:
        print("[-] Invalid backend response: Missing public key")
        return

    create_conf_file(
        private_key=private_key,
        address=address,
        peer_public_key=vm_public_key,
        allowed_ips=allowed_ips,
        vm_peer_address=vm_peer_address,
        endpoint=endpoint,
        config_path=CONFIG_PATH,
    )

    if not is_admin():
        if platform.system() == "Windows":
            print("[-] This script requires admin privileges. Please run as administrator or open a new admin shell.")
        else:
            print("[-] This script requires root privileges. Please run with sudo.")
        return
    print("[+] Running WireGuard tunnel service...")
    install_tunnel(CONFIG_PATH, CONFIG_NAME)

    time.sleep(5)

    open_shell_with_ssh(username, wireguard_ip)

