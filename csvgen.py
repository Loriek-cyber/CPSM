import random
import csv
from datetime import datetime, timedelta
import pandas as pd

def genera_dati_incidenti(n, output_csv="incidenti_generati.csv"):
    province_italiane = [
        "Roma", "Milano", "Napoli", "Torino", "Bologna", "Firenze", "Genova",
        "Bari", "Palermo", "Catania", "Venezia", "Verona", "Trieste"
    ]
    tipi_strada = ["Urbana", "Extraurbana", "Autostrada"]
    
    dati = []
    for _ in range(n):
        data_ora = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        provincia = random.choice(province_italiane)
        giorno_settimana = data_ora.strftime('%A')
        tipo_strada = random.choice(tipi_strada)
        numero_feriti = random.randint(0, 10)
        numero_morti = random.choices([0, 1, 2, 3], weights=[90, 8, 1.5, 0.5])[0]
        velocita_media = round(random.uniform(30, 150), 1)

        dati.append([
            data_ora.strftime('%Y-%m-%d %H:%M:%S'),
            provincia,
            giorno_settimana,
            tipo_strada,
            numero_feriti,
            numero_morti,
            velocita_media
        ])
    
    # Salvataggio in CSV
    intestazioni = ["Data_Ora_Incidente", "Provincia", "Giorno_Settimana", "Tipo_Strada", "Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"]
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(intestazioni)
        writer.writerows(dati)

    print(f"{n} entry generate e salvate in '{output_csv}'.")

# ESEMPIO USO
genera_dati_incidenti(5000)
