# =============================================================================
# CHANGELOG ULTIME MODIFICHE
# =============================================================================
# ... (changelog precedente omesso per brevità)
# 17. [NUOVO] Generatore Dati Simulati Randomici: La funzione "Usa Dati Simulati" ora crea un dataset
#     completamente casuale e realistico ad ogni click, per test più dinamici.
# 18. [NUOVO] Analisi di Poisson su Fascia Oraria: È ora possibile inserire una fascia oraria (es. 7-13)
#     per calcolare la probabilità di incidenti in un intervallo di tempo.
# 19. [NUOVO] Dati di Test Inferenziale Migliorati: Il generatore casuale produce dataset più ampi
#     e variegati, ideali per testare a fondo le analisi inferenziali.
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
import random
from datetime import datetime, timedelta
import locale

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

    def _crea_titolo_sezione(self, parent, row, testo_titolo, testo_info, columnspan=1, testo_guida=None):
        """Metodo helper per creare una riga di titolo centrata con bottone info e un opzionale bottone guida."""
        frame_titolo = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame_titolo.grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(15, 5))
        
        inner_frame = customtkinter.CTkFrame(frame_titolo, fg_color="transparent")
        inner_frame.pack()
        
        customtkinter.CTkLabel(inner_frame, text=testo_titolo, font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        customtkinter.CTkButton(inner_frame, text="i", command=lambda: self.show_info(f"Info: {testo_titolo}", testo_info), width=28, height=28, corner_radius=14).pack(side="left", padx=(0, 5))
        
        if testo_guida:
            customtkinter.CTkButton(inner_frame, text="?", command=lambda: self.show_info("Come Leggere il Grafico", testo_guida), width=28, height=28, corner_radius=14).pack(side="left")

    def show_info(self, title, message):
        """Crea e mostra una finestra popup con un messaggio informativo e dimensione adattiva."""
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title)
        info_window.transient(self)
        info_window.grab_set()

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
        """
        Genera un DataFrame di dati simulati randomici e coerenti.
        """
        try:
            # Imposta la lingua italiana per i nomi dei giorni
            locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
        except locale.Error:
            print("Locale 'it_IT.UTF-8' non trovato. I nomi dei giorni potrebbero essere in inglese.")
        
        records = []
        province = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Catania', 'Salerno', 'Bologna']
        tipi_strada = ['Urbana', 'Statale', 'Autostrada']
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        for _ in range(200): # Genera 200 record
            # Data e ora random
            random_date = start_date + (end_date - start_date) * random.random()
            
            # Provincia e tipo di strada
            prov = random.choice(province)
            strada = random.choice(tipi_strada)
            
            # Velocità coerente con tipo di strada
            if strada == 'Urbana':
                velocita = random.randint(30, 65)
            elif strada == 'Statale':
                velocita = random.randint(60, 95)
            else: # Autostrada
                velocita = random.randint(100, 140)
            
            # Feriti e morti con distribuzione realistica
            numero_morti = random.choices([0, 1, 2], weights=[95, 4, 1], k=1)[0]
            if numero_morti > 0:
                numero_feriti = random.randint(numero_morti, 8) # Se c'è un morto, c'è almeno un ferito
            else:
                numero_feriti = random.choices([0, 1, 2, 3, 4], weights=[20, 40, 25, 10, 5], k=1)[0]
                
            records.append({
                'Data_Ora_Incidente': random_date.strftime("%Y-%m-%d %H:%M:%S"),
                'Provincia': prov,
                'Giorno_Settimana': random_date.strftime('%A').capitalize(),
                'Tipo_Strada': strada,
                'Numero_Feriti': numero_feriti,
                'Numero_Morti': numero_morti,
                'Velocita_Media_Stimata': velocita
            })
            
        df = pd.DataFrame(records)
        self.inizializza_dati(df)
        self.label_file.configure(text="Caricati 200 record di dati simulati randomici.")


    def inizializza_dati(self, df):
        self.df = df
        for col in self.df.columns:
            try:
                # Usa errors='coerce' per trasformare i valori non numerici in NaT/NaN
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            except (ValueError, TypeError):
                pass
        if 'Data_Ora_Incidente' in self.df.columns:
            try:
                # Usa errors='coerce' per gestire eventuali formati data non validi
                self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce')
                # Rimuove le righe dove la data non è stata convertita correttamente
                self.df.dropna(subset=['Data_Ora_Incidente'], inplace=True)
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
        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []
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
        tab.grid_rowconfigure(0, weight=1)

        scroll_frame = customtkinter.CTkScrollableFrame(tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # --- Sezione 1: Modello di Poisson ---
        frame_poisson = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_poisson.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame_poisson.grid_columnconfigure(1, weight=1)
        
        info_poisson = """**Cos'è?**
Il Modello di Poisson è uno strumento statistico usato per calcolare la probabilità che un certo numero di eventi (k) accada in un intervallo di tempo o spazio, dato un tasso medio di accadimento (λ).

**A Cosa Serve?**
In questo contesto, serve a stimare la probabilità di osservare un numero specifico di incidenti (es. 2 incidenti) in una data ora e provincia, basandosi sulla frequenza storica.

--- Legenda dei Termini ---
- **λ (Lambda):** Tasso medio di accadimento. È il numero medio di incidenti stimato per la provincia e l'ora selezionate.
- **k:** Il numero esatto di eventi (incidenti) di cui si vuole calcolare la probabilità.
- **P(X=k):** La probabilità calcolata che il numero di incidenti sia esattamente 'k'."""
        self._crea_titolo_sezione(frame_poisson, 0, "Modello di Poisson", info_poisson, columnspan=3)

        customtkinter.CTkLabel(frame_poisson, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_poisson = customtkinter.CTkComboBox(frame_poisson, values=[])
        self.selettore_provincia_poisson.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # MODIFICA: Label e placeholder per fascia oraria
        customtkinter.CTkLabel(frame_poisson, text="Fascia Oraria (es. 7-13):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_ora_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Inserisci un range orario, es. 8-12")
        self.entry_ora_poisson.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        customtkinter.CTkLabel(frame_poisson, text="Numero incidenti (k):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_k_poisson = customtkinter.CTkEntry(frame_poisson, placeholder_text="Es. 2")
        self.entry_k_poisson.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_poisson, text="Calcola Probabilità", command=self.esegui_poisson).grid(row=4, column=0, padx=10, pady=10)
        
        self.risultato_poisson_textbox = customtkinter.CTkTextbox(frame_poisson, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_poisson_textbox.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.risultato_poisson_textbox.configure(state="disabled")

        # --- Sezione 2: Test T ---
        frame_ttest = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ttest.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame_ttest.grid_columnconfigure(1, weight=1)
        
        info_ttest="""**Cos'è?**
Il Test T per Campioni Indipendenti è un test di ipotesi che confronta le medie di due gruppi di dati separati e indipendenti (es. feriti di giorno vs feriti di notte).

**A Cosa Serve?**
Determina se la differenza osservata tra le due medie è statisticamente significativa o se potrebbe essere semplicemente dovuta al caso.

--- Legenda dei Termini ---
- **Ipotesi Nulla (H₀):** L'ipotesi di partenza che non esista una vera differenza tra le medie dei due gruppi.
- **p-value:** La probabilità di osservare i dati attuali (o dati ancora più estremi) se l'Ipotesi Nulla fosse vera. Un p-value basso (tipicamente < 0.05) suggerisce di rigettare H₀.
- **Statistica t:** Misura la dimensione della differenza tra le medie relativa alla variabilità dei dati. Più è lontana da zero, più la differenza è marcata."""
        self._crea_titolo_sezione(frame_ttest, 0, "Test T per Campioni Indipendenti", info_ttest, columnspan=2)

        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0))
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10, sticky="n")
        
        self.risultato_ttest_textbox = customtkinter.CTkTextbox(frame_ttest, wrap="word", font=customtkinter.CTkFont(size=13))
        self.risultato_ttest_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.risultato_ttest_textbox.configure(state="disabled")

        # --- Sezione 3: Intervallo di Confidenza ---
        frame_ci = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ci.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame_ci.grid_columnconfigure(1, weight=1)
        
        info_ci="""**Cos'è?**
Un Intervallo di Confidenza (IC) è un range di valori, calcolato a partire da dati campionari, che si stima possa contenere il vero valore di un parametro della popolazione (es. la 'vera' media di incidenti giornalieri).

**A Cosa Serve?**
Fornisce una misura della precisione della stima. Invece di avere un singolo valore (la media del campione), si ottiene un intervallo di valori plausibili.

--- Legenda dei Termini ---
- **Livello di Confidenza:** La probabilità (es. 95%) che, ripetendo l'esperimento più volte, l'intervallo calcolato contenga il vero parametro della popolazione.
- **Media Campionaria:** La media calcolata sui dati a disposizione.
- **Range (IC):** L'intervallo [valore inferiore, valore superiore]. Un intervallo stretto indica una stima più precisa."""
        self._crea_titolo_sezione(frame_ci, 0, "Intervallo di Confidenza", info_ci, columnspan=2)

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
        self.frame_risultati_descrittiva.grid_rowconfigure(2, weight=1)
        
        info_temporale = """**Cos'è?**
Questa sezione analizza la distribuzione degli incidenti nel tempo.

**A Cosa Serve?**
Permette di identificare pattern temporali, come giorni della settimana o periodi dell'anno con picchi di incidentalità, fornendo indicazioni utili per la pianificazione di interventi preventivi."""
        guida_temporale = """**Interpretazione del Grafico a Linee:**
- **Asse delle ascisse (X):** Rappresenta la variabile temporale (date).
- **Asse delle ordinate (Y):** Mostra la frequenza assoluta degli incidenti per unità di tempo.
- **Linea di tendenza:** La polilinea congiunge i punti-dati, ciascuno rappresentante la frequenza di incidenti per un dato giorno. La pendenza dei segmenti indica la variazione della frequenza tra giorni consecutivi."""
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, "Andamento Temporale Incidenti", info_temporale, testo_guida=guida_temporale)
        
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
        self.frame_risultati_descrittiva.grid_columnconfigure((0, 1), weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(3, weight=1)
        
        info_indici = """**Cosa Sono?**
Gli indici statistici sono valori numerici che riassumono le caratteristiche principali di un insieme di dati.

**A Cosa Servono?**
Forniscono una visione sintetica e quantitativa della variabile analizzata, descrivendone la tendenza centrale (dove si concentrano i dati) e la variabilità (quanto sono dispersi).

--- Legenda dei Termini ---
- **Misure Centrali (Media, Mediana, Moda):** Indicano il 'centro' dei dati.
- **Misure di Dispersione (Varianza, Dev. Standard):** Indicano quanto i dati sono sparsi.
- **Asimmetria (Skewness):** Misura la simmetria della distribuzione. (>0: coda a destra; <0: coda a sinistra).
- **Curtosi (Kurtosis):** Misura la 'pesantezza' delle code e la presenza di valori anomali."""
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, f"Indici Statistici per '{variable}'", info_indici, columnspan=2)

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
        
        info_distribuzione="""**Cosa Sono?**
Sono rappresentazioni visuali che mostrano come i valori di una variabile sono distribuiti.

**A Cosa Servono?**
Aiutano a comprendere la forma della distribuzione, a identificare i valori più frequenti, la presenza di anomalie (outlier) e la dispersione dei dati in modo intuitivo."""
        guida_distribuzione="""**Interpretazione dei Grafici:**
- **Istogramma:** Rappresenta la distribuzione di frequenza di una variabile numerica. L'asse X è suddiviso in intervalli (bin) e l'altezza di ciascuna barra è proporzionale al numero di osservazioni che ricadono in quell'intervallo.

- **Box Plot:** Sintetizza la distribuzione attraverso cinque numeri:
  - Il **limite inferiore/superiore della scatola** indica il primo (Q1) e il terzo (Q3) quartile.
  - La **linea interna** rappresenta la mediana (Q2).
  - I **baffi (whiskers)** si estendono fino ai valori minimi e massimi esclusi gli outlier.
  - La visualizzazione degli **outlier** è disattivata per favorire la leggibilità della distribuzione centrale."""
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 2, "Grafici di Distribuzione", info_distribuzione, columnspan=2, testo_guida=guida_distribuzione)
        
        canvas_hist_frame, canvas_box_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 0), self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 1)
        fig_hist, ax_hist = plt.subplots(figsize=(5, 4))
        ax_hist.hist(data, bins='auto', color='#3b82f6', alpha=0.7, rwidth=0.85)
        ax_hist.set_title(f'Istogramma di {variable}'), ax_hist.set_xlabel(variable), ax_hist.set_ylabel('Frequenza'), ax_hist.grid(axis='y', alpha=0.75), fig_hist.tight_layout()
        canvas_hist = FigureCanvasTkAgg(fig_hist, master=canvas_hist_frame)
        canvas_hist.draw(), canvas_hist.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        fig_box, ax_box = plt.subplots(figsize=(5, 4))
        ax_box.boxplot(data, vert=False, patch_artist=True, boxprops=dict(facecolor='#ec4899', alpha=0.7), showfliers=False)
        ax_box.set_title(f'Box Plot di {variable}'), ax_box.set_yticklabels([variable]), ax_box.grid(axis='x', alpha=0.75), fig_box.tight_layout()
        canvas_box = FigureCanvasTkAgg(fig_box, master=canvas_box_frame)
        canvas_box.draw(), canvas_box.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        plt.close(fig_hist)
        plt.close(fig_box)

    def analisi_categorica(self, variable, data):
        self.frame_risultati_descrittiva.grid_columnconfigure(1, weight=0, minsize=0)
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(3, weight=1)
        self.frame_risultati_descrittiva.grid_rowconfigure(4, weight=1)

        info_frequenze="""**Cos'è?**
Una tabella che mostra quante volte appare ogni categoria (modalità) di una variabile.

**A Cosa Serve?**
Permette di quantificare la distribuzione delle osservazioni tra le diverse categorie, identificando quelle più e meno comuni.

--- Legenda dei Termini ---
- **Freq. Assoluta:** Il conteggio esatto di ogni categoria.
- **Freq. Relativa (%):** La percentuale di ogni categoria sul totale.
- **Freq. Cumulata:** La somma progressiva delle frequenze."""
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 0, f"Tabella Frequenze per '{variable}'", info_frequenze)
        
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

        info_grafici_freq="""**Cosa Sono?**
Sono rappresentazioni visuali che mostrano la frequenza o la proporzione delle diverse categorie di una variabile.

**A Cosa Servono?**
Offrono un modo immediato per confrontare le categorie, evidenziando le proporzioni e le differenze tra di esse."""
        guida_grafici_freq="""**Interpretazione dei Grafici:**
- **Grafico a Barre:**
  Visualizza le frequenze delle categorie. La lunghezza di ciascuna barra è direttamente proporzionale alla frequenza della categoria che rappresenta, permettendo un confronto quantitativo diretto.

- **Grafico a Torta (o Ciambella):**
  Rappresenta la composizione proporzionale del totale. L'area di ciascuno spicchio è proporzionale alla frequenza relativa della categoria, illustrando il contributo di ogni parte al tutto (100%)."""
        self._crea_titolo_sezione(self.frame_risultati_descrittiva, 2, "Grafici di Frequenza", info_grafici_freq, testo_guida=guida_grafici_freq)
        
        def autopct_conditional(pct):
            return f'{pct:.1f}%' if pct > 4 else ''

        text_props = {'fontsize': 12, 'bbox': {'facecolor': 'white', 'alpha': 0.7, 'edgecolor':'none', 'pad':2}}

        canvas_bar_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 0)
        fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
        counts.sort_values().plot(kind='barh', ax=ax_bar, color=plt.cm.viridis(np.linspace(0, 1, len(counts))))
        ax_bar.set_title(f'Grafico a Barre di {variable}'), ax_bar.set_xlabel('Frequenza Assoluta'), fig_bar.tight_layout()
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=canvas_bar_frame)
        canvas_bar.draw(), canvas_bar.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        
        canvas_pie_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 4, 0)
        fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
        counts.plot(kind='pie', ax=ax_pie, autopct=autopct_conditional, startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'), colors=plt.cm.viridis(np.linspace(0, 1, len(counts))), textprops=text_props)
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

        info_bivariata="""**Cos'è?**
Un'analisi che studia la relazione tra due variabili numeriche contemporaneamente.

**A Cosa Serve?**
A capire se esiste un legame tra le due variabili, in che direzione (positivo o negativo) e con quale forza. La regressione permette anche di prevedere il valore di una variabile basandosi sull'altra.

--- Legenda dei Termini ---
- **Coefficiente di Correlazione (r):** Varia da -1 (relazione inversa perfetta) a +1 (relazione diretta perfetta). 0 indica assenza di relazione *lineare*.
- **Retta di Regressione (y = mx + b):** La linea che meglio approssima i dati.
- **Pendenza (m):** Indica di quanto aumenta in media Y per ogni aumento di 1 unità in X.
- **Intercetta (b):** Il valore previsto di Y quando X è 0."""
        guida_bivariata="""**Interpretazione del Diagramma a Dispersione:**
- **Assi Cartesiani:** Gli assi X e Y rappresentano le due variabili oggetto di analisi.
- **Punti Dati:** Ciascun punto sul piano cartesiano corrisponde a un'osservazione bivariata.
- **Distribuzione dei Punti:** La configurazione dei punti (la 'nuvola') indica la natura della relazione. Un andamento crescente/decrescente suggerisce una correlazione positiva/negativa.
- **Retta di Regressione:** La linea rossa rappresenta il modello di regressione lineare semplice, che interpola la nuvola di punti minimizzando la somma dei quadrati dei residui."""
        self._crea_titolo_sezione(self.frame_risultati_bivariata, 0, "Analisi di Correlazione e Regressione", info_bivariata, testo_guida=guida_bivariata)
        
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
        """Metodo helper per aggiornare il contenuto di una CTkTextbox e adattarne l'altezza."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        
        textbox.update_idletasks()
        font = textbox.cget("font")
        line_height = font.cget("size") + 6 
        num_lines = int(textbox.index('end-1c').split('.')[0])
        new_height = num_lines * line_height
        textbox.configure(height=new_height)
        
        textbox.configure(state="disabled")

    def esegui_poisson(self):
        if self.df is None: return
        try:
            provincia = self.selettore_provincia_poisson.get()
            k = int(self.entry_k_poisson.get())
            fascia_oraria_str = self.entry_ora_poisson.get()
            
            # Parsing della fascia oraria
            parts = fascia_oraria_str.split('-')
            if len(parts) != 2:
                raise ValueError("Formato fascia oraria non valido. Usare 'inizio-fine'.")
            
            ora_inizio = int(parts[0])
            ora_fine = int(parts[1])
            
            if not (0 <= ora_inizio <= 23 and 0 <= ora_fine <= 23 and ora_inizio <= ora_fine):
                raise ValueError("Valori orari non validi. Devono essere tra 0-23 e inizio <= fine.")

            durata_ore = ora_fine - ora_inizio + 1
            
            # Calcolo
            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique()
            if giorni_osservati == 0:
                risultato = "Nessun dato disponibile per questa provincia."
            else:
                incidenti_nella_fascia = df_prov[
                    (df_prov['Ora'] >= ora_inizio) & (df_prov['Ora'] <= ora_fine)
                ].shape[0]
                
                lambda_val = incidenti_nella_fascia / giorni_osservati
                prob = stats.poisson.pmf(k, lambda_val)
                
                risultato = f"ANALISI PER {provincia.upper()}\n"
                risultato += "--------------------------------------------------\n"
                risultato += f"Fascia oraria: {ora_inizio}:00 - {ora_fine}:00 (Durata: {durata_ore} ore)\n\n"
                risultato += f"Tasso medio stimato (λ) per la fascia oraria:\n{lambda_val:.4f} incidenti (calcolato su {giorni_osservati} giorni)\n\n"
                risultato += f"Probabilità di osservare esattamente {k} incidenti:\n{prob:.4%}"

        except (ValueError, TypeError) as e:
            risultato = f"Errore: Dati inseriti non validi.\n{e}"
        self._update_textbox(self.risultato_poisson_textbox, risultato)

    def esegui_ttest(self):
        if self.df is None: return
        data_diurno = self.df[(self.df['Ora'] >= 7) & (self.df['Ora'] < 20)]['Numero_Feriti'].dropna()
        data_notturno = self.df[(self.df['Ora'] < 7) | (self.df['Ora'] >= 20)]['Numero_Feriti'].dropna()
        if len(data_diurno) < 2 or len(data_notturno) < 2:
            risultato = "Dati insufficienti: sono necessari almeno 2 campioni sia per il gruppo diurno che notturno."
        else:
            ttest_res = stats.ttest_ind(data_diurno, data_notturno, equal_var=False)
            risultato = "CONFRONTO NUMERO FERITI: DIURNO vs. NOTTURNO\n"
            risultato += "--------------------------------------------------\n"
            risultato += f"Gruppo Diurno (n={len(data_diurno)}):\n  - Media Feriti: {data_diurno.mean():.3f}\n\n"
            risultato += f"Gruppo Notturno (n={len(data_notturno)}):\n  - Media Feriti: {data_notturno.mean():.3f}\n\n"
            risultato += f"RISULTATI DEL TEST:\n  - Statistica t = {ttest_res.statistic:.4f}\n  - p-value = {ttest_res.pvalue:.4f}\n\n"
            risultato += "CONCLUSIONE:\n"
            if ttest_res.pvalue < 0.05:
                risultato += "Poiché p < 0.05, la differenza tra le medie del numero di feriti di giorno e di notte è statisticamente significativa."
            else:
                risultato += "Poiché p >= 0.05, non c'è evidenza statistica sufficiente per affermare che esista una vera differenza nel numero di feriti tra giorno e notte."
        self._update_textbox(self.risultato_ttest_textbox, risultato)

    def esegui_ci(self):
        if self.df is None: return
        try:
            provincia, livello = self.selettore_provincia_ci.get(), int(self.entry_livello_ci.get())
            if not 0 < livello < 100: raise ValueError("Livello confidenza deve essere tra 1 e 99.")
            incidenti_per_giorno = self.df[self.df['Provincia'] == provincia].groupby('Giorno').size()
            if len(incidenti_per_giorno) < 2:
                risultato = "Dati insufficienti: sono necessari almeno 2 giorni di osservazioni per la provincia selezionata."
            else:
                mean, std, n = incidenti_per_giorno.mean(), incidenti_per_giorno.std(ddof=1), len(incidenti_per_giorno)
                if n == 0 or np.isnan(std) or std == 0:
                     risultato = "Impossibile calcolare l'intervallo: deviazione standard è zero o i dati sono insufficienti."
                else:
                    interval = stats.t.interval(confidence=livello/100, df=n-1, loc=mean, scale=std / np.sqrt(n))
                    risultato = f"STIMA INCIDENTI GIORNALIERI MEDI - {provincia.upper()}\n"
                    risultato += "--------------------------------------------------\n"
                    risultato += f"DATI CAMPIONARI:\n  - Media: {mean:.3f} incidenti/giorno\n  - Deviazione Standard: {std:.3f}\n  - Giorni Osservati: {n}\n\n"
                    risultato += f"INTERVALLO DI CONFIDENZA AL {livello}%:\n"
                    risultato += f"  [{interval[0]:.4f}, {interval[1]:.4f}]\n\n"
                    risultato += f"Ciò significa che siamo sicuri al {livello}% che la vera media di incidenti giornalieri per {provincia} si trovi in questo intervallo."

        except (ValueError, TypeError, ZeroDivisionError) as e:
            risultato = f"Errore: Inserire valori validi.\nIl livello di confidenza deve essere un numero intero tra 1 e 99.\nDettagli: {e}"
        self._update_textbox(self.risultato_ci_textbox, risultato)

# =============================================================================
# BLOCCO DI ESECUZIONE PRINCIPALE
# =============================================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()