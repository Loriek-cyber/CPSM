# =============================================================================
# CHANGELOG ULTIME MODIFICHE
# =============================================================================
# 1. Finestra Info Adattiva: Rimosso il dimensionamento fisso da `show_info` per adattarsi al contenuto.
# 2. Titoli Centrati: Creato un metodo helper `_crea_titolo_sezione` per centrare tutti i titoli di sezione in modo uniforme.
# 3. Spiegazioni Migliorate: Arricchite tutte le stringhe `info_..._msg` con dettagli e una legenda dei termini.
# 4. UI Inferenziale Corretta: Configurato il layout della griglia per permettere ai riquadri dei risultati di espandersi verticalmente.
# =============================================================================

# =============================================================================
# IMPORTAZIONE DELLE LIBRERIE NECESSARIE
# =============================================================================
import tkinter
from tkinter import filedialog, ttk
import customtkinter
import pandas as pd
import numpy as np
import io
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# =============================================================================
# IMPOSTAZIONI INIZIALI DELL'INTERFACCIA
# =============================================================================
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# =============================================================================
# DEFINIZIONE DELLA CLASSE PRINCIPALE DELL'APPLICAZIONE
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
        
        # --- FRAME SUPERIORE: CARICAMENTO DATI ---
        self.frame_caricamento = customtkinter.CTkFrame(self)
        self.frame_caricamento.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.frame_caricamento.grid_columnconfigure((0, 1, 2), weight=1)
        self.label_file = customtkinter.CTkLabel(self.frame_caricamento, text="Nessun dato caricato.", text_color="gray")
        self.label_file.grid(row=0, column=0, padx=20, pady=20)
        self.bottone_carica_csv = customtkinter.CTkButton(self.frame_caricamento, text="Carica File CSV", command=self.carica_csv)
        self.bottone_carica_csv.grid(row=0, column=1, padx=20, pady=20)
        self.bottone_dati_esempio = customtkinter.CTkButton(self.frame_caricamento, text="Usa Dati Simulati", command=self.carica_dati_esempio)
        self.bottone_dati_esempio.grid(row=0, column=2, padx=20, pady=20)

        # --- WIDGET A SCHEDE (TAB) PER LE DIVERSE ANALISI ---
        self.tab_view = customtkinter.CTkTabview(self, width=250)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.tab_view.add("Analisi Descrittiva")
        self.tab_view.add("Analisi Bivariata")
        self.tab_view.add("Analisi Inferenziale")
        
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

    # =============================================================================
    # FUNZIONI DI UTILITÀ E GESTIONE DATI
    # =============================================================================

    def _crea_titolo_sezione(self, parent, row, testo_titolo, testo_info, columnspan=1):
        """Metodo helper per creare una riga di titolo centrata con bottone info."""
        # Crea un frame contenitore che si espande orizzontalmente.
        frame_titolo = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame_titolo.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(15, 5))
        
        # Crea un frame interno che verrà centrato grazie a .pack()
        inner_frame = customtkinter.CTkFrame(frame_titolo, fg_color="transparent")
        inner_frame.pack()
        
        # Aggiunge etichetta e bottone al frame interno.
        customtkinter.CTkLabel(inner_frame, text=testo_titolo, font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        customtkinter.CTkButton(inner_frame, text="i", command=lambda: self.show_info(f"Info: {testo_titolo}", testo_info), width=28, height=28, corner_radius=14).pack(side="left")

    def show_info(self, title, message):
        """Crea e mostra una finestra popup con un messaggio informativo e dimensione adattiva."""
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title)
        info_window.transient(self)
        info_window.grab_set()

        # Etichetta per visualizzare il messaggio, che determinerà la dimensione della finestra.
        label = customtkinter.CTkLabel(info_window, text=message, wraplength=550, justify="left", font=customtkinter.CTkFont(size=14))
        label.pack(padx=20, pady=20, expand=True, fill="both")

        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")

    def carica_csv(self):
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        if not filepath: return
        try:
            df = pd.read_csv(filepath)
            self.inizializza_dati(df)
            self.label_file.configure(text=f"Caricato: {filepath.split('/')[-1]}")
        except Exception as e:
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    def carica_dati_esempio(self):
        sample_csv = """Data_Ora_Incidente,Provincia,Giorno_Settimana,Tipo_Strada,Numero_Feriti,Numero_Morti,Velocita_Media_Stimata
2023-01-15 08:30:00,Milano,Domenica,Urbana,2,0,45
2023-01-15 18:45:00,Milano,Domenica,Autostrada,3,1,110
2023-01-16 12:10:00,Roma,Lunedì,Statale,1,0,75
2023-01-16 19:00:00,Napoli,Lunedì,Urbana,1,0,50
2023-01-17 09:05:00,Milano,Martedì,Urbana,0,0,30
2023-01-17 22:30:00,Roma,Martedì,Autostrada,5,0,130
2023-01-18 17:50:00,Torino,Mercoledì,Urbana,2,0,55
2023-01-18 03:15:00,Napoli,Mercoledì,Statale,4,1,90
2023-01-19 11:20:00,Milano,Giovedì,Statale,1,0,80
2023-01-20 23:55:00,Roma,Venerdì,Urbana,3,0,60
2023-01-21 15:00:00,Torino,Sabato,Autostrada,2,0,120
2023-01-22 01:00:00,Milano,Domenica,Urbana,1,0,65
2023-01-22 08:15:00,Napoli,Domenica,Urbana,2,0,40
2023-01-23 18:00:00,Milano,Lunedì,Urbana,1,0,50
2023-01-23 18:30:00,Milano,Lunedì,Urbana,3,0,45
"""
        df = pd.read_csv(io.StringIO(sample_csv))
        self.inizializza_dati(df)
        self.label_file.configure(text="Caricati dati di esempio.")

    def inizializza_dati(self, df):
        self.df = df
        for col in self.df.columns:
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except (ValueError, TypeError):
                pass
        if 'Data_Ora_Incidente' in self.df.columns:
            try:
                self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'])
                self.df['Ora'] = self.df['Data_Ora_Incidente'].dt.hour
                self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
            except Exception as e:
                print(f"Errore nella conversione di Data_Ora_Incidente: {e}")
        if 'Numero_Morti' in self.df.columns:
            self.df['Mortale'] = (self.df['Numero_Morti'] > 0).astype(int)
        self.aggiorna_selettori()

    def aggiorna_selettori(self):
        if self.df is None: return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category', 'datetime64[ns]']).columns.tolist()
        all_columns = object_columns + numeric_columns
        if 'Data_Ora_Incidente' in self.df.columns and 'Data_Ora_Incidente' in all_columns:
            all_columns.remove('Data_Ora_Incidente')
            all_columns.insert(0, 'Data_Ora_Incidente')
        province_uniche = self.df['Provincia'].unique().tolist() if 'Provincia' in self.df.columns else []
        self.selettore_var_descrittiva.configure(values=all_columns)
        if all_columns:
            self.selettore_var_descrittiva.set(all_columns[0])
            self.esegui_analisi_descrittiva()
        self.selettore_var_biv_x.configure(values=numeric_columns)
        self.selettore_var_biv_y.configure(values=numeric_columns)
        if numeric_columns and len(numeric_columns) > 1:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[1])
        elif numeric_columns:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[0])
        self.selettore_provincia_poisson.configure(values=province_uniche)
        self.selettore_provincia_ci.configure(values=province_uniche)
        if province_uniche:
            self.selettore_provincia_poisson.set(province_uniche[0])
            self.selettore_provincia_ci.set(province_uniche[0])

    def pulisci_grafici(self):
        for widget in self.matplotlib_widgets:
            widget.destroy()
        self.matplotlib_widgets = []

    def crea_canvas_matplotlib(self, parent, r, c, w=1, h=1):
        frame = customtkinter.CTkFrame(parent)
        frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew", rowspan=h, columnspan=w)
        self.matplotlib_widgets.append(frame)
        return frame

    # =============================================================================
    # SETUP DELLE SCHEDE (TAB)
    # =============================================================================

    def setup_tab_descrittiva(self):
        tab = self.tab_view.tab("Analisi Descrittiva")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Seleziona una variabile:").pack(side="left", padx=10)
        self.selettore_var_descrittiva = customtkinter.CTkComboBox(frame_controlli, values=[], command=lambda _: self.esegui_analisi_descrittiva())
        self.selettore_var_descrittiva.pack(side="left", padx=10, expand=True, fill="x")
        self.frame_risultati_descrittiva = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Analisi Descrittiva")
        self.frame_risultati_descrittiva.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)
    
    def setup_tab_bivariata(self):
        tab = self.tab_view.tab("Analisi Bivariata")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure((1, 3), weight=1)
        customtkinter.CTkLabel(frame_controlli, text="Variabile X:").grid(row=0, column=0, padx=10, pady=5)
        self.selettore_var_biv_x = customtkinter.CTkComboBox(frame_controlli, values=[])
        self.selettore_var_biv_x.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Variabile Y:").grid(row=0, column=2, padx=10, pady=5)
        self.selettore_var_biv_y = customtkinter.CTkComboBox(frame_controlli, values=[])
        self.selettore_var_biv_y.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_controlli, text="Esegui Analisi", command=self.esegui_analisi_bivariata).grid(row=0, column=4, padx=10, pady=5)
        self.frame_risultati_bivariata = customtkinter.CTkFrame(tab)
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1)
        self.frame_risultati_bivariata.grid_rowconfigure(2, weight=1)

    def setup_tab_inferenziale(self):
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1)
        # Configura le righe per dare peso ai riquadri dei test, permettendo loro di espandersi.
        tab.grid_rowconfigure((0, 1, 2), weight=1)
        
        # --- Sezione 1: Modello di Poisson ---
        frame_poisson = customtkinter.CTkFrame(tab, border_width=1)
        frame_poisson.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame_poisson.grid_columnconfigure(1, weight=1)
        # Configura la riga del risultato per espandersi.
        frame_poisson.grid_rowconfigure(5, weight=1) 
        
        self._crea_titolo_sezione(frame_poisson, 0, "Modello di Poisson", 
            """Il Modello di Poisson calcola la probabilità che un certo numero di eventi (k) si verifichi in un intervallo fissato, dato un tasso medio di accadimento (λ).

--- Legenda Termini ---
- **λ (Lambda):** Tasso medio di accadimento. In questo caso, è il numero medio di incidenti stimato per la provincia e l'ora selezionate.
- **k:** Il numero esatto di eventi (incidenti) di cui si vuole calcolare la probabilità.
- **P(X=k):** La probabilità che il numero di incidenti sia esattamente uguale a 'k' (calcolata tramite la Funzione di Massa di Probabilità - PMF).""", columnspan=3)

        customtkinter.CTkLabel(frame_poisson, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_poisson = customtkinter.CTkComboBox(frame_poisson, values=[])
        self.selettore_provincia_poisson.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Fascia Oraria (0-23):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_ora_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Es. 18")
        self.entry_ora_poisson.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_poisson, text="Numero incidenti (k):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_k_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Es. 2")
        self.entry_k_poisson.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_poisson, text="Calcola Probabilità", command=self.esegui_poisson).grid(row=4, column=0, padx=10, pady=10)
        
        self.risultato_poisson_textbox = customtkinter.CTkTextbox(frame_poisson, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_poisson_textbox.grid(row=4, column=1, rowspan=2, columnspan=2, padx=10, pady=10, sticky="nsew") # rowspan e sticky per espansione
        self.risultato_poisson_textbox.configure(state="disabled")

        # --- Sezione 2: Test T ---
        frame_ttest = customtkinter.CTkFrame(tab, border_width=1)
        frame_ttest.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame_ttest.grid_columnconfigure(1, weight=1)
        frame_ttest.grid_rowconfigure(2, weight=1) # Riga del risultato espandibile
        
        self._crea_titolo_sezione(frame_ttest, 0, "Test T per Campioni Indipendenti",
            """Il Test T confronta le medie di due gruppi indipendenti (es. feriti di giorno vs notte) per determinare se la loro differenza è statisticamente significativa o dovuta al caso.

--- Legenda Termini ---
- **Ipotesi Nulla (H₀):** La supposizione iniziale che non esista una vera differenza tra le medie dei due gruppi.
- **p-value:** La probabilità di osservare una differenza grande come quella nei dati (o più grande) se l'Ipotesi Nulla fosse vera. Un p-value basso (< 0.05) è un'evidenza forte contro H₀.
- **Statistica t:** Misura la dimensione della differenza tra le medie in rapporto alla variabilità dei dati. Più è lontana da zero, più la differenza è marcata.""", columnspan=2)

        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0))
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        
        self.risultato_ttest_textbox = customtkinter.CTkTextbox(frame_ttest, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_ttest_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ttest_textbox.configure(state="disabled")

        # --- Sezione 3: Intervallo di Confidenza ---
        frame_ci = customtkinter.CTkFrame(tab, border_width=1)
        frame_ci.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame_ci.grid_columnconfigure(1, weight=1)
        frame_ci.grid_rowconfigure(3, weight=1) # Riga del risultato espandibile
        
        self._crea_titolo_sezione(frame_ci, 0, "Intervallo di Confidenza",
            """L'Intervallo di Confidenza (IC) fornisce un range di valori plausibili per la 'vera' media di una popolazione, basandosi sui dati di un campione.

--- Legenda Termini ---
- **Livello di Confidenza:** La probabilità (es. 95%) che, ripetendo il campionamento molte volte, l'intervallo calcolato contenga la vera media della popolazione.
- **Media Campionaria:** La media calcolata solo sui dati a disposizione.
- **Range (IC):** L'intervallo [valore inferiore, valore superiore]. Un intervallo stretto indica una stima più precisa.""", columnspan=2)

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

    # =============================================================================
    # FUNZIONI DI ESECUZIONE DELLE ANALISI
    # =============================================================================
    
    def esegui_analisi_descrittiva(self):
        if self.df is None: return
        variable = self.selettore_var_descrittiva.get()
        if not variable: return
        for widget in self.frame_risultati_descrittiva.winfo_children():
            widget.destroy()
        self.pulisci_grafici()
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato per questa variabile.").pack()
            return
        if variable == 'Data_Ora_Incidente':
            self.analisi_temporale(variable)
        elif pd.api.types.is_numeric_dtype(data):
            self.analisi_numerica(variable, data)
        else:
            self.analisi_categorica(variable, data)

    def analisi_temporale(self, variable):
        self.frame_risultati_descrittiva.grid_columnconfigure(1, weight=0, minsize=0)
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(2, weight=1) # Riga del grafico espandibile
        
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, "Andamento Temporale Incidenti",
            "Questo grafico mostra il numero di incidenti registrati giorno per giorno, permettendo di identificare trend, picchi o periodi di maggiore criticità.")
        
        daily_counts = self.df.groupby('Giorno').size()
        if daily_counts.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato giornaliero da analizzare.").grid(row=1, column=0)
            return
        frame_stats = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_stats.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        giorno_max = daily_counts.idxmax()
        count_max = daily_counts.max()
        stats_text = (f"Periodo analizzato: dal {pd.to_datetime(daily_counts.index.min()).strftime('%d/%m/%Y')} al {pd.to_datetime(daily_counts.index.max()).strftime('%d/%m/%Y')}\n"
                      f"Totale giorni con incidenti: {len(daily_counts)}\n"
                      f"Giorno con più incidenti: {pd.to_datetime(giorno_max).strftime('%d/%m/%Y')} (con {count_max} incidenti)")
        customtkinter.CTkLabel(frame_stats, text=stats_text, justify="left").pack(padx=10, pady=10)
        
        canvas_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 2, 0)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linestyle='-', color='#3b82f6')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        ax.set_title('Numero di Incidenti al Giorno')
        ax.set_xlabel('Data')
        ax.set_ylabel('Numero di Incidenti')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        plt.close(fig)

    def analisi_numerica(self, variable, data):
        self.frame_risultati_descrittiva.grid_columnconfigure((0, 1), weight=1) # 2 colonne
        self.frame_risultati_descrittiva.grid_rowconfigure(3, weight=1) # Riga dei grafici espandibile
        
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, f"Indici Statistici per '{variable}'",
            """Questi indici riassumono le principali caratteristiche della distribuzione dei dati.

--- Legenda Termini ---
- **Media, Mediana, Moda:** Misure di tendenza centrale che indicano il 'centro' dei dati.
- **Varianza, Dev. Standard:** Misure di dispersione che indicano quanto i dati sono sparsi attorno alla media.
- **Asimmetria (Skewness):** Misura l'asimmetria della distribuzione. >0: coda a destra; <0: coda a sinistra.
- **Curtosi (Kurtosis):** Misura la 'pesantezza' delle code. >0: code più pesanti di una normale (più outlier).""", columnspan=2)

        frame_valori_indici = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_valori_indici.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        frame_valori_indici.grid_columnconfigure((0,1,2,3), weight=1)
        mean, median, mode = data.mean(), data.median(), data.mode().iloc[0] if not data.mode().empty else 'N/A'
        variance, std_dev = data.var(), data.std()
        mad = (data - data.mean()).abs().mean()
        range_val = data.max() - data.min()
        cv = std_dev / mean if mean != 0 else 0
        skew, kurt = data.skew(), data.kurtosis()
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        indici = {'Media Camp.': mean, 'Mediana': median, 'Moda': mode, 'Varianza Camp.': variance, 'Dev. Standard': std_dev, 'Scarto Medio Ass.': mad, 'Range': range_val, 'Coeff. Variazione': cv, 'Asimmetria': skew, 'Curtosi': kurt, '1° Quartile (Q1)': q1, '3° Quartile (Q3)': q3}
        row, col = 0, 0
        for key, value in indici.items():
            text = f"{key}\n{value:.3f}" if isinstance(value, (int, float)) else f"{key}\n{value}"
            customtkinter.CTkLabel(frame_valori_indici, text=text, justify="center").grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 3: col, row = 0, row + 1
        
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 2, "Grafici di Distribuzione",
            """I grafici visualizzano la forma della distribuzione dei dati.

--- Legenda Termini ---
- **Istogramma:** Mostra la frequenza dei dati in intervalli (bin). Utile per capire la forma, la centralità e la dispersione.
- **Box Plot:** Riassume la distribuzione con 5 numeri (min, Q1, mediana, Q3, max) e mostra eventuali valori anomali (outlier).""", columnspan=2)
        
        canvas_hist_frame, canvas_box_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 0), self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 1)
        fig_hist, ax_hist = plt.subplots(figsize=(5, 4))
        ax_hist.hist(data, bins='auto', color='#3b82f6', alpha=0.7, rwidth=0.85)
        ax_hist.set_title(f'Istogramma di {variable}'), ax_hist.set_xlabel(variable), ax_hist.set_ylabel('Frequenza'), ax_hist.grid(axis='y', alpha=0.75), fig_hist.tight_layout()
        canvas_hist = FigureCanvasTkAgg(fig_hist, master=canvas_hist_frame)
        canvas_hist.draw(), canvas_hist.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        fig_box, ax_box = plt.subplots(figsize=(5, 4))
        ax_box.boxplot(data, vert=False, patch_artist=True, boxprops=dict(facecolor='#ec4899', alpha=0.7))
        ax_box.set_title(f'Box Plot di {variable}'), ax_box.set_yticklabels([variable]), ax_box.grid(axis='x', alpha=0.75), fig_box.tight_layout()
        canvas_box = FigureCanvasTkAgg(fig_box, master=canvas_box_frame)
        canvas_box.draw(), canvas_box.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        plt.close(fig_hist)
        plt.close(fig_box)

    def analisi_categorica(self, variable, data):
        # Configurazione griglia per espansione verticale dei grafici
        self.frame_risultati_descrittiva.grid_columnconfigure(1, weight=0, minsize=0)
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(3, weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(4, weight=1)

        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, f"Tabella Frequenze per '{variable}'",
            """La tabella riassume quante volte appare ogni categoria.

--- Legenda Termini ---
- **Freq. Assoluta:** Il conteggio esatto di ogni categoria.
- **Freq. Relativa:** La percentuale di ogni categoria sul totale.
- **Freq. Cumulata:** La somma progressiva delle frequenze assolute.""")
        
        frame_tabella_main = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_tabella_main.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        frame_tabella_main.grid_columnconfigure(0, weight=1)
        counts = data.value_counts()
        relative_freq = data.value_counts(normalize=True)
        cumulative_freq = counts.cumsum()
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=('Calibri', 12))
        style.configure("Treeview.Heading", font=('Calibri', 13,'bold'), anchor="center")
        tree = ttk.Treeview(frame_tabella_main, columns=('Categoria', 'Assoluta', 'Relativa', 'Cumulata'), show='headings', height=len(counts))
        for col in ('Categoria', 'Assoluta', 'Relativa', 'Cumulata'):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        for index, value in counts.items():
            tree.insert('', 'end', values=(index, value, f"{relative_freq[index] * 100:.2f}%", cumulative_freq[index]))
        tree.pack(fill="x", expand=True)
        self.matplotlib_widgets.append(frame_tabella_main)

        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 2, "Grafici di Frequenza",
            """I grafici visualizzano le proporzioni delle categorie.

--- Legenda Termini ---
- **Grafico a Barre:** Confronta la frequenza delle categorie. Ottimo per vedere 'chi vince'.
- **Grafico a Torta/Ciambella:** Mostra la percentuale di ogni categoria rispetto al totale.""")
        
        canvas_bar_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 0)
        fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
        counts.sort_values().plot(kind='barh', ax=ax_bar, color=plt.cm.viridis(np.linspace(0, 1, len(counts))))
        ax_bar.set_title(f'Grafico a Barre di {variable}'), ax_bar.set_xlabel('Frequenza Assoluta'), fig_bar.tight_layout()
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=canvas_bar_frame)
        canvas_bar.draw(), canvas_bar.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        canvas_pie_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 4, 0)
        fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
        counts.plot(kind='pie', ax=ax_pie, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'), colors=plt.cm.viridis(np.linspace(0, 1, len(counts))), textprops={'fontsize': 12})
        ax_pie.set_ylabel(''), ax_pie.set_title(f'Grafico a Torta di {variable}'), fig_pie.tight_layout()
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=canvas_pie_frame)
        canvas_pie.draw(), canvas_pie.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        plt.close(fig_bar)
        plt.close(fig_pie)

    def esegui_analisi_bivariata(self):
        if self.df is None: return
        var_x, var_y = self.selettore_var_biv_x.get(), self.selettore_var_biv_y.get()
        if not var_x or not var_y: return
        for widget in self.frame_risultati_bivariata.winfo_children():
            widget.destroy()
        self.pulisci_grafici()
        df_subset = self.df[[var_x, var_y]].dropna()
        if len(df_subset) < 2:
            customtkinter.CTkLabel(self.frame_risultati_bivariata, text="Dati insufficienti per l'analisi.").grid(row=0, column=0)
            return
            
        x_data, y_data = df_subset[var_x], df_subset[var_y]
        if var_x == var_y: correlation = 1.0
        else: correlation = df_subset.corr().iloc[0, 1]
        regression = stats.linregress(x=x_data, y=y_data)

        self._crea_titolo_sezione(self.frame_risultati_bivariata, 0, "Analisi di Correlazione e Regressione",
            """Questa analisi esplora la relazione lineare tra due variabili numeriche.

--- Legenda Termini ---
- **Coefficiente di Correlazione (r):** Varia da -1 (relazione inversa perfetta) a +1 (relazione diretta perfetta). 0 indica assenza di relazione *lineare*.
- **Retta di Regressione (y = mx + b):** La linea che meglio approssima i dati.
- **Pendenza (m):** Di quanto aumenta in media Y per ogni aumento di 1 unità in X.
- **Intercetta (b):** Il valore previsto di Y quando X è uguale a 0.""")
        
        frame_risultati_testuali = customtkinter.CTkFrame(self.frame_risultati_bivariata)
        frame_risultati_testuali.grid(row=1, column=0, sticky="ew", padx=10)
        risultati_testuali = f"Coefficiente di Correlazione (r): {correlation:.4f}\nEquazione Retta di Regressione: y = {regression.slope:.4f}x + {regression.intercept:.4f}"
        customtkinter.CTkLabel(frame_risultati_testuali, text=risultati_testuali, justify="left").pack(pady=5)
        
        canvas_frame = self.crea_canvas_matplotlib(self.frame_risultati_bivariata, 2, 0)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x_data, y_data, alpha=0.6, label='Dati')
        line_x = np.array([x_data.min(), x_data.max()])
        line_y = regression.slope * line_x + regression.intercept
        ax.plot(line_x, line_y, color='red', label='Retta di Regressione')
        ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}'), ax.set_xlabel(var_x), ax.set_ylabel(var_y), ax.legend(), ax.grid(True), fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw(), canvas.get_tk_widget().pack(fill='both', expand=True)
        plt.close(fig)

    def _update_textbox(self, textbox, text):
        """Metodo helper per aggiornare in modo sicuro il contenuto di una CTkTextbox."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def esegui_poisson(self):
        if self.df is None: return
        try:
            provincia, ora, k = self.selettore_provincia_poisson.get(), int(self.entry_ora_poisson.get()), int(self.entry_k_poisson.get())
            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique()
            if giorni_osservati == 0:
                risultato = "Nessun dato per questa provincia."
            else:
                incidenti_nell_ora = df_prov[df_prov['Ora'] == ora].shape[0]
                lambda_val = incidenti_nell_ora / giorni_osservati
                prob = stats.poisson.pmf(k, lambda_val)
                risultato = f"Provincia: {provincia}, Ora: {ora}:00\nTasso medio stimato (λ): {lambda_val:.4f} incidenti/ora\nProbabilità di {k} incidenti (P(X={k})): {prob:.4%}"
        except (ValueError, TypeError) as e:
            risultato = f"Errore: Inserire valori numerici validi.\nDettagli: {e}"
        self._update_textbox(self.risultato_poisson_textbox, risultato)

    def esegui_ttest(self):
        if self.df is None: return
        data_diurno = self.df[(self.df['Ora'] >= 7) & (self.df['Ora'] < 20)]['Numero_Feriti'].dropna()
        data_notturno = self.df[(self.df['Ora'] < 7) | (self.df['Ora'] >= 20)]['Numero_Feriti'].dropna()
        if len(data_diurno) < 2 or len(data_notturno) < 2:
            risultato = "Dati insufficienti (necessari almeno 2 campioni per gruppo)."
        else:
            ttest_res = stats.ttest_ind(data_diurno, data_notturno, equal_var=False)
            risultato = f"Confronto Numero Feriti: Diurno vs. Notturno\n\n"
            risultato += f"Media Diurna (n={len(data_diurno)}): {data_diurno.mean():.3f}\n"
            risultato += f"Media Notturna (n={len(data_notturno)}): {data_notturno.mean():.3f}\n\n"
            risultato += f"Statistica t = {ttest_res.statistic:.4f}\np-value = {ttest_res.pvalue:.4f}\n\n"
            if ttest_res.pvalue < 0.05:
                risultato += "Conclusione: Poiché p < 0.05, la differenza tra le medie è statisticamente significativa."
            else:
                risultato += "Conclusione: Poiché p >= 0.05, non c'è evidenza sufficiente per affermare che la differenza sia statisticamente significativa."
        self._update_textbox(self.risultato_ttest_textbox, risultato)

    def esegui_ci(self):
        if self.df is None: return
        try:
            provincia, livello = self.selettore_provincia_ci.get(), int(self.entry_livello_ci.get())
            if not 0 < livello < 100: raise ValueError("Livello confidenza deve essere tra 1 e 99.")
            incidenti_per_giorno = self.df[self.df['Provincia'] == provincia].groupby('Giorno').size()
            if len(incidenti_per_giorno) < 2:
                risultato = "Dati insufficienti (meno di 2 giorni di osservazioni)."
            else:
                mean, std, n = incidenti_per_giorno.mean(), incidenti_per_giorno.std(ddof=1), len(incidenti_per_giorno)
                if n == 0 or np.isnan(std) or std == 0:
                     risultato = "Impossibile calcolare: dati insufficienti o deviazione standard è zero."
                else:
                    interval = stats.t.interval(confidence=livello/100, df=n-1, loc=mean, scale=std / np.sqrt(n))
                    risultato = f"Stima Incidenti Giornalieri per {provincia}\n\n"
                    risultato += f"Media campionaria: {mean:.3f}\nDeviazione Standard: {std:.3f}\nNumero di giorni osservati: {n}\n\n"
                    risultato += f"Intervallo di Confidenza al {livello}%:\n[{interval[0]:.4f}, {interval[1]:.4f}]"
        except (ValueError, TypeError, ZeroDivisionError) as e:
            risultato = f"Errore: Inserire valori validi.\nDettagli: {e}"
        self._update_textbox(self.risultato_ci_textbox, risultato)

# =============================================================================
# BLOCCO DI ESECUZIONE PRINCIPALE
# =============================================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()