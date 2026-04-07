#!/bin/bash
# Install-ckart.sh
set -e

# Get the real user and their home directory
REAL_USER=${SUDO_USER:-$USER}
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)

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
        sudo apt-get update && sudo apt-get install -y python3-pip
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
        sudo apt-get update && sudo apt-get install -y wireguard
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y epel-release && sudo yum install -y wireguard-tools
    else
        echo "[-] Please install WireGuard manually for your distribution."
        exit 1
    fi
}

# Function to install ckart CLI
function install_ckart_cli() {
    local repo_url="git+https://github.com/ProjectIndra/Indra-cli.git"
    local venv_dir="/opt/ckart-cli"
    
    # If run from within the repo, install local version for testing
    if [ -f "pyproject.toml" ]; then
        repo_url="."
        echo "[*] Found local pyproject.toml, installing local version..."
    fi

    echo "[*] Installing ckart CLI from $repo_url into a virtual environment..."
    
    # Ensure the venv exists and is owned by the real user for easier updates
    if [ ! -d "$venv_dir" ]; then
        sudo mkdir -p "$venv_dir"
        sudo chown "$REAL_USER":"$REAL_USER" "$venv_dir"
        python3 -m venv "$venv_dir" || {
            echo "[-] Failed to create venv. You may need to run: sudo apt install python3-venv"
            exit 1
        }
    fi
    
    # Ensure user has permissions if it already existed
    sudo chown -R "$REAL_USER":"$REAL_USER" "$venv_dir"
    
    "$venv_dir/bin/python3" -m pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        "$venv_dir/bin/python3" -m pip install -r requirements.txt
    fi
    "$venv_dir/bin/python3" -m pip install --upgrade --force-reinstall "$repo_url"
    
    # Make the CLI globally available
    sudo ln -sf "$venv_dir/bin/ckart" /usr/local/bin/ckart
}

# Function to write .env file
function write_env_file() {
    local env_dir="$REAL_HOME/.ckart-cli"
    local env_file="$env_dir/.env"
    
    # Create directory as user
    if [ "$REAL_USER" != "$(whoami)" ]; then
        sudo -u "$REAL_USER" mkdir -p "$env_dir"
    else
        mkdir -p "$env_dir"
    fi

    local config_path="$REAL_HOME/.ckart-cli/wg-demo-client.conf"
    
    local tmp_env=$(mktemp)
    cat > "$tmp_env" <<EOF
MGMT_SERVER="https://backend.computekart.com"
LISTEN_PORT=51820
WIREGUARD_EXE="$(command -v wg)"
CONFIG_PATH="$config_path"
CONFIG_NAME="demo-client"
EOF
    
    if [ "$REAL_USER" != "$(whoami)" ]; then
        sudo mv "$tmp_env" "$env_file"
        sudo chown "$REAL_USER":"$REAL_USER" "$env_file"
    else
        mv "$tmp_env" "$env_file"
    fi
    
    echo "[+] Environment variables written to $env_file"
}

# Main
# check_root "$@"
check_python
# install_pip
install_wireguard
install_ckart_cli
write_env_file

echo "[>] Setup complete. You can now run: ckart"
