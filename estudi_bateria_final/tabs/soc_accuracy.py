
from utils import merge
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np


def render_tab(dfs, battery_capacity):
    st.header('State of Charge accuracy')

    df_soc = dfs.get('df_soc', pd.DataFrame()).rename(columns= {'value': 'soc'})
    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})

    df_merged = merge(df_soc, df_power_global)
    df_merged = df_merged.sort_values('timestamp').reset_index(drop=True)
    df_merged['soc_est'] = df_merged['soc'].iloc[0]
    df_merged['delta_t'] = df_merged['timestamp'].diff().dt.total_seconds().fillna(0)

    max_delta_t = 60

    for i in range(1, len(df_merged)):
        dt = df_merged.loc[i, 'delta_t']
        if dt > max_delta_t:
            df_merged.loc[i, 'soc_est'] = df_merged.loc[i, 'soc']
        else:
            delta_soc = (df_merged.loc[i, 'power'] * dt / 3600 / battery_capacity) * 100
            df_merged.loc[i, 'soc_est'] = df_merged.loc[i-1, 'soc_est'] + delta_soc
            df_merged.loc[i, 'soc_est'] = np.clip(df_merged.loc[i, 'soc_est'], 0, 100)

    df_merged['soc_error'] = df_merged['soc'] - df_merged['soc_est']
    soc_accuracy = 100 - df_merged['soc_error'].abs().mean()
    st.metric('Average SOC Accuracy (%)', f'{soc_accuracy:.2f}')

    df_merged = df_merged.drop(columns=['delta_t'], errors='ignore')
    st.dataframe(df_merged)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_merged['timestamp'], y=df_merged['soc'], 
        mode='markers', 
        name='Mesured SOC'
    ))
    fig.add_trace(go.Scatter(
        x=df_merged['timestamp'], y=df_merged['soc_est'], 
        mode='markers', 
        name='Estimated SOC'
    ))
    fig.add_trace(go.Scatter(
        x=df_merged['timestamp'], y=df_merged['soc_error'], 
        mode='markers', 
        name='SOC error'
    ))
    fig.update_layout(
        title='SOC Accuracy Graphic',
        xaxis_title="Timestamp", yaxis_title="SOC (%)",
    )

    st.plotly_chart(fig, use_container_width=True)