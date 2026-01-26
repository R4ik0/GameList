import sqlite3
data_path = "data/"

conn = sqlite3.connect(data_path +"users.db")  # crée le fichier s'il n'existe pas
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    gamelist TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()
conn.close()
