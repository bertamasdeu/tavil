
import sqlite3
import pandas as pd
import os
import streamlit as st

def load_data(file_db, tables):
    dfs = {}
    if os.path.exists(file_db):
        conn = sqlite3.connect(file_db)
        for var_name, table_name in tables.items():
            df = pd.read_sql_query(f'SELECT * FROM [{table_name}]', conn)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').reset_index(drop=True)
            dfs[var_name] = df
        conn.close()
    else:
        st.error('The data file does not exist.')
    return dfs
