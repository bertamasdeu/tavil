
import streamlit as st 
import pandas as pd 
import sqlite3 
import os 
import plotly.express as px 
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

file_db = 'battery_all.db'
battery_capacity = 10240

tables = {
    'df_power': 'p_data',
    'df_soc': 'soc_data',
    'df_temph': 'temph_data',
    'df_vdc': 'vdc_data',
    'df_palet': 'detpalet_data',
    'df_speed': 'tracciovelocitat_data',
    'df_power_axis': 'tracciopower_data'
}
dfs = {}


def classify_state(power):
    if power > 100:
        return 'charging'
    elif power < -200:
        return 'discharging'
    else:
        return 'idle'


def merge(table1, table2, tol_seconds=9):     
    if table1.empty or table2.empty:
        st.warning('One of the dataset tables is empty.')
        return None
    t = pd.Timedelta(f'{tol_seconds}s')
    table_merged = pd.merge_asof(
        table1.sort_values('timestamp'), table2.sort_values('timestamp'),
        on='timestamp', direction='backward', tolerance=t
    )
    table_merged = table_merged.drop(columns=['id_x','id_y','id'], errors='ignore')
    if table_merged.empty:
        st.warning('Not enough data to compare the two dataset.')
        return None
    return table_merged


def plot_scatter(df, x, y, title, xlabel, ylabel, fit_line=False):
    fig = px.scatter(df, x=x, y=y, title=title, labels={x: xlabel, y: ylabel})
    if fit_line:
        if len(df) >= 2:
            m, b = np.polyfit(df[x], df[y], 1)
            fig.add_scatter(x=df[x], y=m*df[x]+b, mode='lines',
                            name=f'Linear Fit (y={m:.2f}x+{b:.2f})',
                            line=dict(dash='dash'))
        else: 
            st.info('Not enough data for a fit line.')
    return fig


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
        energia_total_Wh = (df_window['power'] * df_window['delta_h']).sum()  # Wh
        temps_total_h = (df_window['timestamp'].iloc[-1] - df_window['timestamp'].iloc[0]).total_seconds() / 3600

        return energia_total_Wh / temps_total_h if temps_total_h > 0 else np.nan  # W


if os.path.exists(file_db):
    conn = sqlite3.connect(file_db)
    for var_name, table_name in tables.items():
        df = pd.read_sql_query(f'SELECT * FROM [{table_name}]', conn)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
        dfs[var_name] = df
        
    conn.close()
else:
    st.error('The data file does not exist.')


df_soc = dfs.get('df_soc', pd.DataFrame()).rename(columns={'value':'soc'})
df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})
df_temph = dfs.get('df_temph', pd.DataFrame()).rename(columns={'value':'temp'})
df_vdc = dfs.get('df_vdc', pd.DataFrame()).rename(columns={'value':'vdc'})
df_palet = dfs.get('df_palet', pd.DataFrame()).rename(columns={'value':'palet'})
df_speed = dfs.get('df_speed', pd.DataFrame()).rename(columns={'value':'speed'})
df_power_axis = dfs.get('df_power_axis', pd.DataFrame()).rename(columns={'value':'power'})


classify_colors = {
    'charging': 'blue',
    'discharging': 'red',
    'idle': 'gray'
}

tabs = st.tabs([
    'Battery Data', 
    'Power - Axis Speed and Acceleration', 
    'Voltage - State of Charge',
    'Power - Pallet presence',
    'Power - State of Charge',
    'Temperature - Average Consumtion',
    'State of Charge accuracy',
    'Estimated full charge/discharge time',
    'Battery cells balancing'
])


