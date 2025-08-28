
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = "bateria_soh.db"

# Reads the dataset information
def llegir_dades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, value FROM soh_data ORDER BY timestamp ASC")
    files = cursor.fetchall()
    conn.close()
    return files

def main():
    # Calls previous function to obtain data
    dades = llegir_dades()
    if not dades:
        print("No s'han trobat dades a la base de dades.")
        return

    # Separes the gained data in lists
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in dades]
    valors = [row[1] for row in dades]

    # Creates and shows final graphic
    plt.figure(figsize=(12,6))
    plt.plot(timestamps, valors, marker='o', linestyle='-', color='blue', label='SoH (%)')
    plt.title('Evolució del State of Health (SoH)')
    plt.xlabel('Temps')
    plt.ylabel('SoH (%)')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
