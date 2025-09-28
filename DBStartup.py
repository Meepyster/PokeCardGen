import sqlite3

DB_FILE = "set_counts.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sets (
            set_id TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            regen_per_minute INTEGER NOT NULL
        )
    """
    )
    conn.commit()

    # Seed with your sets (only runs if missing)
    sets = [("sv8pt5", 1000, 10), ("me1", 1000, 10)]
    for set_id, count, regen in sets:
        c.execute(
            """
            INSERT OR IGNORE INTO sets (set_id, count, regen_per_minute)
            VALUES (?, ?, ?)
        """,
            (set_id, count, regen),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
