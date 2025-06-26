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

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

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
        for tab in tabs:
            self.tab_view.add(tab)
        self.setup_tab_dati_forniti()
        self.setup_tab_calcolo_dati()
        self.setup_tab_campionatura()
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

    def carica_csv(self):
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        if not filepath:
            return
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
                strada = random.choice(tipi_strada) if random.random() >= 0.05 else None
                velocita = None
                if strada == 'Urbana':
                    velocita = random.randint(30, 65)
                elif strada == 'Statale':
                    velocita = random.randint(60, 95)
                elif strada == 'Autostrada':
                    velocita = random.randint(100, 140)
                numero_morti = random.choices([0, 1, 2, 3], weights=[94, 4, 1.5, 0.5], k=1)[0]
                numero_feriti = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 40, 25, 15, 5, 5], k=1)[0]
                if numero_morti > 0:
                    numero_feriti += numero_morti
                records.append({
                    'Data_Ora_Incidente': random_date,
                    'Provincia': random.choice(province),
                    'Giorno_Settimana': giorni_map[random_date.weekday()],
                    'Tipo_Strada': strada,
                    'Numero_Feriti': numero_feriti,
                    'Numero_Morti': numero_morti,
                    'Velocita_Media_Stimata': velocita
                })
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
        if 'Numero_Morti' in self.df.columns:
            self.df['Mortale'] = (self.df['Numero_Morti'] > 0).astype(int)
        self.popola_tabella_dati()
        self.aggiorna_selettori(variabile_da_mantenere)

    def aggiorna_selettori(self, variabile_da_mantenere=None):
        if self.df is None:
            return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        all_columns = datetime_cols + object_columns + numeric_columns
        if 'Giorno' not in all_columns and 'Giorno' in self.df.columns:
            all_columns.insert(1, 'Giorno')
        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []

        # Selettori per Analisi Descrittiva
        self.selettore_var_descrittiva.configure(values=all_columns)
        if variabile_da_mantenere and variabile_da_mantenere in all_columns:
            self.selettore_var_descrittiva.set(variabile_da_mantenere)
        elif all_columns:
            self.selettore_var_descrittiva.set(all_columns[0])

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
        pass  # Analisi vengono eseguite su selezione variabile o refresh

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
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        data_frame = customtkinter.CTkFrame(tab)
        data_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_rowconfigure(0, weight=1)
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Calibri', 11))
        style.configure("Treeview.Heading", font=('Calibri', 12,'bold'))
        columns = ('Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata')
        self.data_table = ttk.Treeview(data_frame, columns=columns, show='headings')
        for col in columns:
            width = {'Data_Ora_Incidente': 160}.get(col, 120)
            anchor = 'center'
            self.data_table.column(col, width=width, anchor=anchor)
            self.data_table.heading(col, text=col)
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_table.yview)
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.data_table.xview)
        self.data_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.data_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

    def popola_tabella_dati(self):
        if not hasattr(self, 'data_table'):
            return
        self.data_table.delete(*self.data_table.get_children())
        if self.df is None:
            return
        for _, row in self.df.head(100).iterrows():
            values = []
            for col in self.data_table["columns"]:
                val = row.get(col, "")
                if isinstance(val, float):
                    val = f"{val:.2f}"
                elif isinstance(val, pd.Timestamp):
                    val = val.strftime("%Y-%m-%d %H:%M")
                values.append(val)
            self.data_table.insert("", "end", values=values)

    def setup_tab_calcolo_dati(self):
        tab = self.tab_view.tab("Calcolo Dati")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
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

    def esegui_calcolo_dati(self, *args):
        self.pulisci_frame(self.frame_risultati_calcolo)
        if self.df is None:
            return
        var = self.selettore_var_calcolo.get()
        if var not in self.df.columns:
            return
        serie = self.df[var].dropna()
        if serie.empty:
            customtkinter.CTkLabel(self.frame_risultati_calcolo, text="Nessun dato disponibile per la variabile selezionata.").pack(padx=10, pady=10)
            return
        descrittive = {
            "Media": np.mean(serie),
            "Mediana": np.median(serie),
            "Moda": serie.mode().iloc[0] if not serie.mode().empty else "N/A",
            "Varianza": np.var(serie, ddof=1),
            "Deviazione Standard": np.std(serie, ddof=1),
            "Minimo": np.min(serie),
            "Massimo": np.max(serie),
            "Quantile 25%": np.percentile(serie, 25),
            "Quantile 75%": np.percentile(serie, 75),
            "Numero Valori": len(serie)
        }
        df_descr = pd.DataFrame(list(descrittive.items()), columns=["Statistica", "Valore"])
        self._crea_tabella_treeview(self.frame_risultati_calcolo, df_descr, title="Statistiche Descrittive")

    def setup_tab_campionatura(self):
        tab = self.tab_view.tab("Campionatura")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
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

    def esegui_campionatura(self):
        self.pulisci_frame(self.frame_risultati_campionatura)
        if self.df is None:
            return
        var = self.selettore_var_campionatura.get()
        if var not in self.df.columns:
            return
        try:
            n = int(self.entry_dim_campione.get())
        except Exception:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text="Dimensione campione non valida.").pack(padx=10, pady=10)
            return
        serie = self.df[var].dropna()
        if len(serie) < n or n <= 0:
            customtkinter.CTkLabel(self.frame_risultati_campionatura, text="Campione troppo grande o vuoto.").pack(padx=10, pady=10)
            return
        campione = serie.sample(n)
        descrittive = {
            "Media campione": np.mean(campione),
            "Mediana": np.median(campione),
            "Varianza": np.var(campione, ddof=1),
            "Deviazione Standard": np.std(campione, ddof=1),
            "Minimo": np.min(campione),
            "Massimo": np.max(campione),
            "Numero Valori": len(campione)
        }
        df_descr = pd.DataFrame(list(descrittive.items()), columns=["Statistica", "Valore"])
        self._crea_tabella_treeview(self.frame_risultati_campionatura, df_descr, title="Statistiche Campione")

    def setup_tab_descrittiva(self):
        tab = self.tab_view.tab("Analisi Descrittiva")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        self.frame_controlli_descrittiva = customtkinter.CTkFrame(tab)
        self.frame_controlli_descrittiva.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.frame_controlli_descrittiva.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(self.frame_controlli_descrittiva, text="Variabile:").grid(row=0, column=0, padx=(10,5))
        self.selettore_var_descrittiva = customtkinter.CTkComboBox(self.frame_controlli_descrittiva, values=[], command=self.esegui_descrittiva)
        self.selettore_var_descrittiva.grid(row=0, column=1, padx=5, sticky="ew")
        self.bottone_refresh_descrittiva = customtkinter.CTkButton(self.frame_controlli_descrittiva, text="🔄", command=self.esegui_descrittiva, width=35, height=35)
        self.bottone_refresh_descrittiva.grid(row=0, column=2, padx=(5,10), pady=5)
        self.frame_risultati_descrittiva = customtkinter.CTkScrollableFrame(tab, label_text="Grafici e Tabelle")
        self.frame_risultati_descrittiva.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)

    def esegui_descrittiva(self, *args):
        self.pulisci_frame(self.frame_risultati_descrittiva)
        if self.df is None:
            return
        var = self.selettore_var_descrittiva.get()
        if var not in self.df.columns:
            return
        serie = self.df[var].dropna()
        if serie.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato disponibile per la variabile selezionata.").pack(padx=10, pady=10)
            return
        fig, ax = plt.subplots(figsize=(6, 3))
        if pd.api.types.is_numeric_dtype(serie):
            ax.hist(serie, bins=15, color='skyblue', edgecolor='black')
            ax.set_title(f"Istogramma di {var}")
        else:
            serie.value_counts().plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(f"Distribuzione di {var}")
        ax.set_xlabel(var)
        ax.set_ylabel("Frequenza")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.frame_risultati_descrittiva)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
        self.matplotlib_widgets.append(canvas)

    def setup_tab_bivariata(self):
        tab = self.tab_view.tab("Analisi Bivariata")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(frame_controlli, text="Variabile X:").grid(row=0, column=0, padx=(10,5))
        self.selettore_var_biv_x = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_bivariata)
        self.selettore_var_biv_x.grid(row=0, column=1, padx=5, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Variabile Y:").grid(row=0, column=2, padx=(10,5))
        self.selettore_var_biv_y = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_bivariata)
        self.selettore_var_biv_y.grid(row=0, column=3, padx=5, sticky="ew")
        self.bottone_refresh_bivariata = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_bivariata, width=35, height=35)
        self.bottone_refresh_bivariata.grid(row=0, column=4, padx=(5,10), pady=5)
        self.frame_risultati_bivariata = customtkinter.CTkScrollableFrame(tab, label_text="Grafico e Statistiche")
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1)

    def esegui_bivariata(self, *args):
        self.pulisci_frame(self.frame_risultati_bivariata)
        if self.df is None:
            return
        x = self.selettore_var_biv_x.get()
        y = self.selettore_var_biv_y.get()
        if x not in self.df.columns or y not in self.df.columns:
            return
        serie_x = self.df[x].dropna()
        serie_y = self.df[y].dropna()
        df_xy = self.df[[x, y]].dropna()
        if df_xy.empty:
            customtkinter.CTkLabel(self.frame_risultati_bivariata, text="Nessun dato disponibile per le variabili selezionate.").pack(padx=10, pady=10)
            return
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.scatter(df_xy[x], df_xy[y], alpha=0.6)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"Scatterplot: {x} vs {y}")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.frame_risultati_bivariata)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
        self.matplotlib_widgets.append(canvas)
        # Calcolo correlazione
        corr, pval = stats.pearsonr(df_xy[x], df_xy[y])
        df_corr = pd.DataFrame([["Pearson r", corr], ["p-value", pval]], columns=["Statistica", "Valore"])
        self._crea_tabella_treeview(self.frame_risultati_bivariata, df_corr, title="Correlazione Pearson")

    def setup_tab_inferenziale(self):
        tab = self.tab_view.tab("Analisi Inferenziale")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(frame_controlli, text="Provincia (Poisson):").grid(row=0, column=0, padx=(10,5))
        self.selettore_provincia_poisson = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_poisson)
        self.selettore_provincia_poisson.grid(row=0, column=1, padx=5, sticky="ew")
        self.bottone_refresh_poisson = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_poisson, width=35, height=35)
        self.bottone_refresh_poisson.grid(row=0, column=2, padx=(5,10), pady=5)
        customtkinter.CTkLabel(frame_controlli, text="Provincia (CI):").grid(row=1, column=0, padx=(10,5))
        self.selettore_provincia_ci = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_ci)
        self.selettore_provincia_ci.grid(row=1, column=1, padx=5, sticky="ew")
        self.bottone_refresh_ci = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_ci, width=35, height=35)
        self.bottone_refresh_ci.grid(row=1, column=2, padx=(5,10), pady=5)
        self.frame_risultati_inferenziale = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Inferenza")
        self.frame_risultati_inferenziale.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_inferenziale.grid_columnconfigure(0, weight=1)

    def esegui_poisson(self, *args):
        self.pulisci_frame(self.frame_risultati_inferenziale)
        if self.df is None or 'Provincia' not in self.df.columns:
            return
        provincia = self.selettore_provincia_poisson.get()
        df_prov = self.df[self.df['Provincia'] == provincia]
        if df_prov.empty:
            customtkinter.CTkLabel(self.frame_risultati_inferenziale, text="Nessun dato per la provincia selezionata.").pack(padx=10, pady=10)
            return
        # Esempio: stima Poisson per incidenti mortali
        if 'Mortale' not in df_prov.columns:
            customtkinter.CTkLabel(self.frame_risultati_inferenziale, text="Colonna 'Mortale' non trovata.").pack(padx=10, pady=10)
            return
        n_incidenti = len(df_prov)
        n_mortali = df_prov['Mortale'].sum()
        tasso = n_mortali / n_incidenti if n_incidenti else 0
        ci_low, ci_up = stats.poisson.interval(0.95, n_mortali)
        df_poisson = pd.DataFrame([
            ["Incidenti totali", n_incidenti],
            ["Incidenti mortali", n_mortali],
            ["Tasso incidenti mortali", tasso],
            ["CI 95% Poisson (basso)", ci_low],
            ["CI 95% Poisson (alto)", ci_up]
        ], columns=["Statistica", "Valore"])
        self._crea_tabella_treeview(self.frame_risultati_inferenziale, df_poisson, title=f"Inferenza Poisson - {provincia}")

    def esegui_ci(self, *args):
        self.pulisci_frame(self.frame_risultati_inferenziale)
        if self.df is None or 'Provincia' not in self.df.columns:
            return
        provincia = self.selettore_provincia_ci.get()
        df_prov = self.df[self.df['Provincia'] == provincia]
        if df_prov.empty:
            customtkinter.CTkLabel(self.frame_risultati_inferenziale, text="Nessun dato per la provincia selezionata.").pack(padx=10, pady=10)
            return
        # Esempio: intervallo di confidenza per la media dei feriti
        if 'Numero_Feriti' not in df_prov.columns:
            customtkinter.CTkLabel(self.frame_risultati_inferenziale, text="Colonna 'Numero_Feriti' non trovata.").pack(padx=10, pady=10)
            return
        serie = df_prov['Numero_Feriti'].dropna()
        n = len(serie)
        if n == 0:
            customtkinter.CTkLabel(self.frame_risultati_inferenziale, text="Nessun dato valido per la provincia.").pack(padx=10, pady=10)
            return
        media = np.mean(serie)
        std = np.std(serie, ddof=1)
        ci = stats.t.interval(0.95, n-1, loc=media, scale=std/np.sqrt(n))
        df_ci = pd.DataFrame([
            ["Media feriti", media],
            ["IC 95% (basso)", ci[0]],
            ["IC 95% (alto)", ci[1]],
            ["Numero osservazioni", n]
        ], columns=["Statistica", "Valore"])
        self._crea_tabella_treeview(self.frame_risultati_inferenziale, df_ci, title=f"IC Media Feriti - {provincia}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
