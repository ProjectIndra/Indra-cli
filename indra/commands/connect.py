
import subprocess
import sys
import ctypes
import platform
import os

WG_INTERFACE = (
    "wg-client"  # Change this if your WireGuard interface has a different name
)
WG_CONFIG_PATH = f"C:\\Users\\hetar\\Documents\\WireGuard\\{WG_INTERFACE}.conf"  # Default WireGuard config path
KEYS_DIR = "C:\\Users\\hetar\\Documents\\WireGuard\\keys"  # Store keys here
import os


def create_wireguard_config(
    interface_name, private_key, address, listen_port, save_path
):
    """
    Create a basic WireGuard config file with only the interface section.

    Args:
        interface_name (str): Name of the WireGuard interface.
        private_key (str): Private key for the interface.
        address (str): IP address for the interface (e.g., "10.0.0.1/24").
        listen_port (int): WireGuard listening port.
        save_path (str): Full path to save the configuration file.
    """

    wg_config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
ListenPort = {listen_port}
"""

    try:
        os.makedirs(
            os.path.dirname(save_path), exist_ok=True
        )  # Ensure directory exists
        with open(save_path, "w") as config_file:
            config_file.write(wg_config_content)

        print(f"✅ WireGuard config file created at: {save_path}")
    except Exception as e:
        print(f"❌ Error creating WireGuard config file: {e}")


def install_wireguard():
    """Install WireGuard based on OS."""
    os_type = platform.system().lower()

    if "linux" in os_type:
        print("🔹 Installing WireGuard on Linux...")
        subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)
    elif "windows" in os_type:
        try:
            subprocess.run(
                [
                    "winget",
                    "install",
                    "--id",
                    "WireGuard.WireGuard",
                    "-e",
                    "--source",
                    "winget",
                    "--silent",
                ],
                check=True,
                shell=True,
            )
            print("WireGuard installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing WireGuard: {e}")
    else:
        print("Error installing WireGuard: Unsupported OS.")


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


def request_admin():
    """Request administrator privileges via UAC popup on Windows."""
    if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
        print("Requesting Administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        # sys.exit()


def check_wg_installed():
    """Check if WireGuard is installed."""
    try:
        subprocess.run(
            ["wg", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except FileNotFoundError:
        print("WireGuard is not installed. Please install it first.")
        return False


def check_wg_interface(interface):
    """Check if the WireGuard interface exists."""
    try:
        subprocess.run(
            ["wg", "show", interface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def setup_wireguard_interface():
    """Setup WireGuard interface if it doesn't exist."""
    if not check_wg_interface(WG_INTERFACE):
        print(f"🛠 Creating WireGuard interface: {WG_INTERFACE}")

        wg_config_file = WG_CONFIG_PATH
        if not os.path.exists(wg_config_file):
            print(f"WireGuard config file not found: {wg_config_file}")
            print("Make sure to create a WireGuard config file before proceeding.")
            return

        try:
            subprocess.run(["wireguard", "/installtunnelservice", wg_config_file], check=True)
            print(f"WireGuard interface '{WG_INTERFACE}' created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error setting up WireGuard interface: {e}")
    else:
        print(f"WireGuard interface '{WG_INTERFACE}' already exists.")

def setup_temp_wireguard_peer(peer_public_key, allowed_ips):
    """Setup a temporary WireGuard peer."""
    if not peer_public_key or not allowed_ips:
        print("Missing WireGuard peer details.")
        return

    print("🔹 Configuring WireGuard peer...")

    try:
        # Set up WireGuard peer
        subprocess.run(
            [
                "wg",
                "set",
                WG_INTERFACE,
                "peer",
                peer_public_key,
                "allowed-ips",
                allowed_ips,
            ],
            check=True,
        )
        print("WireGuard peer setup complete!")

    except subprocess.CalledProcessError as e:
        print(f"Error setting up WireGuard peer: {e}")


def handle(args):
    request_admin()
    # OR run in admin shell
    # install wireguard if not installed.
    if not check_wg_installed():
        install_wireguard()
    # check if keys exist else generate keys
    pri, pub = generate_wireguard_keys()
    create_wireguard_config(WG_INTERFACE, pri, "10.0.0.0/32", "3000", WG_CONFIG_PATH)
    setup_wireguard_interface()
    peer_public_key, allowed_ips = "cFDZrUpWaKunkwqDnzcQC+p+Tb/H/8KxcvrQnx+CWlQ=", "10.0.0.2/32"
    setup_temp_wireguard_peer(peer_public_key, allowed_ips)
    print("Done")

# # -------------------------------------------------
# import subprocess
# import sys
# import ctypes
# import platform
# import os
# import time

