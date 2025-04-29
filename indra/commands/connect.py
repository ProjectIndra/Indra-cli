import os
import subprocess
import requests
import base64
import nacl.public
from dotenv import load_dotenv

load_dotenv()

KEYS_DIR=r"C:\\Program Files\\WireGuard"
LISTEN_PORT=51820
WIREGUARD_EXE = r"C:\\Program Files\\WireGuard\\wireguard.exe"
CONFIG_PATH = r"C:\\Users\\hetar\\Documents\\WireGuard\\new-client.conf"


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
ListenPort = 51820
Address = {address}

[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {allowed_ips}
PersistentKeepalive = 25
"""
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"Configuration file created at {config_path}")

def install_tunnel(config_path):
    subprocess.run([WIREGUARD_EXE, '/installtunnelservice', config_path], check=True)
    print("Tunnel installed and started.")

def uninstall_tunnel(config_name):
    subprocess.run([WIREGUARD_EXE, '/uninstalltunnelservice', config_name], check=True)
    print("Tunnel stopped and uninstalled.")

def get_public_ip():
    """Fetches the system's public IP address."""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"[-] Failed to get public IP: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Exception while getting public IP: {e}")
        return None

def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("INDRA_SESSION")
    url = base_url + "/cli/wg/connect"

    private_key, public_key = generate_wireguard_keys()

    # Fetch public IP automatically
    public_ip = get_public_ip()
    if not public_ip:
        print("[-] Could not determine public IP. Aborting.")
        return

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
    wireguard_ip = data.get('wireguard_ip')
    vm_public_key = data.get('wireguard_public_key')

    if not wireguard_ip or not vm_public_key:
        print("[-] Invalid backend response: Missing IP or public key")
        return

    create_conf_file(
        private_key=private_key,
        address=wireguard_ip,
        peer_public_key=vm_public_key,
        allowed_ips="0.0.0.0/0",
        config_path=CONFIG_PATH
    )

    install_tunnel(CONFIG_PATH)