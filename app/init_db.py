from app.database import USE_SQLITE, get_connection


def init_db():
    """
    Create tables if not exist (SQLite local testing only).
    RDS production already has schema from schema.sql.
    """
    if not USE_SQLITE:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_lots (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            name        TEXT     NOT NULL,
            location    TEXT     NOT NULL,
            total_slots INTEGER  NOT NULL DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER  PRIMARY KEY AUTOINCREMENT,
            lot_id          INTEGER  NOT NULL UNIQUE,
            username        TEXT     NOT NULL UNIQUE,
            password        TEXT     NOT NULL,
            recovery_email  TEXT     NOT NULL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_slots (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            lot_id      INTEGER  NOT NULL,
            slot_number TEXT     NOT NULL,
            status      TEXT     NOT NULL DEFAULT 'free',
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (lot_id, slot_number),
            FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slot_history (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            slot_id     INTEGER  NOT NULL,
            status      TEXT     NOT NULL,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_key   TEXT     NOT NULL,
            FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
        )
    """)

    conn.commit()
    conn.close()
