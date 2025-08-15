#!/bin/bash
# Install-ckart.sh
set -e

# Function to check if running as root
function check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "[*] Relaunching script as root..."
        exec sudo bash "$0" "$@"
        exit 1
    fi
}

# Function to check if python3 is installed
function check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "[-] Python3 is not installed. Please install Python 3.7+ and try again."
        exit 1
    fi
}

# Function to install pip if not present
function install_pip() {
    if ! command -v pip3 &> /dev/null; then
        echo "[*] Installing pip3..."
        apt-get update && apt-get install -y python3-pip
    fi
}

# Function to install WireGuard
function install_wireguard() {
    if command -v wg &> /dev/null; then
        echo "[+] WireGuard is already installed."
        return
    fi
    echo "[*] Installing WireGuard..."
    if [ -f /etc/debian_version ]; then
        apt-get update && apt-get install -y wireguard
    elif [ -f /etc/redhat-release ]; then
        yum install -y epel-release && yum install -y wireguard-tools
    else
        echo "[-] Please install WireGuard manually for your distribution."
        exit 1
    fi
}

# Function to install ckart CLI
function install_ckart_cli() {
    local repo_url="git+https://github.com/ProjectIndra/Indra-cli.git"
    echo "[*] Installing ckart CLI from GitHub..."
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade --force-reinstall "$repo_url"
}

# Function to write .env file
function write_env_file() {
    local env_dir="$HOME/.ckart-cli"
    local env_file="$env_dir/.env"
    mkdir -p "$env_dir"
    local config_path="$HOME/wg-demo-client.conf"
    cat > "$env_file" <<EOF
MGMT_SERVER="https://backend.computekart.com"
LISTEN_PORT=51820
WIREGUARD_EXE="$(command -v wg)"
CONFIG_PATH="$config_path"
CONFIG_NAME="demo-client"
EOF
    echo "[+] Environment variables written to $env_file"
}

# Main
check_root "$@"
check_python
# install_pip
install_wireguard
install_ckart_cli
write_env_file

echo "[>] Setup complete. You can now run: ckart"
