
import streamlit as st
from data_loader import load_data
from tabs import battery_data, power_axis, voltage_soc, power_palet, power_soc, temp_consum, soc_accuracy, battery_charge

file_db = 'battery_all.db'
battery_capacity = 10240
tables = {
    'df_power': 'p_data',
    'df_soc': 'soc_data',
    'df_temph': 'temph_data',
    'df_vdc': 'vdc_data',
    'df_palet': 'detpalet_data',
    'df_speed': 'tracciovelocitat_data',
    'df_power_axis': 'tracciopower_data',
    'df_idc': 'idc_data'
}

dfs = load_data(file_db, tables)

tabs = st.tabs([
    'Battery Data',
    'Power - Axis Speed and Acceleration',
    'Voltage - State of Charge',
    'Power - Pallet presence',
    'Power - State of Charge',
    'Temperature - Average Consumption',
    'State of Charge accuracy',
    'Current Battery Charge situation'
])

with tabs[0]: battery_data.render_tab(dfs)
with tabs[1]: power_axis.render_tab(dfs)
with tabs[2]: voltage_soc.render_tab(dfs)
with tabs[3]: power_palet.render_tab(dfs)
with tabs[4]: power_soc.render_tab(dfs)
with tabs[5]: temp_consum.render_tab(dfs)
with tabs[6]: soc_accuracy.render_tab(dfs, battery_capacity)
with tabs[7]: battery_charge.render_tab(dfs, battery_capacity)

