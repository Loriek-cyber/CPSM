import pandas as pd
import os

def prepare_istat_data(input_filepath, output_filepath):
    """
    Loads raw ISTAT road accident data, cleans it, and formats it
    to be compatible with the analysis application.

    Args:
        input_filepath (str): Path to the raw ISTAT CSV file.
        output_filepath (str): Path to save the cleaned CSV file.
    """
    if not os.path.exists(input_filepath):
        print(f"Errore: Il file di input '{input_filepath}' non è stato trovato.")
        print("Assicurati di aver scaricato il file CSV da ISTAT e di averlo inserito nella stessa cartella di questo script.")
        return

    print(f"Loading raw data from {input_filepath}...")
    # ISTAT files can have mixed types, so low_memory=False is safer.
    # They are often semicolon-separated.
    try:
        try:
            # ISTAT files often use latin1 encoding and semicolon separators
            df = pd.read_csv(input_filepath, sep=';', low_memory=False, encoding='latin1')
        except (pd.errors.ParserError, UnicodeDecodeError):
            print("Rilevato possibile separatore diverso dal punto e virgola. Tento con la virgola...")
            df = pd.read_csv(input_filepath, sep=',', low_memory=False, encoding='latin1')
    except Exception as e:
        print(f"Error loading file: {e}")
        print("Please ensure the file path is correct and it's a semicolon- or comma-separated CSV.")
        return

    print("Selecting and renaming columns...")
    # Mapping from ISTAT column names to our application's column names
    column_map = {
        'anno': 'Anno',
        'mese': 'Mese',
        'giorno': 'Giorno',
        'ora': 'Ora',
        'den_prov': 'Provincia',
        'des_giornosett': 'Giorno_Settimana',
        'des_tipostrada': 'Tipo_Strada',
        'tot_feriti': 'Numero_Feriti',
        'tot_morti': 'Numero_Morti',
        'lim_vel': 'Velocita_Media_Stimata' # Using speed limit as a proxy
    }

    missing_cols = [col for col in column_map.keys() if col not in df.columns]
    if missing_cols:
        print(f"Errore: Colonne richieste mancanti nel file CSV: {missing_cols}")
        print(f"Le colonne trovate sono: {list(df.columns)}")
        return

    df_clean = df[list(column_map.keys())].copy()
    df_clean.rename(columns=column_map, inplace=True)

    print("Cleaning data...")
    # ISTAT uses 24 for midnight, which causes errors. Replace with 0.
    if 'Ora' in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean['Ora']):
        df_clean['Ora'] = df_clean['Ora'].replace(24, 0)

    print("Creating 'Data_Ora_Incidente' column...")
    # Combine date and time parts into a single datetime column
    # errors='coerce' will turn invalid dates into NaT (Not a Time)
    # .str.split('.').str[0] handles cases where hour is a float (e.g., '18.0')
    df_clean['Data_Ora_Incidente'] = pd.to_datetime(
        df_clean['Anno'].astype(str) + '-' + df_clean['Mese'].astype(str) + '-' + df_clean['Giorno'].astype(str) + ' ' + df_clean['Ora'].astype(str).str.split('.').str[0] + ':00',
        errors='coerce'
    )

    # Drop rows where datetime conversion failed
    original_rows = len(df_clean)
    df_clean.dropna(subset=['Data_Ora_Incidente'], inplace=True)
    if len(df_clean) < original_rows:
        print(f"Rimosse {original_rows - len(df_clean)} righe con data/ora non valide.")

    print(f"Saving cleaned data to {output_filepath}...")
    df_clean.to_csv(output_filepath, index=False, encoding='utf-8')
    print(f"Done! You can now load '{cleaned_file}' into your application using the 'Carica Dati ISTAT' button.")

if __name__ == '__main__':
    # IMPORTANT: Replace with the actual name of the downloaded ISTAT file
    raw_istat_file = 'incidenti_istat_2022.csv' 
    cleaned_file = 'incidenti_pronti.csv'
    prepare_istat_data(raw_istat_file, cleaned_file)