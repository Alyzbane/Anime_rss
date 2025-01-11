# test/test_feed.py
import pytest
from unittest.mock import mock_open, patch, MagicMock
import xml.etree.ElementTree as ET
from src.feed import load_config, fetch_rss_feed, parse_rss_feed, save_to_page
from src.db import save_to_database, fetch_from_database

@pytest.fixture
def nyaa_config():
    return {
        "rss_url": "https://nyaa.si/?page=rss",
        "fields": ["title", "nyaa:category", "pubDate", "nyaa:downloads", "nyaa:categoryId"],
        "namespaces": {"nyaa": "https://nyaa.si/xmlns/nyaa"}
    }

@pytest.fixture
def nyaa_rss_content():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:nyaa="https://nyaa.si/xmlns/nyaa">
        <channel>
            <item>
                <title>Test Anime</title>
                <nyaa:category>Anime</nyaa:category>
                <pubDate>Sat, 11 Jan 2025 19:00:00 +0000</pubDate>
                <nyaa:downloads>100</nyaa:downloads>
                <nyaa:categoryId>1_0</nyaa:categoryId>
            </item>
        </channel>
    </rss>
    """

def test_load_nyaa_config():
    mock_config = """
    rss_url: "https://nyaa.si/?page=rss"
    fields:
      - title
      - nyaa:category
      - pubDate
      - nyaa:downloads
      - nyaa:categoryId
    namespaces:
      nyaa: "https://nyaa.si/xmlns/nyaa"
    """
    with patch("builtins.open", mock_open(read_data=mock_config)):
        config = load_config("config/nyaa.yaml")
        assert config["rss_url"] == "https://nyaa.si/?page=rss"
        assert len(config["fields"]) == 5
        assert config["namespaces"]["nyaa"] == "https://nyaa.si/xmlns/nyaa"

def test_parse_nyaa_feed(nyaa_rss_content, nyaa_config):
    fields = nyaa_config["fields"]
    namespaces = nyaa_config["namespaces"]
    
    items = parse_rss_feed(nyaa_rss_content, fields, namespaces)
    
    assert len(items) == 1
    assert items[0]["title"] == "Test Anime"
    assert items[0]["nyaa:category"] == "Anime"
    assert items[0]["nyaa:downloads"] == "100"
    assert items[0]["nyaa:categoryId"] == "1_0"

def test_full_nyaa_workflow(tmp_path, nyaa_config, nyaa_rss_content):
    db_path = str(tmp_path / "test_nyaa.db")
    output_file = str(tmp_path / "output.md")
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = nyaa_rss_content.encode('utf-8')
        
        # Run the workflow
        rss_content = fetch_rss_feed(nyaa_config["rss_url"])
        items = parse_rss_feed(rss_content, nyaa_config["fields"], nyaa_config["namespaces"])
        save_to_database(db_path, items, nyaa_config["fields"])
        rows = fetch_from_database(db_path)
        save_to_page(rows, nyaa_config["fields"], output_file)
        
        # Verify database has correct data
        assert len(rows) == 1
        assert "Test Anime" in str(rows[0])
