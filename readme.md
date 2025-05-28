

# Ckart CLI - Installation Guide

## 🛠️ Requirements

- **Python** 3.7+
- **WireGuard** (Automatically installed by script)
- Administrator privileges to run installation script

## 🔧 Installation (Recommended)

### 1. Download the PowerShell Installer

Download `Install-ckart.ps1` from the [Releases](https://github.com/ProjectIndra/Indra-cli/releases) section of this repository.

### 2. Run in PowerShell (as Administrator)

```powershell
powershell -ExecutionPolicy Bypass -File Install-ckart.ps1
````

This will:

* Install WireGuard (if not present)
* Install the CLI from GitHub
* Set up required environment variables

---

## 🔐 Environment Variables (`.env`)

After installation, a `.env` file will be created. It must contain:

```env
LISTEN_PORT=51820
WIREGUARD_EXE=C:\Program Files\WireGuard\wireguard.exe
CONFIG_PATH=C:\Users\<YourUsername>\Documents\new-client.conf
CONFIG_NAME=new-client
CKART_SESSION=<automatically set on auth>
```

---

## 🔥 Firewall Rules (Optional for Some Systems)

Run the following commands in **PowerShell as Admin** to allow WireGuard traffic:

```powershell
New-NetFirewallRule -DisplayName "Allow WireGuard" -Direction Inbound -InterfaceAlias "new-client" -Action Allow
netsh advfirewall firewall add rule name="Allow ICMPv4" protocol=icmpv4 dir=in action=allow
```

---

## 🧪 Build & Install (For Developers)

### 1. Build from source

From the root of the project (where `pyproject.toml` is located):

```bash
python -m build
```

### 2. Install the wheel

```bash
pip install dist/ckart_cli-0.1-py3-none-any.whl --force-reinstall
```

---

## 📦 Alternative Installation (Offline)

If you have the built distribution files (`.whl` or `.tar.gz`), install using:

```bash
# For .whl
pip install ckart_cli-0.1-py3-none-any.whl

# For .tar.gz
pip install ckart_cli-0.1.tar.gz
```

---

## 🔄 Upgrade CLI

To upgrade the CLI directly from GitHub:

```bash
pip install --upgrade git+https://github.com/ProjectIndra/Indra-cli.git
```

---

## ✅ You're ready!

Run the CLI with:

```bash
ckart
```

Authenticate with your token:

```bash
ckart auth --token <your-token>
```