# --------------- Tab 0: Dades filtrades per temps ----------------
with tabs[0]:
    st.header('Battery data by type')
    options = ['Power', 'Intensity', 'State of Charge', 'Voltage', 'Axis speed']
    selection = st.selectbox('Select battery data:', options)

    file_names = {
        'Power': 'p_data',
        'Intensity': 'idc_data',
        'State of Charge': 'soc_data',
        'Voltage': 'vdc_data',
        'Axis speed': 'tracciovelocitat_data'
    }
    table_name = file_names[selection]

    conn = sqlite3.connect(file_db) 
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    conn.close()

    if df.empty:
        st.warning('The dataset for this selection is empty.')
    else:
        df = df.drop(columns=['id'], errors='ignore')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        min_time = df['timestamp'].min().to_pydatetime()
        max_time = df['timestamp'].max().to_pydatetime()

        time_range = st.slider(
            'Select a time interval:',
            min_value=min_time, max_value=max_time,
            value=(min_time, max_time), format='YYYY-MM-DD HH:mm:ss'
        )

        df_filtered = df[
            (df['timestamp'] >= time_range[0]) & 
            (df['timestamp'] <= time_range[1])]

        col1, col2, col3 = st.columns(3)
        col1.metric('Average', f"{df_filtered['value'].mean():.2f}")
        col2.metric('Maximum value', f"{df_filtered['value'].max():.2f}")
        col3.metric('Minimum value', f"{df_filtered['value'].min():.2f}")
        st.dataframe(df_filtered)

        graphic_name= { 
            'Power': 'Power (W)',
            'Intensity': 'Intensity (A)',
            'State of Charge': 'State of Charge (%)',
            'Voltage': 'Voltage (V)',
            'Axis speed': 'Axis speed (mm/s)'
        }
        fig = plot_scatter(df_filtered, 'timestamp', 'value', f'{selection} over Time', 'Timestamp', graphic_name[selection])

        if selection == 'State of Charge':
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)


# ---------------- Tab 1: Power vs axis speed ----------------
with tabs[1]:
    st.header('Power and Axis Speed and Acceleration Correlation')

    df_speed['acceleration'] = df_speed['speed'].diff() / df_speed['timestamp'].diff().dt.total_seconds()
    table_merged = merge(df_speed, df_power_axis)

    col1, col2, col3 = st.columns(3)
    col1.metric('Average axis power', f'{table_merged['power'].mean():.2f}')
    col2.metric('Maximum axis power value', f'{table_merged['power'].max():.2f}')
    col3.metric('Minimum axis power value', f'{table_merged['power'].min():.2f}')

    st.dataframe(table_merged)

    table_merged[['speed', 'acceleration']] = table_merged[['speed', 'acceleration']].abs()

    fig = go.Figure()
    common = table_merged[['speed','power']].dropna()
    fig = plot_scatter(common, 'speed', 'power', 'Power and Axis Speed Graphic', 'Speed (mm/s)', 'Power (W)', fit_line=True)
    st.plotly_chart(fig, use_container_width=True)

    fig1 = go.Figure()
    common = table_merged[['acceleration','power']].dropna()
    fig1 = plot_scatter(common, 'acceleration', 'power', 'Power and Axis Acceleration Graphic', 'Acceleration (mm/s²)', 'Power (W)', fit_line=True)
    st.plotly_chart(fig1, use_container_width=True)


