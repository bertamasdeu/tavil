
from utils import merge, classify_state, classify_colors
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def render_tab(dfs):
    st.header('Power - State of Charge Correlation')

    df_soc = dfs.get('df_soc', pd.DataFrame()).rename(columns={'value':'soc'})
    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})

    table_merged = merge(df_soc, df_power_global)
    st.dataframe(table_merged)

    table_merged['status'] = table_merged['power'].apply(lambda p: pd.Series(classify_state(p)))
    
    fig = go.Figure()
    for status, group in table_merged.groupby('status'):
        if group.empty:
            continue
        fig.add_trace(go.Scatter(
            x=group['soc'], y=group['power'], 
            mode='markers', 
            marker=dict(color=classify_colors(status)), 
            name=status
        ))
    fig.update_layout(
        title='Power and State of Charge Graphic',
        xaxis_title='State of Charge (%)', yaxis_title='Power (W)',
        margin=dict(l=40, r=40, t=50, b=40), 
        legend=dict(title='State')
    )
    fig.update_xaxes(range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)