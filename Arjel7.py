# ==================================================================================
# SOFTWARE DI ANALISI STATISTICA INCIDENTI STRADALI (v7.1 - Aggregazione temporale)
# ==================================================================================
import tkinter
from tkinter import filedialog, ttk
import customtkinter
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from datetime import datetime, timedelta, date
import collections
import locale

# Imposta la lingua italiana per i nomi dei giorni/mesi
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    print("Locale 'it_IT.UTF-8' non trovato. Verrà usata una mappatura interna.")

# =============================================================================
# IMPOSTAZIONI INIZIALI DELL'INTERFACCIA
# =============================================================================
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# =============================================================================
# CLASSE PRINCIPALE DELL'APPLICAZIONE
# =============================================================================
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Software di Analisi Statistica Incidenti Stradali")
        self.geometry("1200x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.df = None
        self.matplotlib_widgets = []

        self.setup_loading_frame()
        self.setup_tab_view()
        self.tab_view.set("Dati Forniti")

    def setup_loading_frame(self):
        self.frame_caricamento = customtkinter.CTkFrame(self)
        self.frame_caricamento.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.frame_caricamento.grid_columnconfigure((0, 1, 2), weight=1)
        self.label_file = customtkinter.CTkLabel(self.frame_caricamento, text="Nessun dato caricato.", text_color="gray")
        self.label_file.grid(row=0, column=0, padx=20, pady=20)
        self.bottone_carica_csv = customtkinter.CTkButton(self.frame_caricamento, text="Carica File CSV", command=self.carica_csv)
        self.bottone_carica_csv.grid(row=0, column=1, padx=20, pady=20)
        self.bottone_dati_esempio = customtkinter.CTkButton(self.frame_caricamento, text="Usa Dati Simulati", command=self.carica_dati_esempio)
        self.bottone_dati_esempio.grid(row=0, column=2, padx=20, pady=20)

    def setup_tab_view(self):
        self.tab_view = customtkinter.CTkTabview(self, width=250, command=self.on_tab_change)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        tabs = ["Dati Forniti", "Calcolo Dati", "Campionatura", "Analisi Descrittiva", "Analisi Bivariata", "Analisi Inferenziale"]
        for tab in tabs: self.tab_view.add(tab)
        self.setup_tab_dati_forniti()
        self.setup_tab_calcolo_dati()
        self.setup_tab_campionatura()
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

    def carica_csv(self):
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        if not filepath: return
        try:
            try:
                df = pd.read_csv(filepath, sep=';')
                if df.shape[1] == 1:
                    df = pd.read_csv(filepath, sep=',')
            except:
                 df = pd.read_csv(filepath, sep=',')

            filename = filepath.split('/')[-1]
            self.label_file.configure(text=f"Caricato: {filename} ({len(df)} record)", text_color='white')
            self.inizializza_dati(df)
            self.tab_view.set("Dati Forniti")
        except Exception as e:
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    def carica_dati_esempio(self):
        try:
            records = []
            province = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Catania', 'Salerno', 'Bologna', 'Venezia', 'Bari']
            tipi_strada = ['Urbana', 'Statale', 'Autostrada']
            giorni_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}

            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            for _ in range(500):
                random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
                random_date = start_date + timedelta(seconds=random_seconds)

                if random.random() < 0.05:
                    strada = None
                else:
                    strada = random.choice(tipi_strada)

                velocita = None
                if strada == 'Urbana': velocita = random.randint(30, 65)
                elif strada == 'Statale': velocita = random.randint(60, 95)
                elif strada == 'Autostrada': velocita = random.randint(100, 140)

                numero_morti = random.choices([0, 1, 2, 3], weights=[94, 4, 1.5, 0.5], k=1)[0]
                numero_feriti = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 40, 25, 15, 5, 5], k=1)[0]
                if numero_morti > 0: numero_feriti += numero_morti

                records.append({'Data_Ora_Incidente': random_date, 'Provincia': random.choice(province), 'Giorno_Settimana': giorni_map[random_date.weekday()], 'Tipo_Strada': strada, 'Numero_Feriti': numero_feriti, 'Numero_Morti': numero_morti, 'Velocita_Media_Stimata': velocita})

            df = pd.DataFrame(records)
            self.label_file.configure(text=f"Caricati {len(df)} record simulati.", text_color="white")
            self.inizializza_dati(df)
        except Exception as e:
            self.label_file.configure(text=f"Errore Dati Esempio: {e}", text_color="red")

    def inizializza_dati(self, df, variabile_da_mantenere=None):
        self.df = df.copy()
        if 'Data_Ora_Incidente' in self.df.columns:
            self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce')
        for col in ['Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        original_rows = len(self.df)
        self.df.dropna(subset=['Data_Ora_Incidente', 'Provincia'], inplace=True)
        dropped_rows = original_rows - len(self.df)
        if dropped_rows > 0:
            print(f"Rimosse {dropped_rows} righe con valori mancanti in 'Data_Ora_Incidente' o 'Provincia'.")

        if self.df.empty:
            self.label_file.configure(text="Errore: Nessun dato valido trovato.", text_color="orange")
            self.df = None
            return
        self.df['Ora'] = self.df['Data_Ora_Incidente'].dt.hour
        #self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
        self.popola_tabella_dati()
        self.aggiorna_selettori(variabile_da_mantenere)

    def aggiorna_selettori(self, variabile_da_mantenere=None):
        if self.df is None: return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        # Costruisce la lista di colonne per l'analisi descrittiva escludendo 'Giorno'
        all_columns = [col for col in datetime_cols + object_columns + numeric_columns if col != 'Giorno']

        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []
        
        # Selettori per Analisi Descrittiva
        self.selettore_var_descrittiva.configure(values=all_columns)
        if variabile_da_mantenere and variabile_da_mantenere in all_columns: self.selettore_var_descrittiva.set(variabile_da_mantenere)
        elif all_columns: self.selettore_var_descrittiva.set(all_columns[0])
        
        # Selettori per Calcolo Dati e Campionatura
        self.selettore_var_calcolo.configure(values=numeric_columns)
        self.selettore_var_campionatura.configure(values=numeric_columns)
        if numeric_columns: 
            self.selettore_var_calcolo.set(numeric_columns[0])
            self.selettore_var_campionatura.set(numeric_columns[0])

        # Selettori per Analisi Bivariata
        self.selettore_var_biv_x.configure(values=numeric_columns)
        self.selettore_var_biv_y.configure(values=numeric_columns)
        if len(numeric_columns) > 1:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[1])
        elif numeric_columns:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[0])
        
        # Selettori per Analisi Inferenziale
        self.selettore_provincia_poisson.configure(values=province_uniche)
        self.selettore_provincia_ci.configure(values=province_uniche)
        if province_uniche:
            self.selettore_provincia_poisson.set(province_uniche[0])
            self.selettore_provincia_ci.set(province_uniche[0])
        
        self.after(50, self.on_tab_change)


    def on_tab_change(self, *args):
        # Le analisi ora vengono eseguite automaticamente alla selezione di una variabile
        # o al click sul pulsante di refresh, non più al cambio di scheda.
        pass

    def _crea_titolo_sezione(self, parent, testo_titolo, testo_info, testo_guida=None, row=None, columnspan=1):
        if row is not None:
            frame_titolo = customtkinter.CTkFrame(parent, fg_color="transparent")
            frame_titolo.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(15, 5))
        else:
            frame_titolo = customtkinter.CTkFrame(parent)
            frame_titolo.pack(fill="x", expand=True, padx=10, pady=(10,0))
        
        inner_frame = customtkinter.CTkFrame(frame_titolo, fg_color="transparent")
        inner_frame.pack(pady=5)
        
        customtkinter.CTkLabel(inner_frame, text=testo_titolo, font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        if testo_info:
            customtkinter.CTkButton(inner_frame, text="i", command=lambda: self.show_info(f"Informazioni: {testo_titolo}", testo_info), width=28, height=28, corner_radius=14).pack(side="left", padx=(0, 5))
        if testo_guida:
            customtkinter.CTkButton(inner_frame, text="?", command=lambda: self.show_info("Guida alla Lettura", testo_guida), width=28, height=28, corner_radius=14).pack(side="left")


    def _crea_tabella_treeview(self, parent, df, title="Dati"):
        frame = customtkinter.CTkFrame(parent)
        frame.pack(fill="x", expand=True, padx=5, pady=5)
        
        customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=(5,5), padx=10, anchor="w")

        table_frame = customtkinter.CTkFrame(frame)
        table_frame.pack(fill="x", expand=True, padx=5, pady=(0,5))
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Calibri', 11))
        style.configure("Treeview.Heading", font=('Calibri', 12, 'bold'))
        
        columns = df.columns.tolist()
        table = ttk.Treeview(table_frame, columns=columns, show='headings', height=min(len(df), 10))
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, anchor='center', width=120, minwidth=100)

        for _, row in df.iterrows():
            formatted_row = []
            for val in row:
                if isinstance(val, float):
                    formatted_row.append(f"{val:.4f}")
                else:
                    formatted_row.append(val)
            table.insert("", "end", values=formatted_row)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=vsb.set)

        table.grid(row=0, column=0, sticky='ew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        return frame


    def show_info(self, title, message):
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title)
        info_window.transient(self)
        info_window.geometry("550x450")
        
        textbox = customtkinter.CTkTextbox(info_window, wrap="word", font=customtkinter.CTkFont(size=14))
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        textbox.insert("1.0", message)
        textbox.configure(state="disabled")

        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")


    def pulisci_frame(self, frame):
        for widget in self.matplotlib_widgets:
            if widget.get_tk_widget().winfo_exists():
                widget.get_tk_widget().destroy()
        self.matplotlib_widgets = []
        for widget in frame.winfo_children():
            widget.destroy()

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
                                                             values=['Mensile', 'Giornaliero', 'Annuale', ], # 'Distribuzione Oraria', 'Distribuzione Settimanale' 
                                                             command=self.esegui_analisi_descrittiva)
        self.selettore_andamento.set('Mensile')

        self.label_tipo_grafico = customtkinter.CTkLabel(self.frame_controlli_contestuali, text="Tipo Grafico:")
        self.selettore_grafico_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_contestuali, values=['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste'], command=self.esegui_analisi_descrittiva)
        self.selettore_grafico_descrittiva.set('Barre')
        
        self.bottone_refresh_descrittiva = customtkinter.CTkButton(self.frame_controlli_descrittiva, text="🔄", command=self.esegui_analisi_descrittiva, width=35, height=35)
        self.bottone_refresh_descrittiva.grid(row=0, column=3, padx=(5, 10), pady=5)

        self.frame_risultati_descrittiva = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Analisi Descrittiva")
        self.frame_risultati_descrittiva.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)

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
        self.bottone_refresh_bivariata = customtkinter.CTkButton(frame_controlli, text="🔂", command=self.esegui_analisi_bivariata, width=35, height=35)
        self.bottone_refresh_bivariata.grid(row=0, column=4, padx=(5,10), pady=5)
        self.frame_risultati_bivariata = customtkinter.CTkFrame(tab)
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1)

    def setup_tab_inferenziale(self):
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll_frame = customtkinter.CTkScrollableFrame(tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        info_poisson = ("Il Modello di Poisson è un modello di probabilità discreta utilizzato per descrivere il numero di eventi che si verificano in un intervallo fisso di tempo o spazio, data una frequenza media nota e costante (λ, lambda) e assumendo che gli eventi siano indipendenti l'uno dall'altro.\n\n"
                        "**Applicazione Pratica:**\n"
                        "Questo strumento permette di stimare la probabilità di osservare un numero esatto 'k' di incidenti (es. 0, 1, 2...) in un determinato periodo (es. un giorno) e in una specifica area (es. una provincia), basandosi sulla media storica degli incidenti per quella stessa area e periodo. È fondamentale per la valutazione del rischio e l'allocazione predittiva delle risorse.")
        
        frame_poisson = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_poisson.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_poisson.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_poisson, "Modello di Poisson", info_poisson, row=0, columnspan=3)
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

        info_ttest = ("Il Test T per Campioni Indipendenti è un test di ipotesi inferenziale utilizzato per determinare se esiste una differenza statisticamente significativa tra le medie di due gruppi indipendenti e non correlati.\n\n"
                      "**Ipotesi del Test:**\n"
                      "1. **Ipotesi Nulla (H₀):** Non c'è differenza tra le medie dei due gruppi (μ₁ = μ₂). La differenza osservata è dovuta puramente al caso.\n"
                      "2. **Ipotesi Alternativa (H₁):** Esiste una differenza tra le medie (μ₁ ≠ μ₂).\n\n"
                      "**Interpretazione (p-value):**\n"
                      "Il p-value indica la probabilità di osservare una differenza grande come quella campionaria (o più grande) se l'ipotesi nulla fosse vera. Un p-value basso (convenzionalmente < 0.05) fornisce l'evidenza per rigettare H₀, suggerendo che la differenza tra i gruppi è 'statisticamente significativa'.")
        
        frame_ttest = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ttest.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        frame_ttest.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_ttest, "Test T per Campioni Indipendenti", info_ttest, row=0, columnspan=2)
        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0))
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        self.risultato_ttest_textbox = customtkinter.CTkTextbox(frame_ttest, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_ttest_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ttest_textbox.configure(state="disabled")

        info_ci = ("Un Intervallo di Confidenza (IC) è un range di valori, calcolato a partire da dati campionari, che si stima possa contenere il vero valore di un parametro della popolazione (es. la media reale, μ) con un determinato livello di fiducia.\n\n"
                   "**Cosa significa 'Fiducia al 95%'?**\n"
                   "Non significa che c'è una probabilità del 95% che il vero valore della media cada in *questo specifico* intervallo. Significa che, se ripetessimo l'esperimento di campionamento molte volte, il 95% degli intervalli di confidenza così calcolati conterrebbe il vero parametro della popolazione.\n\n"
                   "**Utilità:**\n"
                   "Fornisce una misura della precisione della stima puntuale (la media campionaria). Un intervallo stretto indica una stima precisa, mentre un intervallo ampio riflette una maggiore incertezza dovuta alla variabilità dei dati o alla ridotta dimensione del campione.")
        
        frame_ci = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ci.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        frame_ci.grid_columnconfigure(1, weight=1)
        self._crea_titolo_sezione(frame_ci, "Intervallo di Confidenza", info_ci, row=0, columnspan=2)
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

    def popola_tabella_dati(self):
        for item in self.data_table.get_children(): self.data_table.delete(item)
        if self.df is None or self.df.empty: return
        cols_da_mostrare = [col for col in ['Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata'] if col in self.df.columns]
        display_df = self.df[cols_da_mostrare].copy()
        display_df = display_df.sort_values(by='Data_Ora_Incidente', ascending=False)
        display_df['Data_Ora_Incidente'] = display_df['Data_Ora_Incidente'].dt.strftime('%Y-%m-%d %H:%M:%S')
        for _, row in display_df.head(500).iterrows(): self.data_table.insert("", "end", values=list(row))

    def esegui_calcolo_dati(self, *args):
        self.pulisci_frame(self.frame_risultati_calcolo)
        if self.df is None: return
        variable = self.selettore_var_calcolo.get()
        if not variable: return

        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_calcolo, text="Nessun dato disponibile per la variabile selezionata.", text_color="orange").pack(pady=20)
            return
        
        title = "Analisi sulla Popolazione"
        info = ("Questa sezione esegue un'analisi statistica descrittiva sull'**intera popolazione** dei dati caricati per la variabile selezionata. I valori calcolati (media, varianza, ecc.) sono considerati i **parametri reali** del dataset fornito.")
        guida = ("**Interpretazione:**\nI risultati mostrati rappresentano le caratteristiche esatte dell'insieme di dati a tua disposizione. Utilizza questi valori per ottenere una comprensione completa e accurata della distribuzione della variabile scelta all'interno del tuo dataset specifico.\n\n"
                 "- **Tabelle di Frequenza:** Mostrano come si distribuiscono esattamente i valori.\n"
                 "- **Indici:** Descrivono le proprietà matematiche (tendenza centrale, variabilità, forma) dell'intero set di dati.\n"
                 "- **Grafici:** Offrono una visualizzazione completa della distribuzione della popolazione.")
        
        self._esegui_analisi_numerica_dettagliata(self.frame_risultati_calcolo, data, variable, title, info, guida)

    def esegui_campionatura(self):
        self.pulisci_frame(self.frame_risultati_campionatura)
        if self.df is None: return
        variable = self.selettore_var_campionatura.get()
        n_str = self.entry_dim_campione.get()
        
        if not variable or not n_str:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text="Selezionare una variabile e inserire la dimensione del campione.", text_color="orange").pack(pady=20)
            return

        try:
            n = int(n_str)
            if n <= 0: raise ValueError("La dimensione del campione deve essere positiva.")
        except ValueError as e:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text=f"Errore: Inserire un numero intero valido per la dimensione del campione.\n({e})", text_color="orange").pack(pady=20)
            return

        data = self.df[variable].dropna()
        if n > len(data):
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text=f"Errore: La dimensione del campione ({n}) non può superare il numero di dati disponibili ({len(data)}).", text_color="orange").pack(pady=20)
            return
        
        campione = data.sample(n=n, random_state=None) 
        title = f"Analisi su un Campione Casuale (n={n})"
        info = ("Questa sezione esegue un'analisi statistica su un **campione casuale** di dimensione 'n' estratto dalla popolazione dei dati. I valori calcolati (media campionaria, varianza campionaria, ecc.) sono **stime** (o statistiche) dei veri parametri della popolazione. L'obiettivo è fare **inferenza**, ovvero dedurre le caratteristiche della popolazione partendo da un suo sottoinsieme.")
        guida = ("**Interpretazione:**\nI risultati di un campione sono soggetti a **variabilità campionaria**: ogni estrazione produrrà risultati leggermente diversi. Questi valori sono stime dei parametri della popolazione.\n\n"
                 "- **Confronto:** Confronta la media del campione con la media della popolazione (calcolata nella scheda 'Calcolo Dati') per osservare l'effetto del campionamento.\n"
                 "- **Legge dei Grandi Numeri:** Aumentando la dimensione del campione 'n', le statistiche calcolate tenderanno a convergere verso i veri parametri della popolazione.")

        self._esegui_analisi_numerica_dettagliata(self.frame_risultati_campionatura, campione, variable, title, info, guida)

    def _esegui_analisi_numerica_dettagliata(self, container, data_series, variable_name, title, info_text, guide_text):
        self._crea_titolo_sezione(container, title, info_text, guide_text)
        
        frame_indici_main = customtkinter.CTkFrame(container, border_width=1)
        frame_indici_main.pack(fill="x", expand=True, padx=10, pady=10)
        frame_indici_main.grid_columnconfigure((0, 1, 2), weight=1)
        
        frame_pos = customtkinter.CTkFrame(frame_indici_main)
        frame_pos.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_pos, text="Indici di Posizione", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        mean, median, mode_val = data_series.mean(), data_series.median(), data_series.mode().iloc[0] if not data_series.mode().empty else 'N/A'
        customtkinter.CTkLabel(frame_pos, text=f"Media: {mean:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_pos, text=f"Mediana: {median:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_pos, text=f"Moda: {mode_val}").pack(anchor="w", padx=10, pady=(0,5))

        frame_var = customtkinter.CTkFrame(frame_indici_main)
        frame_var.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_var, text="Indici di Variabilità", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        variance, std_dev, range_val = data_series.var(ddof=1), data_series.std(ddof=1), data_series.max() - data_series.min()
        mad = (data_series - mean).abs().mean()
        cv = std_dev / mean if mean != 0 else 0
        customtkinter.CTkLabel(frame_var, text=f"Varianza: {variance:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Dev. Std: {std_dev:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Scarto Medio Assoluto: {mad:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Ampiezza del campo di variazione(Range): {range_val:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_var, text=f"Coeff. Variazione: {cv:.4f}").pack(anchor="w", padx=10, pady=(0,5))

        frame_form = customtkinter.CTkFrame(frame_indici_main)
        frame_form.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        customtkinter.CTkLabel(frame_form, text="Forma e Quartili", font=customtkinter.CTkFont(size=13, weight="bold")).pack(pady=5)
        skew, kurt = data_series.skew(), data_series.kurtosis()
        q1, q3, iqr = data_series.quantile(0.25), data_series.quantile(0.75), data_series.quantile(0.75) - data_series.quantile(0.25)
        cheb_low, cheb_high = mean - 2 * std_dev, mean + 2 * std_dev
        customtkinter.CTkLabel(frame_form, text=f"Asimmetria (Skew): {skew:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_form, text=f"Curtosi: {kurt:.4f}").pack(anchor="w", padx=10)
        customtkinter.CTkLabel(frame_form, text=f"Q1: {q1:.4f} | Q3: {q3:.4f} | IQR: {iqr:.4f}").pack(anchor="w", padx=10, pady=(10,0))
        customtkinter.CTkLabel(frame_form, text=f"Interv. Chebyshev (k=2): [{cheb_low:.2f}, {cheb_high:.2f}]", font=customtkinter.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(5,5))

        num_unique = data_series.nunique()
        if num_unique > 25 and pd.api.types.is_float_dtype(data_series):
            bins = min(num_unique, 15)
            freq_table = pd.cut(data_series, bins=bins).value_counts().sort_index().to_frame(name='Frequenza Assoluta')
            freq_table.index = freq_table.index.astype(str)
        else:
            freq_table = data_series.value_counts().sort_index().to_frame(name='Frequenza Assoluta')
        
        freq_table['Frequenza Relativa'] = freq_table['Frequenza Assoluta'] / len(data_series)
        freq_table['Freq. Ass. Cumulata'] = freq_table['Frequenza Assoluta'].cumsum()
        freq_table['Freq. Rel. Cumulata'] = freq_table['Frequenza Relativa'].cumsum()
        freq_table.index.name = "Classe/Valore"
        self._crea_tabella_treeview(container, freq_table.reset_index(), "Tabella delle Frequenze")
        
        frame_grafici = customtkinter.CTkFrame(container, fg_color="transparent")
        frame_grafici.pack(fill="x", expand=True, padx=5, pady=5)
        frame_grafici.grid_columnconfigure((0, 1), weight=1)

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
        plt.close(fig_hist)

        frame_box = customtkinter.CTkFrame(frame_grafici)
        frame_box.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        fig_box, ax_box = plt.subplots(figsize=(6, 4))
        ax_box.boxplot(data_series, vert=False, showfliers=True, patch_artist=True,
                       boxprops=dict(facecolor="lightblue"))
        ax_box.set_title(f"Box Plot di '{variable_name}'")
        ax_box.set_yticklabels([])
        ax_box.grid(True, linestyle='--', alpha=0.6)
        fig_box.tight_layout()
        canvas_box = FigureCanvasTkAgg(fig_box, master=frame_box)
        canvas_box.draw()
        canvas_box.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        self.matplotlib_widgets.append(canvas_box)
        plt.close(fig_box)

    def esegui_analisi_descrittiva(self, *args):
        if self.df is None: return
        variable = self.selettore_var_descrittiva.get()
        if not variable: return

        # Gestione visibilità controlli contestuali
        if variable == 'Data_Ora_Incidente':
            self.label_andamento.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_andamento.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.label_tipo_grafico.grid(row=0, column=2, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            
            opzioni_grafico = ['Barre','Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_grafico:
                self.selettore_grafico_descrittiva.set(opzioni_grafico[0])
            self.selettore_grafico_descrittiva.configure(values=opzioni_grafico)
            
            self.analisi_speciale_data_ora()
        elif variable == 'Tipo_Strada' or  variable == 'Provincia':
            self.label_andamento.grid_forget()
            self.selettore_andamento.grid_forget()
            self.label_tipo_grafico.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            opzioni_standard = ['Barre', 'Torta', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Barre')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            self.analisi_generica(variable)
        elif variable == 'Giorno_Settimana':
            self.label_andamento.grid_forget()
            self.selettore_andamento.grid_forget()
            self.label_tipo_grafico.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            opzioni_standard = ['Barre', 'Linee' ,'Torta', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Barre')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            self.analisi_generica(variable)
            
        else:
            self.label_andamento.grid_forget()
            self.selettore_andamento.grid_forget()
            
            self.label_tipo_grafico.grid(row=0, column=0, padx=(10,5), pady=5)
            self.selettore_grafico_descrittiva.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            opzioni_standard = ['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Barre')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            self.analisi_generica(variable)

    def analisi_speciale_data_ora(self):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        
        tipo_aggregazione = self.selettore_andamento.get()
        tipo_grafico = self.selettore_grafico_descrittiva.get()

        info = ("L'analisi della variabile temporale è fondamentale per identificare pattern e tendenze nel verificarsi degli incidenti. Permette di capire 'quando' gli incidenti sono più frequenti, supportando decisioni strategiche su sorveglianza e prevenzione.")
        guida = ("- **Annuale (Barre):** Mostra il numero totale di incidenti per ogni anno. Utile per identificare trend di lungo periodo.\n\n"
                 "- **Mensile (Linee):** Mostra l'evoluzione del numero di incidenti mese per mese. Ottimo per individuare cicli stagionali o l'impatto di interventi specifici.\n\n"
                 "- **Giornaliero (Linee):** Mostra l'evoluzione del numero di incidenti giorno per giorno. Utile per analisi dettagliate su brevi periodi.\n\n"
                 "- **Distribuzione Oraria (Barre):** Aggrega gli incidenti per ora del giorno. Cruciale per individuare le fasce orarie a maggior rischio.\n\n"
                 "- **Distribuzione Settimanale (Barre):** Aggrega gli incidenti per giorno della settimana. Evidenzia le differenze tra giorni feriali e weekend.")
        
        container = self.frame_risultati_descrittiva
        self._crea_titolo_sezione(container, f"Analisi Temporale: {tipo_aggregazione}", info, guida)

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
        
        if tipo_aggregazione == 'Annuale':
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.year).size()
            ax_title, ax_xlabel = 'Andamento Annuale degli Incidenti', 'Anno'
        elif tipo_aggregazione == 'Mensile':
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.to_period('M')).size()
            plot_data.index = plot_data.index.strftime('%Y-%m')
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
            plot_data = daily_names.value_counts().reindex(days_order)
            ax_title, ax_xlabel = 'Distribuzione Incidenti per Giorno della Settimana', 'Giorno della Settimana'

        df_tabella = plot_data.to_frame(name="Numero Incidenti")
        df_tabella.index.name = ax_xlabel
        self._crea_tabella_treeview(frame_tabella, df_tabella.reset_index(), "Dati del Grafico")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title(ax_title); ax.set_xlabel(ax_xlabel); ax.set_ylabel('Numero di Incidenti')
        
        if tipo_aggregazione in ['Distribuzione Settimanale', 'Mensile'] or (tipo_aggregazione == 'Giornaliero' and len(plot_data) > 30):
             ax.tick_params(axis='x', rotation=45)
        
        try:
            if tipo_grafico == 'Barre': plot_data.plot(kind='bar', ax=ax)
            elif tipo_grafico == 'Linee': plot_data.plot(kind='line', ax=ax, marker='o')
            elif tipo_grafico == 'Aste': ax.stem(plot_data.index.astype(str), plot_data.values)
            else: plot_data.plot(kind='line', ax=ax)
        except Exception as e:
            ax.text(0.5, 0.5, f"Impossibile generare il grafico: {e}", ha='center')

        ax.grid(True, linestyle='--', alpha=0.7); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.matplotlib_widgets.append(canvas)
        plt.close(fig)
        
    def analisi_generica(self, variable):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        tipo_grafico = self.selettore_grafico_descrittiva.get()
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato disponibile.").pack()
            return
        
        container = self.frame_risultati_descrittiva
        
        # Lista di possibili nomi per la variabile velocità (gestisce variazioni di nome)
        velocity_variations = ["Velocita_Media_Stimata", "Velocità_media_Stimata", "Velocità_Media_Stimata", "velocita_media_stimata"]
        
        if variable in velocity_variations or "velocit" in variable.lower():
            # Mantieni i dati originali numerici per i calcoli statistici
            original_data = data.copy()
            
            # Crea gli intervalli per la visualizzazione
            bins = list(range(0, int(data.max()) + 20, 10))
            labels = [f"{i}-{i+9} km/h" for i in range(0, int(data.max()) + 10, 10)]

            # Correzione: assicurati che il numero di labels sia corretto
            required_labels = len(bins) - 1 if len(bins) > 1 else 0
            if required_labels > 0 and len(labels) >= required_labels:
                labels_to_use = labels[:required_labels]
            else:
                labels_to_use = None

            try:
                if labels_to_use:
                    categorized_data = pd.cut(data, bins=bins, labels=labels_to_use, include_lowest=True)
                else:
                    categorized_data = pd.cut(data, bins=bins, include_lowest=True)
            except ValueError:
                # Fallback: usa pd.cut senza labels personalizzate
                categorized_data = pd.cut(data, bins=bins, include_lowest=True)

            # Per i grafici categorici usa i dati categorizzati, per numerici usa gli originali
            is_numeric = True  # La velocità è sempre numerica
            display_data = categorized_data  # Per grafici a barre/torta
            numeric_data = original_data     # Per istogramma/boxplot
        else:
            is_numeric = pd.api.types.is_numeric_dtype(data)
            display_data = data
            numeric_data = data
        
        info = ("L'analisi descrittiva univariata esplora una singola variabile alla volta per riassumerne le caratteristiche principali attraverso indici numerici e rappresentazioni grafiche. È il primo passo fondamentale per comprendere la struttura dei dati.")
        guida = ("**Indici Numerici (se applicabili):**\n"
            "- **Media, Mediana, Moda:** Indicano il 'centro' della distribuzione. Confrontarli aiuta a capirne la simmetria.\n"
            "- **Dev. Std, Varianza:** Misurano la dispersione dei dati attorno alla media. Valori alti indicano maggiore variabilità.\n"
            "- **Asimmetria (Skewness):** > 0 coda a destra; < 0 coda a sinistra; ≈ 0 simmetrica.\n"
            "- **Curtosi:** Misura la 'pesantezza' delle code. > 0 code più pesanti (distribuzione leptocurtica); < 0 code più leggere (platicurtica).\n\n"
            "**Grafici:**\n"
            "- **Istogramma/Barre:** Mostra la frequenza di ogni valore o classe.\n"
            "- **Box Plot:** Visualizza i quartili (il box centrale contiene il 50% dei dati), la mediana (linea nel box) e gli outlier (punti esterni).\n"
            "- **Torta:** Mostra la proporzione di ogni categoria sul totale. Efficace per un numero limitato di categorie.")

        self._crea_titolo_sezione(container, f"Analisi Descrittiva: '{variable}'", info, guida)
        plot_container = customtkinter.CTkFrame(container, fg_color="transparent")
        plot_container.pack(fill="both", expand=True, padx=5, pady=5)
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        # Usa sempre i dati numerici originali per gli indici statistici
        if is_numeric:
            # Per le statistiche usa sempre i dati numerici originali
            stats_data = numeric_data if variable in velocity_variations or "velocit" in variable.lower() else data
            
            frame_indici = customtkinter.CTkFrame(plot_container)
            frame_indici.grid(row=0, column=0, sticky='ew', pady=(0, 10))
            frame_indici.grid_columnconfigure((0,1,2,3), weight=1)
            
            mean = stats_data.mean()
            median = stats_data.median()
            mode = stats_data.mode().iloc[0] if not stats_data.mode().empty else 'N/A'
            variance = stats_data.var(ddof=1)
            std_dev = stats_data.std(ddof=1)
            skew = stats_data.skew()
            kurt = stats_data.kurtosis()
            
            indici = {
                'Media': mean, 
                'Mediana': median, 
                'Moda': mode, 
                'Varianza': variance, 
                'Dev. Std': std_dev, 
                'Asimmetria': skew, 
                'Curtosi': kurt
            }
            
            row, col = 0, 0
            for key, val in indici.items():
                text = f"{key}\n{val:.3f}" if isinstance(val, (int, float)) else f"{key}\n{val}"
                customtkinter.CTkLabel(frame_indici, text=text, justify="center").grid(
                    row=row, column=col, padx=5, pady=5, sticky="ew"
                )
                col = (col + 1) % 4
                if col == 0: 
                    row += 1

        frame_grafico = customtkinter.CTkFrame(plot_container)
        frame_grafico.grid(row=1, column=0, sticky='nsew') 

        fig, ax = plt.subplots(figsize=(8, 5))
        try:
            plot_title = f"{tipo_grafico} di '{variable}'"

            if tipo_grafico == 'Istogramma':
                if is_numeric: 
                    # Per istogramma usa sempre i dati numerici originali
                    plot_data = numeric_data if variable in velocity_variations or "velocit" in variable.lower() else data
                    ax.hist(plot_data, bins='auto', edgecolor='black')
                    ax.set_xlabel(variable)
                    ax.set_ylabel('Frequenza')
                else: 
                    ax.text(0.5, 0.5, 'Istogramma non applicabile a dati non numerici', 
                        ha='center', va='center', transform=ax.transAxes)
                    
            elif tipo_grafico == 'Box Plot':
                if is_numeric: 
                    # Per box plot usa sempre i dati numerici originali
                    plot_data = numeric_data if variable in velocity_variations or "velocit" in variable.lower() else data
                    ax.boxplot(plot_data, vert=False, showfliers=True)
                    ax.set_yticklabels([variable])
                    ax.set_xlabel('Valore')
                else: 
                    ax.text(0.5, 0.5, 'Box Plot non applicabile a dati non numerici', 
                        ha='center', va='center', transform=ax.transAxes)
            else:
                # Per altri grafici usa i dati categorizzati se appropriato
                freq_data = display_data.value_counts()
                plot_data = freq_data
                
                # Ordinamento intelligente basato sul tipo di dati
                if tipo_grafico != 'Torta':
                    try:
                        if is_numeric and not (variable in velocity_variations or "velocit" in variable.lower()):
                            # Per dati numerici normali, ordina numericamente
                            plot_data = plot_data.sort_index()
                        else:
                            # Per dati categorici o velocità categorizzata, prova ordinamento naturale
                            if all(str(idx).replace('-', '').replace('.', '').replace(' ', '').replace('km/h', '').isdigit() 
                                for idx in plot_data.index if str(idx) != 'nan'):
                                # Estrai il primo numero da ogni categoria per l'ordinamento
                                def extract_number(x):
                                    import re
                                    match = re.search(r'\d+', str(x))
                                    return int(match.group()) if match else float('inf')
                                
                                plot_data = plot_data.reindex(sorted(plot_data.index, key=extract_number))
                            else:
                                # Ordinamento alfabetico standard
                                plot_data = plot_data.sort_index()
                    except (TypeError, ValueError):
                        # Se ci sono tipi misti o altri problemi, converte tutto a stringa
                        plot_data.index = plot_data.index.astype(str)
                        plot_data = plot_data.sort_index()

                ax.set_xlabel('Categorie')
                ax.set_ylabel('Frequenza')
                
                if tipo_grafico == 'Barre': 
                    plot_data.plot(kind='bar', ax=ax)
                elif tipo_grafico == 'Linee': 
                    plot_data.plot(kind='line', ax=ax, marker='o')
                elif tipo_grafico == 'Torta': 
                    ax.pie(plot_data, labels=plot_data.index, 
                        autopct=lambda p: f'{p:.1f}%' if p > 3 else '', 
                        textprops={'fontsize': 10})
                    ax.set_ylabel('')
                elif tipo_grafico == 'Aste': 
                    ax.stem(plot_data.index.astype(str), plot_data.values)
                    
                ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            ax.set_title(plot_title)
            ax.grid(True, linestyle='--', alpha=0.6)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            self.matplotlib_widgets.append(canvas)
            
        finally:
            plt.close(fig)

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
            container.grid_rowconfigure(1, weight=1) 
            container.grid_columnconfigure(0, weight=1)
            
            x_data, y_data = df_subset[var_x], df_subset[var_y]
            
            # Determina il tipo di variabili
            x_is_numeric = pd.api.types.is_numeric_dtype(x_data)
            y_is_numeric = pd.api.types.is_numeric_dtype(y_data)
            
            if x_is_numeric and y_is_numeric:
                # ANALISI NUMERICA vs NUMERICA (codice originale)
                info = ("L'analisi bivariata esamina la relazione tra due variabili numeriche. Gli strumenti principali sono il coefficiente di correlazione, che misura la forza e la direzione del legame lineare, e il modello di regressione lineare, che descrive tale legame tramite un'equazione matematica.")
                guida = ("- **Diagramma a Dispersione (Scatter Plot):** Ogni punto rappresenta un'osservazione (un incidente). La disposizione dei punti suggerisce visivamente la natura della relazione (lineare, non lineare, assente).\n\n"
                        "- **Coefficiente di Correlazione (r):** Varia da -1 a +1.\n"
                        "  - Vicino a +1: Forte correlazione lineare positiva (al crescere di X, cresce Y).\n"
                        "  - Vicino a -1: Forte correlazione lineare negativa (al crescere di X, decresce Y).\n"
                        "  - Vicino a 0: Scarsa o nulla correlazione lineare.\n"
                        "  Il **p-value** associato testa se la correlazione osservata è statisticamente significativa o se potrebbe essere dovuta al caso.\n\n"
                        "- **Retta di Regressione:** È la linea che 'meglio si adatta' ai dati, minimizzando la distanza verticale totale dei punti dalla linea stessa. La sua equazione (y = mx + q) può essere usata per prevedere il valore di Y dato un valore di X.")
                
                frame_info_biv = customtkinter.CTkFrame(container)
                frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Correlazione e Regressione", info, guida)

                if var_x == var_y:
                    correlation, p_value, slope, intercept = 1.0, 0.0, 1.0, 0.0
                else:
                    regression = stats.linregress(x=x_data, y=y_data)
                    slope, intercept, correlation, p_value = regression.slope, regression.intercept, regression.rvalue, regression.pvalue

                risultati = (f"Coefficiente di Correlazione (r): {correlation:.4f} (p-value: {p_value:.3g})\n"
                            f"Equazione Retta di Regressione: Y = {slope:.4f}X + {intercept:.4f}")
                customtkinter.CTkLabel(frame_info_biv, text=risultati, justify="left").pack(pady=5, padx=10, anchor="w")
                
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

                canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
                canvas.get_tk_widget().pack(fill='both', expand=True)
                self.matplotlib_widgets.append(canvas)
                plt.close(fig)
                
            elif (x_is_numeric and not y_is_numeric) or (not x_is_numeric and y_is_numeric):
                # ANALISI CATEGORICA vs NUMERICA
                if not x_is_numeric:
                    cat_var, num_var = var_x, var_y
                    cat_data, num_data = x_data, y_data
                else:
                    cat_var, num_var = var_y, var_x
                    cat_data, num_data = y_data, x_data
                    
                info = ("L'analisi bivariata tra una variabile categorica e una numerica esamina come i valori della variabile numerica si distribuiscono tra le diverse categorie. Si utilizzano confronti tra gruppi per identificare differenze significative.")
                guida = ("- **Box Plot:** Mostra la distribuzione della variabile numerica per ogni categoria, evidenziando mediana, quartili e valori anomali.\n\n"
                        "- **Statistiche Descrittive:** Media, deviazione standard, mediana per ogni gruppo.\n\n"
                        "- **Test ANOVA:** Verifica se esistono differenze significative tra i gruppi (p-value < 0.05 indica differenze statisticamente significative).")
                
                frame_info_biv = customtkinter.CTkFrame(container)
                frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Categorica vs Numerica", info, guida)
                
                # Statistiche per gruppo
                gruppi = df_subset.groupby(cat_data)[num_data]
                stats_text = "Statistiche per gruppo:\n"
                for nome_gruppo, gruppo in gruppi:
                    media = gruppo.mean()
                    std = gruppo.std()
                    mediana = gruppo.median()
                    n = len(gruppo)
                    stats_text += f"• {nome_gruppo}: Media={media:.2f}, Std={std:.2f}, Mediana={mediana:.2f}, N={n}\n"
                
                # Test ANOVA
                try:
                    gruppi_valori = [gruppo.values for nome, gruppo in gruppi]
                    f_stat, p_value_anova = stats.f_oneway(*gruppi_valori)
                    stats_text += f"\nTest ANOVA: F={f_stat:.3f}, p-value={p_value_anova:.3g}"
                except:
                    stats_text += "\nTest ANOVA: Non calcolabile"
                
                customtkinter.CTkLabel(frame_info_biv, text=stats_text, justify="left").pack(pady=5, padx=10, anchor="w")
                
                # Grafico Box Plot
                frame_grafico = customtkinter.CTkFrame(container)
                frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
                
                fig, ax = plt.subplots()
                categories = df_subset[cat_var].unique()
                box_data = [df_subset[df_subset[cat_var] == cat][num_var].values for cat in categories]
                
                ax.boxplot(box_data, labels=categories)
                ax.set_title(f'Distribuzione di {num_var} per {cat_var}')
                ax.set_xlabel(cat_var)
                ax.set_ylabel(num_var)
                ax.grid(True, linestyle='--', alpha=0.6)
                plt.xticks(rotation=45)
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
                canvas.get_tk_widget().pack(fill='both', expand=True)
                self.matplotlib_widgets.append(canvas)
                plt.close(fig)
                
            else:
                # ANALISI CATEGORICA vs CATEGORICA
                info = ("L'analisi bivariata tra due variabili categoriche esamina la relazione tra le categorie attraverso tabelle di contingenza. Si verifica se le categorie sono indipendenti o se esiste un'associazione significativa.")
                guida = ("- **Tabella di Contingenza:** Mostra la frequenza di ogni combinazione di categorie.\n\n"
                        "- **Test Chi-quadrato:** Verifica l'indipendenza tra le variabili (p-value < 0.05 indica associazione significativa).\n\n"
                        "- **Heatmap:** Visualizzazione grafica delle frequenze nella tabella di contingenza.")
                
                frame_info_biv = customtkinter.CTkFrame(container)
                frame_info_biv.pack(fill="x", padx=10, pady=10)
                self._crea_titolo_sezione(frame_info_biv, "Analisi Categorica vs Categorica", info, guida)
                
                # Tabella di contingenza
                crosstab = pd.crosstab(x_data, y_data)
                
                # Test Chi-quadrato
                try:
                    chi2, p_value_chi2, dof, expected = stats.chi2_contingency(crosstab)
                    stats_text = f"Test Chi-quadrato: χ² = {chi2:.3f}, p-value = {p_value_chi2:.3g}, df = {dof}"
                except:
                    stats_text = "Test Chi-quadrato: Non calcolabile"
                
                customtkinter.CTkLabel(frame_info_biv, text=stats_text, justify="left").pack(pady=5, padx=10, anchor="w")
                
                # Tabella di contingenza come testo
                table_text = "Tabella di Contingenza:\n" + str(crosstab)
                customtkinter.CTkLabel(frame_info_biv, text=table_text, justify="left", font=("Courier", 10)).pack(pady=5, padx=10, anchor="w")
                
                # Heatmap
                frame_grafico = customtkinter.CTkFrame(container)
                frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)
                
                fig, ax = plt.subplots()
                im = ax.imshow(crosstab.values, cmap='Blues', aspect='auto')
                
                # Imposta etichette
                ax.set_xticks(range(len(crosstab.columns)))
                ax.set_yticks(range(len(crosstab.index)))
                ax.set_xticklabels(crosstab.columns, rotation=45)
                ax.set_yticklabels(crosstab.index)
                
                # Aggiungi valori nelle celle
                for i in range(len(crosstab.index)):
                    for j in range(len(crosstab.columns)):
                        ax.text(j, i, crosstab.iloc[i, j], ha='center', va='center')
                
                ax.set_title(f'Tabella di Contingenza: {var_x} vs {var_y}')
                ax.set_xlabel(var_y)
                ax.set_ylabel(var_x)
                plt.colorbar(im, ax=ax)
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
                canvas.get_tk_widget().pack(fill='both', expand=True)
                self.matplotlib_widgets.append(canvas)
                plt.close(fig)

        except Exception as e:
            error_label = customtkinter.CTkLabel(self.frame_risultati_bivariata, text=f"Si è verificato un errore: {e}\nControlla le variabili selezionate.", text_color="orange")
            error_label.pack(pady=20)

    def _update_textbox(self, textbox, text):
        textbox.configure(state="normal"); textbox.delete("1.0", "end"); textbox.insert("1.0", text); textbox.update_idletasks(); font = textbox.cget("font"); line_height = font.cget("size") + 6; num_lines = int(textbox.index('end-1c').split('.')[0]); new_height = num_lines * line_height; textbox.configure(height=new_height); textbox.configure(state="disabled")

    def esegui_poisson(self):
        if self.df is None: return
        try:
            provincia = self.selettore_provincia_poisson.get()
            k_entry = self.entry_k_poisson.get()
            fascia_oraria_str = self.entry_ora_poisson.get().strip()

            if not k_entry or not fascia_oraria_str: raise ValueError("Tutti i campi sono obbligatori.")
            k = int(k_entry)

            if '-' in fascia_oraria_str:
                parts = fascia_oraria_str.split('-')
                if len(parts) != 2 or not parts[0].strip() or not parts[1].strip(): raise ValueError("Formato range non valido (es. '8-17').")
                ora_inizio, ora_fine = int(parts[0]), int(parts[1])
            else:
                ora_inizio = ora_fine = int(fascia_oraria_str)

            if not (0 <= ora_inizio <= 23 and 0 <= ora_fine <= 23 and ora_inizio <= ora_fine):
                raise ValueError("Le ore devono essere valide (0-23) e l'inizio <= fine.")

            durata_ore = ora_fine - ora_inizio + 1

            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique()

            if giorni_osservati == 0:
                risultato = f"Nessun dato per la provincia di {provincia}."
            else:
                incidenti_fascia = df_prov[df_prov['Ora'].between(ora_inizio, ora_fine)].shape[0]
                lambda_val = incidenti_fascia / giorni_osservati
                prob = stats.poisson.pmf(k, lambda_val)
                risultato = (f"ANALISI PER {provincia.upper()} (Fascia {ora_inizio:02d}:00-{ora_fine:02d}:59)\n"
                             f"Durata della fascia considerata: {durata_ore} ore\n"
                             f"--------------------------------------------------\n"
                             f"Tasso medio stimato (λ): {lambda_val:.4f} incidenti/giorno\n"
                             f"(Calcolato su {incidenti_fascia} incidenti totali osservati in {giorni_osservati} giorni unici)\n\n"
                             f"Probabilità di osservare esattamente {k} incidenti in un giorno in questa fascia oraria:\n\n"
                             f"P(X=k) = {prob:.4%} (cioè {prob*100:.2f} su 100)")
        except Exception as e:
            risultato = f"Errore di Input:\n{e}"
        self._update_textbox(self.risultato_poisson_textbox, risultato)

    def esegui_ttest(self):
        if self.df is None or 'Numero_Feriti' not in self.df.columns: return
        data_diurno = self.df[self.df['Ora'].between(7, 19)]['Numero_Feriti'].dropna()
        data_notturno = self.df[~self.df['Ora'].between(7, 19)]['Numero_Feriti'].dropna()

        if len(data_diurno) < 2 or len(data_notturno) < 2:
            risultato = "Dati insufficienti: necessari almeno 2 campioni per gruppo (diurno e notturno)."
        else:
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

    def esegui_ci(self):
        if self.df is None: return
        try:
            provincia = self.selettore_provincia_ci.get()
            livello_entry = self.entry_livello_ci.get()
            if not livello_entry: raise ValueError("Livello di confidenza non può essere vuoto.")
            livello = int(livello_entry)
            if not 0 < livello < 100: raise ValueError("Il livello di confidenza deve essere un numero intero tra 1 e 99.")

            incidenti_giorno = self.df[self.df['Provincia'] == provincia].groupby('Giorno').size()
            if len(incidenti_giorno) < 2:
                risultato = f"Dati insufficienti per la provincia di {provincia} (necessari almeno 2 giorni con incidenti per calcolare la variabilità)."
            else:
                mean, std, n = incidenti_giorno.mean(), incidenti_giorno.std(ddof=1), len(incidenti_giorno)
                if n == 0 or np.isnan(std) or std == 0:
                    risultato = "Impossibile calcolare l'intervallo: la deviazione standard è zero o non valida (tutti i giorni hanno lo stesso numero di incidenti)."
                else:
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

if __name__ == "__main__":
    app = App()
    app.mainloop()