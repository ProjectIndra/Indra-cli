import os
import sys
import ctypes
import subprocess
import urllib.request
import time
import psutil
import requests
from dotenv import load_dotenv

load_dotenv()

KEYS_DIR=r"C:\\Program Files\\WireGuard"
# Path to wireguard.exe
WIREGUARD_EXE = r"C:\\Program Files\\WireGuard\\wireguard.exe"
# Path where you want to save the WireGuard config
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

def generate_wireguard_keys():
    """Generate private and public keys for WireGuard."""
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

    private_key_file = os.path.join(KEYS_DIR, "private.key")
    public_key_file = os.path.join(KEYS_DIR, "public.key")

    if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
        print("🔹 Generating WireGuard keys...")
        private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
        public_key = (
            subprocess.check_output(["echo", private_key, "|", "wg", "pubkey"])
            .decode()
            .strip()
        )

        with open(private_key_file, "w") as pk:
            pk.write(private_key)
        with open(public_key_file, "w") as pub:
            pub.write(public_key)
    else:
        with open(private_key_file, "r") as pk:
            private_key = pk.read().strip()
        with open(public_key_file, "r") as pub:
            public_key = pub.read().strip()

    return private_key, public_key


def setup_wireguard_tunnel(
    tunnel_name,
    private_key,
    address,
    dns,
    peer_public_key,
    allowed_ips,
    endpoint,
    persistent_keepalive=25
):
    """
    Creates and installs a WireGuard tunnel on Windows using Python.

    Args:
        tunnel_name (str): Name for the WireGuard tunnel.
        private_key (str): Private key for the local WireGuard interface.
        address (str): IP address for the WireGuard interface (e.g., "10.0.0.2/24").
        dns (str): DNS server(s) to use (e.g., "1.1.1.1").
        peer_public_key (str): Public key of the WireGuard server peer.
        allowed_ips (str): Allowed IPs for the tunnel (e.g., "0.0.0.0/0").
        endpoint (str): Endpoint address (e.g., "vpn.example.com:51820").
        persistent_keepalive (int): Optional PersistentKeepalive interval.

    Returns:
        None
    """

    config_dir = r"C:\\Program Files\\WireGuard"
    config_path = os.path.join(config_dir, f"{tunnel_name}.conf")

    config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = {dns}

[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {allowed_ips}
Endpoint = {endpoint}
PersistentKeepalive = {persistent_keepalive}
"""

    # Ensure the Configurations folder exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Save the configuration file
    try:
        with open(config_path, "w", encoding="ascii") as f:
            f.write(config_content)
        print(f"[+] WireGuard configuration saved at {config_path}")
    except Exception as e:
        print(f"[-] Failed to write configuration: {e}")
        return

    # Install the tunnel as a service
    try:
        subprocess.run(
            [
                r"C:\\Program Files\\WireGuard\\wireguard.exe",
                "/installtunnelservice",
                f"{tunnel_name}.conf"
            ],
            check=True
        )
        print(f"[+] Tunnel '{tunnel_name}' installed as a service.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to install tunnel service: {e}")
        return

    # Start the tunnel service
    # try:
    #     subprocess.run(
    #         ["sc", "start", f"WireGuardTunnel${tunnel_name}"],
    #         check=True
    #     )
    #     print(f"[+] Tunnel '{tunnel_name}' service started.")
    # except subprocess.CalledProcessError as e:
    #     print(f"[-] Failed to start tunnel service: {e}")
    #     return

    # Optional: Show tunnel status
    # try:
    #     output = subprocess.check_output(["wg", "show"], text=True)
    #     print("[+] Current WireGuard status:")
    #     print(output)
    # except subprocess.CalledProcessError:
    #     print("[-] Could not retrieve WireGuard status.")

def is_service_running(service_name):
    """Check if a Windows service is already running."""
    try:
        output = subprocess.check_output(["sc", "query", service_name], text=True)
        if "RUNNING" in output:
            return True
        else:
            return False
    except Exception:
        return False
    
def service_exists(service_name):
    """Return True if a Windows service exists."""
    try:
        output = subprocess.check_output(["sc", "query", service_name], text=True)
        if "SERVICE_NAME" in output:
            return True
    except subprocess.CalledProcessError:
        return False
    return False



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

    client_endpoint = f"{public_ip}:51820"   # Assuming you listen on 51820

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
    vm_endpoint = data.get('vm_endpoint')   # Optional: if you get endpoint from backend

    if not wireguard_ip or not vm_public_key:
        print("[-] Invalid backend response: Missing IP or public key")
        return

    # Save the conf
    tunnel_name = "client"
    config_dir = r"C:\\Program Files\\WireGuard"
    # config_path = os.path.join(config_dir, f"{tunnel_name}.conf")
    config_path=CONFIG_PATH

    create_conf_file(
        private_key=private_key,
        address=wireguard_ip,
        peer_public_key=vm_public_key,
        allowed_ips="0.0.0.0/0",
        config_path=config_path
    )

    install_tunnel(config_path)
