# =============================================================================
# Software di Analisi Statistica Incidenti Stradali (v7.0 - Richiesta Utente)
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
import matplotlib.ticker as mticker
import random
from datetime import datetime, timedelta, date
import collections

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
        self.tab_view = customtkinter.CTkTabview(self, command=self.on_tab_change)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_view.add("Dati Forniti")
        self.tab_view.add("Analisi Descrittiva")
        self.tab_view.add("Analisi Bivariata")
        self.tab_view.add("Analisi Inferenziale")

        # Setup di tutte le schede
        self.setup_tab_dati_forniti()
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.setup_tab_inferenziale()

        self.tab_view.set("Dati Forniti")

    def carica_csv(self):
        filepath = filedialog.askopenfilename(title="Seleziona un file CSV", filetypes=(("File CSV", "*.csv"), ("Tutti i file", "*.*")))
        if not filepath: return
        try:
            df = pd.read_csv(filepath)
            filename = filepath.split('/')[-1]
            self.label_file.configure(text=f"Caricato: {filename} ({len(df)} record)")
            self.inizializza_dati(df)
            self.tab_view.set("Dati Forniti")
        except Exception as e:
            self.label_file.configure(text=f"Errore nel caricamento: {e}", text_color="red")

    def carica_dati_esempio(self):
        variabile_selezionata = self.selettore_var_descrittiva.get()
        records = []
        province = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Catania', 'Salerno', 'Bologna', 'Venezia', 'Bari']
        tipi_strada = ['Urbana', 'Statale', 'Autostrada']
        giorni_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        for _ in range(400):
            random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
            random_date = start_date + timedelta(seconds=random_seconds)
            prov = random.choice(province)
            strada = random.choice(tipi_strada)
            if strada == 'Urbana': velocita = random.randint(30, 65)
            elif strada == 'Statale': velocita = random.randint(60, 95)
            else: velocita = random.randint(100, 140)
            numero_morti = random.choices([0, 1, 2], weights=[95, 4, 1], k=1)[0]
            if numero_morti > 0: numero_feriti = random.randint(numero_morti, 8)
            else: numero_feriti = random.choices([0, 1, 2, 3, 4], weights=[20, 40, 25, 10, 5], k=1)[0]
            records.append({'Data_Ora_Incidente': random_date, 'Provincia': prov, 'Giorno_Settimana': giorni_map[random_date.weekday()], 'Tipo_Strada': strada, 'Numero_Feriti': numero_feriti, 'Numero_Morti': numero_morti, 'Velocita_Media_Stimata': velocita})
        df = pd.DataFrame(records)
        self.label_file.configure(text=f"Caricati {len(df)} record simulati.")
        self.inizializza_dati(df, variabile_da_mantenere=variabile_selezionata)
        

    def inizializza_dati(self, df, variabile_da_mantenere=None):
        self.df = df.copy()
        # Pulizia e preparazione dati
        if 'Data_Ora_Incidente' in self.df.columns:
            self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce')
        for col in ['Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.df.dropna(subset=['Data_Ora_Incidente', 'Provincia'], inplace=True)
        if self.df.empty:
            self.label_file.configure(text="Errore: Nessun dato valido trovato dopo la pulizia.", text_color="orange")
            self.df = None
            return

        self.df['Ora'] = self.df['Data_Ora_Incidente'].dt.hour
        self.df['Giorno'] = self.df['Data_Ora_Incidente'].dt.date
        if 'Numero_Morti' in self.df.columns:
            self.df['Mortale'] = (self.df['Numero_Morti'] > 0).astype(int)
        
        self.popola_tabella_dati()
        self.aggiorna_selettori(variabile_da_mantenere)

    def aggiorna_selettori(self, variabile_da_mantenere=None):
        if self.df is None: return
        numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        object_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        all_columns = datetime_cols + object_columns + numeric_columns
        province_uniche = sorted(self.df['Provincia'].unique().tolist()) if 'Provincia' in self.df.columns else []
        
        self.selettore_var_descrittiva.configure(values=all_columns)
        if variabile_da_mantenere and variabile_da_mantenere in all_columns:
            self.selettore_var_descrittiva.set(variabile_da_mantenere)
        elif all_columns:
            self.selettore_var_descrittiva.set(all_columns[0])
        
        self.selettore_var_biv_x.configure(values=numeric_columns)
        self.selettore_var_biv_y.configure(values=numeric_columns)
        if numeric_columns and len(numeric_columns) > 1:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[1])
        elif numeric_columns:
            self.selettore_var_biv_x.set(numeric_columns[0])
            self.selettore_var_biv_y.set(numeric_columns[0])
        
        # [FIX] Rimosso il self.after(50) per eliminare il delay all'aggiornamento dei selettori.
        # L'aggiornamento delle analisi è comunque gestito dal comando del tab_view e dai selettori stessi.
        self.after(50, self.on_tab_change)

        self.selettore_provincia_poisson.configure(values=province_uniche)
        self.selettore_provincia_ci.configure(values=province_uniche)
        if province_uniche:
            self.selettore_provincia_poisson.set(province_uniche[0])
            self.selettore_provincia_ci.set(province_uniche[0])

    def on_tab_change(self, *args):
        """Esegue l'analisi appropriata quando l'utente cambia scheda.
        Questa funzione è chiamata automaticamente dal CTkTabview."""
        # La logica di aggiornamento è stata spostata nei comandi dei singoli widget (ComboBox, Button)
        current_tab = self.tab_view.get()
        if self.df is None: return
            
        if current_tab == "Analisi Descrittiva":
            self.esegui_analisi_descrittiva()
        elif current_tab == "Analisi Bivariata":
            self.esegui_analisi_bivariata()
        elif current_tab == "Dati Forniti":
            self.popola_tabella_dati() # [FIX] Assicura che la tabella dati sia sempre aggiornata
            # self.popola_tabella_dati()

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
        
        label = customtkinter.CTkLabel(info_window, text=message, wraplength=450, justify="left", font=customtkinter.CTkFont(size=14))
        label.pack(padx=20, pady=20)

        close_button = customtkinter.CTkButton(info_window, text="Chiudi", command=info_window.destroy)
        close_button.pack(padx=20, pady=10, side="bottom")

    def pulisci_grafici(self):
        for widget in self.matplotlib_widgets:
            widget.destroy()
        self.matplotlib_widgets = []

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
            self.data_table.heading(col, text=col)
            if col == 'Data_Ora_Incidente':
                self.data_table.column(col, width=160, anchor='w')
            elif col in ['Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata']:
                self.data_table.column(col, width=140, anchor='center')
            else:
                 self.data_table.column(col, width=120, anchor='w')

        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_table.yview)
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.data_table.xview)
        self.data_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.data_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

    def popola_tabella_dati(self):
        """Popola la tabella nella scheda 'Dati Forniti'."""
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        if self.df is None or self.df.empty:
            return

        display_df = self.df.copy()
        columns_to_display = ['Data_Ora_Incidente', 'Provincia', 'Giorno_Settimana', 'Tipo_Strada', 'Numero_Feriti', 'Numero_Morti', 'Velocita_Media_Stimata']
        
        columns_to_display = [col for col in columns_to_display if col in display_df.columns]
        if not columns_to_display: return
        
        display_df = display_df[columns_to_display].sort_values(by='Data_Ora_Incidente', ascending=False)
        display_df['Data_Ora_Incidente'] = display_df['Data_Ora_Incidente'].dt.strftime('%Y-%m-%d %H:%M:%S')

        for index, row in display_df.iterrows():
            self.data_table.insert("", "end", values=list(row))

    def setup_tab_descrittiva(self):
        tab = self.tab_view.tab("Analisi Descrittiva")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Seleziona una variabile:").pack(side="left", padx=(10,5))
        self.selettore_var_descrittiva = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_analisi_descrittiva)
        self.selettore_var_descrittiva.pack(side="left", padx=5, expand=True, fill="x")

        customtkinter.CTkLabel(frame_controlli, text="Tipo Grafico:").pack(side="left", padx=(20,5))
        self.selettore_grafico_descrittiva = customtkinter.CTkComboBox(frame_controlli, values=['Barre', 'Torta', 'Linee', 'Istogramma', 'Aste', 'Box Plot'], command=self.esegui_analisi_descrittiva)
        self.selettore_grafico_descrittiva.pack(side="left", padx=5)
        self.selettore_grafico_descrittiva.set('Barre')

        self.bottone_refresh_descrittiva = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_analisi_descrittiva, width=35, height=35)
        self.bottone_refresh_descrittiva.pack(side="left", padx=(10, 10))

        self.frame_risultati_descrittiva = customtkinter.CTkScrollableFrame(tab, label_text="Risultati Analisi Descrittiva")
        self.frame_risultati_descrittiva.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_descrittiva.grid_columnconfigure(0, weight=1)

    def esegui_analisi_descrittiva(self, *args):
        if self.df is None: 
            for widget in self.frame_risultati_descrittiva.winfo_children():
                widget.destroy()
            return

        variable = self.selettore_var_descrittiva.get()
        tipo_grafico = self.selettore_grafico_descrittiva.get()
        if not variable: return
        
        for widget in self.frame_risultati_descrittiva.winfo_children():
            widget.destroy()
        self.pulisci_grafici()
        
        if variable not in self.df.columns:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text=f"Variabile '{variable}' non trovata nei dati.").pack()
            return
            
        data = self.df[variable].dropna()
        if data.empty:
            customtkinter.CTkLabel(self.frame_risultati_descrittiva, text="Nessun dato disponibile per questa variabile.").pack()
            return

        # --- FRAME CONTENITORI ---
        frame_stats = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_stats.pack(fill='x', expand=True, padx=10, pady=5)
        frame_grafico = customtkinter.CTkFrame(self.frame_risultati_descrittiva)
        frame_grafico.pack(fill='both', expand=True, padx=10, pady=5)

        # --- ANALISI BASATA SUL TIPO DI DATO ---
        if pd.api.types.is_numeric_dtype(data):
            # [FEATURE] Accorpamento dati in classi per l'istogramma e tabelle
            bins = np.histogram_bin_edges(data, bins='auto')
            freq_ass_binned = pd.cut(data, bins).value_counts().sort_index()

            # --- 1. TABELLA FREQUENZE (per dati binnati) ---
            customtkinter.CTkLabel(frame_stats, text=f"Tabella Frequenze (in classi) per '{variable}'", font=customtkinter.CTkFont(weight="bold")).pack(pady=(5,0))
            freq_rel = freq_ass_binned / freq_ass_binned.sum()
            freq_cum = freq_ass_binned.cumsum()
            df_freq = pd.DataFrame({'Freq. Assoluta': freq_ass_binned, 'Freq. Relativa (%)': freq_rel * 100, 'Freq. Cumulata': freq_cum})
            
            tree = ttk.Treeview(frame_stats, columns=('', *df_freq.columns), show='headings', height=min(len(df_freq), 7))
            tree.heading('', text='Classe')
            for col in df_freq.columns: tree.heading(col, text=col)
            for index, row in df_freq.iterrows():
                tree.insert('', 'end', values=(index, row.iloc[0], f"{row.iloc[1]:.2f}%", row.iloc[2]))
            tree.pack(fill='x', expand=True, pady=5, padx=5)

            # --- 2. INDICI STATISTICI ---
            customtkinter.CTkLabel(frame_stats, text=f"Indici Statistici per '{variable}'", font=customtkinter.CTkFont(weight="bold")).pack(pady=(10,0))
            # [FEATURE] Calcolo indici di posizione
            mean, median, mode = data.mean(), data.median(), data.mode().iloc[0] if not data.mode().empty else 'N/A'
            # [FEATURE] Calcolo indici di variabilità
            variance, std_dev = data.var(ddof=1), data.std(ddof=1)
            mad = (data - data.mean()).abs().mean()
            range_val = data.max() - data.min()
            cv = std_dev / mean if mean != 0 else 0
            # [FEATURE] Calcolo indici di forma
            skew, kurt = data.skew(), data.kurtosis()
            # [FEATURE] Calcolo di quartili
            q1, q3 = data.quantile(0.25), data.quantile(0.75)
            iqr = q3 - q1
            # [FEATURE] Individuazione intervallo di Chebyshev
            cheb_low, cheb_high = mean - 2 * std_dev, mean + 2 * std_dev

            text_stats = (
                f"POSIZIONE: Media: {mean:.3f} | Mediana: {median:.3f} | Moda: {mode}\n"
                f"VARIABILITÀ: Varianza: {variance:.3f} | Dev. Std: {std_dev:.3f} | Range: {range_val:.3f} | CV: {cv:.3f}\n"
                f"FORMA: Asimmetria: {skew:.3f} | Curtosi: {kurt:.3f}\n"
                f"QUARTILI: Q1: {q1:.3f} | Q3: {q3:.3f} | IQR: {iqr:.3f}\n"
                f"INTERVALLO DI CHEBYSHEV (k=2): [{cheb_low:.3f}, {cheb_high:.3f}]"
            )
            customtkinter.CTkLabel(frame_stats, text=text_stats, justify='left', font=('Consolas', 12)).pack(anchor='w', padx=10, pady=5)

        else:
            # Dati categorici o temporali (trattati come categorici)
            # [FEATURE] Costruzione tabella frequenze (assolute, relative, cumulative)
            customtkinter.CTkLabel(frame_stats, text=f"Tabella Frequenze per '{variable}'", font=customtkinter.CTkFont(weight="bold")).pack(pady=(5,0))
            freq_ass = data.value_counts()
            freq_rel = freq_ass / freq_ass.sum()
            freq_cum = freq_ass.cumsum()
            df_freq = pd.DataFrame({'Freq. Assoluta': freq_ass, 'Freq. Relativa (%)': freq_rel * 100, 'Freq. Cumulata': freq_cum})
            
            tree = ttk.Treeview(frame_stats, columns=('', *df_freq.columns), show='headings', height=min(len(df_freq), 10))
            tree.heading('', text='Categoria')
            for col in df_freq.columns: tree.heading(col, text=col)
            for index, row in df_freq.iterrows():
                tree.insert('', 'end', values=(index, row.iloc[0], f"{row.iloc[1]:.2f}%", row.iloc[2]))
            tree.pack(fill='x', expand=True, pady=5, padx=5)

        # --- 3. GRAFICO SELEZIONATO ---
        # [FEATURE] Rappresentazione dei dati mediante grafici selezionabili
        customtkinter.CTkLabel(frame_grafico, text=f"Grafico: {tipo_grafico} per '{variable}'", font=customtkinter.CTkFont(weight="bold")).pack()
        fig, ax = plt.subplots(figsize=(8, 5))
        try:
            # Logica di plottaggio basata sulla selezione
            if tipo_grafico == 'Istogramma':
                if pd.api.types.is_numeric_dtype(data):
                    ax.hist(data, bins='auto', edgecolor='black')
                else:
                    ax.text(0.5, 0.5, 'Istogramma applicabile solo a dati numerici', ha='center', va='center')
            elif tipo_grafico == 'Box Plot':
                # [FEATURE] Costruzione di box plot (eventualmente con outlier)
                if pd.api.types.is_numeric_dtype(data):
                    ax.boxplot(data, vert=False, showfliers=True) # showfliers=True per mostrare outlier
                    ax.set_yticklabels([variable])
                else:
                    ax.text(0.5, 0.5, 'Box Plot applicabile solo a dati numerici', ha='center', va='center')
            else:
                # Grafici basati su frequenze
                freq_data = freq_ass_binned if pd.api.types.is_numeric_dtype(data) else data.value_counts()
                if tipo_grafico == 'Barre':
                    freq_data.plot(kind='bar', ax=ax)
                elif tipo_grafico == 'Linee':
                    freq_data.sort_index().plot(kind='line', ax=ax, marker='o')
                elif tipo_grafico == 'Torta':
                    freq_data.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
                    ax.set_ylabel('')
                elif tipo_grafico == 'Aste':
                    ax.stem(freq_data.index.astype(str), freq_data.values)
                    plt.xticks(rotation=45, ha="right")

            ax.set_title(f"{tipo_grafico} di '{variable}'")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        finally:
            plt.close(fig)

    def crea_canvas_matplotlib(self, parent, r, c, w=1, h=1):
        frame = customtkinter.CTkFrame(parent)
        frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew", rowspan=h, columnspan=w)
        self.matplotlib_widgets.append(frame)
        return frame

    def setup_tab_bivariata(self):
        tab = self.tab_view.tab("Analisi Bivariata")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        frame_controlli = customtkinter.CTkFrame(tab)
        frame_controlli.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_controlli.grid_columnconfigure((1, 3), weight=1)
        customtkinter.CTkLabel(frame_controlli, text="Variabile X:").grid(row=0, column=0, padx=(10,5), pady=5)
        self.selettore_var_biv_x = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_analisi_bivariata)
        self.selettore_var_biv_x.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkLabel(frame_controlli, text="Variabile Y:").grid(row=0, column=2, padx=(10,5), pady=5)
        self.selettore_var_biv_y = customtkinter.CTkComboBox(frame_controlli, values=[], command=self.esegui_analisi_bivariata)
        self.selettore_var_biv_y.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.bottone_refresh_bivariata = customtkinter.CTkButton(frame_controlli, text="🔄", command=self.esegui_analisi_bivariata, width=35, height=35)
        self.bottone_refresh_bivariata.grid(row=0, column=4, padx=(10, 10))
        
        self.frame_risultati_bivariata = customtkinter.CTkFrame(tab)
        self.frame_risultati_bivariata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_risultati_bivariata.grid_columnconfigure(0, weight=1)
        self.frame_risultati_bivariata.grid_rowconfigure(2, weight=1)

    def esegui_analisi_bivariata(self, *args):
        if self.df is None: return
        var_x, var_y = self.selettore_var_biv_x.get(), self.selettore_var_biv_y.get()
        if not var_x or not var_y: return
        
        # Pulisce i risultati precedenti
        for widget in self.frame_risultati_bivariata.winfo_children(): 
            widget.destroy()
        self.pulisci_grafici()
        
        df_subset = self.df[[var_x, var_y]].dropna()
        if len(df_subset) < 2:
            customtkinter.CTkLabel(self.frame_risultati_bivariata, text="Dati insufficienti per l'analisi.").pack(pady=20)
            return
            
        x_data, y_data = df_subset[var_x], df_subset[var_y]
        
        # FIX 3: Gestisce il caso x == y per prevenire l'errore e dare un output corretto
        LinregressResult = collections.namedtuple('LinregressResult', ['slope', 'intercept', 'rvalue', 'pvalue', 'stderr'])
        if var_x == var_y:
            correlation = 1.0
            regression = LinregressResult(slope=1.0, intercept=0.0, rvalue=1.0, pvalue=0.0, stderr=0.0)
        else:
            # [FEATURE] Calcolo del coefficiente di correlazione campionario
            correlation = df_subset.corr().iloc[0, 1]
            # [FEATURE] Calcolo della retta di regressione stimata
            regression = stats.linregress(x=x_data, y=y_data)

        info_bivariata="""**Cos'è?**\nUn'analisi che studia la relazione tra due variabili numeriche contemporaneamente.\n\n**A Cosa Serve?**\nA capire se esiste un legame tra le due variabili, in che direzione (positivo o negativo) e con quale forza. La regressione permette anche di prevedere il valore di una variabile basandosi sull'altra.\n\n--- Legenda dei Termini ---\n- **Coefficiente di Correlazione (r):** Varia da -1 (relazione inversa perfetta) a +1 (relazione diretta perfetta). 0 indica assenza di relazione *lineare*.\n- **Retta di Regressione (y = mx + b):** La linea che meglio approssima i dati.\n- **Pendenza (m):** Indica di quanto aumenta in media Y per ogni aumento di 1 unità in X.\n- **Intercetta (b):** Il valore previsto di Y quando X è 0."""
        guida_bivariata="""**Interpretazione del Diagramma a Dispersione:**\n- **Assi Cartesiani:** Gli assi X e Y rappresentano le due variabili oggetto di analisi.\n- **Punti Dati:** Ciascun punto sul piano cartesiano corrisponde a un'osservazione bivariata.\n- **Distribuzione dei Punti:** La configurazione dei punti (la 'nuvola') indica la natura della relazione. Un andamento crescente/decrescente suggerisce una correlazione positiva/negativa.\n- **Retta di Regressione:** La linea rossa rappresenta il modello di regressione lineare semplice, che interpola la nuvola di punti minimizzando la somma dei quadrati dei residui."""
        self._crea_titolo_sezione(self.frame_risultati_bivariata, 0, "Analisi di Correlazione e Regressione", info_bivariata, testo_guida=guida_bivariata)
        
        frame_risultati_testuali = customtkinter.CTkFrame(self.frame_risultati_bivariata)
        frame_risultati_testuali.grid(row=1, column=0, sticky="ew", padx=10)
        risultati_testuali = f"Coefficiente di Correlazione (r): {correlation:.4f}\nEquazione Retta di Regressione: y = {regression.slope:.4f}x + {regression.intercept:.4f}"
        customtkinter.CTkLabel(frame_risultati_testuali, text=risultati_testuali, justify="left").pack(pady=5)
        
        # [FEATURE] Costruzione di diagramma a dispersione
        canvas_frame = self.crea_canvas_matplotlib(self.frame_risultati_bivariata, 2, 0)
        fig, ax = plt.subplots(figsize=(8, 6))
        
        num_points = len(x_data)
        point_size = 20 if num_points < 1000 else 5
        alpha_value = 0.6 if num_points < 1000 else 0.3
        ax.scatter(x_data, y_data, alpha=alpha_value, s=point_size, label='Dati')

        x_range = x_data.max() - x_data.min()
        y_range = y_data.max() - y_data.min()
        x_pad = x_range * 0.05 if x_range > 0 else 1
        y_pad = y_range * 0.05 if y_range > 0 else 1
        ax.set_xlim(x_data.min() - x_pad, x_data.max() + x_pad)
        ax.set_ylim(y_data.min() - y_pad, y_data.max() + y_pad)
        
        line_x = np.array(ax.get_xlim())
        line_y = regression.slope * line_x + regression.intercept
        ax.plot(line_x, line_y, color='red', label='Retta di Regressione')
        
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=7, prune='both'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=7, prune='both'))

        ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}'), ax.set_xlabel(var_x), ax.set_ylabel(var_y), ax.legend(), ax.grid(True), fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw(), canvas.get_tk_widget().pack(fill='both', expand=True)
        plt.close(fig)

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
        
        info_poisson = """**Cos'è?**\nIl Modello di Poisson è uno strumento statistico usato per calcolare la probabilità che un certo numero di eventi (k) accada in un intervallo di tempo o spazio, dato un tasso medio di accadimento (λ).\n\n**A Cosa Serve?**\nIn questo contesto, serve a stimare la probabilità di osservare un numero specifico di incidenti (es. 2 incidenti) in una data ora, o fascia oraria, e provincia, basandosi sulla frequenza storica.\n\n--- Legenda dei Termini ---\n- **λ (Lambda):** Tasso medio di accadimento. È il numero medio di incidenti stimato per la provincia e l'ora/fascia selezionata.\n- **k:** Il numero esatto di eventi (incidenti) di cui si vuole calcolare la probabilità.\n- **P(X=k):** La probabilità calcolata che il numero di incidenti sia esattamente 'k'."""
        self._crea_titolo_sezione(frame_poisson, 0, "Modello di Poisson", info_poisson, columnspan=3)

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

        # --- Sezione 2: Test T ---
        frame_ttest = customtkinter.CTkFrame(scroll_frame, border_width=1)
        frame_ttest.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame_ttest.grid_columnconfigure(1, weight=1)
        
        info_ttest="""**Cos'è?**\nIl Test T per Campioni Indipendenti è un test di ipotesi che confronta le medie di due gruppi di dati separati e indipendenti (es. feriti di giorno vs feriti di notte).\n\n**A Cosa Serve?**\nDetermina se la differenza osservata tra le due medie è statisticamente significativa o se potrebbe essere semplicemente dovuta al caso.\n\n--- Legenda dei Termini ---\n- **Ipotesi Nulla (H₀):** L'ipotesi di partenza che non esista una vera differenza tra le medie dei due gruppi.\n- **p-value:** La probabilità di osservare i dati attuali (o dati ancora più estremi) se l'Ipotesi Nulla fosse vera. Un p-value basso (tipicamente < 0.05) suggerisce di rigettare H₀.\n- **Statistica t:** Misura la dimensione della differenza tra le medie relativa alla variabilità dei dati. Più è lontana da zero, più la differenza è marcata."""
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
        
        info_ci="""**Cos'è?**\nUn Intervallo di Confidenza (IC) è un range di valori, calcolato a partire da dati campionari, che si stima possa contenere il vero valore di un parametro della popolazione (es. la 'vera' media di incidenti giornalieri).\n\n**A Cosa Serve?**\nFornisce una misura della precisione della stima. Invece di avere un singolo valore (la media del campione), si ottiene un intervallo di valori plausibili.\n\n--- Legenda dei Termini ---\n- **Livello di Confidenza:** La probabilità (es. 95%) che, ripetendo l'esperimento più volte, l'intervallo calcolato contenga il vero parametro della popolazione.\n- **Media Campionaria:** La media calcolata sui dati a disposizione.\n- **Range (IC):** L'intervallo [valore inferiore, valore superiore]. Un intervallo stretto indica una stima più precisa."""
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
            k_entry = self.entry_k_poisson.get()
            if not k_entry: raise ValueError("Il numero di incidenti (k) non può essere vuoto.")
            k = int(k_entry)

            fascia_oraria_str = self.entry_ora_poisson.get().strip()
            if not fascia_oraria_str: raise ValueError("La fascia oraria non può essere vuota.")

            if '-' in fascia_oraria_str:
                parts = fascia_oraria_str.split('-')
                if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                    raise ValueError("Formato range non valido. Usare 'ora_inizio-ora_fine'.")
                ora_inizio, ora_fine = int(parts[0]), int(parts[1])
            else:
                ora_inizio = ora_fine = int(fascia_oraria_str)

            if not (0 <= ora_inizio <= 23 and 0 <= ora_fine <= 23):
                raise ValueError("Le ore devono essere comprese tra 0 e 23.")
            if ora_inizio > ora_fine:
                raise ValueError("L'ora di inizio non può essere successiva all'ora di fine.")

            durata_ore = ora_fine - ora_inizio + 1
            
            df_prov = self.df[self.df['Provincia'] == provincia]
            giorni_osservati = df_prov['Giorno'].nunique()
            
            if giorni_osservati == 0:
                risultato = f"Nessun dato disponibile per la provincia di {provincia}."
            else:
                incidenti_nella_fascia = df_prov[
                    (df_prov['Ora'] >= ora_inizio) & (df_prov['Ora'] <= ora_fine)
                ].shape[0]
                
                lambda_val = incidenti_nella_fascia / giorni_osservati
                prob = stats.poisson.pmf(k, lambda_val)
                
                risultato = f"ANALISI PER {provincia.upper()}\n"
                risultato += "--------------------------------------------------\n"
                if durata_ore == 1:
                    risultato += f"Ora specifica: {ora_inizio}:00 (Durata: {durata_ore} ora)\n\n"
                else:
                    risultato += f"Fascia oraria: {ora_inizio}:00 - {ora_fine}:00 (Durata: {durata_ore} ore)\n\n"
                risultato += f"Tasso medio stimato (λ) per la fascia oraria:\n{lambda_val:.4f} incidenti (calcolato su {giorni_osservati} giorni)\n\n"
                risultato += f"Probabilità di osservare esattamente {k} incidenti:\n{prob:.4%}"

        except (ValueError, TypeError, IndexError) as e:
            risultato = f"Errore di Input:\n{e}"
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
            provincia = self.selettore_provincia_ci.get()
            livello_entry = self.entry_livello_ci.get()
            if not livello_entry: raise ValueError("Il livello di confidenza non può essere vuoto.")

            livello = int(livello_entry)
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

if __name__ == '__main__':
    app = App()
    app.mainloop()
