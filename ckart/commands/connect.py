import base64
import ctypes
import os
import subprocess
import time

import nacl.public
import requests
from ckart import output

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
    private_key_b64 = base64.standard_b64encode(private_key_bytes).decode("ascii")
    public_key_b64 = base64.standard_b64encode(public_key_bytes).decode("ascii")

    return private_key_b64, public_key_b64


def create_conf_file(
    private_key,
    address,
    peer_public_key,
    allowed_ips,
    vm_peer_address,
    endpoint,
    config_path,
):
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
    ## create the path if it does not exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w") as f:
        f.write(config_content)


def uninstall_tunnel(config_name):
    try:
        subprocess.run(
            [WIREGUARD_EXE, "/uninstalltunnelservice", config_name], check=True
        )
        output.success(f"Tunnel '{config_name}' stopped and uninstalled.")
    except subprocess.CalledProcessError:
        output.info(f"No existing tunnel service '{config_name}' to uninstall.")


def install_tunnel(config_path, config_name):
    # Step 1: Uninstall if already installed
    uninstall_tunnel(config_name)

    # Step 2: Wait a moment to ensure service is removed
    time.sleep(1)

    # Step 3: Reinstall
    try:
        subprocess.run(
            [WIREGUARD_EXE, "/installtunnelservice", config_path], check=True
        )
        output.success(f"Tunnel '{config_name}' installed and started.")
    except subprocess.CalledProcessError as e:
        output.error(f"Failed to install tunnel: {e}")


def open_powershell_with_ssh(username, wireguard_ip):
    output.info(f"Opening PowerShell with SSH to {username}@{wireguard_ip}")

    wireguard_ip = wireguard_ip.split("/")[0]

    # Use the full path to PowerShell executable
    # powershell_path = r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

    # Open PowerShell in a new window with the SSH command
    subprocess.Popen(
        [
            "start",
            "powershell",
            "-NoExit",
            "-Command",
            f"ssh {username}@{wireguard_ip}",
        ],
        shell=True,
    )


def is_admin():
    """Check if script is running with admin rights."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("CKART_SESSION")

    if args.connect != None:
        url = f"{base_url}/cli/wg/connect"
    else:
        output.error("Please provide a VM ID to connect.")
        return

    # private_key, public_key = generate_wireguard_keys()

    payload = {
        "vm_id": args.connect,
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Authorization": f"BearerCLI {token}"}
        )
        data = response.json()
        # User-friendly error for peer already exists
        if response.status_code != 200 or data.get("error"):
            error_msg = data.get("error", "Unknown error occurred.")
            if "Peer already exists" in error_msg:
                output.warning(
                    "You are already connected to this VM's WireGuard network. To reconnect, disconnect first using 'ckart vms --disconnect <vm_id>'."
                )
            else:
                output.error(f"Failed to connect to VM: {error_msg}")
            return
        wireguard_ip = data.get("vm_peer_address")
        vm_public_key = data.get("interface_public_key")
        allowed_ips = data.get("interface_allowed_ips")
        username = data.get("username", "mega")
        private_key = data.get("client_peer_private_key")
        address = data.get("client_peer_address")
        endpoint = data.get("interface_endpoint")
        vm_peer_address = data.get("vm_peer_address")

        if not vm_public_key:
            output.error(
                "Invalid backend response: missing public key. Please contact support."
            )
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
            output.error(
                "This script requires administrator privileges. Run as admin or open an elevated shell."
            )
            return
        output.info("Running WireGuard tunnel service...")
        install_tunnel(CONFIG_PATH, CONFIG_NAME)
        time.sleep(5)
        open_powershell_with_ssh(username, wireguard_ip)
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to connect to VM: {e}")
