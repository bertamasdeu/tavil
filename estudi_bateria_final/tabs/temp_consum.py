
from utils import plot, calcular_consum_mitja
import streamlit as st
import pandas as pd


def render_tab(dfs):
    st.header('Temperature - Average Consumtion Correlation')

    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})
    df_temph = dfs.get('df_temph', pd.DataFrame()).rename(columns={'value':'temp'})

    df_temph['power_avg_W'] = df_temph['timestamp'].apply(lambda t: calcular_consum_mitja(t, 60, df_power_global))
    df_temph = df_temph.drop(columns=['id'], errors='ignore')

    last_timestamp = df_power_global['timestamp'].max()
    avg_consum = calcular_consum_mitja(last_timestamp, 60, df_power_global)
    st.metric('Average consumtion for the last hour:',f'{avg_consum:.2f} W')

    st.dataframe(df_temph)

    df_plot = df_temph.dropna(subset=['power_avg_W', 'temp'])
    
    fig = plot(df_plot, 'power_avg_W', 'temp', 'Temperature and Average Consumtion Graphic', 'Average Power (W)', 'Temperature (°C)')
    st.plotly_chart(fig, use_container_width=True)