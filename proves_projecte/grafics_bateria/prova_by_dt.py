import streamlit as st 
import pandas as pd 
import sqlite3 
import os 
import plotly.express as px 

# Selection of battery data to be shown
options = ["Power", "Intensity", "State of Charge", "State of Health", "Voltage"]
selection = st.selectbox("Select battery data source:", options)

file_names = {
    "Power": "p",
    "Intensity": "idc",
    "State of Charge": "soc",
    "State of Health": "soh",
    "Voltage": "vdc"
}
current_file = file_names[selection] 

file_db = f"bateria_{current_file}.db"

if not os.path.exists(file_db):
    st.error(f"The file {file_db} does not exist.")
else:
    conn = sqlite3.connect(file_db) 

    try:
        df = pd.read_sql_query(f"SELECT * FROM {current_file}_data", conn)
        df = df.drop(columns=['id'], errors='ignore')
        st.success(f"Loaded data from {file_db}")
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Convert pandas Timestamp to python native datetime for Streamlit slider
            min_time = df['timestamp'].min().to_pydatetime()
            max_time = df['timestamp'].max().to_pydatetime()

            # Slider to filter the time
            time_range = st.slider(
                "Select a data time interval:",
                min_value=min_time,
                max_value=max_time,
                value=(min_time, max_time),
                format="YYYY-MM-DD HH:mm:ss"
            )

            # Filter data by time
            df_filtered = df[(df['timestamp'] >= time_range[0]) & (df['timestamp'] <= time_range[1])]
        else:
            df_filtered = df

        st.metric("Mitjana", f"{df_filtered['value'].mean():.2f}")
        st.metric("Valor màxim", f"{df_filtered['value'].max():.2f}")
        st.metric("Valor mínim", f"{df_filtered['value'].min():.2f}")

        st.dataframe(df_filtered)      # Show filtred table
        
        fig = px.line(         
            df_filtered,                        # Used data
            x="timestamp",                      # Set the title for each axis
            y="value",
            title=f"{selection} over Time",     # Graphic title
            labels={                            
                "timestamp": "Timestamp",
                "value": selection
            }
        )

        if selection in ['State of Charge', 'State of Health']: # Set a max and min for range of the percent
            fig.update_yaxes(range=[0, 100]) # Max will always be 100 and min 0

        st.plotly_chart(fig, use_container_width=True) # Show filtred data graphic
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        conn.close()

