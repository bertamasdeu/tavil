from utils import merge
from utils import plot
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def render_tab(dfs):
    st.header('Power and Axis Speed and Acceleration Correlation')

    df_speed = dfs.get('df_speed', pd.DataFrame()).rename(columns={'value':'speed'})
    df_power_axis = dfs.get('df_power_axis', pd.DataFrame()).rename(columns={'value':'power'})

    df_speed['acceleration'] = df_speed['speed'].diff() / df_speed['timestamp'].diff().dt.total_seconds()
    table_merged = merge(df_speed, df_power_axis)

    col1, col2, col3 = st.columns(3)
    col1.metric('Average axis power', f'{table_merged['power'].mean():.2f}')
    col2.metric('Maximum axis power value', f'{table_merged['power'].max():.2f}')
    col3.metric('Minimum axis power value', f'{table_merged['power'].min():.2f}')

    col1, col2, col3 = st.columns(3)
    col1.metric('Average axis speed', f'{table_merged['speed'].mean():.2f}')
    col2.metric('Maximum axis speed value', f'{table_merged['speed'].max():.2f}')
    col3.metric('Minimum axis speed value', f'{table_merged['speed'].min():.2f}')

    col1, col2, col3 = st.columns(3)
    col1.metric('Average axis acceleration', f'{table_merged['acceleration'].mean():.2f}')
    col2.metric('Maximum axis acceleration value', f'{table_merged['acceleration'].max():.2f}')
    col3.metric('Minimum axis acceleration value', f'{table_merged['acceleration'].min():.2f}')

    st.dataframe(table_merged)

    table_merged[['speed', 'acceleration']] = table_merged[['speed', 'acceleration']].abs()

    common = table_merged[['speed','power']].dropna()
    fig = plot(common, 'speed', 'power', 'Power and Axis Speed Graphic', 'Speed (mm/s)', 'Power (W)', fit_line=True)
    st.plotly_chart(fig, use_container_width=True)

    common = table_merged[['acceleration','power']].dropna()
    fig1 = plot(common, 'acceleration', 'power', 'Power and Axis Acceleration Graphic', 'Acceleration (mm/s²)', 'Power (W)', fit_line=True)
    st.plotly_chart(fig1, use_container_width=True)
