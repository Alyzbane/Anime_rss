import xml.etree.ElementTree as ET
import requests
import yaml
import logging
from .db import save_to_database, fetch_from_database

# Get a logger specific to the module
logger = logging.getLogger('feed')

def load_config(config_file):
    logging.info(f"Loading config from {config_file}")
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    logging.info("Config loaded successfully")
    return config

def fetch_rss_feed(url):
    logging.info(f"Fetching RSS feed from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("RSS feed fetched successfully")
    else:
        logging.error(f"Failed to fetch RSS feed. Status code: {response.status_code}")
    return response.content

def parse_rss_feed(rss_content, fields, namespaces):
    logging.info("Parsing RSS feed content")
    root = ET.fromstring(rss_content)
    items = []
    for item in root.findall(".//item"):
        entry = {}
        for field in fields:
            namespace, tag = field.split(":") if ":" in field else ("", field)
            if namespace:
                value = item.find(f"{namespace}:{tag}", namespaces=namespaces)
            else:
                value = item.find(tag)
            entry[field] = value.text if value is not None else None
        items.append(entry)
    logging.info(f"Parsed {len(items)} items from RSS feed")
    return items

def save_to_page(rows, fields, file_path):
    logging.info(f"Saving data to {file_path}")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# RSS Feed Data\n\n")
        file.write("| " + " | ".join(fields) + " |\n")
        file.write("|" + " --- |" * len(fields) + "\n")
        for row in rows:
            file.write("| " + " | ".join(row[1:]) + " |\n")  # Skip the `id` column
    logging.info("Updated main page...")
