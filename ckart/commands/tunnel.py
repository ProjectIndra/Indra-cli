import json
import os
import subprocess
from typing import Optional

import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))
BASE_URL = os.getenv("MGMT_SERVER")


def _ensure_env_file() -> str:
    env_file_path = os.path.expanduser("~/.ckart-cli/.env")
    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
    if not os.path.exists(env_file_path):
        open(env_file_path, "w").close()
    return env_file_path


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
    jar_url = "https://fileshare.computekart.com/ComputeKart-tunnel-client-1.0.0.jar"
    try:
        resp = requests.get(jar_url, stream=True, timeout=30)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        return True
    except requests.exceptions.RequestException:
        return False


def _pretty_list_clients(clients_json):
    if not clients_json:
        print("[!] No tunnels found for your account.")
        return
    print("\nYour tunnel clients:")
    headers = ["Tunnel ID", "Username", "Tunnel Token"]
    table_data = [
        [c.get("tunnelNo"), c.get("username"), c.get("tunnelToken")]
        for c in clients_json
    ]
    print(tabulate(table_data, headers=headers))
    print()


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
            print(f"[+] Tunnel created: {tunnel_url}")
            parts = tunnel_url.split(".")[0].split("-")
            if len(parts) >= 2:
                tunnel_no = parts[0]
                username = parts[1]
                _set_env_var("TUNNEL_NO", tunnel_no)
                _set_env_var("TUNNEL_USERNAME", username)
            if session_tok:
                _set_env_var("TUNNEL_TOKEN", session_tok)
            print("[i] Saved tunnel details to ~/.ckart-cli/.env")
        else:
            print("[-] Unexpected response from server when creating tunnel.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to create tunnel client: {e}")


def _get_user_clients(session_token: Optional[str]):
    url = f"{BASE_URL}/ui/getUserClients"
    headers = {"Authorization": f"BearerCLI {session_token}"} if session_token else {}
    try:
        resp = requests.post(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to list tunnels: {e}")
        return None


def _delete_tunnel(session_token: Optional[str], tunnel_id: str):
    url = f"{BASE_URL}/ui/deleteTunnel"
    headers = {"Authorization": f"BearerCLI {session_token}"} if session_token else {}
    payload = {"tunnel_id": tunnel_id}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json() if resp.content else {"message": "Deleted"}
        print(f"[+] {data.get('message', 'Tunnel deleted successfully')}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to delete tunnel: {e}")


def _run_jar_connect(dest_path: str, host: str, port: str):
    if not os.path.isfile(dest_path):
        print(
            "[-] Tunnel client not found. Please download it first using 'ckart tunnel --download' or use --connect to download automatically."
        )
        return
    cmd = ["java", "-cp", dest_path, "main.Main", host, str(port)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode != 0:
            print(f"[-] Tunnel client exited with error:\n{err or out}")
            return
        print("[+] Tunnel client finished successfully.")
        if out:
            try:
                parsed = json.loads(out)
                print(json.dumps(parsed, indent=2))
            except Exception:
                lines = [line for line in out.splitlines() if line.strip()]
                if lines:
                    print(lines[-1])
        else:
            print("[i] Tunnel client ran but did not produce console output.")
    except subprocess.TimeoutExpired:
        print("[-] Tunnel client timed out. It may be running in background or hung.")
    except FileNotFoundError:
        print(
            "[-] Java runtime not found. Please install Java and ensure 'java' is on your PATH."
        )
    except Exception as e:
        print(f"[-] Failed to run tunnel client: {e}")


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
        print(
            "[-] MGMT_SERVER is not set. Please set the management server URL in your .env file."
        )
        return

    session_token = os.getenv("CKART_SESSION")
    downloads_dir = os.path.join(os.path.expanduser("~"), ".ckart-cli")
    dest_path = os.path.join(downloads_dir, "ComputeKart-tunnel-client-1.0.0.jar")

    # SWITCH-like dispatch
    if getattr(args, "list", False):
        clients = _get_user_clients(session_token)
        if clients is not None:
            _pretty_list_clients(clients)
        return

    if getattr(args, "download", False):
        if os.path.isfile(dest_path):
            print("[+] Tunnel client already downloaded at:", dest_path)
            return
        print("[i] Downloading tunnel client...")
        ok = _download_jar(dest_path)
        if ok:
            print(f"[+] Tunnel client downloaded to: {dest_path}")
        else:
            print("[-] Failed to download tunnel client. Check network and try again.")
        return

    if getattr(args, "connect", False):
        if not os.path.isfile(dest_path):
            print("[i] Tunnel client not found locally; downloading first...")
            if not _download_jar(dest_path):
                print("[-] Failed to download tunnel client. Aborting connect.")
                return
        host = input("Enter host name to expose (e.g. myservice): ").strip()
        port = input("Enter local port to forward (e.g. 8080): ").strip()
        if not host or not port:
            print("[-] Host and port are required to connect.")
            return
        print(f"[i] Starting tunnel for {host}:{port}...")
        _run_jar_connect(dest_path, host, port)
        t_no = os.getenv("TUNNEL_NO")
        t_user = os.getenv("TUNNEL_USERNAME")
        if t_no and t_user:
            url = f"{t_no}-{t_user}.computekart.com"
            print(f"[+] Public URL: {url}")
        return

    if getattr(args, "config", None):
        token = args.config
        clients = _get_user_clients(session_token)
        if clients is not None:
            valid_tokens = [c.get("tunnelToken") for c in clients if c.get("tunnelToken")]
            if token in valid_tokens:
                _set_env_var("TUNNEL_TOKEN", token)
                print("[+] Tunnel token saved to ~/.ckart-cli/.env")
            else:
                print("[-] The provided tunnel token does not exist in your account.")
        else:
            print("[-] No Tunnel clients exist!")
        return

    if getattr(args, "create", False):
        _create_tunnel_client(session_token)
        return

    if getattr(args, "delete", None):
        tid = args.delete
        _delete_tunnel(session_token, tid)
        return

    print("[-] No tunnel action provided. Use 'ckart tunnel -h' for usage information.")