# ---------------- Tab 2: Voltage vs SOC ----------------
with tabs[2]:
    st.header('Voltage and State of Charge correlation')

    table_merged = merge(df_vdc, df_soc)
    table_merged = merge(table_merged, df_power_global)
    table_merged['status'] = table_merged['power'].apply(classify_state)

    st.dataframe(table_merged)

    fig = go.Figure()
    for status in ['idle', 'charging', 'discharging']:
        group = table_merged[table_merged['status'] == status]
        if not group.empty:
            fig.add_trace(go.Scatter(
                x=group['soc'], y=group['vdc'], 
                mode='markers', marker=dict(color=classify_colors[status]), 
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


# ---------------- Tab 3: Power vs Pallet presence ----------------
with tabs[3]:
    st.header('Power variation depending on Pallet presence')

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
            x=df_palet_false['timestamp'], y=df_palet_false['power'],
            mode='markers', name='Palet absent'
        ))
    if not df_palet_true.empty:
        fig.add_trace(go.Scatter(
            x=df_palet_true['timestamp'], y=df_palet_true['power'],
            mode='markers', name='Palet present'
        ))
    fig.update_layout(
        title='Power depending on Pallet Presence Graphic',
        xaxis_title='Timestamp', yaxis_title='Power (W)',
        margin=dict(l=40, r=40, t=50, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)



# ---------------- Tab 4: Power vs SOC ----------------
with tabs[4]:
    st.header('Power - State of Charge Correlation')
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
            marker=dict(color=classify_colors[status]), 
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



# ---------------- Tab 5: Temperature vs average consumption ----------------
with tabs[5]:
    st.header('Temperature - Average Consumtion Correlation')

    df_temph['power_avg_W'] = df_temph['timestamp'].apply(lambda t: calcular_consum_mitja(t, 60, df_power_global))
    df_temph = df_temph.drop(columns=['id'], errors='ignore')

    last_timestamp = df_power_global['timestamp'].max()
    avg_consum = calcular_consum_mitja(last_timestamp, 60, df_power_global)
    st.metric('Average consumtion for the last hour:',f'{avg_consum:.2f} W')

    st.dataframe(df_temph)

    df_plot = df_temph.dropna(subset=['power_avg_W', 'temp'])
    
    fig = go.Figure()
    fig = plot_scatter(df_plot, 'power_avg_W', 'temp', 'Temperature and Average Consumtion Graphic', 'Average Power (W)', 'Temperature (°C)')
    st.plotly_chart(fig, use_container_width=True)



# ---------------- Tab 6: State of Charge Accuracy ----------------
with tabs[6]:
    st.header('State of Charge accuracy')

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



# ---------------- Tab 7: Estimated full charge/discharge time ----------------
with tabs[7]:
    df = merge(df_soc, df_power_global)

    df = df.sort_values('timestamp').reset_index(drop=True)
    df['state'] = df['power'].apply(classify_state)

    soc_now = df['soc'].iloc[-1]
    charge_mask = df['state'] == 'charging'
    discharge_mask = df['state'] == 'discharging'

    avg_power_charge = df.loc[charge_mask, 'power'].mean() if charge_mask.any() else np.nan 
    avg_power_discharge = df.loc[discharge_mask, 'power'].mean() if discharge_mask.any() else np.nan

    hours_to_100 = ((100 - soc_now) / 100 * battery_capacity) / avg_power_charge if pd.notna(avg_power_charge) else np.inf
    hours_to_0 = (soc_now / 100 * battery_capacity) / abs(avg_power_discharge) if pd.notna(avg_power_discharge) else np.inf

    st.metric('Current State of Charge:',  f'{soc_now:.2f} %')
    st.metric('Estimated full charge time:', f'{hours_to_100:.2f} hours')
    st.metric('Estimated full discharge time:', f'{hours_to_0:.2f} hours')



# ---------------- Tab 8: Battery cells balancing ----------------
with tabs[8]:
    table_merged = merge(df_soc, df_power_global)

    last_7_days = table_merged['timestamp'].max() - pd.Timedelta(days=7) # Només es compten els últims 7 dies
    table_merged = table_merged[table_merged['timestamp'] >= last_7_days]

    if table_merged.empty:
        st.warning('Not enough data in the last 7 days.')
    else:
        table_merged = table_merged.sort_values('timestamp').reset_index(drop=True)
        table_merged['delta_t'] = table_merged['timestamp'].diff().dt.total_seconds()
        table_merged['status'] = table_merged['power'].apply(classify_state)

        time_bal = 0
        for soc, state, delta in zip(table_merged['soc'], table_merged['status'], table_merged['delta_t']):
            if soc >= 99 and state == 'charging':
                if pd.notna(delta):
                    time_bal += delta
        time_bal_h = time_bal / 3600
        st.metric('Battery cells balancing time accumulated (in the last 7 days):',f'{time_bal_h:.2f} hours')

        if time_bal_h < 5:
            remaining = 5 - time_bal_h
            st.metric('Remaining full charging time for full cells balancing: ',f'{remaining:.2f} hours')
        else:
            st.metric('Battery cells are fully balanced.')


