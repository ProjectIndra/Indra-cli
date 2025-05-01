import os
import subprocess
import requests
import base64
import nacl.public
from dotenv import load_dotenv
import time
import socket

load_dotenv()

LISTEN_PORT=os.getenv("LISTEN_PORT")
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

def create_conf_file(private_key, address, peer_public_key, allowed_ips, config_path):
    config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
ListenPort = {LISTEN_PORT}

[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {allowed_ips}
PersistentKeepalive = 5
"""
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"Configuration file created at {config_path}")

def uninstall_tunnel(config_name):
    try:
        subprocess.run([WIREGUARD_EXE, '/uninstalltunnelservice', config_name], check=True)
        print(f"Tunnel '{config_name}' stopped and uninstalled.")
    except subprocess.CalledProcessError:
        print(f"No existing tunnel service '{config_name}' to uninstall.")

def install_tunnel(config_path, config_name):
    # Step 1: Uninstall if already installed
    uninstall_tunnel(config_name)

    # Step 2: Wait a moment to ensure service is removed
    time.sleep(1)

    # Step 3: Reinstall
    try:
        subprocess.run([WIREGUARD_EXE, '/installtunnelservice', config_path], check=True)
        print(f"Tunnel '{config_name}' installed and started.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install tunnel: {e}")

def get_ipv4_address():
    try:
        # This connects to an external host to find your primary local IPv4 address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's DNS, used only to determine route
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error: {e}")
        return None

def open_powershell_with_ssh(username, wireguard_ip):
    print(f"Opening PowerShell with SSH to {username}@{wireguard_ip}")
    
    wireguard_ip = wireguard_ip.split("/")[0]

    # Use the full path to PowerShell executable
    powershell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

    # Open PowerShell in a new window with the SSH command
    subprocess.Popen(["start", "powershell", "-NoExit", "-Command", f"ssh {username}@{wireguard_ip}"], shell=True)

def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("INDRA_SESSION")
    url = base_url + "/cli/wg/connect"

    private_key, public_key = generate_wireguard_keys()

    # Fetch public IP automatically
    public_ip = get_ipv4_address()
    if not public_ip:
        print("[-] Could not determine public IP. Aborting.")
        return

    # public_ip = "192.168.83.95"

    client_endpoint = f"{public_ip}:{LISTEN_PORT}"

    payload = {
        "vm_name": args.connect,
        "client_public_key": public_key,
        "client_endpoint": client_endpoint
    }

    response = requests.post(url, json=payload , headers={"Authorization": f"BearerCLI {token}"})

    if response.status_code != 200:
        print(f"[-] Error: {response.status_code} {response.text}")
        return

    data = response.json()
    print(data)
    wireguard_ip = data.get('wiregaurd_ip')
    vm_public_key = data.get('public_key')
    allowed_ips = data.get('allowed_ips')
    status = data.get('status')
    msg = data.get('messsage')
    username = data.get('username')
    password = data.get('password')

    if not wireguard_ip or not vm_public_key:
        print("[-] Invalid backend response: Missing IP or public key")
        return

    create_conf_file(
        private_key=private_key,
        address="10.0.0.1/32",
        peer_public_key=vm_public_key,
        allowed_ips=wireguard_ip,
        config_path=CONFIG_PATH,
    )

    install_tunnel(CONFIG_PATH,CONFIG_NAME)

    time.sleep(5)

    open_powershell_with_ssh(username,wireguard_ip)