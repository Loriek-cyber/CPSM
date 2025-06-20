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

"""
Software di Analisi Statistica per Incidenti Stradali

Questo script crea un'applicazione desktop con interfaccia grafica (GUI) per l'analisi
statistica di dati sugli incidenti stradali.

L'applicazione permette di:
- Caricare dati da un file CSV o utilizzare un set di dati di esempio.
- Eseguire analisi statistiche descrittive su singole variabili (numeriche, categoriche e temporali).
- Condurre analisi bivariate (correlazione e regressione lineare) tra due variabili numeriche.
- Effettuare analisi inferenziali, tra cui:
  - Calcolo di probabilità con il modello di Poisson.
  - Test T per campioni indipendenti per confrontare medie.
  - Calcolo di intervalli di confidenza per la media.

Le analisi vengono presentate attraverso tabelle, indici statistici e grafici interattivi.
"""

# Imposta l'aspetto dell'interfaccia grafica
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    """Classe principale dell'applicazione che gestisce la GUI e le logiche di analisi."""
    def __init__(self):
        super().__init__()
        self.title("Software di Analisi Statistica Incidenti Stradali")
        self.geometry("1200x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.df = None
        self.matplotlib_widgets = []

        # --- Frame Superiore per Caricamento Dati ---
        self.frame_caricamento = customtkinter.CTkFrame(self)
        self.frame_caricamento.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.frame_caricamento.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.label_file = customtkinter.CTkLabel(self.frame_caricamento, text="Nessun dato caricato.", text_color="gray")
        self.label_file.grid(row=0, column=0, padx=20, pady=20)
        self.bottone_carica_csv = customtkinter.CTkButton(self.frame_caricamento, text="Carica File CSV", command=self.carica_csv)
        self.bottone_carica_csv.grid(row=0, column=1, padx=20, pady=20)
        
        self.bottone_carica_istat = customtkinter.CTkButton(self.frame_caricamento, text="Carica Dati ISTAT", command=self.carica_dati_istat, fg_color="#1D6F42", hover_color="#175734")
        self.bottone_carica_istat.grid(row=0, column=2, padx=20, pady=20)

        self.bottone_dati_esempio = customtkinter.CTkButton(self.frame_caricamento, text="Usa Dati Simulati", command=self.carica_dati_esempio)
        self.bottone_dati_esempio.grid(row=0, column=3, padx=20, pady=20)
        
        # --- Contenitore a Tab per le Analisi ---
        self.tab_view = customtkinter.CTkTabview(self, width=250)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.tab_view.add("Analisi Descrittiva")
        self.tab_view.add("Analisi Bivariata")
        self.tab_view.add("Analisi Inferenziale")
        
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

    def show_info(self, title, message):
        """
        Mostra una finestra di dialogo modale con un messaggio informativo.

        Args:
            title (str): Il titolo della finestra.
            message (str): Il messaggio da visualizzare all'interno della finestra.
        """
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(title)
        info_window.geometry("500x300")
        info_window.transient(self)
        info_window.grab_set()
        label = customtkinter.CTkLabel(info_window, text=message, wraplength=460, justify="left", font=customtkinter.CTkFont(size=14))
        label.pack(padx=20, pady=20, expand=True, fill="both")
        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")

    def carica_csv(self):
        """
        Apre una finestra di dialogo per selezionare un file CSV.
        Se un file viene selezionato, lo carica in un DataFrame pandas e
        inizializza l'applicazione con i nuovi dati.
        """
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        if not filepath:
            return
        try:
            df = pd.read_csv(filepath)
            self.inizializza_dati(df)
            self.label_file.configure(text=f"Caricato: {filepath.split('/')[-1]}", text_color="white")
        except Exception as e:
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    def carica_dati_istat(self):
        """
        Carica il set di dati ISTAT pre-processato ('incidenti_pronti.csv').
        Se il file non esiste, mostra un messaggio di errore.
        """
        filepath = 'incidenti_pronti.csv'
        try:
            df = pd.read_csv(filepath)
            self.inizializza_dati(df)
            self.label_file.configure(text=f"Caricato: {filepath}", text_color="white")
        except FileNotFoundError:
            error_msg = f"File '{filepath}' non trovato.\n\nAssicurati di aver prima eseguito lo script 'prepare_data.py' sul file CSV scaricato da ISTAT."
            self.label_file.configure(text=f"Errore: File '{filepath}' non trovato.", text_color="red")
            self.show_info("File non trovato", error_msg)
        except Exception as e:
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    def carica_dati_esempio(self):
        """
        Carica un set di dati di esempio predefinito per dimostrare
        le funzionalità dell'applicazione.
        """
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
        """
        Pre-processa il DataFrame caricato.

        Esegue le seguenti operazioni:
        - Converte le colonne in tipo numerico dove possibile.
        - Converte la colonna 'Data_Ora_Incidente' in formato datetime.
        - Estrae 'Ora' e 'Giorno' dalla colonna datetime.
        - Crea una colonna binaria 'Mortale' se 'Numero_Morti' > 0.
        """
        self.df = df
        for col in self.df.columns:
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except (ValueError, TypeError):
                pass
        if 'Data_Ora_Incidente' in self.df.columns:
            self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'])
            self.df['Ora'] = self.df['Data_Ora_Incidente'].dt.hour
            self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
        if 'Numero_Morti' in self.df.columns:
            self.df['Mortale'] = (self.df['Numero_Morti'] > 0).astype(int)
        self.aggiorna_selettori()

    def aggiorna_selettori(self):
        """
        Aggiorna i valori disponibili nei vari selettori (ComboBox) della GUI.
        Popola i selettori con i nomi delle colonne del DataFrame, distinguendo
        tra colonne numeriche e non, e con le province uniche.
        """
        if self.df is None: return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        # Modifica: Includiamo 'datetime' come tipo non numerico per la lista
        object_columns = self.df.select_dtypes(include=['object', 'category', 'datetime64[ns]']).columns.tolist()
        all_columns = numeric_columns + object_columns
        # Assicuriamoci che 'Data_Ora_Incidente' sia nella lista se esiste
        if 'Data_Ora_Incidente' in self.df.columns and 'Data_Ora_Incidente' not in all_columns:
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
        """
        Rimuove tutti i widget contenenti grafici Matplotlib dall'interfaccia.
        Questa funzione è essenziale per liberare memoria e pulire la GUI
        prima di visualizzare nuove analisi.
        """
        for widget in self.matplotlib_widgets:
            widget.destroy()
        self.matplotlib_widgets = []

    def crea_canvas_matplotlib(self, parent, r, c, w=1, h=1):
        """
        Crea e posiziona un frame CTkFrame destinato a contenere un grafico Matplotlib.

        Args:
            parent: Il widget genitore in cui inserire il frame.
            r (int): La riga della griglia del genitore.
            c (int): La colonna della griglia del genitore.
            w (int): Il columnspan del frame nella griglia.
            h (int): Il rowspan del frame nella griglia.

        Returns:
            customtkinter.CTkFrame: Il frame creato.
        """
        frame = customtkinter.CTkFrame(parent)
        frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew", rowspan=h, columnspan=w)
        self.matplotlib_widgets.append(frame)
        return frame

    def setup_tab_descrittiva(self):
        """Inizializza i widget all'interno della tab 'Analisi Descrittiva'."""
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
        """Inizializza i widget all'interno della tab 'Analisi Bivariata'."""
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
        """Inizializza i widget all'interno della tab 'Analisi Inferenziale'."""
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure((0,1,2), weight=1)
        frame_poisson = customtkinter.CTkFrame(tab, border_width=1)
        frame_poisson.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame_poisson.grid_columnconfigure(1, weight=1)
        frame_titolo_poisson = customtkinter.CTkFrame(frame_poisson, fg_color="transparent")
        frame_titolo_poisson.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_titolo_poisson, text="Modello di Poisson", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        info_poisson_msg = "Questo strumento usa la distribuzione di Poisson per calcolare la probabilità che un dato numero di eventi (k) si verifichi in un intervallo di tempo (un'ora), dato il tasso medio di accadimento (λ) stimato dai dati per la provincia e l'ora selezionate. È utile per modellare eventi rari."
        customtkinter.CTkButton(frame_titolo_poisson, text="i", command=lambda: self.show_info("Info: Modello di Poisson", info_poisson_msg), width=28, height=28, corner_radius=14).pack(side="left")
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
        self.label_risultato_poisson = customtkinter.CTkLabel(frame_poisson, text="", justify="left")
        self.label_risultato_poisson.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        frame_ttest = customtkinter.CTkFrame(tab, border_width=1)
        frame_ttest.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame_ttest.grid_columnconfigure(1, weight=1)
        frame_titolo_ttest = customtkinter.CTkFrame(frame_ttest, fg_color="transparent")
        frame_titolo_ttest.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_titolo_ttest, text="Test T per Campioni Indipendenti", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        info_ttest_msg = "Questo test statistico confronta le medie del 'Numero di Feriti' in due gruppi indipendenti (incidenti diurni vs. notturni) per determinare se la differenza osservata sia statisticamente significativa. Un p-value basso (tipicamente < 0.05) suggerisce che la differenza non è casuale."
        customtkinter.CTkButton(frame_titolo_ttest, text="i", command=lambda: self.show_info("Info: Test T", info_ttest_msg), width=28, height=28, corner_radius=14).pack(side="left")
        customtkinter.CTkLabel(frame_ttest, text="Confronto 'Numero_Feriti' tra Diurno (7-19) e Notturno").grid(row=1, column=0, columnspan=2, padx=10)
        customtkinter.CTkButton(frame_ttest, text="Esegui Test T", command=self.esegui_ttest).grid(row=2, column=0, padx=10, pady=10)
        self.label_risultato_ttest = customtkinter.CTkLabel(frame_ttest, text="", justify="left")
        self.label_risultato_ttest.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        frame_ci = customtkinter.CTkFrame(tab, border_width=1)
        frame_ci.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame_ci.grid_columnconfigure(1, weight=1)
        frame_titolo_ci = customtkinter.CTkFrame(frame_ci, fg_color="transparent")
        frame_titolo_ci.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_titolo_ci, text="Intervallo di Confidenza", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        info_ci_msg = "Questo strumento calcola un intervallo di valori entro cui, con un certo livello di confidenza (es. 95%), si stima che cada la vera media della popolazione (in questo caso, il numero medio di incidenti giornalieri per una provincia). Fornisce una misura della precisione della stima basata sui dati campione."
        customtkinter.CTkButton(frame_titolo_ci, text="i", command=lambda: self.show_info("Info: Intervallo di Confidenza", info_ci_msg), width=28, height=28, corner_radius=14).pack(side="left")
        customtkinter.CTkLabel(frame_ci, text="Provincia:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.selettore_provincia_ci = customtkinter.CTkComboBox(frame_ci, values=[])
        self.selettore_provincia_ci.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_ci, text="Livello Confidenza (%):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_livello_ci = customtkinter.CTkEntry(frame_ci, placeholder_text="Es. 95")
        self.entry_livello_ci.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(frame_ci, text="Calcola Intervallo", command=self.esegui_ci).grid(row=3, column=0, padx=10, pady=10)
        self.label_risultato_ci = customtkinter.CTkLabel(frame_ci, text="", justify="left")
        self.label_risultato_ci.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    def esegui_analisi_descrittiva(self):
        """
        Funzione principale per l'analisi descrittiva.
        Pulisce i risultati precedenti, ottiene la variabile selezionata dall'utente
        e chiama la funzione di analisi appropriata in base al tipo di dati
        (temporale, numerico o categorico).
        """
        if self.df is None: return
        variable = self.selettore_var_descrittiva.get()
        if not variable: return
        for widget in self.frame_risultati_descrittiva.winfo_children():
            widget.destroy()
        self.pulisci_grafici()
        self.frame_risultati_descrittiva.grid_columnconfigure(1, weight=0, minsize=0)
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato per questa variabile.").pack()
            return

        # ==========================================================================================
        # MODIFICA CHIAVE: Aggiunto un controllo specifico per la colonna 'Data_Ora_Incidente'
        # ==========================================================================================
        if variable == 'Data_Ora_Incidente':
            self.analisi_temporale(variable)
        elif pd.api.types.is_numeric_dtype(data):
            self.analisi_numerica(variable, data)
        else:
            self.analisi_categorica(variable, data)

    # ==========================================================================================
    # NUOVA FUNZIONE: Analisi specifica per dati temporali
    # ==========================================================================================
    def analisi_temporale(self, variable):
        """
        Esegue e visualizza un'analisi temporale per la colonna 'Data_Ora_Incidente'.
        Raggruppa gli incidenti per giorno, calcola le statistiche di base e
        mostra un grafico a linee dell'andamento del numero di incidenti nel tempo.
        """
        
        # Titolo della sezione
        frame_titolo = customtkinter.CTkFrame(self.frame_risultati_descrittiva, fg_color="transparent")
        frame_titolo.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_titolo, text="Andamento Temporale degli Incidenti", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Raggruppa i dati per giorno e conta gli incidenti
        daily_counts = self.df.groupby('Giorno').size()
        
        if daily_counts.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato giornaliero da analizzare.").grid(row=1, column=0)
            return
            
        # Frame per le statistiche
        frame_stats = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_stats.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        giorno_max = daily_counts.idxmax()
        count_max = daily_counts.max()
        
        stats_text = (f"Periodo analizzato: dal {daily_counts.index.min().strftime('%d/%m/%Y')} al {daily_counts.index.max().strftime('%d/%m/%Y')}\n"
                      f"Totale giorni con incidenti: {len(daily_counts)}\n"
                      f"Giorno con più incidenti: {giorno_max.strftime('%d/%m/%Y')} (con {count_max} incidenti)")
                      
        customtkinter.CTkLabel(frame_stats, text=stats_text, justify="left").pack(padx=10, pady=10)
        
        # Crea il grafico a linee
        canvas_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 2, 0)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linestyle='-', color='#3b82f6')
        
        # Formattazione dell'asse X per mostrare bene le date
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


    def analisi_numerica(self, variable, data):
        """
        Esegue e visualizza un'analisi descrittiva per una variabile numerica.
        Calcola e mostra una serie completa di indici statistici (media, mediana,
        deviazione standard, etc.), intervalli rappresentativi (IQR, Chebyshev)
        e genera un istogramma e un box plot per visualizzare la distribuzione dei dati.

        Args:
            variable (str): Il nome della variabile da analizzare.
            data (pd.Series): La serie di dati numerici da analizzare.
        """
        self.frame_risultati_descrittiva.grid_columnconfigure((0, 1), weight=1)
        frame_indici_main = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_indici_main.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        frame_indici_main.grid_columnconfigure(0, weight=1)
        frame_titolo_indici = customtkinter.CTkFrame(frame_indici_main, fg_color="transparent")
        frame_titolo_indici.grid(row=0, column=0, pady=(5,10), sticky="ew")
        customtkinter.CTkLabel(frame_titolo_indici, text=f"Indici Statistici per '{variable}'", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        info_indici_msg = "Questa sezione mostra i principali indici di statistica descrittiva..."
        customtkinter.CTkButton(frame_titolo_indici, text="i", command=lambda: self.show_info(f"Info: Indici Statistici", info_indici_msg), width=28, height=28, corner_radius=14).pack(side="left")
        frame_valori_indici = customtkinter.CTkFrame(frame_indici_main)
        frame_valori_indici.grid(row=1, column=0, sticky="ew")
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
        frame_intervalli = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_intervalli.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        frame_titolo_intervalli = customtkinter.CTkFrame(frame_intervalli, fg_color="transparent")
        frame_titolo_intervalli.pack(fill="x", padx=0, pady=(5,10))
        customtkinter.CTkLabel(frame_titolo_intervalli, text="Intervalli Rappresentativi", font=customtkinter.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        info_intervalli_msg = "L'Intervallo Interquartile (IQR) contiene il 50% centrale dei dati..."
        customtkinter.CTkButton(frame_titolo_intervalli, text="i", command=lambda: self.show_info("Info: Intervalli", info_intervalli_msg), width=28, height=28, corner_radius=14).pack(side="left")
        if std_dev > 0:
            k=2
            chebyshev_bound = 1 - (1 / (k**2))
            actual_percentage = len(data[abs(data - mean) < k * std_dev]) / len(data)
            chebyshev_text = f"Disuguaglianza di Chebyshev: Almeno il {chebyshev_bound:.0%} dei dati entro {k} dev. standard dalla media (Reale: {actual_percentage:.2%})"
        else:
            chebyshev_text = "Disuguaglianza di Chebyshev: non applicabile (dev. std. è zero)."
        customtkinter.CTkLabel(frame_intervalli, text=f"Intervallo Interquartile (IQR): Contiene il 50% centrale dei dati: [{q1:.2f}, {q3:.2f}]").pack(pady=(0,5))
        customtkinter.CTkLabel(frame_intervalli, text=chebyshev_text).pack(pady=(0,5))
        info_grafici_num_msg = "L'Istogramma mostra la frequenza dei dati in specifici intervalli (bin)..."
        frame_titolo_grafici = customtkinter.CTkFrame(self.frame_risultati_descrittiva, fg_color="transparent")
        frame_titolo_grafici.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_titolo_grafici, text="Grafici di Distribuzione", font=customtkinter.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        customtkinter.CTkButton(frame_titolo_grafici, text="i", command=lambda: self.show_info("Info: Grafici Numerici", info_grafici_num_msg), width=28, height=28, corner_radius=14).pack(side="left")
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

    def analisi_categorica(self, variable, data):
        """
        Esegue e visualizza un'analisi descrittiva per una variabile categorica.
        Crea una tabella di frequenza (assoluta, relativa, cumulata) e
        genera un grafico a barre orizzontali e un grafico a torta per
        visualizzare la distribuzione delle categorie.

        Args:
            variable (str): Il nome della variabile da analizzare.
            data (pd.Series): La serie di dati categorici da analizzare.
        """
        counts = data.value_counts()
        relative_freq = data.value_counts(normalize=True)
        cumulative_freq = counts.cumsum()
        frame_tabella_main = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_tabella_main.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_tabella_main.grid_columnconfigure(0, weight=1)
        frame_tabella_main.grid_rowconfigure(1, weight=1)
        frame_titolo_tabella = customtkinter.CTkFrame(frame_tabella_main, fg_color="transparent")
        frame_titolo_tabella.grid(row=0, column=0, sticky="ew", pady=(5,10))
        customtkinter.CTkLabel(frame_titolo_tabella, text=f"Tabella Frequenze per '{variable}'", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        info_tabella_msg = "La tabella riassume la distribuzione della variabile..."
        customtkinter.CTkButton(frame_titolo_tabella, text="i", command=lambda: self.show_info("Info: Tabella Frequenze", info_tabella_msg), width=28, height=28, corner_radius=14).pack(side="left")
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=('Calibri', 12))
        style.configure("Treeview.Heading", font=('Calibri', 13,'bold'), anchor="center")
        tree = ttk.Treeview(frame_tabella_main, columns=('Categoria', 'Assoluta', 'Relativa', 'Cumulata'), show='headings')
        for col in ('Categoria', 'Assoluta', 'Relativa', 'Cumulata'):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        for index, value in counts.items():
            tree.insert('', 'end', values=(index, value, f"{relative_freq[index] * 100:.2f}%", cumulative_freq[index]))
        tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.matplotlib_widgets.append(frame_tabella_main)
        info_grafici_cat_msg = "Questi grafici visualizzano le proporzioni della variabile..."
        frame_titolo_grafici = customtkinter.CTkFrame(self.frame_risultati_descrittiva, fg_color="transparent")
        frame_titolo_grafici.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")
        customtkinter.CTkLabel(frame_titolo_grafici, text="Grafici di Frequenza", font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left")
        customtkinter.CTkButton(frame_titolo_grafici, text="i", command=lambda: self.show_info("Info: Grafici Categorici", info_grafici_cat_msg), width=28, height=28, corner_radius=14).pack(side="left", padx=10)
        canvas_bar_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 2, 0)
        fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
        counts.sort_values().plot(kind='barh', ax=ax_bar, color=plt.cm.viridis(np.linspace(0, 1, len(counts))))
        ax_bar.set_title(f'Grafico a Barre di {variable}'), ax_bar.set_xlabel('Frequenza Assoluta'), fig_bar.tight_layout()
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=canvas_bar_frame)
        canvas_bar.draw(), canvas_bar.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        canvas_pie_frame = self.crea_canvas_matplotlib(self.frame_risultati_descrittiva, 3, 0)
        fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
        counts.plot(kind='pie', ax=ax_pie, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'), colors=plt.cm.viridis(np.linspace(0, 1, len(counts))), textprops={'fontsize': 12})
        ax_pie.set_ylabel(''), ax_pie.set_title(f'Grafico a Torta di {variable}'), fig_pie.tight_layout()
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=canvas_pie_frame)
        canvas_pie.draw(), canvas_pie.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def esegui_analisi_bivariata(self):
        """
        Esegue un'analisi bivariata tra due variabili numeriche selezionate.
        Calcola il coefficiente di correlazione di Pearson e i parametri della
        retta di regressione lineare. Visualizza i risultati in un diagramma
        a dispersione (scatter plot) con la retta di regressione sovrapposta.
        """
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
        correlation, regression = x_data.corr(y_data), stats.linregress(x_data, y_data)
        frame_titolo_biv = customtkinter.CTkFrame(self.frame_risultati_bivariata, fg_color="transparent")
        frame_titolo_biv.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        info_biv_msg = "Questa analisi esplora la relazione tra due variabili numeriche..."
        customtkinter.CTkLabel(frame_titolo_biv, text=f"Analisi di Correlazione e Regressione", font=customtkinter.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        customtkinter.CTkButton(frame_titolo_biv, text="i", command=lambda: self.show_info("Info: Analisi Bivariata", info_biv_msg), width=28, height=28, corner_radius=14).pack(side="left")
        risultati_testuali = f"Coefficiente di Correlazione (r): {correlation:.4f}\nEquazione Retta di Regressione: y = {regression.slope:.4f}x + {regression.intercept:.4f}"
        customtkinter.CTkLabel(self.frame_risultati_bivariata, text=risultati_testuali, justify="left").grid(row=1, column=0, padx=20, pady=(0, 10))
        canvas_frame = self.crea_canvas_matplotlib(self.frame_risultati_bivariata, 2, 0)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x_data, y_data, alpha=0.6, label='Dati')
        line_x = np.array([x_data.min(), x_data.max()])
        line_y = regression.slope * line_x + regression.intercept
        ax.plot(line_x, line_y, color='red', label='Retta di Regressione')
        ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}'), ax.set_xlabel(var_x), ax.set_ylabel(var_y), ax.legend(), ax.grid(True), fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw(), canvas.get_tk_widget().pack(fill='both', expand=True)

    def esegui_poisson(self):
        """
        Calcola la probabilità di Poisson.
        Stima il tasso medio di incidenti (lambda) per una data provincia e fascia oraria,
        quindi utilizza la distribuzione di Poisson per calcolare la probabilità che
        si verifichi un numero specifico di incidenti (k) in quell'ora.
        Gestisce gli input dell'utente e visualizza il risultato.
        """
        if self.df is None: return
        try:
            provincia, ora, k = self.selettore_provincia_poisson.get(), int(self.entry_ora_poisson.get()), int(self.entry_k_poisson.get())
            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique()
            if giorni_osservati == 0:
                self.label_risultato_poisson.configure(text="Nessun dato per questa provincia.")
                return
            incidenti_nell_ora = df_prov[df_prov['Ora'] == ora].shape[0]
            lambda_val = incidenti_nell_ora / giorni_osservati
            prob = stats.poisson.pmf(k, lambda_val)
            self.label_risultato_poisson.configure(text=f"Provincia: {provincia}, Ora: {ora}:00\nTasso medio stimato (λ): {lambda_val:.4f} incidenti/ora\nP(X = {k} incidenti) = {prob:.4%}")
        except (ValueError, TypeError) as e:
            self.label_risultato_poisson.configure(text=f"Errore: Inserire valori validi.\n({e})")

    def esegui_ttest(self):
        """
        Esegue un test T per campioni indipendenti (test di Welch).
        Confronta le medie del 'Numero_Feriti' tra incidenti diurni (7-19) e notturni.
        Visualizza le medie dei due gruppi, la statistica t e il p-value,
        indicando se la differenza osservata è statisticamente significativa (p < 0.05).
        """
        if self.df is None: return
        data_diurno = self.df[(self.df['Ora'] >= 7) & (self.df['Ora'] < 20)]['Numero_Feriti'].dropna()
        data_notturno = self.df[(self.df['Ora'] < 7) | (self.df['Ora'] >= 20)]['Numero_Feriti'].dropna()
        if len(data_diurno) < 2 or len(data_notturno) < 2:
            self.label_risultato_ttest.configure(text="Dati insuff. (necessari almeno 2 campioni per gruppo).")
            return
        ttest_res = stats.ttest_ind(data_diurno, data_notturno, equal_var=False)
        risultato = f"Confronto Numero Feriti: Diurno vs. Notturno\nMedia Diurna (n={len(data_diurno)}): {data_diurno.mean():.3f} | Media Notturna (n={len(data_notturno)}): {data_notturno.mean():.3f}\nStatistica t = {ttest_res.statistic:.4f}\np-value = {ttest_res.pvalue:.4f}"
        risultato += "\n\nConclusione: La differenza è statisticamente significativa." if ttest_res.pvalue < 0.05 else "\n\nConclusione: La differenza non è statisticamente significativa."
        self.label_risultato_ttest.configure(text=risultato)

    def esegui_ci(self):
        """
        Calcola l'intervallo di confidenza per la media del numero di incidenti giornalieri.
        Per una data provincia e un livello di confidenza specificato dall'utente,
        calcola e visualizza l'intervallo entro cui si stima che si trovi la vera
        media della popolazione di incidenti giornalieri.
        Utilizza la distribuzione t di Student, adatta per campioni di piccole dimensioni.
        """
        if self.df is None: return
        try:
            provincia, livello = self.selettore_provincia_ci.get(), int(self.entry_livello_ci.get())
            if not 0 < livello < 100: raise ValueError("Livello confidenza tra 1 e 99.")
            incidenti_per_giorno = self.df[self.df['Provincia'] == provincia].groupby('Giorno').size()
            if len(incidenti_per_giorno) < 2:
                self.label_risultato_ci.configure(text="Dati insuff. (meno di 2 giorni osservati).")
                return
            mean, std, n = incidenti_per_giorno.mean(), incidenti_per_giorno.std(ddof=1), len(incidenti_per_giorno)
            if n == 0 or np.isnan(std) or std == 0:
                 self.label_risultato_ci.configure(text="Impossibile calcolare: dati insufficienti o dev. std. è zero.")
                 return
            interval = stats.t.interval(confidence=livello/100, df=n-1, loc=mean, scale=std / np.sqrt(n))
            self.label_risultato_ci.configure(text=f"Stima Incidenti Giornalieri per {provincia}\nMedia campionaria: {mean:.3f} | Dev. Std: {std:.3f} | n. giorni: {n}\nIntervallo di Confidenza al {livello}%:\n[{interval[0]:.4f}, {interval[1]:.4f}]")
        except (ValueError, TypeError, ZeroDivisionError) as e:
            self.label_risultato_ci.configure(text=f"Errore: Inserire valori validi.\n({e})")

if __name__ == "__main__":
    app = App()
    app.mainloop()