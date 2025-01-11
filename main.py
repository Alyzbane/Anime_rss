import logging.config
from src.feed import load_config, fetch_rss_feed, parse_rss_feed, save_to_page
from src.db import save_to_database, fetch_from_database

# Load logging configuration from the .ini file
logging.config.fileConfig('logging_config.ini')

# Now you can use the logger in your code
logger = logging.getLogger()

def main():
    logging.info("Starting main process")
    config = load_config("config/nya.yaml")
    rss_url = config["rss_url"]
    fields = config["fields"]
    namespaces = config.get("namespaces", {})
    db_path = "data/rss_feed.db"

    # Fetch, parse, and save RSS feed to database
    rss_content = fetch_rss_feed(rss_url)
    items = parse_rss_feed(rss_content, fields, namespaces)
    save_to_database(db_path, items, fields)

    # Fetch data from database and save to README.md
    rows = fetch_from_database(db_path)
    save_to_page(rows, fields, "README.md")

if __name__ == "__main__":
    main()
