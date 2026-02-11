import sqlite3

DB_NAME = "channels.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        url TEXT PRIMARY KEY,
        status TEXT,
        subscribers TEXT,
        views TEXT,
        videos TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_channel(url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM channels WHERE url=?", (url,))
    data = c.fetchone()
    conn.close()
    return data

def update_channel(url, status, subs, views, videos):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO channels 
    (url, status, subscribers, views, videos)
    VALUES (?, ?, ?, ?, ?)
    """, (url, status, subs, views, videos))
    conn.commit()
    conn.close()
