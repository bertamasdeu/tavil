import streamlit as st
import pandas as pd 
from datetime import timedelta
import numpy as np
import plotly.express as px


def classify_state(power):
    if power > 100:
        return 'charging'
    elif power < -200:
        return 'discharging'
    else:
        return 'idle'
    
def classify_colors(state):
    if state == 'charging':
        return 'blue'
    elif state == 'discharging':
        return 'red'
    else:
        return 'gray'

def merge(table1, table2, tol_seconds=9):
    if table1.empty or table2.empty:
        st.warning('One of the dataset tables is empty.')
        return None
    t = pd.Timedelta(f'{tol_seconds}s')
    table_merged = pd.merge_asof(
        table1.sort_values('timestamp'),
        table2.sort_values('timestamp'),
        on='timestamp', direction='backward', tolerance=t
    )
    table_merged = table_merged.drop(columns=['id_x','id_y','id'], errors='ignore')
    return table_merged

def calcular_consum_mitja(timestamp, interval_minutes, df_power_global):
    t_ini = timestamp - timedelta(minutes=interval_minutes)
    df_window = df_power_global[
        (df_power_global['timestamp'] >= t_ini) &
        (df_power_global['timestamp'] <= timestamp)]
    if df_window.shape[0] < 2:
        return np.nan
    df_window = df_window.sort_values('timestamp')
    df_window['delta_h'] = df_window['timestamp'].diff().dt.total_seconds() / 3600
    df_window = df_window.iloc[1:]
    energia_total_Wh = (df_window['power'] * df_window['delta_h']).sum()
    temps_total_h = (df_window['timestamp'].iloc[-1] - df_window['timestamp'].iloc[0]).total_seconds() / 3600
    return energia_total_Wh / temps_total_h if temps_total_h > 0 else np.nan

def plot(df, x, y, title, xlabel, ylabel, fit_line=False):
    fig = px.scatter(df, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
    if fit_line and len(df) >= 2:
        m, b = np.polyfit(df[x], df[y], 1)
        fig.add_scatter(x=df[x], y=m*df[x]+b, mode='lines',
                        name=f'Linear Fit (y={m:.2f}x+{b:.2f})',
                        line=dict(dash='dash'))
    return fig