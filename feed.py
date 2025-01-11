import requests
import xml.etree.ElementTree as ET
import yaml

def fetch_rss_feed(url):
    response = requests.get(url)
    return response.content

def load_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

def parse_rss_feed(rss_content, fields):
    root = ET.fromstring(rss_content)
    items = []
    for item in root.findall(".//item"):
        entry = {}
        for field in fields:
            namespace, tag = field.split(":") if ":" in field else ("", field)
            if namespace:
                value = item.find(f"{namespace}:{tag}", namespaces={namespace: f"https://nyaa.si/xmlns/{namespace}"}).text
            else:
                value = item.find(tag).text
            entry[field] = value
        items.append(entry)
    return items

def save_to_readme(items, fields, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# RSS Feed Data\n\n")
        file.write("| " + " | ".join(fields) + " |\n")
        file.write("|" + " --- |" * len(fields) + "\n")
        for item in items:
            file.write("| " + " | ".join(item[field] for field in fields) + " |\n")

def main():
    config = load_config("config.yaml")
    rss_url = config["rss_url"]
    fields = config["fields"]

    rss_content = fetch_rss_feed(rss_url)

    items = parse_rss_feed(rss_content, fields)
    save_to_readme(items, fields, "README.md")

if __name__ == "__main__":
    main()
