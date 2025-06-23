# ==================================================================================
# SOFTWARE DI ANALISI STATISTICA INCIDENTI STRADALI (v4.7 - Correzione Grafico a Barre)
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
        tabs = ["Dati Forniti", "Analisi Descrittiva", "Analisi Bivariata", "Analisi Inferenziale"]
        for tab in tabs: self.tab_view.add(tab)
        self.setup_tab_dati_forniti()
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
        self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
        if 'Numero_Morti' in self.df.columns: self.df['Mortale'] = (self.df['Numero_Morti'] > 0).astype(int)
        self.popola_tabella_dati()
        self.aggiorna_selettori(variabile_da_mantenere)

    def aggiorna_selettori(self, variabile_da_mantenere=None):
        if self.df is None: return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        all_columns = datetime_cols + object_columns + numeric_columns
        
        if 'Giorno' not in all_columns and 'Giorno' in self.df.columns:
            all_columns.insert(1, 'Giorno')

        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []
        self.selettore_var_descrittiva.configure(values=all_columns)
        if variabile_da_mantenere and variabile_da_mantenere in all_columns: self.selettore_var_descrittiva.set(variabile_da_mantenere)
        elif all_columns: self.selettore_var_descrittiva.set(all_columns[0])
        self.selettore_var_biv_x.configure(values=numeric_columns)
        self.selettore_var_biv_y.configure(values=numeric_columns)
        if len(numeric_columns) > 1:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[1])
        elif numeric_columns:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[0])
        self.after(50, self.on_tab_change)
        self.selettore_provincia_poisson.configure(values=province_uniche)
        self.selettore_provincia_ci.configure(values=province_uniche)
        if province_uniche:
            self.selettore_provincia_poisson.set(province_uniche[0])
            self.selettore_provincia_ci.set(province_uniche[0])

    def on_tab_change(self, *args):
        current_tab = self.tab_view.get()
        if self.df is None: return
        if current_tab == "Analisi Descrittiva": self.esegui_analisi_descrittiva()
        elif current_tab == "Analisi Bivariata": self.esegui_analisi_bivariata()
        elif current_tab == "Dati Forniti": self.popola_tabella_dati()

    def _crea_titolo_sezione(self, parent, row, testo_titolo, testo_info, columnspan=1, testo_guida=None):
        frame_titolo = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame_titolo.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(15, 5))
        inner_frame = customtkinter.CTkFrame(frame_titolo, fg_color="transparent")
        inner_frame.pack()
        customtkinter.CTkLabel(inner_frame, text=testo_titolo, font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        customtkinter.CTkButton(inner_frame, text="i", command=lambda: self.show_info(f"Info: {testo_titolo}", testo_info), width=28, height=28, corner_radius=14).pack(side="left", padx=(0, 5))
        if testo_guida:
            customtkinter.CTkButton(inner_frame, text="?", command=lambda: self.show_info("Come Leggere il Grafico", testo_guida), width=28, height=28, corner_radius=14).pack(side="left")

    def show_info(self, title, message):
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title)
        info_window.transient(self)
        label = customtkinter.CTkLabel(info_window, text=message, wraplength=450, justify="left", font=customtkinter.CTkFont(size=14))
        label.pack(padx=20, pady=20)
        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")

    def pulisci_frame(self, frame):
        for widget in self.matplotlib_widgets:
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
            width = {'Data_Ora_Incidente': 160}.get(col, 120); anchor = 'center' if col not in ['Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada'] else 'w'
            self.data_table.column(col, width=width, anchor=anchor); self.data_table.heading(col, text=col)
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_table.yview); hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.data_table.xview)
        self.data_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set); self.data_table.grid(row=0, column=0, sticky='nsew'); vsb.grid(row=0, column=1, sticky='ns'); hsb.grid(row=1, column=0, sticky='ew')

    def setup_tab_descrittiva(self):
        tab = self.tab_view.tab("Analisi Descrittiva")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        
        # Frame principale dei controlli
        self.frame_controlli_descrittiva = customtkinter.CTkFrame(tab)
        self.frame_controlli_descrittiva.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Selettore variabile (sempre visibile)
        customtkinter.CTkLabel(self.frame_controlli_descrittiva, text="Seleziona una variabile:").pack(side="left", padx=(10,5))
        self.selettore_var_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_descrittiva, values=[], command=self.esegui_analisi_descrittiva)
        self.selettore_var_descrittiva.pack(side="left", padx=5, expand=True, fill="x")
        
        # Frame per i controlli contestuali (per nascondere/mostrare)
        self.frame_controlli_contestuali = customtkinter.CTkFrame(self.frame_controlli_descrittiva, fg_color="transparent")
        self.frame_controlli_contestuali.pack(side="left", fill="x", expand=True)

        # --- WIDGET CONTESTUALI (inseriti nel frame contestuale) ---
        # 1. Selettore Aggregazione Temporale (per Data_Ora_Incidente)
        self.label_andamento = customtkinter.CTkLabel(self.frame_controlli_contestuali, text="Tipo di Aggregazione:")
        self.selettore_andamento = customtkinter.CTkComboBox(self.frame_controlli_contestuali, 
                                                             values=['Andamento Generale', 'Distribuzione Oraria', 'Distribuzione Settimanale'], 
                                                             command=self.esegui_analisi_descrittiva)
        self.selettore_andamento.set('Andamento Generale')

        # 2. Selettore Tipo Grafico (sempre visibile, ma le cui opzioni cambiano)
        self.label_tipo_grafico = customtkinter.CTkLabel(self.frame_controlli_contestuali, text="Tipo Grafico:")
        self.selettore_grafico_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_contestuali, values=['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste'], command=self.esegui_analisi_descrittiva)
        self.selettore_grafico_descrittiva.set('Barre')

        # Bottone Refresh (sempre visibile)
        self.bottone_refresh_descrittiva = customtkinter.CTkButton(self.frame_controlli_descrittiva, text="🔄", command=self.esegui_analisi_descrittiva, width=35, height=35)
        self.bottone_refresh_descrittiva.pack(side="left", padx=(10, 10))

        # Frame per i risultati
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
        self.bottone_refresh_bivariata = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_analisi_bivariata, width=35, height=35)
        self.bottone_refresh_bivariata.grid(row=0, column=4, padx=(5,10), pady=5)
        self.frame_risultati_bivariata = customtkinter.CTkFrame(tab)
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1); self.frame_risultati_bivariata.grid_rowconfigure(1, weight=1)

    def setup_tab_inferenziale(self):
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(0, weight=1)
        scroll_frame = customtkinter.CTkScrollableFrame(tab); scroll_frame.grid(row=0, column=0, sticky="nsew"); scroll_frame.grid_columnconfigure(0, weight=1)
        self.setup_poisson_section(scroll_frame); self.setup_ttest_section(scroll_frame); self.setup_ci_section(scroll_frame)

    def setup_poisson_section(self, parent):
        frame_poisson = customtkinter.CTkFrame(parent, border_width=1); frame_poisson.grid(row=0, column=0, padx=10, pady=10, sticky="nsew"); frame_poisson.grid_columnconfigure(1, weight=1)
        info_poisson = ("Il Modello di Poisson è uno strumento statistico usato per calcolare la probabilità che un certo numero di eventi (k) si verifichi in un intervallo di tempo o spazio fissato, conoscendo il tasso medio di accadimento (λ).\n\n"
                        "**A Cosa Serve Qui?**\n"
                        "Serve a rispondere a domande come: 'Qual è la probabilità che domani, nella provincia di Milano tra le 8 e le 9, si verifichino esattamente 2 incidenti?'.\n"
                        "Si basa sulla media storica degli incidenti in quella stessa provincia e fascia oraria, fornendo una stima predittiva.")
        self._crea_titolo_sezione(frame_poisson, 0, "Modello di Poisson", info_poisson, columnspan=3)
        customtkinter.CTkLabel(frame_poisson, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_poisson = customtkinter.CTkComboBox(frame_poisson, values=[]); self.selettore_provincia_poisson.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Ora o Fascia Oraria (es. 14 o 8-17):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_ora_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Inserisci un'ora singola (0-23) o un range"); self.entry_ora_poisson.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Numero incidenti (k):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_k_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Es. 2"); self.entry_k_poisson.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_poisson, text="Calcola Probabilità", command=self.esegui_poisson).grid(row=4, column=0, padx=10, pady=10)
        self.risultato_poisson_textbox = customtkinter.CTkTextbox(frame_poisson, wrap="word", font=customtkinter.CTkFont(size=13)); self.risultato_poisson_textbox.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.risultato_poisson_textbox.configure(state="disabled")

    def setup_ttest_section(self, parent):
        frame_ttest = customtkinter.CTkFrame(parent, border_width=1); frame_ttest.grid(row=1, column=0, padx=10, pady=10, sticky="nsew"); frame_ttest.grid_columnconfigure(1, weight=1)
        info_ttest = ("Il Test T per Campioni Indipendenti è un test di ipotesi che confronta le medie di due gruppi distinti e non correlati per determinare se la differenza osservata tra le loro medie è statisticamente significativa o se potrebbe essere dovuta al caso.\n\n"
                      "**A Cosa Serve Qui?**\n"
                      "Lo usiamo per verificare se c'è una differenza reale nel numero medio di feriti tra gli incidenti che avvengono di giorno (7-19) e quelli che avvengono di notte. Un p-value basso (solitamente < 0.05) suggerisce che la differenza non è casuale, ma sistematica (es. gli incidenti notturni sono mediamente più gravi).")
        self._crea_titolo_sezione(frame_ttest, 0, "Test T per Campioni Indipendenti", info_ttest, columnspan=2)
        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0))
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        self.risultato_ttest_textbox = customtkinter.CTkTextbox(frame_ttest, wrap="word", font=customtkinter.CTkFont(size=13)); self.risultato_ttest_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ttest_textbox.configure(state="disabled")

    def setup_ci_section(self, parent):
        frame_ci = customtkinter.CTkFrame(parent, border_width=1); frame_ci.grid(row=2, column=0, padx=10, pady=10, sticky="nsew"); frame_ci.grid_columnconfigure(1, weight=1)
        info_ci = ("Un Intervallo di Confidenza (IC) è un intervallo di valori, calcolato a partire dai dati campionari, che si stima con un certo livello di fiducia (es. 95%) possa contenere il 'vero' valore di un parametro della popolazione (es. la 'vera' media di incidenti giornalieri, che non possiamo conoscere con certezza).\n\n"
                   "**A Cosa Serve Qui?**\n"
                   "Invece di avere solo la media di incidenti giornalieri per una provincia (una stima puntuale), l'IC ci fornisce un range di plausibilità. Un intervallo stretto (es. [2.1, 2.5]) indica una stima molto precisa; un intervallo largo (es. [1.5, 5.5]) indica maggiore incertezza.")
        self._crea_titolo_sezione(frame_ci, 0, "Intervallo di Confidenza", info_ci, columnspan=2)
        customtkinter.CTkLabel(frame_ci, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_ci = customtkinter.CTkComboBox(frame_ci, values=[]); self.selettore_provincia_ci.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_ci, text="Livello Confidenza (%):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_livello_ci = customtkinter.CTkEntry(frame_ci, placeholder_text="Es. 95"); self.entry_livello_ci.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_ci, text="Calcola Intervallo", command=self.esegui_ci).grid(row=3, column=0, padx=10, pady=10, sticky="n")
        self.risultato_ci_textbox = customtkinter.CTkTextbox(frame_ci, wrap="word", font=customtkinter.CTkFont(size=13)); self.risultato_ci_textbox.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ci_textbox.configure(state="disabled")

    def popola_tabella_dati(self):
        for item in self.data_table.get_children(): self.data_table.delete(item)
        if self.df is None or self.df.empty: return
        cols_da_mostrare = [col for col in ['Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata'] if col in self.df.columns]
        display_df = self.df[cols_da_mostrare].copy()
        display_df = display_df.sort_values(by='Data_Ora_Incidente', ascending=False)
        display_df['Data_Ora_Incidente'] = display_df['Data_Ora_Incidente'].dt.strftime('%Y-%m-%d %H:%M:%S')
        for _, row in display_df.head(500).iterrows(): self.data_table.insert("", "end", values=list(row))

    def esegui_analisi_descrittiva(self, *args):
        if self.df is None: return
        variable = self.selettore_var_descrittiva.get()
        if not variable: return

        # Gestione dinamica dei controlli UI
        if variable == 'Data_Ora_Incidente':
            # Mostra i controlli per l'analisi temporale
            self.label_andamento.pack(side="left", padx=(20,5))
            self.selettore_andamento.pack(side="left", padx=5)
            self.label_tipo_grafico.pack(side="left", padx=(20,5))
            self.selettore_grafico_descrittiva.pack(side="left", padx=5)
            
            # Imposta le opzioni grafiche adatte all'analisi temporale
            opzioni_grafico = ['Barre', 'Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_grafico:
                self.selettore_grafico_descrittiva.set(opzioni_grafico[0])
            self.selettore_grafico_descrittiva.configure(values=opzioni_grafico)
            
            self.analisi_speciale_data_ora()
        else:
            # Nascondi i controlli per l'analisi temporale
            self.label_andamento.pack_forget()
            self.selettore_andamento.pack_forget()

            # Mostra solo il selettore del tipo di grafico standard
            self.label_tipo_grafico.pack(side="left", padx=(20,5))
            self.selettore_grafico_descrittiva.pack(side="left", padx=5, expand=True, fill="x")

            opzioni_standard = ['Istogramma', 'Box Plot', 'Barre', 'Torta', 'Linee', 'Aste']
            if self.selettore_grafico_descrittiva.get() not in opzioni_standard:
                 self.selettore_grafico_descrittiva.set('Barre')
            self.selettore_grafico_descrittiva.configure(values=opzioni_standard)
            self.analisi_generica(variable)

    def analisi_speciale_data_ora(self):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        
        tipo_aggregazione = self.selettore_andamento.get()
        tipo_grafico = self.selettore_grafico_descrittiva.get()

        info = ("L'analisi della variabile temporale è cruciale per la sicurezza stradale. Permette di identificare pattern e ciclicità nel fenomeno degli incidenti, rispondendo a domande fondamentali come:\n\n"
                "- Ci sono più incidenti in certi periodi dell'anno?\n"
                "- Quali sono le ore del giorno più pericolose?\n"
                "- Il rischio è maggiore nei giorni feriali o nel weekend?")
        guida = ("- **Andamento Generale**: Mostra il numero di incidenti giorno per giorno. Utile per identificare trend a lungo termine, stagionalità (es. picchi estivi) o l'impatto di eventi specifici.\n\n"
                 "- **Distribuzione Oraria**: Aggrega tutti gli incidenti in base all'ora in cui sono avvenuti. Essenziale per localizzare le fasce orarie critiche (es. ora di punta mattutina/serale).\n\n"
                 "- **Distribuzione Settimanale**: Aggrega gli incidenti per giorno della settimana. Evidenzia le differenze tra giorni lavorativi e festivi, aiutando a pianificare controlli mirati.")
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, f"Analisi Temporale: {tipo_aggregazione}", info, testo_guida=guida)
        
        frame_grafico = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_grafico.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.frame_risultati_descrittiva.grid_rowconfigure(1, weight=1)

        fig, ax = plt.subplots(figsize=(12, 6))
        plot_data = None
        ax.set_ylabel('Numero di Incidenti')

        if tipo_aggregazione == 'Distribuzione Oraria':
            plot_data = self.df['Ora'].value_counts().sort_index()
            ax.set_title('Distribuzione Incidenti per Ora del Giorno')
            ax.set_xlabel('Ora del Giorno')
        
        elif tipo_aggregazione == 'Distribuzione Settimanale':
            days_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
            days_order = list(days_map.values())
            daily_names = self.df['Data_Ora_Incidente'].dt.weekday.map(days_map)
            plot_data = daily_names.value_counts().reindex(days_order)
            ax.set_title('Distribuzione Incidenti per Giorno della Settimana')
            ax.set_xlabel('Giorno della Settimana')
            ax.tick_params(axis='x', rotation=45)

        else: # Default: 'Andamento Generale'
            plot_data = self.df.groupby(self.df['Data_Ora_Incidente'].dt.date).size()
            ax.set_title('Andamento Temporale degli Incidenti')
            ax.set_xlabel('Data')
        
        # ==================== INIZIO BLOCCO DI CORREZIONE ====================
        try:
            if tipo_grafico == 'Barre':
                plot_data.plot(kind='bar', ax=ax)
            elif tipo_grafico == 'Linee':
                plot_data.plot(kind='line', ax=ax, marker='o')
            elif tipo_grafico == 'Aste':
                ax.stem(plot_data.index.astype(str), plot_data.values)
            else:
                # Fallback nel caso in cui un tipo non sia gestito
                plot_data.plot(kind='line', ax=ax)
        # ===================== FINE BLOCCO DI CORREZIONE =====================
        except Exception as e:
            ax.text(0.5, 0.5, f"Impossibile generare il grafico: {e}", ha='center')

        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.matplotlib_widgets.append(canvas)
        plt.close(fig)
        
    def analisi_generica(self, variable):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        tipo_grafico = self.selettore_grafico_descrittiva.get()
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato disponibile.").pack(); return

        frame_stats = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_stats.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        frame_grafico = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_grafico.grid(row=1, column=0, sticky='nsew', padx=5, pady=10)
        self.frame_risultati_descrittiva.grid_rowconfigure(1, weight=1)
        
        info = ("L'analisi descrittiva univariata esplora una singola variabile alla volta. Il suo scopo è sintetizzare e descrivere le caratteristiche principali dei dati.\n\n"
                "- Per **variabili numeriche** (es. N. Feriti), calcola indici di tendenza centrale (media, mediana), di dispersione (deviazione standard) e di forma (simmetria) per capire l'ordine di grandezza e la variabilità del fenomeno.\n"
                "- Per **variabili categoriche** (es. Tipo Strada), calcola le frequenze di ogni categoria per capire quali sono le modalità più comuni.")
        guida = ("**Come leggere gli Indici (per dati numerici):**\n"
                 "- **Media vs Mediana**: Se sono molto diverse, la distribuzione è asimmetrica.\n"
                 "- **Dev. Std / CV**: Valori alti indicano grande variabilità (dati molto dispersi).\n"
                 "- **Asimmetria (Skew)**: >0 coda a dx, <0 coda a sx.\n"
                 "- **Curtosi (Kurt)**: >0 distribuzione 'appuntita', <0 'piatta'.\n\n"
                 "**Come leggere i Grafici:**\n"
                 "- **Istogramma/Box Plot**: Mostrano la forma della distribuzione di dati numerici.\n"
                 "- **Barre/Torta**: Confrontano le frequenze delle diverse categorie. Il grafico a torta è efficace solo con poche categorie.")
        self._crea_titolo_sezione(frame_stats, 0, f"Analisi: '{variable}'", info, testo_guida=guida)

        is_numeric = pd.api.types.is_numeric_dtype(data)
        is_aggregated = False

        if is_numeric:
            mean, median, mode = data.mean(), data.median(), data.mode().iloc[0] if not data.mode().empty else 'N/A'; variance, std_dev = data.var(ddof=1), data.std(ddof=1); mad = (data - mean).abs().mean(); range_val = data.max() - data.min(); cv = std_dev / mean if mean != 0 else 0; skew, kurt = data.skew(), data.kurtosis(); q1, q3, iqr = data.quantile(0.25), data.quantile(0.75), data.quantile(0.75) - data.quantile(0.25); cheb_low, cheb_high = mean - 2 * std_dev, mean + 2 * std_dev; frame_indici = customtkinter.CTkFrame(frame_stats); frame_indici.grid(row=1, column=0, sticky='ew', pady=10); frame_indici.grid_columnconfigure((0,1,2,3), weight=1); indici = {'Media': mean, 'Mediana': median, 'Moda': mode, 'Varianza': variance, 'Dev. Std': std_dev, 'Range': range_val, 'CV': cv, 'Asimmetria': skew, 'Curtosi': kurt, 'Q1': q1, 'Q3': q3, 'IQR': iqr}; row, col = 0, 0
            for key, val in indici.items():
                text = f"{key}\n{val:.3f}" if isinstance(val, (int, float)) else f"{key}\n{val}"; customtkinter.CTkLabel(frame_indici, text=text, justify="center").grid(row=row, column=col, padx=5, pady=5, sticky="ew"); col = (col + 1) % 4
                if col == 0: row += 1
            customtkinter.CTkLabel(frame_indici, text=f"Intervallo di Chebyshev (k=2): [{cheb_low:.3f}, {cheb_high:.3f}] (contiene almeno il 75% dei dati)", justify='center').grid(row=row+1, column=0, columnspan=4, pady=10)
        else:
            if pd.api.types.is_datetime64_any_dtype(data) or (len(data) > 0 and isinstance(data.iloc[0], date)):
                data = data.astype(str)
            
            freq_data = data.value_counts()
            
            limite_categorie = 10 if tipo_grafico == 'Torta' else 20

            if len(freq_data) > limite_categorie:
                is_aggregated = True
                top_data = freq_data.head(limite_categorie - 1)
                other_sum = freq_data.tail(len(freq_data) - (limite_categorie - 1)).sum()
                freq_data = pd.concat([top_data, pd.Series({'Altro': other_sum})])

        fig, ax = plt.subplots(figsize=(8, 5))
        try:
            plot_title = f"{tipo_grafico} di '{variable}'"
            
            if tipo_grafico == 'Istogramma':
                if is_numeric: ax.hist(data, bins='auto', edgecolor='black'); ax.set_xlabel(variable); ax.set_ylabel('Frequenza')
                else: ax.text(0.5, 0.5, 'Istogramma non applicabile a dati categorici', ha='center')
            elif tipo_grafico == 'Box Plot':
                if is_numeric: ax.boxplot(data, vert=False, showfliers=True); ax.set_yticklabels([variable]); ax.set_xlabel('Valore')
                else: ax.text(0.5, 0.5, 'Box Plot non applicabile a dati categorici', ha='center')
            else:
                # Se freq_data non esiste (perché i dati sono numerici), lo creiamo ora.
                if 'freq_data' not in locals():
                    freq_data = data.value_counts()
                    limite_categorie = 10 if tipo_grafico == 'Torta' else 20
                    if len(freq_data) > limite_categorie:
                        is_aggregated = True
                        top_data = freq_data.head(limite_categorie - 1)
                        other_sum = freq_data.tail(len(freq_data) - (limite_categorie - 1)).sum()
                        freq_data = pd.concat([top_data, pd.Series({'Altro': other_sum})])

                if is_aggregated: plot_title += f" (Top {limite_categorie-1} + Altro)"
                
                # Per grafici a linee con indici non numerici (es. date come stringhe), ordiniamo
                plot_data = freq_data.sort_index() if tipo_grafico == 'Linee' else freq_data
                
                ax.set_xlabel('Categorie'); ax.set_ylabel('Frequenza')
                if tipo_grafico == 'Barre': plot_data.plot(kind='bar', ax=ax)
                elif tipo_grafico == 'Linee': plot_data.plot(kind='line', ax=ax, marker='o')
                elif tipo_grafico == 'Torta': 
                    plot_data.plot(kind='pie', ax=ax, autopct=lambda p: f'{p:.1f}%' if p > 3 else '', textprops={'fontsize': 10})
                    ax.set_ylabel('')
                elif tipo_grafico == 'Aste': ax.stem(plot_data.index.astype(str), plot_data.values)
                ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            ax.set_title(plot_title); ax.grid(True, linestyle='--', alpha=0.6); fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.draw()
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

            x_data, y_data = df_subset[var_x], df_subset[var_y]

            info = ("L'analisi bivariata esplora la relazione tra **due variabili numeriche** contemporaneamente. Si compone di due parti:\n\n"
                    "1.  **Correlazione**: Misura la **forza** e la **direzione** di un legame lineare tra le due variabili. Il coefficiente 'r' varia da -1 (relazione inversa perfetta) a +1 (relazione diretta perfetta), con 0 che indica assenza di legame lineare.\n\n"
                    "2.  **Regressione Lineare Semplice**: Fornisce un'equazione matematica (una retta) che descrive la relazione e permette di **prevedere** il valore di una variabile (Y) conoscendo il valore dell'altra (X).")
            guida = ("- **Punti Blu (Dati Osservati)**: Ogni punto rappresenta un singolo incidente, con le sue coordinate (X, Y).\n"
                     "- **Forma della Nuvola**: Se i punti tendono a salire da sinistra a destra, la correlazione è positiva. Se tendono a scendere, è negativa. Se sono sparsi casualmente, la correlazione è debole o nulla.\n"
                     "- **Retta Rossa (di Regressione)**: È la linea che 'meglio' approssima la nuvola di punti. La sua pendenza indica di quanto cambia mediamente Y per un aumento unitario di X.\n"
                     "- **Dispersione dei Punti**: Più i punti sono vicini alla retta, più forte è la relazione e più affidabili sono le previsioni.")
            self._crea_titolo_sezione(self.frame_risultati_bivariata, 0, "Analisi Correlazione e Regressione", info, testo_guida=guida)

            if var_x == var_y:
                correlation, p_value, slope, intercept = 1.0, 0.0, 1.0, 0.0
            else:
                regression = stats.linregress(x=x_data, y=y_data)
                slope, intercept, correlation, p_value = regression.slope, regression.intercept, regression.rvalue, regression.pvalue

            frame_testuali = customtkinter.CTkFrame(self.frame_risultati_bivariata)
            frame_testuali.grid(row=1, column=0, sticky="ew", padx=10)
            risultati = (f"Coefficiente di Correlazione (r): {correlation:.4f} (p-value: {p_value:.3g})\n"
                         f"Equazione Retta di Regressione: y = {slope:.4f}x + {intercept:.4f}")

            customtkinter.CTkLabel(frame_testuali, text=risultati, justify="left").pack(pady=5)

            frame_grafico = customtkinter.CTkFrame(self.frame_risultati_bivariata)
            frame_grafico.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
            self.frame_risultati_bivariata.grid_rowconfigure(2, weight=1)

            fig, ax = plt.subplots(figsize=(8, 6))

            # ==== BLOCCO MODIFICATO: GESTIONE DINAMICA DELLO SCATTER PLOT ====
            num_points = len(x_data)
            # Adatta la dimensione e la trasparenza in base al numero di punti
            if num_points > 100:
                point_size = max(2, 40 / np.log10(num_points)) # Diminuisce logaritmicamente
                alpha_value = max(0.1, 0.7 / np.log10(num_points)) # Diminuisce logaritmicamente
            else:
                point_size = 20
                alpha_value = 0.6
            
            ax.scatter(x_data, y_data, alpha=alpha_value, s=point_size, label='Dati Osservati')
            # =================================================================

            line_x = np.array(ax.get_xlim()); line_y = slope * line_x + intercept
            ax.plot(line_x, line_y, color='red', label='Retta di Regressione')
            ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}'); ax.set_xlabel(var_x); ax.set_ylabel(var_y)
            ax.legend(); ax.grid(True, linestyle='--', alpha=0.6); fig.tight_layout()

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
            ttest_res = stats.ttest_ind(data_diurno, data_notturno, equal_var=False) # Welch's t-test
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