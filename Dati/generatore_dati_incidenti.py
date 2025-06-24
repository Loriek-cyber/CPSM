import pandas as pd
import random
from datetime import datetime, timedelta

def get_integer_input(prompt, min_val=1):
    """Get validated integer input from user"""
    while True:
        try:
            value = int(input(prompt))
            if value >= min_val:
                return value
            else:
                print(f"Error: Value must be >= {min_val}")
        except ValueError:
            print("Error: Enter a valid integer")

def main():
    """Generate simulated traffic incident CSV data"""
    print("Traffic Incident Data Generator")
    print("=" * 35)
    
    # Get user inputs
    num_records = get_integer_input("Number of incidents to generate: ")
    max_injured = get_integer_input("Max injured per incident: ", 0)
    max_deaths = get_integer_input("Max deaths per incident: ", 0)
    max_speed = get_integer_input("Max estimated speed (km/h): ", 30)
    
    filename = input("Output filename (with .csv): ").strip()
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    # Data for generation
    provinces = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Bologna', 'Genova', 'Bari']
    road_types = ['Urban', 'State', 'Highway']
    days = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    
    # Generate date range (last 3 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)
    
    print(f"\nGenerating {num_records} records...")
    
    records = []
    for _ in range(num_records):
        # Random date in range
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        incident_date = start_date + timedelta(seconds=random_seconds)
        
        record = {
            'Data_Ora_Incidente': incident_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Provincia': random.choice(provinces),
            'Giorno_Settimana': days[incident_date.weekday()],
            'Tipo_Strada': random.choice(road_types),
            'Numero_Feriti': random.randint(0, max_injured),
            'Numero_Morti': random.randint(0, max_deaths),
            'Velocita_Media_Stimata': random.randint(30, max_speed)
        }
        records.append(record)
    
    # Save to CSV
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    
    print(f"Success! Created '{filename}' with {len(df)} records")

if __name__ == "__main__":
    main()