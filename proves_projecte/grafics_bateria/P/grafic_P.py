
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = "bateria_p.db"

# Reads the dataset information
def llegir_dades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, value FROM p_data ORDER BY timestamp ASC")
    files = cursor.fetchall()
    conn.close()
    return files

def main():
    # Calls previous function to obtain the data
    dades = llegir_dades()
    if not dades:
        print("No s'han trobat dades a la base de dades.")
        return
    
    # Separes the gained data in lists
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in dades]
    valors = [row[1] for row in dades]

    # Creates and shows final graphic
    plt.figure(figsize=(12,6))
    plt.plot(timestamps, valors, marker='o', linestyle='-', color='red', label='P (W)')
    plt.title('Evolució de la potència P')
    plt.xlabel('Temps')
    plt.ylabel('Potència (W)')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
