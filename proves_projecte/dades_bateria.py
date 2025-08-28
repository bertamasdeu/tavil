
import asyncio
from asyncua import Client
from datetime import datetime,timedelta
import sqlite3

SERVER_URL = "opc.tcp://172.16.1.10:6001"

DB_PATH = "battery_all.db"

NODES = [
    { "node_id": "ns=6;s=::AsGlobalPV:Bateria.CapacitatRestant",
        "table_name":"capacitatrest_data"},
    { "node_id": "ns=6;s=::AsGlobalPV:Bateria.Idc",
        "table_name": "idc_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:Bateria.P",
        "table_name": "p_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:Bateria.SoC",
        "table_name": "soc_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:Bateria.TemperatureH",
        "table_name":"temph_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:Bateria.TemperatureL",
        "table_name":"templ_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:Bateria.Vdc",
        "table_name": "vdc_data"},

    {"node_id": "ns=6;s=::AsGlobalPV:SistemaDeteccioPalet.SensorCentre",
        "table_name": "detpalet_data"},

    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[0].Status.ActPower",
        "table_name": "tracciopower_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[0].Status.ActVelocity",
        "table_name": "tracciovelocitat_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[1].Status.ActPower",
        "table_name": "girpower_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[1].Status.ActVelocity",
        "table_name": "girvelocitat_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[2].Status.ActPower",
        "table_name": "forqpower_data"},
    {"node_id": "ns=6;s=::AsGlobalPV:gAxis[2].Status.ActVelocity",
        "table_name": "forqvelocitat_data"}
]


def init_db(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            value REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_data(db_path, table_name, timestamp, value):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (timestamp, value) VALUES (?, ?)", (timestamp, value))
    conn.commit()
    conn.close()

def delete_old_data(db_path, table_name):
    cutoff = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S") # Borren les dades de 25 dies enrere
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE timestamp < ?", (cutoff,))
    conn.commit()
    conn.close()


async def read_node(server_url, node_id, db_path, table_name): 
    init_db(db_path, table_name)

    async with Client(url=server_url) as client:
        print(f"Connected for node {node_id}")
        node = client.get_node(node_id)
        while True:
            try:
                value = await node.read_value()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_data(db_path, table_name, timestamp, value)
            except Exception as e:
                print(f"Error reading node {node_id}: {e}")

            await asyncio.sleep(10) # Temps entre recollida de dades


async def delete_data():
    while True:
        for node in NODES:
            delete_old_data(DB_PATH, node["table_name"])
        await asyncio.sleep(1800) # Cada quan es borren les dades

async def main():
    tasks = [
        read_node(SERVER_URL, node["node_id"], DB_PATH, node["table_name"])
        for node in NODES
    ]
    tasks.append(delete_data())
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Program stopped by user.')