# WG_INTERFACE = "wg-client"  # Change this if your WireGuard interface has a different name
# WG_CONFIG_PATH = f"C:\\Users\\hetar\\Documents\\WireGuard\\{WG_INTERFACE}.conf"  # Adjust this to match the UI config path
# KEYS_DIR = "C:\\Users\\hetar\\Documents\\WireGuard\\keys"  # Store keys here
# WIREGUARD_EXE = "C:\\Program Files\\WireGuard\\wireguard.exe"  # Default WireGuard path on Windows


# def request_admin():
#     """Request administrator privileges via UAC popup on Windows."""
#     if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
#         print("Requesting Administrator privileges...")
#         ctypes.windll.shell32.ShellExecuteW(
#             None, "runas", sys.executable, " ".join(sys.argv), None, 1
#         )
#         sys.exit()


# def check_wg_installed():
#     """Check if WireGuard is installed."""
#     if platform.system().lower() == "windows":
#         return os.path.exists(WIREGUARD_EXE)
#     else:
#         try:
#             subprocess.run(
#                 ["wg", "--version"],
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL,
#                 check=True,
#             )
#             return True
#         except FileNotFoundError:
#             return False


# def install_wireguard():
#     """Install WireGuard based on OS."""
#     os_type = platform.system().lower()

#     if "linux" in os_type:
#         print("🔹 Installing WireGuard on Linux...")
#         subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)
#     elif "windows" in os_type:
#         try:
#             subprocess.run(
#                 [
#                     "winget",
#                     "install",
#                     "--id",
#                     "WireGuard.WireGuard",
#                     "-e",
#                     "--source",
#                     "winget",
#                     "--silent",
#                 ],
#                 check=True,
#                 shell=True,
#             )
#             print("✅ WireGuard installed successfully!")
#         except subprocess.CalledProcessError as e:
#             print(f"❌ Error installing WireGuard: {e}")
#     else:
#         print("❌ Error installing WireGuard: Unsupported OS.")


# def generate_wireguard_keys():
#     """Generate private and public keys for WireGuard."""
#     if not os.path.exists(KEYS_DIR):
#         os.makedirs(KEYS_DIR)

#     private_key_file = os.path.join(KEYS_DIR, "private.key")
#     public_key_file = os.path.join(KEYS_DIR, "public.key")

#     if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
#         print("🔹 Generating WireGuard keys...")
#         private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
#         public_key = (
#             subprocess.check_output(["wg", "pubkey"], input=private_key.encode())
#             .decode()
#             .strip()
#         )

#         with open(private_key_file, "w") as pk:
#             pk.write(private_key)
#         with open(public_key_file, "w") as pub:
#             pub.write(public_key)
#     else:
#         with open(private_key_file, "r") as pk:
#             private_key = pk.read().strip()
#         with open(public_key_file, "r") as pub:
#             public_key = pub.read().strip()

#     return private_key, public_key


# def create_wireguard_config(interface_name, private_key, address, listen_port, save_path):
#     """
#     Create a WireGuard config file.
#     """
#     wg_config_content = f"""[Interface]
# PrivateKey = {private_key}
# Address = {address}
# ListenPort = {listen_port}

# [Peer]
# PublicKey = cFDZrUpWaKunkwqDnzcQC+p+Tb/H/8KxcvrQnx+CWlQ=
# AllowedIPs = 10.0.0.2/32
# """

#     try:
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         with open(save_path, "w") as config_file:
#             config_file.write(wg_config_content)

#         print(f"✅ WireGuard config file created at: {save_path}")
#     except Exception as e:
#         print(f"❌ Error creating WireGuard config file: {e}")


# def restart_wireguard_interface():
#     """Restart WireGuard interface using wireguard.exe (Windows only)."""
#     if platform.system().lower() == "windows":
#         try:
#             # print(f"🔄 Restarting WireGuard interface: {WG_INTERFACE}")
#             # subprocess.run([WIREGUARD_EXE, "/installtunnelservice", WG_INTERFACE], check=True)
#             time.sleep(2)  # Allow time for service to stop
#             subprocess.run([WIREGUARD_EXE, "/installtunnelservice", WG_CONFIG_PATH], check=True)
#             print(f"✅ WireGuard interface '{WG_INTERFACE}' restarted successfully.")
#         except subprocess.CalledProcessError as e:
#             print(f"❌ Error restarting WireGuard: {e}")


# if __name__ == "__main__":
#     request_admin()
    
#     if not check_wg_installed():
#         install_wireguard()
    
#     private_key, public_key = generate_wireguard_keys()
#     create_wireguard_config(WG_INTERFACE, private_key, "10.0.0.1/24", "3000", WG_CONFIG_PATH)
#     restart_wireguard_interface()
    
#     print("✅ WireGuard setup complete!")
