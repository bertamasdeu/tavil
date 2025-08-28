
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Path to the dataset
DB_PATH = "bateria_p.db"
INTERVAL_SECONDS = 1 

# Reads the dataset information
def llegir_dades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, value FROM p_data ORDER BY timestamp ASC")
    files = cursor.fetchall() # Tuples list
    conn.close()
    return files

def main():
    # Calls previous function to obtain the data
    dades = llegir_dades()
    if not dades:
        print("No s'han trobat dades a la base de dades.")
        return

    # Sepates the gained data in lists
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in dades]
    valors = [row[1] for row in dades]

    # Transforms power into energy using the time of measure
    energia_acumulada = []
    energia = 0.0
    dt_hores = INTERVAL_SECONDS / 3600

    # Creates list of acumulated energy
    for p in valors:
        energia += p * dt_hores
        energia_acumulada.append(energia)

    # Creates and shows final graphic
    plt.figure(figsize=(12,6))
    plt.plot(timestamps, energia_acumulada, marker='o', linestyle='-', color='blue', label='Energia acumulada (Wh)')
    plt.title('Energia consumida a partir de la potència en funció del temps')
    plt.xlabel('Temps')
    plt.ylabel('Energia consumida (Wh)')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
