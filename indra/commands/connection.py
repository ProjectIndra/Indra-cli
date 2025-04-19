import os
import sys
import ctypes
import platform
# from wireguard import WireGuard
from pyroute2 import IPRoute
# from python_wireguard import Client, ServerConnection, Key, Interface

# Configuration
WG_INTERFACE = "wg-client"
WG_CONFIG_PATH = f"C:\\Users\\hetar\\Documents\\WireGuard\\{WG_INTERFACE}.conf"
KEYS_DIR = "C:\\Users\\hetar\\Documents\\WireGuard\\keys"

def request_admin():
    """Request administrator privileges via UAC popup on Windows."""
    if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
        print("⚠️ Requesting Administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def generate_wireguard_keys():
    """Generate private and public keys using python-wireguard."""
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

    private_key_file = os.path.join(KEYS_DIR, "private.key")
    public_key_file = os.path.join(KEYS_DIR, "public.key")

    if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
        print("🔹 Generating WireGuard keys using python-wireguard...")
        private_key = Key.generate_private()
        public_key = private_key.public_key()

        with open(private_key_file, "w") as pk:
            pk.write(str(private_key))
        with open(public_key_file, "w") as pub:
            pub.write(str(public_key))

    else:
        with open(private_key_file, "r") as pk:
            private_key = Key(pk.read().strip())
        with open(public_key_file, "r") as pub:
            public_key = Key(pub.read().strip())

    return private_key, public_key

def create_wireguard_config(interface_name, private_key, address, listen_port, save_path):
    """
    Create a basic WireGuard config file using python-wireguard.
    """
    wg = WireGuard(interface_name)
    wg.set_interface(Interface(private_key=str(private_key), addresses=[address], listen_port=int(listen_port)))

    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Ensure directory exists
        with open(save_path, "w") as config_file:
            config_file.write(str(wg))
        
        print(f"✅ WireGuard config file created at: {save_path}")
    except Exception as e:
        print(f"❌ Error creating WireGuard config file: {e}")

def check_wg_installed():
    """Check if WireGuard is installed."""
    try:
        WireGuard.list_interfaces()
        return True
    except Exception:
        print("WireGuard is not installed or not running. Please install it first.")
        return False

def check_wg_interface(interface):
    """Check if the WireGuard interface exists."""
    return interface in WireGuard.list_interfaces()

def setup_wireguard_interface():
    """Setup WireGuard interface if it doesn't exist."""
    if not check_wg_interface(WG_INTERFACE):
        print(f"🛠 Creating WireGuard interface: {WG_INTERFACE}")

        private_key, _ = generate_wireguard_keys()
        create_wireguard_config(WG_INTERFACE, private_key, "10.0.0.1/24", "3000", WG_CONFIG_PATH)

        try:
            wg = WireGuard(WG_INTERFACE)
            wg.apply()
            print(f"✅ WireGuard interface '{WG_INTERFACE}' created successfully.")
        except Exception as e:
            print(f"❌ Error setting up WireGuard interface: {e}")
    else:
        print(f"✅ WireGuard interface '{WG_INTERFACE}' already exists.")

def setup_temp_wireguard_peer(peer_public_key, allowed_ips):
    """Setup a temporary WireGuard peer."""
    if not peer_public_key or not allowed_ips:
        print("❌ Missing WireGuard peer details.")
        return

    print("🔹 Configuring WireGuard peer...")
    
    try:
        wg = WireGuard(WG_INTERFACE)
        peer = Interface(public_key=str(peer_public_key), allowed_ips=[allowed_ips])
        wg.set_peer(peer)
        wg.apply()

        print("✅ WireGuard peer setup complete!")
    
    except Exception as e:
        print(f"❌ Error setting up WireGuard peer: {e}")

if __name__ == "__main__":
    request_admin()
    
    if check_wg_installed():
        pri, pub = generate_wireguard_keys()
        create_wireguard_config(WG_INTERFACE, pri, "10.0.0.1/24", "3000", WG_CONFIG_PATH)
        setup_wireguard_interface()
        print("✅ Done")
