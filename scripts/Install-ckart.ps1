# Install-ckart.ps1
$ErrorActionPreference = "Stop"

function Test-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Host "[*] Relaunching script as administrator..."
        Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
        exit
    }
}

function Test-Python {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python is not installed or not added to PATH. Please install Python 3.7+ and try again."
        exit 1
    }
}

function Install-ckartCLI {
    $repoUrl = "git+https://github.com/ProjectIndra/Indra-cli.git"
    Write-Host "[*] Installing ckart CLI from GitHub..."
    python -m pip install --upgrade pip
    python -m pip install $repoUrl
}

function Install-WireGuard {
    $wgPath = "C:\Program Files\WireGuard\wireguard.exe"
    if (Test-Path $wgPath) {
        Write-Host "[+] WireGuard is already installed."
        return
    }

    $installerUrl = "https://download.wireguard.com/windows-client/wireguard-installer.exe"
    $tempInstaller = "$env:TEMP\wireguard-installer.exe"

    Write-Host "[*] Downloading WireGuard installer..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $tempInstaller

    Write-Host "[*] Installing WireGuard silently..."
    Start-Process -FilePath $tempInstaller -ArgumentList "/install", "/quiet" -Wait

    if (Test-Path $wgPath) {
        Write-Host "[+] WireGuard installed successfully."
    } else {
        Write-Error "[-] WireGuard installation failed."
    }

    # Cleanup installer
    Remove-Item $tempInstaller -Force -ErrorAction SilentlyContinue
}

# ---------------- MAIN ----------------

Test-Admin
Test-Python
Install-WireGuard
Install-ckartCLI

Write-Host "[>] Setup complete. You can now run: ckart"
