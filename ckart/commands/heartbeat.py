import os

import requests
from dotenv import load_dotenv

from ckart import output

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        output.error("MGMT_SERVER URL not set in environment variables.")
        return

    url = f"{base_url}/"  # Adjust if your API uses a different endpoint

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        output.success("MGMT Server is ONLINE!")
        if response.text.strip():
            output.plain(f"[Server Response]: {response.text.strip()}")
    except requests.exceptions.ConnectionError:
        output.error(
            "MGMT Server is OFFLINE or unreachable. Check network or server address."
        )
    except requests.exceptions.Timeout:
        output.error("MGMT Server did not respond in time. Try again later.")
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to check server status: {e}")
