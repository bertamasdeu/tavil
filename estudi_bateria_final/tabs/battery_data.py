
from utils import plot
import pandas as pd
import streamlit as st

def render_tab(dfs):
    st.header('Battery data by type')
    options = ['Power', 'Intensity', 'State of Charge', 'Voltage', 'Axis speed']
    selection = st.selectbox('Select battery data:', options)

    var_names = {
        'Power': 'df_power',
        'Intensity': 'df_idc',
        'State of Charge': 'df_soc',
        'Voltage': 'df_vdc',
        'Axis speed': 'df_speed'
    }
    df = dfs[var_names[selection]]

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
        fig = plot(df_filtered, 'timestamp', 'value', f'{selection} over Time', 'Timestamp', graphic_name[selection])

        if selection == 'State of Charge':
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)