
import streamlit as st 
import pandas as pd 
import sqlite3 
import os 
import plotly.graph_objects as go

options = ["Power", "Intensity", "State of Charge", "Remaining Capacity", "Voltage"]
selection = st.selectbox("Select battery data source:", options)

file_names = {
    "Power": "p_data",
    "Intensity": "idc_data",
    "State of Charge": "soc_data",
    "Remaining Capacity": "capacitatrest_data",
    "Voltage": "vdc_data"
}
table_name = file_names[selection] 

file_db = "bateria_all.db"

if not os.path.exists(file_db):
    st.error(f"The file {file_db} does not exist.")
else:
    conn = sqlite3.connect(file_db) 

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df = df.drop(columns=['id'], errors='ignore')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        st.success(f"Loaded data from {file_db}")

        df_missio = pd.read_sql_query("SELECT * FROM missio_data", conn)
        df_missio = df_missio.drop(columns=['id'], errors='ignore')
        df_missio['timestamp'] = pd.to_datetime(df_missio['timestamp'])
        df_missio = df_missio.rename(columns={'value': 'missio'})

        df = df.sort_values('timestamp')
        df_missio = df_missio.sort_values('timestamp')
        
        df_merged = pd.merge_asof(
            df, df_missio, on='timestamp',
            direction='backward', tolerance=pd.Timedelta("10s")
        )
        df_merged['missio'] = df_merged['missio'].fillna(0).astype(bool)

        min_time = df['timestamp'].min().to_pydatetime()
        max_time = df['timestamp'].max().to_pydatetime()

        time_range = st.slider(
            "Select a data time interval:",
            min_value=min_time,
            max_value=max_time,
            value=(min_time, max_time),
            format="YYYY-MM-DD HH:mm:ss"
            )

        df_filtered = df_merged[(df_merged['timestamp'] >= time_range[0]) & (df_merged['timestamp'] <= time_range[1])]
        

        st.metric("Mitjana", f"{df_filtered['value'].mean():.2f}")
        st.metric("Valor màxim", f"{df_filtered['value'].max():.2f}")
        st.metric("Valor mínim", f"{df_filtered['value'].min():.2f}")

        st.dataframe(df_filtered)
        
        fig = go.line(         
            df_filtered,               
            x="timestamp",    
            y="value",
            title=f"{selection} over Time",
            labels={
                "timestamp": "Timestamp",
                "value": selection
            }
        )

        if selection in ['State of Charge']:
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        conn.close()
