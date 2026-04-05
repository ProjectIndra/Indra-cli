# Ckart CLI - Installation Guide

## 🛠️ System Requirements

-   **Operating System**: Windows, Linux, or macOS
-   **Python Version**: 3.7+
-   **WireGuard**: Installed automatically by the script
-   **Administrator Privileges**: Required for installation

---

## 🔧 Installation Steps

### 1. Download the Installer

-   For Windows: Download `Install-ckart.ps1` from the [Releases](https://github.com/ProjectIndra/Indra-cli/releases).
-   For Linux/Mac: Download `Install-ckart.sh` from the same location.

### 2. Run the Installer

#### Windows

Run the following command in PowerShell (as Administrator):

```powershell
powershell -ExecutionPolicy Bypass -File Install-ckart.ps1
```

#### Linux/Mac

Run the following command in the terminal:

```bash
bash Install-ckart.sh
```

This will:

-   Install WireGuard (if not already installed).
-   Install the CLI from GitHub.
-   Set up required environment variables.

---

## 🔐 Environment Variables

After installation, a `.env` file will be created. It must contain:

```env
LISTEN_PORT=51820
WIREGUARD_EXE=C:\Program Files\WireGuard\wireguard.exe
CONFIG_PATH=C:\Users\<YourUsername>\Documents\new-client.conf
CONFIG_NAME=new-client
CKART_SESSION=<automatically set on auth>
```

---

## 🔄 Upgrade CLI

To upgrade the CLI directly from GitHub:

```bash
pip install --upgrade git+https://github.com/ProjectIndra/Indra-cli.git
```

---

## 🧪 Developer Installation

### 1. Build from Source

From the root of the project (where `pyproject.toml` is located):

```bash
python -m build
```

### 2. Install the Wheel

```bash
pip install dist/ckart_cli-0.1-py3-none-any.whl --force-reinstall
```

---

## ✅ You're Ready!

Run the CLI with:

```bash
ckart
```

Authenticate with your token:

```bash
ckart auth --token <your-token>
```
