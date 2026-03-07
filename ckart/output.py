import sys
from typing import Any, List, Optional

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None  # functions using it will import when needed


def success(message: str) -> None:
    """Print a success message to stdout."""
    print(f"[+] {message}")


def info(message: str) -> None:
    """Print an informational message to stdout."""
    print(f"[i] {message}")


def warning(message: str) -> None:
    """Print a warning message to stderr (non‑fatal)."""
    print(f"[!] {message}", file=sys.stderr)


def error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"[-] {message}", file=sys.stderr)


def plain(message: str = "") -> None:
    """Print a raw message without any prefix."""
    print(message)


def table(data: List[Any], headers: Optional[List[str]] = None) -> None:
    """Render a table using tabulate if available, otherwise fall back to plain printing."""
    if tabulate:
        print(tabulate(data, headers=headers))
    else:
        # simple fallback
        for row in data:
            print("\t".join(str(x) for x in row))
