
from utils import merge, classify_state, classify_colors
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def render_tab(dfs):
    st.header('Voltage and State of Charge correlation')

    df_vdc = dfs.get('df_vdc', pd.DataFrame()).rename(columns={'value':'vdc'})
    df_soc = dfs.get('df_soc', pd.DataFrame()).rename(columns={'value':'soc'})
    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})

    table_merged = merge(df_vdc, df_soc)    
    table_merged = merge(table_merged, df_power_global)
    table_merged['status'] = table_merged['power'].apply(classify_state)

    st.dataframe(table_merged)

    fig = go.Figure()
    for status in ['idle', 'charging', 'discharging']:
        group = table_merged[table_merged['status'] == status]
        if not group.empty:
            fig.add_trace(go.Scatter(
                x=group['soc'], 
                y=group['vdc'], 
                mode='markers', 
                marker=dict(color=classify_colors(status)), 
                name=status
            ))
    fig.update_layout(
        title='Voltage and State of Charge Graphic',
        xaxis_title='State of Charge (%)',
        yaxis_title='Voltage (V)',
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(title='State')
    )
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)