import sqlite3
from typing import Optional, Dict, Any
import json
from pymongo import MongoClient

# SQLite cache for fast lookups without http query

CREATE_CACHE_SQL = """
CREATE TABLE IF NOT EXISTS entity_cache (
    entity TEXT PRIMARY KEY,
    country_json TEXT
);
"""

class GeoCache:
    def __init__(self, path: str):
        self.path = path
        with sqlite3.connect(self.path, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute(CREATE_CACHE_SQL)
            conn.commit()

    def get(self, entity: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.path, timeout=10) as conn:
            cur = conn.execute("SELECT country_json FROM entity_cache WHERE entity=?", (entity,))
            row = cur.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None

    def set(self, entity: str, country_obj: Optional[Dict[str, Any]]) -> None:
        with sqlite3.connect(self.path, timeout=30) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO entity_cache(entity, country_json) VALUES (?, ?)",
                (entity, json.dumps(country_obj) if country_obj else None),
            )
            conn.commit()


# Mongo helper
def get_mongo_collection(uri: str, db: str, col: str):
    client = MongoClient(uri)
    return client, client[db][col]