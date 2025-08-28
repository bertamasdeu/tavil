
import sqlite3

ORIGEN_DB = 'battery_all_1.db'
DESTI_DB = 'battery_all.db'

TABLES = [
    'capacitatrest_data', 'idc_data', 'p_data', 'soc_data', 
    'temph_data', 'templ_data', "vdc_data", 'detpalet_data',
    'tracciopower_data', 'tracciovelocitat_data',
    'girpower_data', 'girvelocitat_data',
    'forqpower_data', 'forqvelocitat_data'
]

def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    return cursor.fetchone() is not None

def copy_data(origen, desti, tables): 
    conn_origen = sqlite3.connect(origen) 
    conn_desti = sqlite3.connect(desti) 

    cur_origen = conn_origen.cursor() 
    cur_desti = conn_desti.cursor() 

    for table in tables: 
        if not table_exists(cur_origen, table): 
            print(f'Taula {table} no existeix a l’origen.') 
            continue 

        cur_desti.execute(f""" 
            CREATE TABLE IF NOT EXISTS {table} ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp TEXT NOT NULL, 
            value REAL NOT NULL 
            ) 
        """) 

        cur_origen.execute(f'SELECT timestamp, value FROM {table}') 
        rows = cur_origen.fetchall() 

        cur_desti.executemany( 
            f'INSERT INTO {table} (timestamp, value) VALUES (?, ?)', 
            rows 
        ) 

        print(f'Copiades {len(rows)} files de {table}') 
        conn_desti.commit() 

    conn_origen.close() 
    conn_desti.close() 

        
if __name__ == '__main__': 
    copy_data(ORIGEN_DB, DESTI_DB, TABLES) 
    print('Còpia completada')

