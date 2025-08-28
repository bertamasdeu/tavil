
import streamlit as st # To show program results as an itneractive web
import pandas as pd # To manipulate python data such as reading a dataset
import sqlite3 # Module to connect and work with SQLite databases
import os # Module to browse through folders and use other files
import plotly.express as px # To design and improve line chart

# Selection of battery data to be shown
options = ["Power", "Intensity", "State of Charge", "State of Health", "Voltage"]
selection = st.selectbox("Select battery data source:", options)

file_names = {
    "Power": "p",
    "Intensity": "idc",
    "State of Charge": "soc",
    "State of Health": "soh",
    "Voltage": "vdc"
}
current_file = file_names[selection] #Chosen file name

# File of selected data
file_db = f"bateria_{current_file}.db"

if not os.path.exists(file_db):  # Check existence of file
    st.error(f"The file {file_db} does not exist.")
else:
    # Establish connection and read data table
    conn = sqlite3.connect(file_db) 

    try:
        df = pd.read_sql_query(f"SELECT * FROM {current_file}_data", conn)
        df = df.drop(columns=['id'], errors='ignore') # Eliminate the column id since it does not provide any information
        st.success(f"Loaded data from {file_db}") # Informs the user of a correct load of data
        
        # Differentiate the time column
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            df = df.set_index('timestamp') 
            df = df.reset_index()      # Reset if needed for plotly in the line chart

        st.dataframe(df)      # Show table

        # Create plotly line chart
        fig = px.line(         # Variable to save the graphic result
            df,                # Dataframe we want to visualize
            x = "timestamp",    
            y = "value",
            title = f"{selection} over Time",
            labels = {
                "timestamp": "Timestamp",
                "value": selection
            }
        )

        if selection in ['State of Charge', 'State of Health']: #If we are visualizing the soh or soc we fix the range of the value
            fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True) # Show line chart
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        conn.close()
