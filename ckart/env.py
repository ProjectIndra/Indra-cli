import os

from ckart import output


def load_env(env_file=".env"):
    if os.path.exists(env_file):
        with open(
            env_file, "r", encoding="utf-8-sig"
        ) as f:  # utf-8-sig removes BOM if present
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    os.environ[key] = value
                except ValueError:
                    continue
    
    # Fallbacks for variables if not set in .env or system environment
    if not os.getenv("MGMT_SERVER"):
        os.environ["MGMT_SERVER"] = "https://backend.computekart.com"
    
    # Sane defaults for WireGuard paths if not provided
    if not os.getenv("WIREGUARD_EXE"):
        if os.name == 'nt': # Windows
            os.environ["WIREGUARD_EXE"] = r"C:\Program Files\WireGuard\wireguard.exe"
        else: # Linux/Mac
            os.environ["WIREGUARD_EXE"] = "wg"
            
    if not os.getenv("CONFIG_PATH"):
        os.environ["CONFIG_PATH"] = os.path.join(os.path.expanduser("~"), ".ckart-cli", "demo-client.conf")

    if not os.getenv("CONFIG_NAME"):
        os.environ["CONFIG_NAME"] = "demo-client"


def set_persistent_env_var(key, value, env_file=".env"):
    """
    Set or update an environment variable in a project-specific .env file.
    The change does not persist globally but can be sourced manually.
    """
    lines = []
    updated = False

    # Read existing .env file if it exists
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8-sig") as file:
            for line in file:
                if line.strip().startswith(f"{key}="):
                    lines.append(f'{key}="{value}"\n')  # Update existing key
                    updated = True
                else:
                    lines.append(line)

    if not updated:
        lines.append(f'{key}="{value}"\n')  # Add new key if missing

    # Ensure parent directories exist
    parent_dir = os.path.dirname(os.path.abspath(env_file))
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    # Write back to .env file
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Now update the environment variable in the current process
    os.environ[key] = value

    # output.success(f"Successfully set {key} in {env_file}.")
