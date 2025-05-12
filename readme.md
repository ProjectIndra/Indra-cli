# connection pre settings

# change firewall settings to allow wireguard connection

`New-NetFirewallRule -DisplayName "Allow WireGuard" -Direction Inbound -InterfaceAlias "new-client" -Action Allow`

# allow wireguard connection to all interfaces

`netsh advfirewall firewall add rule name="Allow ICMPv4" protocol=icmpv4 dir=in action=allow`

# env

The env must have the following variables set:
`LISTEN_PORT=51820
WIREGUARD_EXE = C:\Program Files\WireGuard\wireguard.exe
CONFIG_PATH = D:\ckart-cli\new-client.conf
CONFIG_NAME = "new-client"`

# Install

pip install git+https://github.com/Projectckart/ckart-cli.git

# Upgrade

pip upgrade git+https://github.com/Projectckart/ckart-cli.git
