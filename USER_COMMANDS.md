# Ckart CLI - Commands Documentation

## Overview

Ckart CLI is a command-line tool to manage virtual machines (VMs) and their associated resources. Below is a detailed guide to the commands, arguments, and flags available in the CLI.

---

## Commands

### 1. `auth`

Authenticate the CLI session.

**Usage:**

```bash
ckart auth --token <your-token>
```

**Arguments:**

-   `--token` (required): Authentication token.

---

### 2. `vms`

Manage virtual machines.

**Usage:**

```bash
ckart vms [options]
```

**Options:**

-   `-a`, `--all`: Show all VMs.
-   `--create <provider_id>`: Create a new VM with the given Provider ID.
-   `--connect <vm_name>`: Connect to the VM's WireGuard network.
-   `--disconnect <vm_name>`: Disconnect from the VM's WireGuard network.
-   `--start <vm_name>`: Start a VM.
-   `--stop <vm_name>`: Stop a VM.
-   `-rm`, `--remove <vm_name>`: Remove a VM.
-   `-f`, `--force`: Force remove a VM.
-   `-h`, `--help`: Show help for the `vms` command.

---

### 3. `heartbeat`

Check if the management server is online.

**Usage:**

```bash
ckart heartbeat
```

---

### 4. `providers`

Manage providers.

**Usage:**

```bash
ckart providers [options]
```

**Options:**

-   `-a`, `--all`: List all providers.
-   `-d`, `--details <provider_id>`: Show details of a specific provider.
-   `<provider_id> -q`, `--query <vcpus> <ram> <storage>`: Query providers with specific vCPUs, RAM, and storage.

---

### 5. `start` / `stop`

Start or stop a VM.

**Usage:**

```bash
ckart vms --start <vm_name>
ckart vms --stop <vm_name>
```

---

### 6. `remove`

Remove a VM.

**Usage:**

```bash
ckart vms --remove <vm_name> [--force]
```

---

### 7. `connect` / `disconnect`

Connect or disconnect a VM from the WireGuard network.

**Usage:**

```bash
ckart vms --connect <vm_name>
ckart vms --disconnect <vm_name>
```

---

## Notes

-   Ensure the `CKART_SESSION` environment variable is set before using commands (except `auth`).
-   Use `ckart -h` to view all available commands.
