import sqlite3
import logging

logger = logging.getLogger('db')

def remove_namespace(field):
    return field.split(":")[-1]  # Takes only the part after the colon

def save_to_database(db_path, items, fields):
    logging.info(f"Saving {len(items)} items to database {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Remove namespaces from fields for table creation
    fields_without_namespace = [remove_namespace(field) for field in fields]

    # Create table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS rss_items (
            id INTEGER PRIMARY KEY,
            {", ".join(f"{field} TEXT" for field in fields_without_namespace)}
        )
    """)

    # Insert items into the table
    for item in items:
        cursor.execute(f"""
            INSERT INTO rss_items ({", ".join(fields_without_namespace)})
            VALUES ({", ".join("?" for _ in fields)})
        """, [item[field] for field in fields])

    conn.commit()
    conn.close()
    logging.info("Data saved to database successfully")

def fetch_from_database(db_path):
    logging.info(f"Fetching data from database {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rss_items")
    rows = cursor.fetchall()
    conn.close()
    logging.info(f"Fetched {len(rows)} rows from the database")
    return rows
