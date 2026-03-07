import os

def show_banner():
    banner_path = os.path.join(os.path.dirname(__file__), "banner.txt")
    with open(banner_path, "r", encoding="utf-8") as f:
        print(f.read())
