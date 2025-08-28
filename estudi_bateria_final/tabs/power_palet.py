
from utils import merge
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def render_tab(dfs):
    st.header('Power variation depending on Pallet presence')

    df_palet = dfs.get('df_palet', pd.DataFrame()).rename(columns={'value':'palet'})
    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})


    table_merged = merge(df_palet, df_power_global)

    table_merged['palet'] = table_merged['palet'].fillna(0).astype(bool)
    table_merged['timestamp'] = pd.to_datetime(table_merged['timestamp'])

    min_time = table_merged['timestamp'].min().to_pydatetime()
    max_time = table_merged['timestamp'].max().to_pydatetime()

    time_range = st.slider(
        'Select a time interval:',
        min_value=min_time,
        max_value=max_time,
        value=(min_time, max_time)
    )
    table_merged = table_merged[
        (table_merged['timestamp'] >= time_range[0]) &
        (table_merged['timestamp'] <= time_range[1])]
    
    st.dataframe(table_merged)

    df_palet_true = table_merged[table_merged['palet'] == True]
    df_palet_false = table_merged[table_merged['palet'] == False]

    fig = go.Figure()

    if not df_palet_false.empty:
        fig.add_trace(go.Scatter(
            x=df_palet_false['timestamp'], 
            y=df_palet_false['power'],
            mode='markers', 
            name='Palet absent'
        ))
    if not df_palet_true.empty:
        fig.add_trace(go.Scatter(
            x=df_palet_true['timestamp'], 
            y=df_palet_true['power'],
            mode='markers', 
            name='Palet present'
        ))
    fig.update_layout(
        title='Power depending on Pallet Presence Graphic',
        xaxis_title='Timestamp', 
        yaxis_title='Power (W)',
        margin=dict(l=40, r=40, t=50, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)