# ==================================================================================
# SOFTWARE DI ANALISI STATISTICA INCIDENTI STRADALI (v7.1 - Aggregazione temporale)
# ==================================================================================

# --- IMPORTAZIONE DELLE LIBRERIE NECESSARIE ---
import tkinter  # Libreria standard di Python per la creazione di interfacce grafiche (GUI).
from tkinter import filedialog, ttk  # Componenti specifici di tkinter: 'filedialog' per aprire file, 'ttk' per widget moderni.
import customtkinter  # Libreria esterna per creare interfacce grafiche moderne e personalizzabili.
import pandas as pd  # Libreria fondamentale per la manipolazione e l'analisi di dati, specialmente tramite i suoi DataFrame.
import numpy as np  # Libreria per il calcolo numerico, utilizzata per operazioni matematiche e array.
from scipy import stats  # Sottomodulo della libreria SciPy che fornisce un'ampia gamma di funzioni statistiche.
import matplotlib.pyplot as plt  # Libreria per la creazione di grafici e visualizzazioni statiche.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Modulo per integrare i grafici Matplotlib in applicazioni Tkinter.
import random  # Modulo per la generazione di numeri casuali, usato per creare dati di esempio.
from datetime import datetime, timedelta, date  # Moduli per la gestione di date e orari.
import collections  # Fornisce strutture dati specializzate, non usato esplicitamente ma utile per conteggi.
import locale  # Modulo per la gestione delle impostazioni internazionali (es. lingua per nomi di giorni/mesi).

# --- IMPOSTAZIONE DELLA LINGUA ITALIANA ---
# Tenta di impostare la localizzazione in italiano per visualizzare correttamente nomi di mesi e giorni.
try:
    # Imposta la localizzazione per la gestione del tempo in italiano (formato UTF-8).
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    # Se la localizzazione non è disponibile sul sistema, stampa un messaggio di avviso.
    print("Locale 'it_IT.UTF-8' non trovato. Verrà usata una mappatura interna o l'impostazione di default del sistema.")

# =============================================================================
# IMPOSTAZIONI INIZIALI DELL'INTERFACCIA GRAFICA
# =============================================================================
# Imposta il tema dell'applicazione (System, Light, Dark). "System" si adatta a quello del sistema operativo.
customtkinter.set_appearance_mode("System")
# Imposta il tema di colori predefinito per i widget (es. bottoni, slider).
customtkinter.set_default_color_theme("blue")

