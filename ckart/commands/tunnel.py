import json
import os
import subprocess
from typing import Optional
import requests
from ckart import output

BASE_URL = os.getenv("MGMT_SERVER")
TUNNEL_VERSION = "1.0.0"
JAR_NAME = f"ComputeKart-tunnel-client-{TUNNEL_VERSION}.jar"
JAR_URL = f"https://fileshare.computekart.com/{JAR_NAME}"
VERSION_FILE = os.path.expanduser("~/.ckart-cli/tunnel.version")


def _ensure_env_file() -> str:
    env_file_path = os.path.expanduser("~/.ckart-cli/.env")
    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
    if not os.path.exists(env_file_path):
        open(env_file_path, "w").close()
    return env_file_path


def _read_token(
    key="TUNNEL_TOKEN",
):
    env_file_path = _ensure_env_file()
    token = ""
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                tokens = line.strip().split("=")
                token = tokens[1] if tokens[1] else ""
                break
    token = token.strip('"')
    return token


def _set_env_var(key: str, value: str) -> None:
    env_file_path = _ensure_env_file()
    lines = []
    found = False
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                lines.append(f'{key}="{value}"\n')
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f'{key}="{value}"\n')
    with open(env_file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.environ[key] = value


def _download_jar(dest_path: str) -> bool:
    try:
        resp = requests.get(JAR_URL, stream=True, timeout=30)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

        with open(VERSION_FILE, "w") as f:
            f.write(TUNNEL_VERSION)

        return True

    except requests.exceptions.RequestException:
        return False


def _needs_update() -> bool:
    if not os.path.exists(VERSION_FILE):
        return True

    try:
        with open(VERSION_FILE, "r") as f:
            current = f.read().strip()
            return current != TUNNEL_VERSION
    except Exception:
        return True


def _pretty_list_clients(clients_json):
    if not clients_json:
        output.warning("No tunnels found for your account.")
        return
    output.plain("\nYour tunnel clients:")
    headers = ["Tunnel #", "Username", "Tunnel Token"]
    table_data = [
        [c.get("tunnelNo"), c.get("username"), c.get("tunnelToken")]
        for c in clients_json
    ]
    output.table(table_data, headers=headers)
    output.plain()


def _create_tunnel_client(session_token: Optional[str]):
    url = f"{BASE_URL}/ui/createTunnelClient"
    headers = {"Authorization": f"BearerCLI {session_token}"} if session_token else {}
    try:
        resp = requests.post(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        tunnel_url = data.get("tunnel_url")
        session_tok = data.get("session_token")
        if tunnel_url:
            output.success(f"Tunnel created: {tunnel_url}")
            parts = tunnel_url.split(".")[0].split("-")
            if len(parts) >= 2:
                tunnel_no = parts[0]
                username = parts[1]
                _set_env_var("TUNNEL_NO", tunnel_no)
                _set_env_var("TUNNEL_USERNAME", username)
            if session_tok:
                _set_env_var("TUNNEL_TOKEN", session_tok)
            output.info("Saved tunnel details to ~/.ckart-cli/.env")
        else:
            output.error("Unexpected response from server when creating tunnel.")
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to create tunnel client: {e}")


def _get_user_clients(session_token: Optional[str]):
    url = f"{BASE_URL}/ui/getUserClients"
    headers = {"Authorization": f"BearerCLI {session_token}"} if session_token else {}
    try:
        resp = requests.post(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to list tunnels: {e}")
        return None


def _delete_tunnel(session_token: Optional[str], tunnel_id: str):
    url = f"{BASE_URL}/ui/deleteTunnel"
    headers = {"Authorization": f"BearerCLI {session_token}"} if session_token else {}
    payload = {"tunnel_id": tunnel_id}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json() if resp.content else {"message": "Deleted"}
        output.success(data.get("message", "Tunnel deleted successfully"))
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to delete tunnel: {e}")


def _run_jar_connect(dest_path: str, host: str, port: str, token: str):
    if not os.path.isfile(dest_path):
        output.error(
            "Tunnel client not found. Download with 'ckart tunnel --download' or run --connect to fetch automatically."
        )
        return
    cmd = ["java", "-cp", dest_path, "main.Main", token, host, str(object=port)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode != 0:
            output.error(f"Tunnel client exited with error:\n{err or out}")
            return
        # tunnel client finished successfully (no message)
        if out:
            try:
                parsed = json.loads(out)
                output.plain(json.dumps(parsed, indent=2))
            except Exception:
                lines = [line for line in out.splitlines() if line.strip()]
                if lines:
                    output.plain(lines[-1])
        # else:
            # output.info("Tunnel client ran but did not produce console output.")
    except subprocess.TimeoutExpired:
        output.error("Tunnel client timed out.")
    except FileNotFoundError:
        output.error(
            "Java runtime not found. Please install Java and ensure 'java' is on your PATH."
        )
    except Exception as e:
        output.error(f"Failed to run tunnel client: {e}")


def handle(args):
    """Handle tunnel operations:

    Flags supported:
      --list        : list tunnels
      --download    : install the tunnel client
      --connect     : forward the host:port
      --config <t>  : set TUNNEL_TOKEN in .env (replace old)
      --create      : create tunnel client
      --delete <id> : delete tunnel
    """
    if not BASE_URL:
        output.error(
            "MGMT_SERVER is not set. Please set the management server URL in your .env file."
        )
        return

    session_token = os.getenv("CKART_SESSION")
    downloads_dir = os.path.join(os.path.expanduser("~"), ".ckart-cli")
    dest_path = os.path.join(downloads_dir, JAR_NAME)

    # SWITCH-like dispatch
    if getattr(args, "help", False):
        commands = [
            ["ckart tunnel --list"                 , "List all tunnel clients"],
            ["ckart tunnel --download"             , "Download/install the tunnel client jar"],
            ["ckart tunnel --connect"              , "Expose local host and port to public URL"],
            ["ckart tunnel --config <token>"       , "Set tunnel token for auto-configuration"],
            ["ckart tunnel --create"               , "Create a new tunnel client and auto-config it"],
            ["ckart tunnel --delete <tunnel_id>"   , "Delete a tunnel client by ID"],
        ]
        output.plain("\nAvailable 'ckart tunnel' commands:\n")
        output.table(commands, headers=["Command", "Description"])
        return
    if getattr(args, "list", False):
        clients = _get_user_clients(session_token)
        if clients is not None:
            _pretty_list_clients(clients)
        return

    if getattr(args, "download", False):
        if os.path.isfile(dest_path) and not _needs_update():
            output.info(f"Tunnel client already up-to-date: {dest_path}")
            return

        output.info("Updating tunnel client...")
        ok = _download_jar(dest_path)
        if ok:
            output.success(f"Tunnel client downloaded to: {dest_path}")
        else:
            output.error("Failed to download tunnel client. Check network and try again.")
        return

    if getattr(args, "connect", False):
        if not os.path.isfile(dest_path) or _needs_update():
            output.info("Installing / updating tunnel client...")
            if not _download_jar(dest_path):
                output.error("Failed to download tunnel client. Aborting connect.")
                return
        token = _read_token()
        if token == "":
            output.error("Tunnel token is not configured.")
            return
        host = input("Enter host name to expose (e.g. myservice): ").strip()
        port = input("Enter local port to forward (e.g. 8080): ").strip()
        if not host or not port:
            output.error("Host and port are required to connect.")
            return
        output.info(f"Starting tunnel for {host}:{port}...")
        _run_jar_connect(dest_path, host, port, token)
        t_no = os.getenv("TUNNEL_NO")
        t_user = os.getenv("TUNNEL_USERNAME")
        if t_no and t_user:
            url = f"https://{t_no}-{t_user}.computekart.com"
            output.success(f"Public URL: {url}")
        return

    if getattr(args, "config", None):
        token = args.config
        clients = _get_user_clients(session_token)
        if clients is not None:
            valid_tokens = [
                c.get("tunnelToken") for c in clients if c.get("tunnelToken")
            ]
            if token in valid_tokens:
                _set_env_var("TUNNEL_TOKEN", token)
                output.success("Tunnel token saved to ~/.ckart-cli/.env")
            else:
                output.error(
                    "The provided tunnel token does not exist in your account."
                )
        else:
            output.error("No Tunnel clients exist!")
        return

    if getattr(args, "create", False):
        _create_tunnel_client(session_token)
        return

    if getattr(args, "delete", None):
        tid = args.delete
        _delete_tunnel(session_token, tid)
        return

    output.error("No tunnel action provided. Use 'ckart tunnel -h' for usage information.")
