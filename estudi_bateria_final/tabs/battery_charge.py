
from utils import merge, classify_state
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np


def render_tab(dfs, battery_capacity):

    st.header('Current Battery charging situation')

    df_soc = dfs.get('df_soc', pd.DataFrame()).rename(columns={'value':'soc'})
    df_power_global = dfs.get('df_power', pd.DataFrame()).rename(columns={'value':'power'})

    df = merge(df_soc, df_power_global)

    df = df.sort_values('timestamp').reset_index(drop=True)
    df['state'] = df['power'].apply(classify_state)

    soc_now = df['soc'].iloc[-1]
    if float(df['power'].iloc[-1]) > 100:
        st.info('Charging')
    else:
        st.info('Not Charging')

    charge_mask = df['state'] == 'charging'
    discharge_mask = df['state'] == 'discharging'

    avg_power_charge = df.loc[charge_mask, 'power'].mean() if charge_mask.any() else np.nan 
    avg_power_discharge = df.loc[discharge_mask, 'power'].mean() if discharge_mask.any() else np.nan

    hours_to_100 = ((100 - soc_now) / 100 * battery_capacity) / avg_power_charge if pd.notna(avg_power_charge) else np.inf
    hours_to_0 = (soc_now / 100 * battery_capacity) / abs(avg_power_discharge) if pd.notna(avg_power_discharge) else np.inf

    st.metric('Current State of Charge:',  f'{soc_now:.2f} %')
    st.metric('Estimated full charge time:', f'{hours_to_100:.2f} hours')
    st.metric('Estimated full discharge time:', f'{hours_to_0:.2f} hours')

    st.header('Cells balancing')

    table_merged = merge(df_soc, df_power_global)

    today = pd.Timestamp(datetime.today().date())
    last_7_days = today - pd.Timedelta(days=7)
    table_merged = table_merged[table_merged['timestamp'] >= last_7_days]

    if table_merged.empty:
        st.warning('Not enough data in the last 7 days.')
    else:
        table_merged = table_merged.sort_values('timestamp').reset_index(drop=True)
        table_merged['delta_t'] = table_merged['timestamp'].diff().dt.total_seconds()
        table_merged['status'] = table_merged['power'].apply(classify_state)

        time_bal = 0
        for soc, state, delta in zip(table_merged['soc'], table_merged['status'], table_merged['delta_t']):
            if soc >= 98.5 and state == 'charging':
                if pd.notna(delta):
                    time_bal += delta
        time_bal_h = time_bal / 3600
        st.metric('Battery cells balancing time accumulated (in the last 7 days):',f'{time_bal_h:.2f} hours')

        if time_bal_h < 5:
            remaining = 5 - time_bal_h
            st.metric('Remaining full charging time for full cells balancing: ',f'{remaining:.2f} hours')
        else:
            st.metric('Battery cells are fully balanced.')
