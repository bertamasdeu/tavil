
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

conn = sqlite3.connect("bateria_soc.db")
cursor = conn.cursor()

cursor.execute("SELECT timestamp, value FROM soc_data ORDER BY timestamp ASC")
resultats = cursor.fetchall()
conn.close()

timestamps = []
valors = []

for timestamp_str, value in resultats:
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    timestamps.append(timestamp)
    valors.append(value)

plt.figure(figsize=(12, 6))
plt.plot(timestamps, valors, marker='o', linestyle='-', color='blue', label="SoC (%)")

plt.title("Evolució del SoC de la bateria")
plt.xlabel("Temps")
plt.ylabel("SoC (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()


