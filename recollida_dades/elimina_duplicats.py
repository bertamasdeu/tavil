
import sqlite3

DB_PATH = "battery_all.db"

TABLES = [
    "capacitatrest_data", "idc_data", "p_data", "soc_data",
    "temph_data", "templ_data", "vdc_data", "detpalet_data",
    "tracciopower_data", "tracciovelocitat_data",
    "girpower_data", "girvelocitat_data",
    "forqpower_data", "forqvelocitat_data"
]

def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    return cursor.fetchone() is not None

def remove_duplicates(db_path, tables):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for table in tables:
        if not table_exists(cur, table):
            print(f"Taula {table} no existeix")
            continue

        cur.execute(f"SELECT COUNT(*) FROM {table}")
        before_count = cur.fetchone()[0]

        cur.execute(f"""
            DELETE FROM {table}
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM {table}
                GROUP BY timestamp, value
            )
        """)

        cur.execute(f"SELECT COUNT(*) FROM {table}")
        after_count = cur.fetchone()[0]

        removed = before_count - after_count
        print(f"Taula {table}: eliminades {removed} files duplicades")

    conn.commit()
    cur.execute("VACUUM")
    conn.close()

if __name__ == "__main__":
    remove_duplicates(DB_PATH, TABLES)
    print("Neteja de duplicats completada")
