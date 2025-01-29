import json
import requests

from datetime import datetime
from loguru import logger
from pathlib import Path


def get_update_url_dict(file_path: Path) -> dict:
    with open(file_path, "r") as infile:
        list_urls = json.load(infile)
    return list_urls


def update_list(list_url: str, list_path: Path) -> bool:
    response = requests.get(list_url)

    if response.status_code == 200:
        with open(list_path, "wb") as outfile:
            outfile.write(response.content)
        success = True
        logger.info(f"Successfully retrieved list from {list_url} and saved to {list_path}")
    else:
        success = False
        logger.warning(f"Failed to retrieve list from {list_url}")
    
    return success


def combine_lists() -> None:
    all_domains = []
    all_file_paths = [x for x in Path("by_site").rglob("*.txt")]

    for filepath in all_file_paths:
        with open(filepath, "r") as infile:
            for line in infile.readlines():
                all_domains.append(line)
    
    with open("combined_hosts.txt", "w") as outfile:
        for line in all_domains:
            outfile.write(line)


def main():
    list_urls = get_update_url_dict(Path("src/list_urls.json"))

    try:
        with open(Path("src") / Path("last_updated.json"), "r") as infile:
            last_updated_dict = json.load(infile)
    except FileNotFoundError:
        last_updated_dict = {}

    if any(list_urls.values()):
        logger.info(f"Preparing to update the following lists: {[x for x, y in list_urls.items() if y]}")

        for list_name, list_url in list_urls.items():
            if list_url:
                list_path = Path("by_site") / Path(f"{list_name}.txt")
                success = update_list(list_url, list_path)

                if success:
                    last_updated_dict[list_name] = str(datetime.now())
        if last_updated_dict:
            with open(Path("src") / Path("last_updated.json"), "w") as outfile:
                json.dump(last_updated_dict, outfile)
    else:
        logger.info("No lists to update.")
