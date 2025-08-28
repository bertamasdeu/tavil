
import sqlite3
from datetime import datetime, timedelta
import random

db_name = "bateria_missio.db"

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS missio_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        value INTEGER NOT NULL
    )
""")

cursor.execute("DELETE FROM missio_data")

start_time = datetime(2025, 8, 4, 10, 0, 0)
end_time = datetime(2025, 8, 4, 12, 0, 0)
current_time = start_time

while current_time <= end_time:
    missio_value = random.choice([0, 1])
    
    cursor.execute(
        "INSERT INTO missio_data (timestamp, value) VALUES (?, ?)",
        (current_time.strftime("%Y-%m-%d %H:%M:%S"), missio_value)
    )

    current_time += timedelta(seconds=10)

conn.commit()
conn.close()


"""
import asyncio
from asyncua import Client
from datetime import datetime
import sqlite3

SERVER_URL = "opc.tcp://172.16.1.10:6001"
NODE_ID = "ns=6;s=::AsGlobalPV:Bateria.Missio" # Posar nom

DB_PATH = "bateria_missio.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(""
        CREATE TABLE IF NOT EXISTS missio_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            value BOOL NOT NULL
        )
    "")
    conn.commit()
    conn.close()

def insert_missio_data(timestamp, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO missio_data (timestamp, value) VALUES (?, ?)", (timestamp, value))
    conn.commit()
    conn.close()

async def main():
    init_db()
    async with Client(url=SERVER_URL) as client:
        print("Connectat al servidor OPC UA")
        node = client.get_node(NODE_ID)

        while True:
            try:
                value = await node.read_value()
                value = bool(value)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Missio: {value}")

                insert_missio_data(timestamp, value)
            except Exception as e:
                print(f"Error llegint el node: {e}")

            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma aturat per l'usuari.")
"""
