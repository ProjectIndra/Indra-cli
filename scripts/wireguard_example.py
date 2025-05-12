import subprocess

# Path to wireguard.exe - adjust if needed
WIREGUARD_EXE = r"C:\\Program Files\\WireGuard\\wireguard.exe"

# Path to your WireGuard config file
# CONFIG_PATH = r"C:\Users\DELL\Downloads\wg-client.conf"
CONFIG_PATH = r"C:\\ckart-cli\\new-client.conf"

def install_tunnel(config_path):
    subprocess.run([WIREGUARD_EXE, '/installtunnelservice', config_path], check=True)
    print("Tunnel installed and started.")

def uninstall_tunnel(config_name):
    subprocess.run([WIREGUARD_EXE, '/uninstalltunnelservice', config_name], check=True)
    print("Tunnel stopped and uninstalled.")

# Example usage
install_tunnel(CONFIG_PATH)

# To uninstall later:
# uninstall_tunnel("wg0")