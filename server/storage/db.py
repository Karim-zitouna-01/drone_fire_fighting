# storage/db.py

import json
import os
import threading

DB_PATH = "storage/data.json"
LOCK = threading.Lock()   # prevents concurrent writes


def _load_db():
    """Load the entire DB file, create if not exists."""
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)

    with open(DB_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}   # corrupted → reset empty


def _save_db(data):
    """Overwrite database file safely."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)


def add_entry(drone_id: str, entry: dict):
    """
    Add a new analysis entry for a given drone.
    """
    with LOCK:
        db = _load_db()

        if drone_id not in db:
            db[drone_id] = []

        db[drone_id].append(entry)

        # OPTIONAL: keep only last 200 entries per drone
        db[drone_id] = db[drone_id][-200:]

        _save_db(db)


def get_last_entries(drone_id: str, n: int = 10):
    """
    Get last N entries for a drone.
    """
    with LOCK:
        db = _load_db()
        if drone_id not in db:
            return []
        return db[drone_id][-n:]
