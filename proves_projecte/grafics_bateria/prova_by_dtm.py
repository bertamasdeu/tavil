import streamlit as st  
import pandas as pd 
import sqlite3 
import os 
import plotly.graph_objects as go

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
missio_db = "bateria_missio.db"  # Database with mission state

if not os.path.exists(file_db):
    st.error(f"The file {file_db} does not exist.")
elif not os.path.exists(missio_db):
    st.error(f"The file {missio_db} does not exist.")
else:
    conn = sqlite3.connect(file_db) 
    conn_missio = sqlite3.connect(missio_db)

    try:
        # Load selected battery data
        df = pd.read_sql_query(f"SELECT * FROM {current_file}_data", conn)
        df = df.drop(columns=['id'], errors='ignore')
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Load mission state data
        df_missio = pd.read_sql_query("SELECT * FROM missio_data", conn_missio)
        df_missio = df_missio.drop(columns=['id'], errors='ignore')
        df_missio['timestamp'] = pd.to_datetime(df_missio['timestamp'])
        df_missio = df_missio.rename(columns={'value': 'missio'})
        
        # Sort both DataFrames
        df = df.sort_values('timestamp')
        df_missio = df_missio.sort_values('timestamp')

        # Merge asof (attach mission status to each data row)
        df_merged = pd.merge_asof(
            df, df_missio, on='timestamp',
            direction='backward', tolerance=pd.Timedelta("5s")
        )
        df_merged['missio'] = df_merged['missio'].fillna(0).astype(bool)

        # Time setting
        min_time = df_merged['timestamp'].min().to_pydatetime()
        max_time = df_merged['timestamp'].max().to_pydatetime()

        time_range = st.slider(
            "Select a data time interval:",
            min_value=min_time,
            max_value=max_time,
            value=(min_time, max_time),
            format="YYYY-MM-DD HH:mm:ss"
        )
        
        # We use only the data inside the mission setting and the time range wanted, it is the filter itself
        df_filtered = df_merged[(df_merged['timestamp'] >= time_range[0]) & (df_merged['timestamp'] <= time_range[1])]

        # Chose the mission state
        missio_filter = st.radio("Filter by mission state:", ["All", "Only Mission", "Only Idle"])
        if missio_filter == "Only Mission":
            df_filtered = df_filtered[df_filtered['missio']]
        elif missio_filter == "Only Idle":
            df_filtered = df_filtered[~df_filtered['missio']]

        # Metrics inside the filter
        st.metric("Average", f"{df_filtered['value'].mean():.2f}")
        st.metric("Max Value", f"{df_filtered['value'].max():.2f}")
        st.metric("Min Value", f"{df_filtered['value'].min():.2f}")

        # Data preview
        df_filtered['missio_str'] = df_filtered['missio'].map({True: "Yes", False: "No"})
        st.dataframe(df_filtered[['timestamp', 'value', 'missio_str']])

        df_filtered = df_filtered.sort_values("timestamp")  # Important for plot continuity

        fig = go.Figure()

        prev_row = df_filtered.iloc[0]
        for i in range(1, len(df_filtered)):
            curr_row = df_filtered.iloc[i]
            
            # Color depending on mission state
            color = "blue" if prev_row["missio"] else "red"
            
            fig.add_trace(go.Scatter(
                x=[prev_row["timestamp"], curr_row["timestamp"]],
                y=[prev_row["value"], curr_row["value"]],
                mode="lines",
                line=dict(color=color, width=2),
                showlegend=True
            ))
            
            prev_row = curr_row

        fig.update_layout(
            title=f"{selection} over Time (Color by Mission State)",
            xaxis_title="Timestamp",
            yaxis_title=selection,
            margin=dict(l=40, r=40, t=50, b=40)
        )

        if selection in ['State of Charge', 'State of Health']:
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        conn.close()
        conn_missio.close()