# =============================================================================
# CLASSE PRINCIPALE DELL'APPLICAZIONE
# =============================================================================
# Definisce la classe App, che eredita da customtkinter.CTk, la finestra principale dell'applicazione.
class App(customtkinter.CTk):
    # --- METODO COSTRUTTORE ---
    def __init__(self):
        # Chiama il costruttore della classe genitore (customtkinter.CTk).
        super().__init__()
        # Imposta il titolo della finestra principale.
        self.title("Software di Analisi Statistica Incidenti Stradali")
        # Imposta le dimensioni iniziali della finestra (larghezza x altezza).
        self.geometry("1200x850")
        # Configura la griglia della finestra: la colonna 0 si espande per riempire lo spazio.
        self.grid_columnconfigure(0, weight=1)
        # Configura la griglia della finestra: la riga 1 (quella con il TabView) si espande verticalmente.
        self.grid_rowconfigure(1, weight=1)
        # Inizializza l'attributo 'df' a None. Conterrà il DataFrame di pandas con i dati caricati.
        self.df = None
        # Inizializza una lista vuota per tenere traccia dei widget dei grafici Matplotlib, per poterli poi eliminare correttamente.
        self.matplotlib_widgets = []

        # Chiama i metodi per configurare i vari pezzi dell'interfaccia.
        self.setup_loading_frame()  # Prepara la sezione per il caricamento dei file.
        self.setup_tab_view()  # Prepara la struttura a schede (tab).
        self.tab_view.set("Dati Forniti")  # Imposta la prima scheda come quella attiva all'avvio.

    # --- CONFIGURAZIONE DELLA SEZIONE DI CARICAMENTO ---
    def setup_loading_frame(self):
        # Crea un frame (contenitore) per i controlli di caricamento.
        self.frame_caricamento = customtkinter.CTkFrame(self)
        # Posiziona il frame nella griglia della finestra principale.
        self.frame_caricamento.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        # Configura le colonne del frame di caricamento affinché si espandano in modo uniforme.
        self.frame_caricamento.grid_columnconfigure((0, 1, 2), weight=1)
        # Crea un'etichetta per mostrare lo stato del file caricato.
        self.label_file = customtkinter.CTkLabel(self.frame_caricamento, text="Nessun dato caricato.", text_color="gray")
        # Posiziona l'etichetta nella griglia del suo frame.
        self.label_file.grid(row=0, column=0, padx=20, pady=20)
        # Crea il bottone per caricare un file CSV.
        self.bottone_carica_csv = customtkinter.CTkButton(self.frame_caricamento, text="Carica File CSV", command=self.carica_csv)
        # Posiziona il bottone nella griglia.
        self.bottone_carica_csv.grid(row=0, column=1, padx=20, pady=20)
        # Crea il bottone per usare dati di esempio generati casualmente.
        self.bottone_dati_esempio = customtkinter.CTkButton(self.frame_caricamento, text="Usa Dati Simulati", command=self.carica_dati_esempio)
        # Posiziona il bottone nella griglia.
        self.bottone_dati_esempio.grid(row=0, column=2, padx=20, pady=20)

    # --- CONFIGURAZIONE DELLA VISTA A SCHEDE (TAB) ---
    def setup_tab_view(self):
        # Crea il widget TabView che conterrà tutte le schede di analisi.
        self.tab_view = customtkinter.CTkTabview(self, width=250, command=self.on_tab_change)
        # Posiziona il TabView nella griglia della finestra principale, facendolo espandere in tutte le direzioni.
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        # Definisce i nomi delle schede da creare.
        tabs = ["Dati Forniti", "Calcolo Dati", "Campionatura", "Analisi Descrittiva", "Analisi Bivariata", "Analisi Inferenziale"]
        # Itera sulla lista dei nomi e aggiunge ogni scheda al TabView.
        for tab in tabs: self.tab_view.add(tab)
        # Chiama i metodi specifici per configurare il contenuto di ogni singola scheda.
        self.setup_tab_dati_forniti()
        self.setup_tab_calcolo_dati()
        self.setup_tab_campionatura()
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

    # --- FUNZIONE PER CARICARE DATI DA FILE CSV ---
    def carica_csv(self):
        # Apre una finestra di dialogo per permettere all'utente di selezionare un file CSV.
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        # Se l'utente non seleziona un file e chiude la finestra, la funzione termina.
        if not filepath: return
        # Inizia un blocco try-except per gestire eventuali errori durante la lettura del file.
        try:
            # Prova a leggere il file CSV assumendo che il separatore sia il punto e virgola ';'.
            try:
                df = pd.read_csv(filepath, sep=';')
                # Se dopo la lettura con ';' il DataFrame ha una sola colonna, è probabile che il separatore fosse la virgola ','.
                if df.shape[1] == 1:
                    # Rilegge lo stesso file usando la virgola come separatore.
                    df = pd.read_csv(filepath, sep=',')
            # Se il primo tentativo di lettura fallisce (es. per un errore di parsing), prova direttamente con la virgola.
            except:
                 df = pd.read_csv(filepath, sep=',')

            # Estrae solo il nome del file dal percorso completo.
            filename = filepath.split('/')[-1]
            # Aggiorna l'etichetta mostrando il nome del file e il numero di record caricati.
            self.label_file.configure(text=f"Caricato: {filename} ({len(df)} record)", text_color='white')
            # Chiama la funzione per inizializzare e pre-elaborare i dati del DataFrame.
            self.inizializza_dati(df)
            # Imposta la vista sulla scheda "Dati Forniti" per mostrare subito i dati caricati.
            self.tab_view.set("Dati Forniti")
        # Se si verifica un qualsiasi errore durante il processo, lo cattura.
        except Exception as e:
            # Aggiorna l'etichetta per mostrare un messaggio di errore.
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    # --- FUNZIONE PER CARICARE DATI DI ESEMPIO SIMULATI ---
    def carica_dati_esempio(self):
        # Inizia un blocco try-except per gestire errori durante la generazione dei dati.
        try:
            records = []  # Lista vuota per contenere i record (righe) dei dati simulati.
            # Liste di valori possibili per le variabili categoriche.
            province = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Catania', 'Salerno', 'Bologna', 'Venezia', 'Bari']
            tipi_strada = ['Urbana', 'Statale', 'Autostrada']
            # Mappa per convertire il numero del giorno della settimana (0=Lunedì) nel nome corrispondente.
            giorni_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}

            end_date = datetime.now()  # La data finale per la generazione è oggi.
            start_date = end_date - timedelta(days=730)  # La data iniziale è due anni fa.
            # Cicla 500 volte per creare 500 record di incidenti.
            for _ in range(500):
                # Genera un numero casuale di secondi nell'intervallo di due anni.
                random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
                # Crea una data e ora casuale aggiungendo i secondi casuali alla data di inizio.
                random_date = start_date + timedelta(seconds=random_seconds)

                # Simula la presenza di valori mancanti per 'Tipo_Strada' con una probabilità del 5%.
                if random.random() < 0.05:
                    strada = None
                else:
                    # Altrimenti, sceglie un tipo di strada a caso dalla lista.
                    strada = random.choice(tipi_strada)

                velocita = None  # Inizializza la velocità a None.
                # Assegna una velocità casuale in base al tipo di strada, simulando limiti diversi.
                if strada == 'Urbana': velocita = random.randint(30, 65)
                elif strada == 'Statale': velocita = random.randint(60, 95)
                elif strada == 'Autostrada': velocita = random.randint(100, 140)

                # Genera il numero di morti con probabilità ponderate (molto più probabile che sia 0).
                numero_morti = random.choices([0, 1, 2, 3], weights=[94, 4, 1.5, 0.5], k=1)[0]
                # Genera il numero di feriti con probabilità ponderate.
                numero_feriti = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 40, 25, 15, 5, 5], k=1)[0]
                # Logica semplice: se ci sono morti, ci sono almeno altrettanti feriti.
                if numero_morti > 0: numero_feriti += numero_morti

                # Aggiunge un dizionario (che rappresenta una riga) alla lista dei record.
                records.append({'Data_Ora_Incidente': random_date, 'Provincia': random.choice(province), 'Giorno_Settimana': giorni_map[random_date.weekday()], 'Tipo_Strada': strada, 'Numero_Feriti': numero_feriti, 'Numero_Morti': numero_morti, 'Velocita_Media_Stimata': velocita})

            # Crea un DataFrame di pandas a partire dalla lista di dizionari.
            df = pd.DataFrame(records)
            # Aggiorna l'etichetta per confermare il caricamento dei dati simulati.
            self.label_file.configure(text=f"Caricati {len(df)} record simulati.", text_color="white")
            # Chiama la funzione per inizializzare e pre-elaborare i dati.
            self.inizializza_dati(df)
        # Se si verifica un errore durante la generazione.
        except Exception as e:
            # Mostra un messaggio di errore nell'etichetta.
            self.label_file.configure(text=f"Errore Dati Esempio: {e}", text_color="red")

    # --- FUNZIONE DI PRE-ELABORAZIONE E INIZIALIZZAZIONE DEI DATI ---
    def inizializza_dati(self, df, variabile_da_mantenere=None):
        # Crea una copia del DataFrame ricevuto per evitare di modificare l'originale (buona pratica).
        self.df = df.copy()
        # Se esiste la colonna 'Data_Ora_Incidente', la converte in formato datetime di pandas.
        # 'errors=coerce' trasformerà in 'NaT' (Not a Time) le date non valide, senza bloccare il programma.
        if 'Data_Ora_Incidente' in self.df.columns:
            self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce')
        # Itera su una lista di colonne che dovrebbero essere numeriche.
        for col in ['Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata']:
            # Se la colonna esiste nel DataFrame.
            if col in self.df.columns:
                # La converte in tipo numerico. 'errors=coerce' trasformerà in 'NaN' (Not a Number) i valori non numerici.
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        original_rows = len(self.df)  # Salva il numero di righe originali.
        # Rimuove le righe che hanno valori mancanti ('NaT' o 'NaN') nelle colonne essenziali 'Data_Ora_Incidente' o 'Provincia'.
        self.df.dropna(subset=['Data_Ora_Incidente', 'Provincia'], inplace=True)
        dropped_rows = original_rows - len(self.df)  # Calcola quante righe sono state eliminate.
        # Se sono state eliminate delle righe, stampa un messaggio informativo nella console.
        if dropped_rows > 0:
            print(f"Rimosse {dropped_rows} righe con valori mancanti in 'Data_Ora_Incidente' o 'Provincia'.")

        # Se il DataFrame è vuoto dopo la pulizia, mostra un errore e si ferma.
        if self.df.empty:
            self.label_file.configure(text="Errore: Nessun dato valido trovato.", text_color="orange")
            self.df = None  # Resetta il DataFrame a None.
            return
        # Estrae l'ora e la data da 'Data_Ora_Incidente' e le salva in nuove colonne per facilitare le analisi.
        self.df['Ora'] = self.df['Data_Ora_Incidente'].dt.hour
        self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
        # Popola la tabella nella prima scheda con i dati puliti.
        self.popola_tabella_dati()
        # Aggiorna i menu a tendina (ComboBox) in tutta l'applicazione con le colonne del nuovo dataset.
        self.aggiorna_selettori(variabile_da_mantenere)

    # --- FUNZIONE PER AGGIORNARE I MENU A TENDINA ---
    def aggiorna_selettori(self, variabile_da_mantenere=None):
        # Se non ci sono dati, esce.
        if self.df is None: return
        # Estrae i nomi delle colonne numeriche, di testo/categoriche e di data/ora.
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        # Costruisce una lista di tutte le colonne utili per l'analisi descrittiva, escludendo 'Giorno' che è ridondante.
        all_columns = [col for col in datetime_cols + object_columns + numeric_columns if col != 'Giorno']

        # Estrae le province uniche e le ordina alfabeticamente per i selettori specifici.
        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []
        
        # --- Aggiornamento dei Selettori nelle varie schede ---
        # Analisi Descrittiva:
        self.selettore_var_descrittiva.configure(values=all_columns)
        # Se una variabile specifica deve essere mantenuta (es. dopo una modifica) e esiste ancora, la seleziona.
        if variabile_da_mantenere and variabile_da_mantenere in all_columns: self.selettore_var_descrittiva.set(variabile_da_mantenere)
        # Altrimenti, se ci sono colonne, seleziona la prima della lista.
        elif all_columns: self.selettore_var_descrittiva.set(all_columns[0])
        
        # Calcolo Dati e Campionatura (solo variabili numeriche):
        self.selettore_var_calcolo.configure(values=numeric_columns)
        self.selettore_var_campionatura.configure(values=numeric_columns)
        if numeric_columns: 
            self.selettore_var_calcolo.set(numeric_columns[0])
            self.selettore_var_campionatura.set(numeric_columns[0])

        # Analisi Bivariata (solo variabili numeriche per il setup iniziale, poi esteso):
        # NOTA: Il codice è stato poi esteso per gestire anche variabili categoriche.
        self.selettore_var_biv_x.configure(values=all_columns) # Modificato per includere tutte le colonne
        self.selettore_var_biv_y.configure(values=all_columns) # Modificato per includere tutte le colonne
        if len(all_columns) > 1:
            self.selettore_var_biv_x.set(all_columns[0])
            self.selettore_var_biv_y.set(all_columns[1])
        elif all_columns:
            self.selettore_var_biv_x.set(all_columns[0])
            self.selettore_var_biv_y.set(all_columns[0])
        
        # Analisi Inferenziale (province uniche):
        self.selettore_provincia_poisson.configure(values=province_uniche)
        self.selettore_provincia_ci.configure(values=province_uniche)
        if province_uniche:
            self.selettore_provincia_poisson.set(province_uniche[0])
            self.selettore_provincia_ci.set(province_uniche[0])
        
        # Esegue un piccolo ritardo prima di chiamare on_tab_change per assicurarsi che l'interfaccia sia aggiornata.
        self.after(50, self.on_tab_change)


    # --- FUNZIONE TRIGGERATA AL CAMBIO DI SCHEDA ---
    def on_tab_change(self, *args):
        # Questa funzione è stata svuotata. Le analisi ora vengono eseguite al cambio
        # di selezione nei ComboBox o al click sui bottoni di refresh, rendendo l'UI più reattiva.
        pass

    # --- FUNZIONE HELPER PER CREARE TITOLI DI SEZIONE STANDARDIZZATI ---
    def _crea_titolo_sezione(self, parent, testo_titolo, testo_info, testo_guida=None, row=None, columnspan=1):
        # Se è specificata una riga, crea il frame del titolo e lo posiziona con grid.
        if row is not None:
            frame_titolo = customtkinter.CTkFrame(parent, fg_color="transparent")
            frame_titolo.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(15, 5))
        # Altrimenti, lo crea e lo impacchetta con pack (più semplice).
        else:
            frame_titolo = customtkinter.CTkFrame(parent)
            frame_titolo.pack(fill="x", expand=True, padx=10, pady=(10,0))
        
        # Crea un frame interno per allineare titolo e bottoni.
        inner_frame = customtkinter.CTkFrame(frame_titolo, fg_color="transparent")
        inner_frame.pack(pady=5)
        
        # Crea l'etichetta del titolo con un font più grande e in grassetto.
        customtkinter.CTkLabel(inner_frame, text=testo_titolo, font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        # Se è fornito un testo informativo, crea il bottone "i".
        if testo_info:
            # Il comando lambda cattura il testo_info specifico per questo bottone.
            customtkinter.CTkButton(inner_frame, text="i", command=lambda: self.show_info(f"Informazioni: {testo_titolo}", testo_info), width=28, height=28, corner_radius=14).pack(side="left", padx=(0, 5))
        # Se è fornito un testo di guida, crea il bottone "?".
        if testo_guida:
            customtkinter.CTkButton(inner_frame, text="?", command=lambda: self.show_info("Guida alla Lettura", testo_guida), width=28, height=28, corner_radius=14).pack(side="left")


    # --- FUNZIONE HELPER PER CREARE UNA TABELLA (TREEVIEW) ---
    def _crea_tabella_treeview(self, parent, df, title="Dati"):
        # Crea un frame contenitore per la tabella e il suo titolo.
        frame = customtkinter.CTkFrame(parent)
        frame.pack(fill="x", expand=True, padx=5, pady=5)
        
        # Aggiunge un'etichetta come titolo della tabella.
        customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=(5,5), padx=10, anchor="w")

        # Crea un frame interno per la tabella e le sue barre di scorrimento.
        table_frame = customtkinter.CTkFrame(frame)
        table_frame.pack(fill="x", expand=True, padx=5, pady=(0,5))
        table_frame.grid_columnconfigure(0, weight=1) # La colonna della tabella si espande.

        # Applica uno stile al Treeview per migliorare l'aspetto.
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Calibri', 11))
        style.configure("Treeview.Heading", font=('Calibri', 12, 'bold'))
        
        # Prende i nomi delle colonne dal DataFrame.
        columns = df.columns.tolist()
        # Crea il widget Treeview, che è la vera e propria tabella.
        table = ttk.Treeview(table_frame, columns=columns, show='headings', height=min(len(df), 10))
        
        # Itera sulle colonne per configurare le intestazioni.
        for col in columns:
            table.heading(col, text=col) # Imposta il testo dell'intestazione.
            table.column(col, anchor='center', width=120, minwidth=100) # Imposta allineamento e larghezza.

        # Itera sulle righe del DataFrame per popolarle nella tabella.
        for _, row in df.iterrows():
            formatted_row = []
            # Formatta i valori float con 4 cifre decimali per una migliore leggibilità.
            for val in row:
                if isinstance(val, float):
                    formatted_row.append(f"{val:.4f}")
                else:
                    formatted_row.append(val)
            # Inserisce la riga formattata nella tabella.
            table.insert("", "end", values=formatted_row)

        # Crea e configura la barra di scorrimento verticale.
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=vsb.set)

        # Posiziona la tabella e la barra di scorrimento nella griglia del loro frame.
        table.grid(row=0, column=0, sticky='ew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Restituisce il frame principale, utile se si vuole modificare ulteriormente.
        return frame


    # --- FUNZIONE PER MOSTRARE FINESTRE DI INFORMAZIONE ---
    def show_info(self, title, message):
        # Crea una nuova finestra "Toplevel", che appare sopra la finestra principale.
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title) # Imposta il titolo della finestra di aiuto.
        info_window.transient(self) # Lega la finestra di aiuto a quella principale.
        info_window.geometry("550x450") # Imposta le dimensioni della finestra.
        
        # Crea una casella di testo per mostrare il messaggio di aiuto.
        textbox = customtkinter.CTkTextbox(info_window, wrap="word", font=customtkinter.CTkFont(size=14))
        textbox.pack(padx=20, pady=20, fill="both", expand=True) # La fa espandere per riempire la finestra.
        textbox.insert("1.0", message) # Inserisce il testo.
        textbox.configure(state="disabled") # Rende il testo non modificabile dall'utente.

        # Crea un bottone per chiudere la finestra di aiuto.
        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")


    # --- FUNZIONE PER PULIRE I FRAME DAI GRAFICI MATPLOTLIB ---
    def pulisci_frame(self, frame):
        # Itera su tutti i widget dei grafici Matplotlib che sono stati creati.
        for widget in self.matplotlib_widgets:
            # Se il widget grafico esiste ancora nell'interfaccia...
            if widget.get_tk_widget().winfo_exists():
                # ...lo distrugge per liberare memoria.
                widget.get_tk_widget().destroy()
        # Resetta la lista dei widget dei grafici.
        self.matplotlib_widgets = []
        # Itera su tutti gli altri widget figli del frame specificato e li distrugge.
        # Questo pulisce completamente il frame prima di disegnarci sopra nuovi risultati.
        for widget in frame.winfo_children():
            widget.destroy()

    # --- CONFIGURAZIONE DELLA SCHEDA "DATI FORNITI" ---
    def setup_tab_dati_forniti(self):
        tab = self.tab_view.tab("Dati Forniti")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(0, weight=1)
        data_frame = customtkinter.CTkFrame(tab); data_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        data_frame.grid_columnconfigure(0, weight=1); data_frame.grid_rowconfigure(0, weight=1)
        style = ttk.Style(); style.configure("Treeview", rowheight=25, font=('Calibri', 11)); style.configure("Treeview.Heading", font=('Calibri', 12,'bold'))
        columns = ('Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata')
        self.data_table = ttk.Treeview(data_frame, columns=columns, show='headings')
        for col in columns:
            width = {'Data_Ora_Incidente': 160}.get(col, 120); anchor = 'center'
            self.data_table.column(col, width=width, anchor=anchor); self.data_table.heading(col, text=col)
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_table.yview); hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.data_table.xview)
        self.data_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set); self.data_table.grid(row=0, column=0, sticky='nsew'); vsb.grid(row=0, column=1, sticky='ns'); hsb.grid(row=1, column=0, sticky='ew')

    # --- CONFIGURAZIONE DELLA SCHEDA "CALCOLO DATI" ---
    def setup_tab_calcolo_dati(self):
        tab = self.tab_view.tab("Calcolo Dati")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        
        self.frame_controlli_calcolo = customtkinter.CTkFrame(tab)
        self.frame_controlli_calcolo.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.frame_controlli_calcolo.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(self.frame_controlli_calcolo, text="Seleziona una variabile numerica:").grid(row=0, column=0, padx=(10,5), pady=5)
        self.selettore_var_calcolo = customtkinter.CTkComboBox(self.frame_controlli_calcolo, values=[], command=self.esegui_calcolo_dati)
        self.selettore_var_calcolo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.bottone_refresh_calcolo = customtkinter.CTkButton(self.frame_controlli_calcolo, text="🔄", command=self.esegui_calcolo_dati, width=35, height=35)
        self.bottone_refresh_calcolo.grid(row=0, column=2, padx=(5,10), pady=5)

        self.frame_risultati_calcolo = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Calcoli Statistici sulla Popolazione")
        self.frame_risultati_calcolo.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_calcolo.grid_columnconfigure(0, weight=1)

    # --- CONFIGURAZIONE DELLA SCHEDA "CAMPIONATURA" ---
    def setup_tab_campionatura(self):
        tab = self.tab_view.tab("Campionatura")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(frame_controlli, text="Variabile:").grid(row=0, column=0, padx=(10,5))
        self.selettore_var_campionatura = customtkinter.CTkComboBox(frame_controlli, values=[])
        self.selettore_var_campionatura.grid(row=0, column=1, padx=5, sticky="ew")
        
        customtkinter.CTkLabel(frame_controlli, text="Dim. Campione (n):").grid(row=0, column=2, padx=(10,5))
        self.entry_dim_campione = customtkinter.CTkEntry(frame_controlli, placeholder_text="es. 100", width=120)
        self.entry_dim_campione.grid(row=0, column=3, padx=5)

        self.bottone_esegui_campionatura = customtkinter.CTkButton(frame_controlli, text="Estrai Campione e Calcola", command=self.esegui_campionatura)
        self.bottone_esegui_campionatura.grid(row=0, column=4, padx=(10, 10))

        self.frame_risultati_campionatura = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Calcoli Statistici sul Campione")
        self.frame_risultati_campionatura.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_campionatura.grid_columnconfigure(0, weight=1)

    # --- CONFIGURAZIONE DELLA SCHEDA "ANALISI DESCRITTIVA" ---
    def setup_tab_descrittiva(self):
        tab = self.tab_view.tab("Analisi Descrittiva")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        
        self.frame_controlli_descrittiva = customtkinter.CTkFrame(tab)
        self.frame_controlli_descrittiva.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.frame_controlli_descrittiva.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(self.frame_controlli_descrittiva, text="Seleziona una variabile:").grid(row=0, column=0, padx=(10,5), pady=5)
        self.selettore_var_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_descrittiva, values=[], command=self.esegui_analisi_descrittiva)
        self.selettore_var_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.frame_controlli_contestuali = customtkinter.CTkFrame(self.frame_controlli_descrittiva, fg_color="transparent")
        self.frame_controlli_contestuali.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.frame_controlli_contestuali.grid_columnconfigure(3, weight=1)

        self.label_andamento = customtkinter.CTkLabel(self.frame_controlli_contestuali, text="Aggregazione:")
        self.selettore_andamento = customtkinter.CTkComboBox(self.frame_controlli_contestuali, 
                                                             values=['Mensile', 'Giornaliero', 'Annuale', 'Distribuzione Oraria', 'Distribuzione Settimanale'],
                                                             command=self.esegui_analisi_descrittiva)
        self.selettore_andamento.set('Mensile')

        self.label_tipo_grafico = customtkinter.CTkLabel(self.frame_controlli_contestuali, text="Tipo Grafico:")
        self.selettore_grafico_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_contestuali, values=['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste'], command=self.esegui_analisi_descrittiva)
        self.selettore_grafico_descrittiva.set('Barre')
        
        self.bottone_refresh_descrittiva = customtkinter.CTkButton(self.frame_controlli_descrittiva, text="🔄", command=self.esegui_analisi_descrittiva, width=35, height=35)
        self.bottone_refresh_descrittiva.grid(row=0, column=3, padx=(5, 10), pady=5)

        self.frame_risultati_descrittiva = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Analisi Descrittiva")
        self.frame_risultati_descrittiva.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)

    # --- CONFIGURAZIONE DELLA SCHEDA "ANALISI BIVARIATA" ---
    def setup_tab_bivariata(self):
        tab = self.tab_view.tab("Analisi Bivariata")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab); frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure((1, 3), weight=1)
        customtkinter.CTkLabel(frame_controlli, text="Variabile X:").grid(row=0, column=0, padx=(10,5), pady=5)
        self.selettore_var_biv_x = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_analisi_bivariata)
        self.selettore_var_biv_x.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Variabile Y:").grid(row=0, column=2, padx=(10,5), pady=5)
        self.selettore_var_biv_y = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_analisi_bivariata)
        self.selettore_var_biv_y.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.bottone_refresh_bivariata = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_analisi_bivariata, width=35, height=35)
        self.bottone_refresh_bivariata.grid(row=0, column=4, padx=(5,10), pady=5)
        self.frame_risultati_bivariata = customtkinter.CTkFrame(tab)
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1)

    # --- CONFIGURAZIONE DELLA SCHEDA "ANALISI INFERENZIALE" ---
    def setup_tab_inferenziale(self):
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll_frame = customtkinter.CTkScrollableFrame(tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # --- TESTI DI AIUTO AMPLIATI ---
        info_poisson = ("Il Modello di Poisson è un modello di probabilità per variabili discrete che descrive la probabilità che un dato numero di eventi (k) si verifichi in un intervallo fisso di tempo o spazio.\n\n"
                        "Assunzioni Fondamentali:\n"
                        "1. Indipendenza: Il verificarsi di un evento non influenza la probabilità che se ne verifichi un secondo.\n"
                        "2. Tasso Costante (λ): La frequenza media con cui gli eventi si verificano è costante per l'intervallo considerato.\n"
                        "3. Non-Simultaneità: Due eventi non possono verificarsi esattamente nello stesso istante.\n\n"
                        "Applicazione Pratica:\n"
                        "In questo contesto, stimiamo il tasso medio di incidenti (λ, lambda) per una data provincia e fascia oraria, basandoci sui dati storici. Successivamente, usiamo questo tasso per calcolare la probabilità di osservare un numero esatto 'k' di incidenti in un futuro giorno. Questo è cruciale per la valutazione del rischio, la gestione delle pattuglie e la pianificazione delle risorse di emergenza.")
        
        frame_poisson = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_poisson.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_poisson.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_poisson, "Modello di Poisson", info_poisson, row=0, columnspan=3)
        # (resto del setup del frame Poisson)
        customtkinter.CTkLabel(frame_poisson, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_poisson = customtkinter.CTkComboBox(frame_poisson, values=[])
        self.selettore_provincia_poisson.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Ora o Fascia Oraria (es. 14 o 8-17):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_ora_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Inserisci un'ora singola (0-23) o un range")
        self.entry_ora_poisson.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Numero incidenti (k):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_k_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Es. 2")
        self.entry_k_poisson.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_poisson, text="Calcola Probabilità", command=self.esegui_poisson).grid(row=4, column=0, padx=10, pady=10)
        self.risultato_poisson_textbox = customtkinter.CTkTextbox(frame_poisson, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_poisson_textbox.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.risultato_poisson_textbox.configure(state="disabled")

        info_ttest = ("Il Test T per Campioni Indipendenti è un test statistico inferenziale usato per confrontare le medie di due gruppi indipendenti, al fine di determinare se la differenza osservata tra queste medie è statisticamente significativa o se potrebbe essere dovuta al caso.\n\n"
                      "Sistema di Ipotesi:\n"
                      "1. Ipotesi Nulla (H₀): Le medie delle due popolazioni da cui i campioni sono stati estratti sono uguali (μ₁ = μ₂). Qualsiasi differenza misurata nei campioni è puramente casuale.\n"
                      "2. Ipotesi Alternativa (H₁): Le medie delle due popolazioni sono diverse (μ₁ ≠ μ₂).\n\n"
                      "Interpretazione del p-value:\n"
                      "Il p-value è la probabilità di osservare una differenza tra le medie campionarie pari o più estrema di quella effettivamente misurata, assumendo che l'ipotesi nulla (H₀) sia vera. Un p-value basso (convenzionalmente < 0.05) indica che l'osservazione è molto improbabile sotto H₀, fornendo quindi forte evidenza per rigettare H₀ e accettare l'ipotesi alternativa (H₁). In breve, un p-value basso suggerisce che la differenza è 'reale' e non casuale.\n\n"
                      "Nota: Questo software utilizza il Test T di Welch, che non assume che i due gruppi abbiano la stessa varianza, rendendolo più robusto e applicabile in un maggior numero di contesti reali.")
        
        frame_ttest = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ttest.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        frame_ttest.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_ttest, "Test T per Campioni Indipendenti", info_ttest, row=0, columnspan=2)
        # (resto del setup del frame T-Test)
        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0))
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        self.risultato_ttest_textbox = customtkinter.CTkTextbox(frame_ttest, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_ttest_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ttest_textbox.configure(state="disabled")

        info_ci = ("Un Intervallo di Confidenza (IC) è un range di valori, calcolato a partire da dati campionari, che si stima possa contenere con un certo grado di fiducia il vero valore di un parametro sconosciuto della popolazione (es. la media reale, μ).\n\n"
                   "Cosa significa 'Livello di Fiducia del 95%'?\n"
                   "L'interpretazione corretta è di natura frequentista: NON significa che c'è una probabilità del 95% che il vero parametro μ cada in *questo specifico* intervallo calcolato. Significa che, se ripetessimo il nostro processo di campionamento un numero infinito di volte, il 95% degli intervalli di confidenza così costruiti conterrebbe il vero valore del parametro della popolazione.\n\n"
                   "Fattori che influenzano l'ampiezza dell'intervallo:\n"
                   "1. Livello di Confidenza: Una fiducia maggiore (es. 99% vs 95%) richiede un intervallo più ampio per essere più 'sicuri'.\n"
                   "2. Dimensione del Campione (n): Un campione più grande porta a una stima più precisa, e quindi a un intervallo più stretto.\n"
                   "3. Variabilità dei Dati (Deviazione Standard): Dati più dispersi producono intervalli più ampi.\n\n"
                   "Utilità: L'IC fornisce una misura indispensabile della precisione di una stima puntuale (es. la media campionaria). Un intervallo stretto indica una stima molto precisa, mentre uno ampio riflette una maggiore incertezza.")
        
        frame_ci = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ci.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        frame_ci.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_ci, "Intervallo di Confidenza", info_ci, row=0, columnspan=2)
        # (resto del setup del frame Intervallo di Confidenza)
        customtkinter.CTkLabel(frame_ci, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_ci = customtkinter.CTkComboBox(frame_ci, values=[])
        self.selettore_provincia_ci.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_ci, text="Livello Confidenza (%):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_livello_ci = customtkinter.CTkEntry(frame_ci, placeholder_text="Es. 95")
        self.entry_livello_ci.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_ci, text="Calcola Intervallo", command=self.esegui_ci).grid(row=3, column=0, padx=10, pady=10, sticky="n")
        self.risultato_ci_textbox = customtkinter.CTkTextbox(frame_ci, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_ci_textbox.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ci_textbox.configure(state="disabled")

    # --- FUNZIONE PER POPOLARE LA TABELLA INIZIALE CON I DATI ---
    def popola_tabella_dati(self):
        # Pulisce la tabella da eventuali dati precedenti.
        for item in self.data_table.get_children(): self.data_table.delete(item)
        # Se non ci sono dati, termina la funzione.
        if self.df is None or self.df.empty: return
        # Definisce le colonne da mostrare e si assicura che esistano nel DataFrame.
        cols_da_mostrare = [col for col in ['Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata'] if col in self.df.columns]
        # Crea un DataFrame di visualizzazione con solo le colonne necessarie.
        display_df = self.df[cols_da_mostrare].copy()
        # Ordina i dati per data decrescente (i più recenti in alto).
        display_df = display_df.sort_values(by='Data_Ora_Incidente', ascending=False)
        # Formatta la colonna della data in una stringa più leggibile.
        display_df['Data_Ora_Incidente'] = display_df['Data_Ora_Incidente'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Itera sulle prime 500 righe (per non appesantire l'interfaccia) e le inserisce nella tabella.
        for _, row in display_df.head(500).iterrows(): self.data_table.insert("", "end", values=list(row))

    # --- FUNZIONE PER ESEGUIRE I CALCOLI STATISTICI SULLA POPOLAZIONE ---
    def esegui_calcolo_dati(self, *args):
        # Pulisce il frame dei risultati da analisi precedenti.
        self.pulisci_frame(self.frame_risultati_calcolo)
        # Se non ci sono dati, esce.
        if self.df is None: return
        # Ottiene la variabile selezionata dall'utente.
        variable = self.selettore_var_calcolo.get()
        # Se nessuna variabile è selezionata, esce.
        if not variable: return

        # Seleziona i dati della variabile, rimuovendo i valori mancanti.
        data = self.df[variable].dropna()
        # Se non ci sono dati validi per quella variabile, mostra un messaggio.
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_calcolo, text="Nessun dato disponibile per la variabile selezionata.", text_color="orange").pack(pady=20)
            return
        
        # --- TESTI DI AIUTO AMPLIATI ---
        title = "Analisi sulla Popolazione"
        info = ("In statistica, la 'popolazione' si riferisce all'intero insieme di osservazioni su cui si desidera trarre conclusioni. In questo contesto, la popolazione è costituita da tutti i record presenti nel file caricato.\n\nQuesta sezione calcola i 'parametri' della popolazione, ovvero le misure descrittive (media, varianza, etc.) che descrivono in modo esatto e completo il dataset fornito. Non si tratta di stime, ma di valori reali e definitivi per i dati a disposizione.")
        guida = ("Questa analisi fornisce una fotografia precisa delle caratteristiche del tuo dataset.\n\n"
                 "Interpretazione degli Indici:\n"
                 "- Indici di Posizione: Descrivono il 'centro' dei dati (Media, Mediana, Moda).\n"
                 "- Indici di Variabilità: Misurano la dispersione dei dati (Varianza, Deviazione Standard, Range). Una variabilità alta indica dati molto sparpagliati.\n"
                 "- Indici di Forma: Definiscono la forma della distribuzione. L'Asimmetria (Skewness) misura la simmetria, la Curtosi (Kurtosis) l'altezza dei picchi e la pesantezza delle code.\n\n"
                 "Questi valori sono la 'verità' per il tuo dataset e servono come benchmark per confrontare i risultati ottenuti da un campione (nella scheda 'Campionatura').")
        
        # Chiama la funzione interna che esegue l'analisi numerica dettagliata.
        self._esegui_analisi_numerica_dettagliata(self.frame_risultati_calcolo, data, variable, title, info, guida)

    # --- FUNZIONE PER ESEGUIRE L'ANALISI SU UN CAMPIONE ---
    def esegui_campionatura(self):
        # Pulisce il frame dei risultati.
        self.pulisci_frame(self.frame_risultati_campionatura)
        if self.df is None: return
        # Ottiene la variabile e la dimensione del campione inserite dall'utente.
        variable = self.selettore_var_campionatura.get()
        n_str = self.entry_dim_campione.get()
        
        # Controlla se i campi sono stati compilati.
        if not variable or not n_str:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text="Selezionare una variabile e inserire la dimensione del campione.", text_color="orange").pack(pady=20)
            return

        # Tenta di convertire la dimensione del campione in un numero intero.
        try:
            n = int(n_str)
            if n <= 0: raise ValueError("La dimensione del campione deve essere positiva.")
        except ValueError as e:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text=f"Errore: Inserire un numero intero valido per la dimensione del campione.\n({e})", text_color="orange").pack(pady=20)
            return

        # Seleziona i dati validi per la variabile.
        data = self.df[variable].dropna()
        # Controlla che la dimensione del campione non sia maggiore dei dati disponibili.
        if n > len(data):
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text=f"Errore: La dimensione del campione ({n}) non può superare il numero di dati disponibili ({len(data)}).", text_color="orange").pack(pady=20)
            return
        
        # Estrae un campione casuale di dimensione 'n' senza reinserimento.
        campione = data.sample(n=n, random_state=None) # random_state=None assicura un'estrazione diversa ogni volta.
        
        # --- TESTI DI AIUTO AMPLIATI ---
        title = f"Analisi su un Campione Casuale (n={n})"
        info = ("Il campionamento è il processo di selezione di un sottoinsieme (campione) da una popolazione più grande. L'obiettivo della statistica inferenziale è utilizzare le informazioni del campione per fare deduzioni (inferenze) sulle caratteristiche dell'intera popolazione.\n\nLe misure calcolate su un campione (es. media campionaria) sono chiamate 'statistiche' e sono utilizzate come stime dei 'parametri' della popolazione. A causa della casualità dell'estrazione, ogni campione darà risultati leggermente diversi (variabilità campionaria).")
        guida = ("I risultati di questa analisi sono stime, non valori esatti.\n\n"
                 "Cosa osservare:\n"
                 "- Confronto: Compara la media e la deviazione standard di questo campione con i parametri della popolazione calcolati nella scheda 'Calcolo Dati'. Nota la differenza: questa è la variabilità campionaria.\n"
                 "- Legge dei Grandi Numeri: Prova ad aumentare la dimensione del campione 'n'. Noterai che le statistiche del campione (es. la media campionaria) tenderanno a convergere verso i veri parametri della popolazione. Questo dimostra che campioni più grandi forniscono stime più affidabili.\n"
                 "- Ripetibilità: Clicca di nuovo il bottone 'Estrai'. Verrà estratto un nuovo campione e i risultati cambieranno leggermente, illustrando ancora la natura casuale del campionamento.")

        # Chiama la funzione che esegue l'analisi numerica dettagliata, ma questa volta sul campione.
        self._esegui_analisi_numerica_dettagliata(self.frame_risultati_campionatura, campione, variable, title, info, guida)

    # --- FUNZIONE RIUTILIZZABILE PER L'ANALISI NUMERICA (SIA POPOLAZIONE CHE CAMPIONE) ---
    def _esegui_analisi_numerica_dettagliata(self, container, data_series, variable_name, title, info_text, guide_text):
        # Crea il titolo della sezione usando la funzione helper.
        self._crea_titolo_sezione(container, title, info_text, guide_text)
        
        # Crea un frame principale per contenere i riquadri con gli indici statistici.
        frame_indici_main = customtkinter.CTkFrame(container, border_width=1)
        frame_indici_main.pack(fill="x", expand=True, padx=10, pady=10)
        frame_indici_main.grid_columnconfigure((0, 1, 2), weight=1) # Le tre colonne si espandono uniformemente.
        
        # --- Riquadro Indici di Posizione ---
        frame_pos = customtkinter.CTkFrame(frame_indici_main)
        frame_pos.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_pos, text="Indici di Posizione", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        mean, median, mode_val = data_series.mean(), data_series.median(), data_series.mode().iloc[0] if not data_series.mode().empty else 'N/A'
        customtkinter.CTkLabel(frame_pos, text=f"Media: {mean:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_pos, text=f"Mediana: {median:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_pos, text=f"Moda: {mode_val}").pack(anchor="w", padx=10, pady=(0,5))

        # --- Riquadro Indici di Variabilità ---
        frame_var = customtkinter.CTkFrame(frame_indici_main)
        frame_var.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_var, text="Indici di Variabilità", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        # ddof=1 calcola la varianza/dev.std campionaria (divisione per n-1), che è la prassi.
        variance, std_dev, range_val = data_series.var(ddof=1), data_series.std(ddof=1), data_series.max() - data_series.min()
        mad = (data_series - mean).abs().mean()
        cv = std_dev / mean if mean != 0 else 0
        customtkinter.CTkLabel(frame_var, text=f"Varianza: {variance:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Dev. Std: {std_dev:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Scarto Medio Assoluto: {mad:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Ampiezza del campo di variazione(Range): {range_val:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Coeff. Variazione: {cv:.4f}").pack(anchor="w", padx=10, pady=(0,5))

        # --- Riquadro Forma e Quartili ---
        frame_form = customtkinter.CTkFrame(frame_indici_main)
        frame_form.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_form, text="Forma e Quartili", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        skew, kurt = data_series.skew(), data_series.kurtosis()
        q1, q3, iqr = data_series.quantile(0.25), data_series.quantile(0.75), data_series.quantile(0.75) - data_series.quantile(0.25)
        # Calcola l'intervallo di Chebyshev per k=2 (contiene almeno il 75% dei dati).
        cheb_low, cheb_high = mean - 2 * std_dev, mean + 2 * std_dev
        customtkinter.CTkLabel(frame_form, text=f"Asimmetria (Skew): {skew:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_form, text=f"Curtosi: {kurt:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_form, text=f"Q1: {q1:.4f} | Q3: {q3:.4f} | IQR: {iqr:.4f}").pack(anchor="w", padx=10, pady=(10,0))
        customtkinter.CTkLabel(frame_form, text=f"Interv. Chebyshev (k=2): [{cheb_low:.2f}, {cheb_high:.2f}]", font=customtkinter.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(5,5))

        # --- Creazione Tabella delle Frequenze ---
        num_unique = data_series.nunique()
        # Se la variabile è continua (float) e ha molti valori unici, raggruppa i dati in classi (bin).
        if num_unique > 25 and pd.api.types.is_float_dtype(data_series):
            bins = min(num_unique, 15)
            freq_table = pd.cut(data_series, bins=bins).value_counts().sort_index().to_frame(name='Frequenza Assoluta')
            freq_table.index = freq_table.index.astype(str)
        # Altrimenti (dati discreti o categorici), calcola le frequenze per ogni valore unico.
        else:
            freq_table = data_series.value_counts().sort_index().to_frame(name='Frequenza Assoluta')
        
        # Calcola le frequenze relative e cumulate.
        freq_table['Frequenza Relativa'] = freq_table['Frequenza Assoluta'] / len(data_series)
        freq_table['Freq. Ass. Cumulata'] = freq_table['Frequenza Assoluta'].cumsum()
        freq_table['Freq. Rel. Cumulata'] = freq_table['Frequenza Relativa'].cumsum()
        freq_table.index.name = "Classe/Valore"
        # Crea la tabella visuale usando la funzione helper.
        self._crea_tabella_treeview(container, freq_table.reset_index(), "Tabella delle Frequenze")
        
        # --- Creazione dei Grafici ---
        frame_grafici = customtkinter.CTkFrame(container, fg_color="transparent")
        frame_grafici.pack(fill="x", expand=True, padx=5, pady=5)
        frame_grafici.grid_columnconfigure((0, 1), weight=1)

        # Istogramma
        frame_hist = customtkinter.CTkFrame(frame_grafici)
        frame_hist.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
        ax_hist.hist(data_series, bins='auto', edgecolor='black')
        ax_hist.set_title(f"Istogramma di '{variable_name}'")
        ax_hist.set_ylabel("Frequenza")
        ax_hist.grid(True, linestyle='--', alpha=0.6)
        fig_hist.tight_layout()
        canvas_hist = FigureCanvasTkAgg(fig_hist, master=frame_hist)
        canvas_hist.draw()
        canvas_hist.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        self.matplotlib_widgets.append(canvas_hist)
        plt.close(fig_hist) # Chiude la figura per liberare memoria.

        # Box Plot
        frame_box = customtkinter.CTkFrame(frame_grafici)
        frame_box.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        fig_box, ax_box = plt.subplots(figsize=(6, 4))
        ax_box.boxplot(data_series, vert=False, showfliers=True, patch_artist=True, boxprops=dict(facecolor="lightblue"))
        ax_box.set_title(f"Box Plot di '{variable_name}'")
        ax_box.set_yticklabels([])
        ax_box.grid(True, linestyle='--', alpha=0.6)
        fig_box.tight_layout()
        canvas_box = FigureCanvasTkAgg(fig_box, master=frame_box)
        canvas_box.draw()
        canvas_box.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        self.matplotlib_widgets.append(canvas_box)
        plt.close(fig_box)

    # --- FUNZIONE PRINCIPALE PER L'ANALISI DESCRITTIVA UNIVARIATA ---
    def esegui_analisi_descrittiva(self, *args):
        if self.df is None: return
        variable = self.selettore_var_descrittiva.get()
        if not variable: return

        # --- Logica per mostrare/nascondere controlli contestuali in base alla variabile ---
        if variable == 'Data_Ora_Incidente':
            # Se la variabile è la data, mostra i selettori per aggregazione temporale e tipo di grafico.
            self.label_andamento.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_andamento.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.label_tipo_grafico.grid(row=0, column=2, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            
            # Limita le opzioni di grafico a quelle adatte per le serie temporali.
            opzioni_grafico = ['Barre','Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_grafico:
                self.selettore_grafico_descrittiva.set(opzioni_grafico[0])
            self.selettore_grafico_descrittiva.configure(values=opzioni_grafico)
            
            # Chiama la funzione specifica per l'analisi temporale.
            self.analisi_speciale_data_ora()
            
        elif variable in ['Tipo_Strada', 'Provincia', 'Giorno_Settimana']:
            # Se la variabile è categorica, nasconde il selettore di aggregazione temporale.
            self.label_andamento.grid_forget()
            self.selettore_andamento.grid_forget()
            self.label_tipo_grafico.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            # Imposta le opzioni di grafico adatte per dati categorici.
            opzioni_standard = ['Barre', 'Torta', 'Aste', 'Linee'] if variable == 'Giorno_Settimana' else ['Barre', 'Torta', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Barre')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            # Chiama la funzione di analisi generica.
            self.analisi_generica(variable)
            
        else: # Per tutte le altre variabili (tipicamente numeriche)
            # Nasconde il selettore di aggregazione e mostra solo quello del tipo di grafico.
            self.label_andamento.grid_forget()
            self.selettore_andamento.grid_forget()
            self.label_tipo_grafico.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Imposta le opzioni di grafico adatte per dati numerici.
            opzioni_standard = ['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Istogramma')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            # Chiama la funzione di analisi generica.
            self.analisi_generica(variable)

    # --- FUNZIONE SPECIFICA PER ANALIZZARE LA VARIABILE TEMPORALE ---
    def analisi_speciale_data_ora(self):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        
        # Ottiene le scelte dell'utente per aggregazione e tipo di grafico.
        tipo_aggregazione = self.selettore_andamento.get()
        tipo_grafico = self.selettore_grafico_descrittiva.get()

        # --- TESTI DI AIUTO AMPLIATI ---
        info = ("L'analisi della serie storica degli incidenti è fondamentale per identificare pattern, ciclicità e tendenze nel tempo. Comprendere 'quando' gli incidenti sono più frequenti permette di passare da una gestione reattiva a una proattiva, ottimizzando la distribuzione delle risorse (pattuglie, controlli) e pianificando campagne di sensibilizzazione mirate.")
        guida = ("Ogni tipo di aggregazione offre una prospettiva diversa:\n\n"
                 "- Annuale (Grafico a Barre): Ideale per visualizzare trend di lungo periodo. Il numero di incidenti sta aumentando o diminuendo nel corso degli anni? Ci sono stati effetti dovuti a nuove leggi o interventi infrastrutturali?\n\n"
                 "- Mensile (Grafico a Linee): Perfetto per individuare ciclicità stagionali. Ci sono più incidenti nei mesi estivi per il turismo o in quelli invernali per il maltempo? Questo grafico evidenzia pattern che si ripetono ogni anno.\n\n"
                 "- Giornaliero (Grafico a Linee): Utile per un'analisi ad altissima risoluzione, ad esempio per monitorare l'impatto di un evento specifico (es. un giorno festivo, un blocco del traffico) o per analisi su periodi molto brevi.\n\n"
                 "- Distribuzione Oraria (Grafico a Barre): Raggruppa tutti gli incidenti per ora del giorno (0-23). È cruciale per identificare le fasce orarie a maggior rischio (es. ore di punta mattutine/serali, notte del weekend).\n\n"
                 "- Distribuzione Settimanale (Grafico a Barre/Linee): Mostra il totale degli incidenti per ogni giorno della settimana. Evidenzia le differenze strutturali tra giorni feriali e fine settimana.")
        
        container = self.frame_risultati_descrittiva
        self._crea_titolo_sezione(container, f"Analisi Temporale: {tipo_aggregazione}", info, guida)

        # Crea i contenitori per la tabella dei dati e per il grafico.
        plot_container = customtkinter.CTkFrame(container, fg_color="transparent")
        plot_container.pack(fill="both", expand=True, padx=5, pady=5)
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)
        frame_tabella = customtkinter.CTkFrame(plot_container)
        frame_tabella.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_grafico = customtkinter.CTkFrame(plot_container)
        frame_grafico.grid(row=1, column=0, sticky='nsew')
        
        plot_data = None
        ax_title, ax_xlabel = "", ""
        
        # --- Logica di aggregazione dei dati in base alla scelta ---
        if tipo_aggregazione == 'Annuale':
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.year).size()
            ax_title, ax_xlabel = 'Andamento Annuale degli Incidenti', 'Anno'
        elif tipo_aggregazione == 'Mensile':
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.to_period('M')).size()
            plot_data.index = plot_data.index.strftime('%Y-%m') # Formatta l'indice per la leggibilità.
            ax_title, ax_xlabel = 'Andamento Mensile degli Incidenti', 'Mese'
        elif tipo_aggregazione == 'Giornaliero':
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.date).size()
            ax_title, ax_xlabel = 'Andamento Giornaliero degli Incidenti', 'Data'
        elif tipo_aggregazione == 'Distribuzione Oraria':
            plot_data = self.df['Ora'].value_counts().sort_index()
            ax_title, ax_xlabel = 'Distribuzione Incidenti per Ora del Giorno', 'Ora del Giorno'
        elif tipo_aggregazione == 'Distribuzione Settimanale':
            days_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
            days_order = list(days_map.values())
            daily_names = self.df['Data_Ora_Incidente'].dt.weekday.map(days_map)
            plot_data = daily_names.value_counts().reindex(days_order) # Riordina i giorni correttamente.
            ax_title, ax_xlabel = 'Distribuzione Incidenti per Giorno della Settimana', 'Giorno della Settimana'

        # Crea un DataFrame per la tabella riassuntiva e la visualizza.
        df_tabella = plot_data.to_frame(name="Numero Incidenti")
        df_tabella.index.name = ax_xlabel
        self._crea_tabella_treeview(frame_tabella, df_tabella.reset_index(), "Dati del Grafico")

        # --- Creazione e configurazione del grafico Matplotlib ---
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title(ax_title); ax.set_xlabel(ax_xlabel); ax.set_ylabel('Numero di Incidenti')
        
        # Ruota le etichette dell'asse x se sono troppe o troppo lunghe per evitare sovrapposizioni.
        if tipo_aggregazione in ['Distribuzione Settimanale', 'Mensile'] or (tipo_aggregazione == 'Giornaliero' and len(plot_data) > 30):
             ax.tick_params(axis='x', rotation=45)
        
        # Disegna il tipo di grafico scelto dall'utente.
        try:
            if tipo_grafico == 'Barre': plot_data.plot(kind='bar', ax=ax)
            elif tipo_grafico == 'Linee': plot_data.plot(kind='line', ax=ax, marker='o')
            elif tipo_grafico == 'Aste': ax.stem(plot_data.index.astype(str), plot_data.values)
            else: plot_data.plot(kind='line', ax=ax) # Default
        except Exception as e:
            ax.text(0.5, 0.5, f"Impossibile generare il grafico: {e}", ha='center')

        # Aggiunge una griglia e ottimizza il layout.
        ax.grid(True, linestyle='--', alpha=0.7); fig.tight_layout()
        # Integra il grafico nell'interfaccia Tkinter.
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.matplotlib_widgets.append(canvas)
        plt.close(fig) # Libera memoria.
        
    # --- FUNZIONE GENERICA PER ANALIZZARE UNA SINGOLA VARIABILE (NUMERICA O CATEGORICA) ---
    def analisi_generica(self, variable):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        tipo_grafico = self.selettore_grafico_descrittiva.get()
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato disponibile.").pack()
            return
        
        container = self.frame_risultati_descrittiva
        
        # Gestione speciale per la velocità: la tratta come numerica per i calcoli e categorica (in fasce) per alcuni grafici.
        velocity_variations = ["Velocita_Media_Stimata", "Velocità_media_Stimata", "Velocità_Media_Stimata", "velocita_media_stimata"]
        
        if variable in velocity_variations or "velocit" in variable.lower():
            original_data = data.copy() # Mantiene i dati numerici originali
            bins = list(range(0, int(data.max()) + 20, 10))
            labels = [f"{i}-{i+9} km/h" for i in range(0, int(data.max()) + 10, 10)]
            required_labels = len(bins) - 1 if len(bins) > 1 else 0
            labels_to_use = labels[:required_labels] if required_labels > 0 and len(labels) >= required_labels else None
            try:
                categorized_data = pd.cut(data, bins=bins, labels=labels_to_use, include_lowest=True) if labels_to_use else pd.cut(data, bins=bins, include_lowest=True)
            except ValueError:
                categorized_data = pd.cut(data, bins=bins, include_lowest=True)
            is_numeric = True
            display_data = categorized_data  # Dati da usare per barre/torta
            numeric_data = original_data     # Dati da usare per istogramma/boxplot
        else:
            is_numeric = pd.api.types.is_numeric_dtype(data)
            display_data = data
            numeric_data = data
        
        # --- TESTI DI AIUTO AMPLIATI ---
        info = ("L'analisi descrittiva univariata (su una singola variabile) è il primo passo essenziale di ogni analisi dati. Il suo scopo è riassumere le caratteristiche principali di una variabile attraverso indici numerici e rappresentazioni grafiche, per ottenere una comprensione iniziale della sua distribuzione e struttura.")
        guida = ("Come leggere i risultati:\n\n"
            "Indici Numerici (per variabili quantitative):\n"
            "- Media, Mediana, Moda: Confrontali. Se sono molto diversi, la distribuzione è asimmetrica.\n"
            "- Dev. Std, Varianza: Misurano la dispersione. Valori alti indicano dati molto variabili.\n"
            "- Asimmetria (Skewness): ≈ 0 (simmetrica); > 0 (coda a destra, es. reddito); < 0 (coda a sinistra, es. punteggi test facili).\n"
            "- Curtosi: Misura la 'pesantezza' delle code e l'altezza del picco rispetto a una normale. > 0 (leptocurtica, più picco); < 0 (platicurtica, più piatta).\n\n"
            "Grafici:\n"
            "- Istogramma (per numeriche): Mostra la forma della distribuzione dei dati. Cerca picchi, simmetria, code.\n"
            "- Box Plot (per numeriche): Visualizza il 50% centrale dei dati (box), la mediana (linea), e possibili valori anomali (outliers).\n"
            "- Barre (per categoriche/discrete): Confronta le frequenze delle diverse categorie.\n"
            "- Torta (per categoriche): Mostra la proporzione di ogni categoria sul totale. Efficace solo con poche categorie.")

        self._crea_titolo_sezione(container, f"Analisi Descrittiva: '{variable}'", info, guida)
        plot_container = customtkinter.CTkFrame(container, fg_color="transparent")
        plot_container.pack(fill="both", expand=True, padx=5, pady=5)
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        # Se la variabile è numerica, calcola e mostra un pannello con gli indici statistici.
        if is_numeric:
            stats_data = numeric_data if variable in velocity_variations or "velocit" in variable.lower() else data
            frame_indici = customtkinter.CTkFrame(plot_container)
            frame_indici.grid(row=0, column=0, sticky='ew', pady=(0, 10))
            frame_indici.grid_columnconfigure((0,1,2,3), weight=1)
            indici = {
                'Media': stats_data.mean(), 'Mediana': stats_data.median(), 'Moda': stats_data.mode().iloc[0] if not stats_data.mode().empty else 'N/A', 
                'Varianza': stats_data.var(ddof=1), 'Dev. Std': stats_data.std(ddof=1), 'Asimmetria': stats_data.skew(), 'Curtosi': stats_data.kurtosis()
            }
            row, col = 0, 0
            for key, val in indici.items():
                text = f"{key}\n{val:.3f}" if isinstance(val, (int, float)) else f"{key}\n{val}"
                customtkinter.CTkLabel(frame_indici, text=text, justify="center").grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                col = (col + 1) % 4
                if col == 0: row += 1

        frame_grafico = customtkinter.CTkFrame(plot_container)
        frame_grafico.grid(row=1, column=0, sticky='nsew') 

        # --- Logica per la creazione del grafico corretto ---
        fig, ax = plt.subplots(figsize=(8, 5))
        try:
            plot_title = f"{tipo_grafico} di '{variable}'"
            if tipo_grafico == 'Istogramma':
                if is_numeric: 
                    plot_data = numeric_data # Usa sempre i dati numerici per l'istogramma.
                    ax.hist(plot_data, bins='auto', edgecolor='black')
                    ax.set_xlabel(variable); ax.set_ylabel('Frequenza')
                else: 
                    ax.text(0.5, 0.5, 'Istogramma non applicabile a dati non numerici', ha='center', va='center', transform=ax.transAxes)
            elif tipo_grafico == 'Box Plot':
                if is_numeric: 
                    plot_data = numeric_data # Usa sempre i dati numerici per il box plot.
                    ax.boxplot(plot_data, vert=False, showfliers=True)
                    ax.set_yticklabels([variable]); ax.set_xlabel('Valore')
                else: 
                    ax.text(0.5, 0.5, 'Box Plot non applicabile a dati non numerici', ha='center', va='center', transform=ax.transAxes)
            else: # Per grafici a barre, torta, linee, aste
                freq_data = display_data.value_counts()
                plot_data = freq_data
                
                # Ordinamento intelligente per migliorare la leggibilità dei grafici.
                if tipo_grafico != 'Torta':
                    try:
                        if variable == 'Giorno_Settimana':
                            days_order = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
                            plot_data = plot_data.reindex(days_order).dropna()
                        elif is_numeric and not (variable in velocity_variations or "velocit" in variable.lower()):
                            plot_data = plot_data.sort_index()
                        else:
                            # Tenta un ordinamento "naturale" basato sui numeri nelle etichette (es. per le fasce di velocità).
                            def extract_number(x):
                                import re
                                match = re.search(r'\d+', str(x))
                                return int(match.group()) if match else float('inf')
                            plot_data = plot_data.reindex(sorted(plot_data.index, key=extract_number))
                    except Exception:
                        plot_data = plot_data.sort_index() # Fallback a ordinamento standard.

                ax.set_xlabel('Categorie'); ax.set_ylabel('Frequenza')
                if tipo_grafico == 'Barre': plot_data.plot(kind='bar', ax=ax)
                elif tipo_grafico == 'Linee': plot_data.plot(kind='line', ax=ax, marker='o')
                elif tipo_grafico == 'Torta': ax.pie(plot_data, labels=plot_data.index, autopct=lambda p: f'{p:.1f}%' if p > 3 else '', textprops={'fontsize': 10}); ax.set_ylabel('')
                elif tipo_grafico == 'Aste': ax.stem(plot_data.index.astype(str), plot_data.values)
                ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            ax.set_title(plot_title)
            ax.grid(True, linestyle='--', alpha=0.6)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
            canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)
            self.matplotlib_widgets.append(canvas)
        finally:
            plt.close(fig)

    # --- FUNZIONE PER ESEGUIRE L'ANALISI BIVARIATA ---
    def esegui_analisi_bivariata(self, *args):
        self.pulisci_frame(self.frame_risultati_bivariata)
        if self.df is None: return

        var_x, var_y = self.selettore_var_biv_x.get(), self.selettore_var_biv_y.get()
        if not var_x or not var_y: return

        try:
            df_subset = self.df[[var_x, var_y]].dropna()
            if len(df_subset) < 2:
                customtkinter.CTkLabel(self.frame_risultati_bivariata, text="Dati insufficienti per l'analisi.").pack(); return

            container = self.frame_risultati_bivariata
            container.grid_rowconfigure(1, weight=1); container.grid_columnconfigure(0, weight=1)
            x_data, y_data = df_subset[var_x], df_subset[var_y]
            x_is_numeric = pd.api.types.is_numeric_dtype(x_data)
            y_is_numeric = pd.api.types.is_numeric_dtype(y_data)
            
            # --- CASO 1: NUMERICA vs NUMERICA ---
            if x_is_numeric and y_is_numeric:
                info = ("L'analisi bivariata tra due variabili numeriche esplora la natura e la forza della loro relazione. Gli strumenti chiave sono la correlazione, che quantifica il legame lineare, e la regressione lineare, che modella questo legame con un'equazione per scopi predittivi.")
                guida = ("- Diagramma a Dispersione (Scatter Plot): Fondamentale. La disposizione dei punti rivela la forma della relazione (lineare, curvilinea, etc.), la direzione (positiva/negativa) e la presenza di outliers.\n\n"
                        "- Coefficiente di Correlazione di Pearson (r): Misura la forza e la direzione della *relazione lineare*. Varia da -1 (perfetta correlazione negativa) a +1 (perfetta correlazione positiva). Un valore vicino a 0 indica assenza di relazione *lineare* (ma potrebbe esisterne una non lineare!). Il p-value associato ci dice se la correlazione osservata è statisticamente significativa.\n\n"
                        "- Retta di Regressione (Y = mX + q): È la linea che 'meglio si adatta' ai dati (minimizzando la somma dei quadrati delle distanze verticali dei punti dalla linea). 'm' (pendenza) indica di quanto cambia Y per un aumento unitario di X. Può essere usata per prevedere Y data X, ma attenzione all'estrapolazione! \n\n"
                        "ATTENZIONE: Correlazione non implica causalità! Una forte correlazione tra X e Y non significa che X causi Y.")
                
                frame_info_biv = customtkinter.CTkFrame(container)
                frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Correlazione e Regressione", info, guida)

                if var_x == var_y: # Se le variabili sono identiche, la correlazione è perfetta.
                    correlation, p_value, slope, intercept = 1.0, 0.0, 1.0, 0.0
                else:
                    regression = stats.linregress(x=x_data, y=y_data)
                    slope, intercept, correlation, p_value = regression.slope, regression.intercept, regression.rvalue, regression.pvalue

                risultati = (f"Coefficiente di Correlazione (r): {correlation:.4f} (p-value: {p_value:.3g})\n"
                            f"Equazione Retta di Regressione: Y = {slope:.4f}X + {intercept:.4f}")
                customtkinter.CTkLabel(frame_info_biv, text=risultati, justify="left").pack(pady=5, padx=10, anchor="w")
                
                # Disegno dello scatter plot con retta di regressione.
                frame_grafico = customtkinter.CTkFrame(container)
                frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
                fig, ax = plt.subplots()
                num_points = len(x_data)
                point_size = max(2, 40 / np.log10(num_points)) if num_points > 100 else 20
                alpha_value = max(0.1, 0.7 / np.log10(num_points)) if num_points > 100 else 0.6
                ax.scatter(x_data, y_data, alpha=alpha_value, s=point_size, label='Dati Osservati')
                line_x = np.array(ax.get_xlim()); line_y = slope * line_x + intercept
                ax.plot(line_x, line_y, color='red', label='Retta di Regressione')
                ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}'); ax.set_xlabel(var_x); ax.set_ylabel(var_y)
                ax.legend(); ax.grid(True, linestyle='--', alpha=0.6); fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.get_tk_widget().pack(fill='both', expand=True); self.matplotlib_widgets.append(canvas); plt.close(fig)
                
            # --- CASO 2: CATEGORICA vs NUMERICA ---
            elif (x_is_numeric and not y_is_numeric) or (not x_is_numeric and y_is_numeric):
                # Assegna correttamente le variabili a 'categorica' e 'numerica'.
                cat_var, num_var = (var_x, var_y) if not x_is_numeric else (var_y, var_x)
                cat_data, num_data = (x_data, y_data) if not x_is_numeric else (y_data, x_data)
                    
                info = ("Questo tipo di analisi esamina come i valori di una variabile numerica si distribuiscono tra le diverse categorie di una variabile qualitativa. L'obiettivo è confrontare i gruppi definiti dalle categorie per vedere se ci sono differenze significative nelle loro distribuzioni numeriche.")
                guida = ("- Box Plot Affiancati: È il grafico principe per questo confronto. Ogni box plot rappresenta la distribuzione della variabile numerica per una singola categoria. Permette di confrontare visivamente mediane (linea centrale), dispersione (altezza del box) e presenza di outliers tra i gruppi.\n\n"
                        "- Statistiche Descrittive per Gruppo: Vengono calcolate media, deviazione standard, etc. per ogni categoria. Permette un confronto numerico preciso delle tendenze centrali e della variabilità.\n\n"
                        "- Test ANOVA (F-test): L'Analisi della Varianza (ANOVA) è un test d'ipotesi che verifica se le medie di tre o più gruppi sono uguali. L'ipotesi nulla (H₀) è che tutte le medie dei gruppi siano uguali. Un p-value basso (< 0.05) suggerisce che almeno una media è significativamente diversa dalle altre.")
                
                frame_info_biv = customtkinter.CTkFrame(container); frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Categorica vs Numerica", info, guida)
                
                # Calcola le statistiche per ogni gruppo e le formatta in una stringa.
                gruppi = df_subset.groupby(cat_var)[num_var]
                stats_text = "Statistiche per gruppo:\n" + "\n".join([f"• {nome}: Media={g.mean():.2f}, Std={g.std():.2f}, N={len(g)}" for nome, g in gruppi])
                
                # Esegue il test ANOVA se ci sono almeno due gruppi.
                if len(gruppi) > 1:
                    try:
                        f_stat, p_value_anova = stats.f_oneway(*[g.values for _, g in gruppi])
                        stats_text += f"\n\nTest ANOVA: F-statistic = {f_stat:.3f}, p-value = {p_value_anova:.3g}"
                    except:
                        stats_text += "\n\nTest ANOVA non calcolabile."
                
                customtkinter.CTkLabel(frame_info_biv, text=stats_text, justify="left").pack(pady=5, padx=10, anchor="w")
                
                # Disegna i box plot affiancati.
                frame_grafico = customtkinter.CTkFrame(container); frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
                fig, ax = plt.subplots()
                categories = df_subset[cat_var].unique()
                box_data = [df_subset[df_subset[cat_var] == cat][num_var].values for cat in categories]
                ax.boxplot(box_data, labels=categories)
                ax.set_title(f'Distribuzione di {num_var} per {cat_var}'); ax.set_xlabel(cat_var); ax.set_ylabel(num_var)
                ax.grid(True, linestyle='--', alpha=0.6); plt.xticks(rotation=45); fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.get_tk_widget().pack(fill='both', expand=True); self.matplotlib_widgets.append(canvas); plt.close(fig)
                
            # --- CASO 3: CATEGORICA vs CATEGORICA ---
            else:
                info = ("L'analisi tra due variabili categoriche mira a determinare se esista un'associazione o una dipendenza tra di esse. Ci si chiede: la distribuzione di una variabile cambia a seconda della categoria dell'altra?")
                guida = ("- Tabella di Contingenza (o a doppia entrata): Mostra le frequenze congiunte, ovvero quante osservazioni cadono in ogni combinazione di categorie delle due variabili. È la base per l'analisi.\n\n"
                        "- Test Chi-quadrato (χ²): È il test d'ipotesi fondamentale in questo caso. L'ipotesi nulla (H₀) è che le due variabili siano indipendenti. Un p-value basso (< 0.05) fornisce l'evidenza per rigettare H₀, suggerendo che esiste un'associazione statisticamente significativa tra le variabili.\n\n"
                        "- Heatmap (Mappa di Calore): È una visualizzazione grafica della tabella di contingenza. I colori più intensi indicano le celle con frequenze più alte, permettendo di individuare visivamente le associazioni più forti tra le categorie.")
                
                frame_info_biv = customtkinter.CTkFrame(container); frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Categorica vs Categorica", info, guida)
                
                # Crea la tabella di contingenza.
                crosstab = pd.crosstab(x_data, y_data)
                
                # Esegue il test del Chi-quadrato.
                try:
                    chi2, p_value_chi2, dof, expected = stats.chi2_contingency(crosstab)
                    stats_text = f"Test Chi-quadrato: χ² = {chi2:.3f}, p-value = {p_value_chi2:.3g}, df = {dof}"
                except:
                    stats_text = "Test Chi-quadrato: Non calcolabile"
                customtkinter.CTkLabel(frame_info_biv, text=stats_text, justify="left").pack(pady=5, padx=10, anchor="w")
                
                # Mostra la tabella di contingenza come testo.
                table_text = "Tabella di Contingenza:\n" + str(crosstab)
                customtkinter.CTkLabel(frame_info_biv, text=table_text, justify="left", font=("Courier", 10)).pack(pady=5, padx=10, anchor="w")
                
                # Disegna la heatmap.
                frame_grafico = customtkinter.CTkFrame(container); frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
                fig, ax = plt.subplots()
                im = ax.imshow(crosstab.values, cmap='Blues', aspect='auto')
                ax.set_xticks(range(len(crosstab.columns))); ax.set_yticks(range(len(crosstab.index)))
                ax.set_xticklabels(crosstab.columns, rotation=45); ax.set_yticklabels(crosstab.index)
                for i in range(len(crosstab.index)): # Aggiunge i numeri dentro le celle.
                    for j in range(len(crosstab.columns)):
                        ax.text(j, i, crosstab.iloc[i, j], ha='center', va='center')
                ax.set_title(f'Tabella di Contingenza: {var_x} vs {var_y}'); ax.set_xlabel(var_y); ax.set_ylabel(var_x)
                plt.colorbar(im, ax=ax); fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.get_tk_widget().pack(fill='both', expand=True); self.matplotlib_widgets.append(canvas); plt.close(fig)

        except Exception as e:
            error_label = customtkinter.CTkLabel(self.frame_risultati_bivariata, text=f"Si è verificato un errore: {e}\nControlla le variabili selezionate.", text_color="orange")
            error_label.pack(pady=20)
    
    # --- FUNZIONE HELPER PER AGGIORNARE LE CASELLE DI TESTO DEI RISULTATI ---
    def _update_textbox(self, textbox, text):
        textbox.configure(state="normal")  # Rende la textbox modificabile dal codice.
        textbox.delete("1.0", "end")  # Cancella il contenuto precedente.
        textbox.insert("1.0", text)  # Inserisce il nuovo testo.
        textbox.update_idletasks()  # Forza l'aggiornamento dell'interfaccia.
        # Calcola un'altezza approssimativa per la textbox basata sul numero di righe, per evitare barre di scorrimento inutili.
        font = textbox.cget("font")
        line_height = font.cget("size") + 6
        num_lines = int(textbox.index('end-1c').split('.')[0])
        new_height = num_lines * line_height
        textbox.configure(height=new_height)
        textbox.configure(state="disabled") # Rende di nuovo la textbox non modificabile dall'utente.

    # --- FUNZIONE PER IL CALCOLO DELLA PROBABILITÀ DI POISSON ---
    def esegui_poisson(self):
        if self.df is None: return
        try:
            # Recupera gli input dell'utente.
            provincia = self.selettore_provincia_poisson.get()
            k_entry = self.entry_k_poisson.get()
            fascia_oraria_str = self.entry_ora_poisson.get().strip()

            if not k_entry or not fascia_oraria_str: raise ValueError("Tutti i campi sono obbligatori.")
            k = int(k_entry) # Numero di eventi di cui calcolare la probabilità.

            # Interpreta l'input della fascia oraria (singola ora o range).
            if '-' in fascia_oraria_str:
                parts = fascia_oraria_str.split('-')
                if len(parts) != 2 or not parts[0].strip() or not parts[1].strip(): raise ValueError("Formato range non valido (es. '8-17').")
                ora_inizio, ora_fine = int(parts[0]), int(parts[1])
            else:
                ora_inizio = ora_fine = int(fascia_oraria_str)

            if not (0 <= ora_inizio <= 23 and 0 <= ora_fine <= 23 and ora_inizio <= ora_fine):
                raise ValueError("Le ore devono essere valide (0-23) e l'inizio <= fine.")
            
            # Filtra i dati per la provincia e la fascia oraria selezionate.
            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique() # Calcola il numero di giorni unici con dati per quella provincia.

            if giorni_osservati == 0:
                risultato = f"Nessun dato per la provincia di {provincia}."
            else:
                # Calcola il numero totale di incidenti nella fascia oraria.
                incidenti_fascia = df_prov[df_prov['Ora'].between(ora_inizio, ora_fine)].shape[0]
                # Stima il parametro lambda (tasso medio) come incidenti totali / giorni osservati.
                lambda_val = incidenti_fascia / giorni_osservati
                # Calcola la probabilità di Poisson P(X=k) usando la funzione pmf (Probability Mass Function).
                prob = stats.poisson.pmf(k, lambda_val)
                # Formatta la stringa di output.
                risultato = (f"ANALISI PER {provincia.upper()} (Fascia {ora_inizio:02d}:00-{ora_fine:02d}:59)\n"
                             f"--------------------------------------------------\n"
                             f"Tasso medio stimato (λ): {lambda_val:.4f} incidenti/giorno\n"
                             f"(Calcolato su {incidenti_fascia} incidenti totali osservati in {giorni_osservati} giorni unici)\n\n"
                             f"Probabilità di osservare esattamente {k} incidenti in un giorno in questa fascia oraria:\n\n"
                             f"P(X=k) = {prob:.4%} (cioè {prob*100:.2f} su 100)")
        except Exception as e:
            risultato = f"Errore di Input:\n{e}"
        self._update_textbox(self.risultato_poisson_textbox, risultato)

    # --- FUNZIONE PER IL T-TEST TRA GRUPPI INDIPENDENTI ---
    def esegui_ttest(self):
        if self.df is None or 'Numero_Feriti' not in self.df.columns: return
        # Crea due gruppi: incidenti diurni (7-19) e notturni.
        data_diurno = self.df[self.df['Ora'].between(7, 19)]['Numero_Feriti'].dropna()
        data_notturno = self.df[~self.df['Ora'].between(7, 19)]['Numero_Feriti'].dropna()

        if len(data_diurno) < 2 or len(data_notturno) < 2:
            risultato = "Dati insufficienti: necessari almeno 2 campioni per gruppo (diurno e notturno)."
        else:
            # Esegue il T-test di Welch (equal_var=False), che è più robusto.
            ttest_res = stats.ttest_ind(data_diurno, data_notturno, equal_var=False) 
            risultato = ("CONFRONTO NUMERO MEDIO FERITI: DIURNO vs. NOTTURNO\n"
                         "--------------------------------------------------\n"
                         f"Gruppo Diurno (7-19), n={len(data_diurno)}: Media Feriti = {data_diurno.mean():.3f}\n"
                         f"Gruppo Notturno (<7, >19), n={len(data_notturno)}: Media Feriti = {data_notturno.mean():.3f}\n\n"
                         f"RISULTATI DEL TEST T DI WELCH:\n  - Statistica t = {ttest_res.statistic:.4f}\n  - p-value = {ttest_res.pvalue:.4f}\n\n"
                         "INTERPRETAZIONE:\n" + ("Il p-value è molto basso (p < 0.05). Questo significa che la differenza osservata tra le medie dei due gruppi è statisticamente significativa. Possiamo concludere con ragionevole certezza che non è dovuta al caso." 
                                              if ttest_res.pvalue < 0.05 else 
                                              "Il p-value è alto (p >= 0.05). Non abbiamo sufficiente evidenza statistica per concludere che esista una vera differenza nel numero medio di feriti tra incidenti diurni e notturni. La differenza osservata potrebbe essere dovuta al caso."))
        self._update_textbox(self.risultato_ttest_textbox, risultato)

    # --- FUNZIONE PER IL CALCOLO DELL'INTERVALLO DI CONFIDENZA ---
    def esegui_ci(self):
        if self.df is None: return
        try:
            # Recupera gli input.
            provincia = self.selettore_provincia_ci.get()
            livello_entry = self.entry_livello_ci.get()
            if not livello_entry: raise ValueError("Livello di confidenza non può essere vuoto.")
            livello = int(livello_entry)
            if not 0 < livello < 100: raise ValueError("Il livello di confidenza deve essere un numero intero tra 1 e 99.")

            # Aggrega i dati per calcolare il numero di incidenti per ogni giorno.
            incidenti_giorno = self.df[self.df['Provincia'] == provincia].groupby('Giorno').size()
            if len(incidenti_giorno) < 2:
                risultato = f"Dati insufficienti per la provincia di {provincia} (necessari almeno 2 giorni con incidenti per calcolare la variabilità)."
            else:
                # Calcola media, deviazione standard e numerosità del campione (di giorni).
                mean, std, n = incidenti_giorno.mean(), incidenti_giorno.std(ddof=1), len(incidenti_giorno)
                if n == 0 or np.isnan(std) or std == 0:
                    risultato = "Impossibile calcolare l'intervallo: la deviazione standard è zero o non valida (tutti i giorni hanno lo stesso numero di incidenti)."
                else:
                    # Calcola l'intervallo di confidenza per la media usando la distribuzione t di Student.
                    interval = stats.t.interval(confidence=livello/100, df=n-1, loc=mean, scale=stats.sem(incidenti_giorno, nan_policy='omit'))
                    risultato = (f"STIMA INCIDENTI GIORNALIERI MEDI - {provincia.upper()}\n"
                                 "--------------------------------------------------\n"
                                 f"Media Campionaria (su dati disponibili): {mean:.3f} incidenti/giorno\n"
                                 f"Numero di Giorni con incidenti osservati: {n}\n\n"
                                 f"INTERVALLO DI CONFIDENZA AL {livello}%:\n"
                                 f"  [{interval[0]:.4f}, {interval[1]:.4f}]\n\n"
                                 f"INTERPRETAZIONE:\nSiamo fiduciosi al {livello}% che il 'vero' numero medio di incidenti giornalieri per la provincia di {provincia} si trovi all'interno di questo intervallo. È una misura della precisione della nostra stima basata sui dati a disposizione.")
        except Exception as e:
            risultato = f"Errore: {e}"
        self._update_textbox(self.risultato_ci_textbox, risultato)

# --- BLOCCO DI ESECUZIONE PRINCIPALE ---
# Questo codice viene eseguito solo se lo script è lanciato direttamente (non se importato come modulo).
if __name__ == "__main__":
    app = App()  # Crea un'istanza della nostra applicazione.
    app.mainloop()  # Avvia il ciclo principale di eventi di Tkinter, che disegna la finestra e attende l'interazione dell'utente.