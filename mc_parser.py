import json
import requests
from rich.columns import Columns
from rich.console import Console
import shutil

def pretty_print(string_list):
    if not string_list:
        return
    console = Console(width=shutil.get_terminal_size().columns)
    console.print(Columns(string_list))


def get_mojang_manifest():
    version_manifest = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()
    with open("version_manifest.json", "w") as outfile:
        json.dump(version_manifest, outfile)


def get_mojang(version: str):
    version_manifest = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()
    latest_rel, latest_snap = version_manifest["latest"].values()

    if version == "list":
            version_names = [id["id"] for id in version_manifest["versions"]]
            pretty_print(version_names)
            return None

    if version == "latest":
        version = latest_rel
    elif version == "latest-snap":
        version = latest_snap

    for index in version_manifest["versions"]:
        version_name = index["id"] # string in standard format
        if version_name != version:
            continue
        version_data = requests.get(index["url"]).json()
        server_meta = version_data["downloads"]["server"]
        return server_meta
