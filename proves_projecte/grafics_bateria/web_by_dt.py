
import streamlit as st 
import pandas as pd 
import sqlite3 
import os 
import plotly.express as px 

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

file_db = f"bateria_all.db"

if not os.path.exists(file_db):
    st.error(f"The file {file_db} does not exist.")
else:
    conn = sqlite3.connect(file_db) 

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df = df.drop(columns=['id'], errors='ignore')
        st.success(f"Loaded data from {file_db}")
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            min_time = df['timestamp'].min().to_pydatetime()
            max_time = df['timestamp'].max().to_pydatetime()

            time_range = st.slider(
                "Select a time interval:",
                min_value=min_time,
                max_value=max_time,
                value=(min_time, max_time),
                format="YYYY-MM-DD HH:mm:ss"
            )

            # Filtrar les dades per hores
            df_filtered = df[(df['timestamp'] >= time_range[0]) & (df['timestamp'] <= time_range[1])]
        else:
            st.warning("The 'timestamp' column does not exist.")
            df_filtered = df

        st.metric("Average", f"{df_filtered['value'].mean():.2f}")
        st.metric("Maximum value", f"{df_filtered['value'].max():.2f}")
        st.metric("Minimum value", f"{df_filtered['value'].min():.2f}")

        st.dataframe(df_filtered)
        
        fig = px.line(         
            df_filtered,               
            x="timestamp",    
            y="value",
            title=f"{selection} over Time",
            labels={
                "timestamp": "Timestamp",
                "value": selection
            }
        )

        if selection == "State of Charge":
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        conn.close()
