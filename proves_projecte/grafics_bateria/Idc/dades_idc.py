import asyncio
from asyncua import Client
from datetime import datetime
import sqlite3

SERVER_URL = "opc.tcp://172.16.1.10:6001"
NODE_ID = "ns=6;s=::AsGlobalPV:Bateria.Idc"

DB_PATH = "bateria_idc.db"

# Creates the data table if it doesn't already exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS idc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            value REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Insterts the read data in the now created table
def insert_idc_data(timestamp, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO idc_data (timestamp, value) VALUES (?, ?)", (timestamp, value))
    conn.commit()
    conn.close()

async def main():
    init_db()
    async with Client(url=SERVER_URL) as client:
        print("Connectat al servidor OPC UA")
        node = client.get_node(NODE_ID)

        while True:
            try:
                # Reads the node value
                value = await node.read_value()

                # Saves the current time mark
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Idc: {value}")

                # Saves the data in the dataset
                insert_idc_data(timestamp, value)
            except Exception as e:
                print(f"Error llegint el node: {e}")

            # Await time for the next mark
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma aturat per l'usuari.")
