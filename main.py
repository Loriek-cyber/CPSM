import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from tksheet import Sheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ExcelTableApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisi Statistiche Dati Incidenti Stradali")
        self.geometry("1400x800")
        
        # DataFrame per memorizzare i dati
        self.df = pd.DataFrame()
        
        # Colonne attese per i dati degli incidenti
        self.expected_columns = [
            "Data_Ora_Incidente", "Provincia", "Giorno_Settimana", 
            "Tipo_Strada", "Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"
        ]

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Dati (table)
        self.dati_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.dati_frame, text="Dati")

        # Tab 2: Visualizzazione dei dati
        self.visual_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.visual_frame, text="Grafici")

        # Tab 3: Analisi Statistiche
        self.stats_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.stats_frame, text="Analisi Statistiche")

        # Tab 4: Analisi Bivariata
        self.bivariate_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.bivariate_frame, text="Analisi Bivariata")

        self.setup_data_tab()
        self.setup_visual_tab()
        self.setup_stats_tab()
        self.setup_bivariate_tab()
        

    def setup_data_tab(self):
        # Frame per i pulsanti
        buttons_frame = ctk.CTkFrame(self.dati_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Pulsanti per operazioni sui dati
        upload_btn = ctk.CTkButton(buttons_frame, text="Carica CSV", command=self.upload_csv)
        upload_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(buttons_frame, text="Salva CSV", command=self.save_csv)
        save_btn.pack(side="left", padx=(0, 10))

        add_row_btn = ctk.CTkButton(buttons_frame, text="Aggiungi Riga", command=self.add_row)
        add_row_btn.pack(side="left", padx=(0, 10))

        delete_row_btn = ctk.CTkButton(buttons_frame, text="Elimina Riga", command=self.delete_row)
        delete_row_btn.pack(side="left", padx=(0, 10))

        create_sample_btn = ctk.CTkButton(buttons_frame, text="Crea Dati Esempio", command=self.create_sample_data)
        create_sample_btn.pack(side="left")

        # Tabella modificabile
        self.sheet = Sheet(
            self.dati_frame, 
            data=[[]], 
            headers=self.expected_columns,
            width=1300, 
            height=500
        )
        
        # Abilita tutte le funzionalità di modifica
        self.sheet.enable_bindings([
            "single_select", "row_select", "column_select", "drag_select",
            "column_width_resize", "double_click_column_resize",
            "row_height_resize", "column_height_resize",
            "arrowkeys", "right_click_popup_menu", "rc_select",
            "rc_insert_column", "rc_delete_column", "rc_insert_row", "rc_delete_row",
            "copy", "cut", "paste", "delete", "undo", "edit_cell"
        ])
        
        self.sheet.pack(fill="both", expand=True, padx=10, pady=10)
        self.sheet.bind("<<SheetModified>>", self.on_sheet_modified)

    def setup_visual_tab(self):
        # Frame per i controlli dei grafici
        controls_frame = ctk.CTkFrame(self.visual_frame)
        controls_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Pulsanti per diversi tipi di grafici
        graph_buttons = [
            ("Incidenti per Provincia", self.plot_incidents_by_province),
            ("Incidenti per Giorno", self.plot_incidents_by_day),
            ("Feriti vs Morti", self.plot_casualties),
            ("Tipo Strada", self.plot_road_type),
            ("Velocità Media", self.plot_speed_distribution),
            ("Trend Temporale", self.plot_time_trend)
        ]

        for i, (text, command) in enumerate(graph_buttons):
            btn = ctk.CTkButton(controls_frame, text=text, command=command, width=150)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)

        # Frame per i grafici
        self.graph_frame = ctk.CTkFrame(self.visual_frame)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label iniziale
        self.no_data_label = ctk.CTkLabel(
            self.graph_frame, 
            text="Carica dei dati per visualizzare i grafici",
            font=ctk.CTkFont(size=16)
        )
        self.no_data_label.pack(expand=True)

    def setup_stats_tab(self):
        # Frame principale diviso in due parti
        main_frame = ctk.CTkFrame(self.stats_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame di controllo
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Selezione variabile
        ctk.CTkLabel(control_frame, text="Seleziona Variabile:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        
        self.stats_var = ctk.StringVar(value="Numero_Feriti")
        self.stats_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=["Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"],
            variable=self.stats_var,
            width=200
        )
        self.stats_dropdown.pack(side="left", padx=(0, 10))

        # Pulsanti per analisi
        stats_buttons = [
            ("Tabelle Frequenze", self.show_frequency_tables),
            ("Indici Posizione", self.show_position_indices),
            ("Indici Variabilità", self.show_variability_indices),
            ("Indici Forma", self.show_shape_indices),
            ("Box Plot", self.show_boxplot),
            ("Quartili e Outlier", self.show_quartiles_analysis)
        ]

        for i, (text, command) in enumerate(stats_buttons):
            btn = ctk.CTkButton(control_frame, text=text, command=command, width=130)
            btn.pack(side="left", padx=2)

        # Frame per risultati statistici
        self.stats_result_frame = ctk.CTkFrame(main_frame)
        self.stats_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Textbox per risultati
        self.stats_textbox = ctk.CTkTextbox(self.stats_result_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.stats_textbox.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Frame per grafici statistici
        self.stats_graph_frame = ctk.CTkFrame(self.stats_result_frame)
        self.stats_graph_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

    def setup_bivariate_tab(self):
        # Frame principale
        main_frame = ctk.CTkFrame(self.bivariate_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame di controllo
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Selezione variabili
        ctk.CTkLabel(control_frame, text="Variabile X:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        self.bivar_x = ctk.StringVar(value="Numero_Feriti")
        self.bivar_x_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=["Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"],
            variable=self.bivar_x,
            width=150
        )
        self.bivar_x_dropdown.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(control_frame, text="Variabile Y:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        self.bivar_y = ctk.StringVar(value="Velocita_Media_Stimata")
        self.bivar_y_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=["Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"],
            variable=self.bivar_y,
            width=150
        )
        self.bivar_y_dropdown.pack(side="left", padx=(0, 20))

        # Pulsanti analisi bivariata
        bivar_buttons = [
            ("Diagramma Dispersione", self.show_scatter_plot),
            ("Correlazione", self.show_correlation),
            ("Regressione Lineare", self.show_regression)
        ]

        for text, command in bivar_buttons:
            btn = ctk.CTkButton(control_frame, text=text, command=command, width=150)
            btn.pack(side="left", padx=5)

        # Frame per risultati bivariati
        self.bivar_result_frame = ctk.CTkFrame(main_frame)
        self.bivar_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Textbox per risultati
        self.bivar_textbox = ctk.CTkTextbox(self.bivar_result_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.bivar_textbox.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Frame per grafici bivariati
        self.bivar_graph_frame = ctk.CTkFrame(self.bivar_result_frame)
        self.bivar_graph_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

    def upload_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.update_sheet_from_df()
                messagebox.showinfo("Successo", "File CSV caricato correttamente!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel caricamento del file: {str(e)}")

    def save_csv(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Nessun dato da salvare!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Successo", "File salvato correttamente!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")

    def add_row(self):
        self.sheet.insert_row()
        self.update_df_from_sheet()

    def delete_row(self):
        selected = self.sheet.get_selected_rows()
        if selected:
            for row in sorted(selected, reverse=True):
                self.sheet.delete_row(row)
            self.update_df_from_sheet()
        else:
            messagebox.showwarning("Attenzione", "Seleziona una riga da eliminare!")

    def create_sample_data(self):
        sample_data = []
        provinces = ["Milano", "Roma", "Napoli", "Torino", "Palermo", "Genova", "Bologna", "Firenze"]
        days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        road_types = ["Urbana", "Extraurbana", "Autostrada", "Provinciale"]
        
        np.random.seed(42)  # Per risultati riproducibili
        for i in range(100):
            feriti = np.random.poisson(2)  # Distribuzione Poisson per feriti
            morti = np.random.binomial(feriti, 0.1) if feriti > 0 else 0  # Morti proporzionali ai feriti
            velocita = np.random.normal(70, 25)  # Distribuzione normale per velocità
            velocita = max(20, min(150, velocita))  # Limita velocità tra 20 e 150
            
            sample_data.append([
                f"2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d} {np.random.randint(0,24):02d}:{np.random.randint(0,60):02d}",
                np.random.choice(provinces),
                np.random.choice(days),
                np.random.choice(road_types),
                feriti,
                morti,
                round(velocita, 1)
            ])
        
        self.df = pd.DataFrame(sample_data, columns=self.expected_columns)
        self.update_sheet_from_df()
        messagebox.showinfo("Successo", "Dati di esempio creati!")

    def update_sheet_from_df(self):
        if not self.df.empty:
            self.sheet.set_sheet_data(self.df.values.tolist())
            self.sheet.headers(list(self.df.columns))

    def update_df_from_sheet(self):
        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()
        if data and headers:
            filtered_data = [row for row in data if any(str(cell).strip() for cell in row)]
            self.df = pd.DataFrame(filtered_data, columns=headers)

    def on_sheet_modified(self, event):
        self.update_df_from_sheet()

    def get_numeric_data(self, column_name):
        """Estrae i dati numerici da una colonna"""
        if self.df.empty:
            return None
        return pd.to_numeric(self.df[column_name], errors='coerce').dropna()

    def show_frequency_tables(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Costruisci le classi
        n_classes = min(10, int(np.sqrt(len(data))))
        hist, bin_edges = np.histogram(data, bins=n_classes)
        
        # Tabella delle frequenze
        result = f"TABELLE DELLE FREQUENZE - {variable}\n"
        result += "=" * 60 + "\n\n"
        
        # Frequenze assolute e relative
        result += f"{'Classe':<20} {'Freq. Ass.':<12} {'Freq. Rel.':<12} {'Freq. Ass. Cum.':<15} {'Freq. Rel. Cum.':<15}\n"
        result += "-" * 80 + "\n"
        
        cum_freq = 0
        cum_rel = 0
        
        for i in range(len(hist)):
            freq_abs = hist[i]
            freq_rel = freq_abs / len(data)
            cum_freq += freq_abs
            cum_rel += freq_rel
            
            class_label = f"[{bin_edges[i]:.1f}, {bin_edges[i+1]:.1f})"
            result += f"{class_label:<20} {freq_abs:<12} {freq_rel:<12.4f} {cum_freq:<15} {cum_rel:<15.4f}\n"
        
        result += f"\nTotale: {len(data)} osservazioni\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)
        
        # Crea istogramma
        self.clear_stats_graph()
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(data, bins=n_classes, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title(f'Istogramma - {variable}', fontsize=14, fontweight='bold')
        ax.set_xlabel(variable)
        ax.set_ylabel('Frequenza')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.stats_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_position_indices(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Calcola indici di posizione
        mean_val = data.mean()
        median_val = data.median()
        mode_val = data.mode()
        
        result = f"INDICI DI POSIZIONE - {variable}\n"
        result += "=" * 50 + "\n\n"
        result += f"Media campionaria:           {mean_val:.4f}\n"
        result += f"Mediana campionaria:         {median_val:.4f}\n"
        
        if not mode_val.empty:
            if len(mode_val) == 1:
                result += f"Moda campionaria:            {mode_val.iloc[0]:.4f}\n"
            else:
                result += f"Mode campionarie:            {', '.join([f'{x:.4f}' for x in mode_val])}\n"
        else:
            result += f"Moda campionaria:            Non presente\n"
        
        result += f"\nNumero di osservazioni:      {len(data)}\n"
        result += f"Valore minimo:               {data.min():.4f}\n"
        result += f"Valore massimo:              {data.max():.4f}\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    def show_variability_indices(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Calcola indici di variabilità
        var_sample = data.var(ddof=1)  # Varianza campionaria (n-1)
        std_sample = data.std(ddof=1)  # Deviazione standard campionaria
        mean_val = data.mean()
        mad = np.mean(np.abs(data - mean_val))  # Scarto medio assoluto
        range_val = data.max() - data.min()  # Ampiezza del campo di variazione
        cv = (std_sample / mean_val) * 100 if mean_val != 0 else 0  # Coefficiente di variazione
        
        result = f"INDICI DI VARIABILITÀ - {variable}\n"
        result += "=" * 50 + "\n\n"
        result += f"Varianza campionaria:        {var_sample:.4f}\n"
        result += f"Deviazione standard camp.:   {std_sample:.4f}\n"
        result += f"Scarto medio assoluto:       {mad:.4f}\n"
        result += f"Ampiezza campo variazione:   {range_val:.4f}\n"
        result += f"Coefficiente di variazione:  {cv:.2f}%\n"
        
        result += f"\nMedia:                       {mean_val:.4f}\n"
        result += f"Numero di osservazioni:      {len(data)}\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    def show_shape_indices(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Calcola indici di forma
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        result = f"INDICI DI FORMA - {variable}\n"
        result += "=" * 50 + "\n\n"
        result += f"Indice di asimmetria:        {skewness:.4f}\n"
        
        if skewness > 0.5:
            result += "  → Distribuzione asimmetrica positiva (coda a destra)\n"
        elif skewness < -0.5:
            result += "  → Distribuzione asimmetrica negativa (coda a sinistra)\n"
        else:
            result += "  → Distribuzione approssimativamente simmetrica\n"
        
        result += f"\nIndice di curtosi:           {kurtosis:.4f}\n"
        
        if kurtosis > 0:
            result += "  → Distribuzione leptocurtica (più piccata della normale)\n"
        elif kurtosis < 0:
            result += "  → Distribuzione platicurtica (più piatta della normale)\n"
        else:
            result += "  → Distribuzione mesocurtica (simile alla normale)\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    def show_boxplot(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Crea box plot
        self.clear_stats_graph()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        box_plot = ax.boxplot(data, patch_artist=True, labels=[variable])
        box_plot['boxes'][0].set_facecolor('lightblue')
        
        ax.set_title(f'Box Plot - {variable}', fontsize=14, fontweight='bold')
        ax.set_ylabel(variable)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.stats_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_quartiles_analysis(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        
        if data is None or data.empty:
            messagebox.showwarning("Attenzione", "Nessun dato numerico valido!")
            return

        # Calcola quartili e outlier
        Q1 = data.quantile(0.25)
        Q2 = data.quantile(0.5)  # Mediana
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        # Outlier
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        # Disuguaglianza di Chebyshev
        mean_val = data.mean()
        std_val = data.std()
        
        result = f"ANALISI QUARTILI E OUTLIER - {variable}\n"
        result += "=" * 60 + "\n\n"
        result += f"Primo quartile (Q1):         {Q1:.4f}\n"
        result += f"Secondo quartile (Q2):       {Q2:.4f} (Mediana)\n"
        result += f"Terzo quartile (Q3):         {Q3:.4f}\n"
        result += f"Differenza interquartile:    {IQR:.4f}\n"
        
        result += f"\nLimiti per outlier:\n"
        result += f"Limite inferiore:            {lower_bound:.4f}\n"
        result += f"Limite superiore:            {upper_bound:.4f}\n"
        result += f"Numero di outlier:           {len(outliers)}\n"
        
        if len(outliers) > 0:
            result += f"Valori outlier:              {', '.join([f'{x:.2f}' for x in outliers.head(10)])}\n"
            if len(outliers) > 10:
                result += f"  ... e altri {len(outliers)-10} valori\n"
        
        result += f"\nDISUGUAGLIANZA DI CHEBYSHEV:\n"
        result += f"Media: {mean_val:.4f}, Deviazione standard: {std_val:.4f}\n"
        
        for k in [1.5, 2, 2.5, 3]:
            lower_cheb = mean_val - k * std_val
            upper_cheb = mean_val + k * std_val
            proportion_theory = 1 - 1/(k**2)
            data_in_interval = len(data[(data >= lower_cheb) & (data <= upper_cheb)])
            proportion_actual = data_in_interval / len(data)
            
            result += f"k={k}: [{lower_cheb:.2f}, {upper_cheb:.2f}] "
            result += f"- Teorico: {proportion_theory:.1%}, Effettivo: {proportion_actual:.1%}\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    def show_scatter_plot(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        var_x = self.bivar_x.get()
        var_y = self.bivar_y.get()
        
        data_x = self.get_numeric_data(var_x)
        data_y = self.get_numeric_data(var_y)
        
        if data_x is None or data_y is None or data_x.empty or data_y.empty:
            messagebox.showwarning("Attenzione", "Dati numerici non validi!")
            return

        # Allinea i dati (stesso indice)
        common_index = data_x.index.intersection(data_y.index)
        data_x = data_x.loc[common_index]
        data_y = data_y.loc[common_index]

        # Crea diagramma a dispersione
        self.clear_bivar_graph()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.scatter(data_x, data_y, alpha=0.6, color='blue')
        ax.set_xlabel(var_x)
        ax.set_ylabel(var_y)
        ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.bivar_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_correlation(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        var_x = self.bivar_x.get()
        var_y = self.bivar_y.get()
        
        data_x = self.get_numeric_data(var_x)
        data_y = self.get_numeric_data(var_y)
        
        if data_x is None or data_y is None or data_x.empty or data_y.empty:
            messagebox.showwarning("Attenzione", "Dati numerici non validi!")
            return

        # Allinea i dati
        common_index = data_x.index.intersection(data_y.index)
        data_x = data_x.loc[common_index]
        data_y = data_y.loc[common_index]

        # Calcola coefficiente di correlazione
        correlation = np.corrcoef(data_x, data_y)[0, 1]
        
        # Test di significatività
        n = len(data_x)
        t_stat = correlation * np.sqrt((n-2)/(1-correlation**2)) if correlation != 1 else float('inf')
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n-2)) if correlation != 1 else 0

        result = f"ANALISI DI CORRELAZIONE\n"
        result += "=" * 50 + "\n\n"
        result += f"Variabile X: {var_x}\n"
        result += f"Variabile Y: {var_y}\n"
        result += f"Numero di osservazioni: {n}\n\n"
        
        result += f"Coefficiente di correlazione di Pearson: {correlation:.4f}\n\n"
        
        # Interpretazione della correlazione
        if abs(correlation) >= 0.8:
            strength = "molto forte"
        elif abs(correlation) >= 0.6:
            strength = "forte"
        elif abs(correlation) >= 0.4:
            strength = "moderata"
        elif abs(correlation) >= 0.2:
            strength = "debole"
        else:
            strength = "molto debole"
        
        direction = "positiva" if correlation > 0 else "negativa"
        result += f"Interpretazione: Correlazione {strength} {direction}\n\n"
        
        result += f"Test di significatività:\n"
        result += f"Statistica t: {t_stat:.4f}\n"
        result += f"P-value: {p_value:.4f}\n"
        result += f"Significativo al 5%: {'Sì' if p_value < 0.05 else 'No'}\n\n"
        
        # Covarianza
        covariance = np.cov(data_x, data_y)[0, 1]
        result += f"Covarianza: {covariance:.4f}\n"
        
        # Coefficiente di determinazione
        r_squared = correlation**2
        result += f"Coefficiente di determinazione (R²): {r_squared:.4f}\n"
        result += f"Varianza spiegata: {r_squared*100:.2f}%\n"

        self.bivar_textbox.delete("1.0", "end")
        self.bivar_textbox.insert("1.0", result)

    def show_regression(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima!")
            return

        var_x = self.bivar_x.get()
        var_y = self.bivar_y.get()
        
        data_x = self.get_numeric_data(var_x)
        data_y = self.get_numeric_data(var_y)
        
        if data_x is None or data_y is None or data_x.empty or data_y.empty:
            messagebox.showwarning("Attenzione", "Dati numerici non validi!")
            return

        # Allinea i dati
        common_index = data_x.index.intersection(data_y.index)
        data_x = data_x.loc[common_index]
        data_y = data_y.loc[common_index]

        # Regressione lineare
        X = data_x.values.reshape(-1, 1)
        y = data_y.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        intercept = model.intercept_
        r_squared = model.score(X, y)
        
        # Predizioni
        y_pred = model.predict(X)
        
        # Residui
        residuals = y - y_pred
        mse = np.mean(residuals**2)
        rmse = np.sqrt(mse)
        
        # Statistiche aggiuntive
        n = len(data_x)
        correlation = np.corrcoef(data_x, data_y)[0, 1]
        
        result = f"REGRESSIONE LINEARE\n"
        result += "=" * 50 + "\n\n"
        result += f"Variabile indipendente (X): {var_x}\n"
        result += f"Variabile dipendente (Y): {var_y}\n"
        result += f"Numero di osservazioni: {n}\n\n"
        
        result += f"EQUAZIONE DELLA RETTA:\n"
        result += f"Y = {intercept:.4f} + {slope:.4f} * X\n\n"
        
        result += f"PARAMETRI:\n"
        result += f"Intercetta (a): {intercept:.4f}\n"
        result += f"Coefficiente angolare (b): {slope:.4f}\n\n"
        
        result += f"BONTÀ DEL MODELLO:\n"
        result += f"Coefficiente di correlazione: {correlation:.4f}\n"
        result += f"Coefficiente di determinazione (R²): {r_squared:.4f}\n"
        result += f"Varianza spiegata: {r_squared*100:.2f}%\n"
        result += f"Errore quadratico medio: {mse:.4f}\n"
        result += f"Radice errore quadratico medio: {rmse:.4f}\n\n"
        
        result += f"INTERPRETAZIONE:\n"
        if slope > 0:
            result += f"Per ogni unità di aumento di {var_x}, {var_y} aumenta di {slope:.4f} unità\n"
        else:
            result += f"Per ogni unità di aumento di {var_x}, {var_y} diminuisce di {abs(slope):.4f} unità\n"

        self.bivar_textbox.delete("1.0", "end")
        self.bivar_textbox.insert("1.0", result)

        # Crea grafico di regressione
        self.clear_bivar_graph()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Grafico principale con retta di regressione
        ax1.scatter(data_x, data_y, alpha=0.6, color='blue', label='Dati')
        ax1.plot(data_x, y_pred, color='red', linewidth=2, label=f'Y = {intercept:.2f} + {slope:.2f}X')
        ax1.set_xlabel(var_x)
        ax1.set_ylabel(var_y)
        ax1.set_title('Regressione Lineare', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Grafico dei residui
        ax2.scatter(y_pred, residuals, alpha=0.6, color='green')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.8)
        ax2.set_xlabel('Valori Predetti')
        ax2.set_ylabel('Residui')
        ax2.set_title('Analisi dei Residui', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.bivar_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_graph_frame(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def clear_stats_graph(self):
        for widget in self.stats_graph_frame.winfo_children():
            widget.destroy()

    def clear_bivar_graph(self):
        for widget in self.bivar_graph_frame.winfo_children():
            widget.destroy()

    # Metodi per i grafici della tab Visualizzazione (mantenuti come prima)
    def plot_incidents_by_province(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        province_counts = self.df['Provincia'].value_counts()
        province_counts.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Numero di Incidenti per Provincia', fontsize=16, fontweight='bold')
        ax.set_xlabel('Provincia')
        ax.set_ylabel('Numero di Incidenti')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_incidents_by_day(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        day_order = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        day_counts = self.df['Giorno_Settimana'].value_counts().reindex(day_order, fill_value=0)
        
        day_counts.plot(kind='bar', ax=ax, color='lightcoral')
        ax.set_title('Numero di Incidenti per Giorno della Settimana', fontsize=16, fontweight='bold')
        ax.set_xlabel('Giorno della Settimana')
        ax.set_ylabel('Numero di Incidenti')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_casualties(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Grafico feriti
        feriti = pd.to_numeric(self.df['Numero_Feriti'], errors='coerce').dropna()
        ax1.hist(feriti, bins=10, color='orange', alpha=0.7, edgecolor='black')
        ax1.set_title('Distribuzione Numero Feriti', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Numero Feriti')
        ax1.set_ylabel('Frequenza')
        
        # Grafico morti
        morti = pd.to_numeric(self.df['Numero_Morti'], errors='coerce').dropna()
        ax2.hist(morti, bins=10, color='red', alpha=0.7, edgecolor='black')
        ax2.set_title('Distribuzione Numero Morti', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Numero Morti')
        ax2.set_ylabel('Frequenza')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_road_type(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        road_counts = self.df['Tipo_Strada'].value_counts()
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        wedges, texts, autotexts = ax.pie(
            road_counts.values, 
            labels=road_counts.index, 
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        ax.set_title('Distribuzione Incidenti per Tipo di Strada', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_speed_distribution(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        speed_data = pd.to_numeric(self.df['Velocita_Media_Stimata'], errors='coerce').dropna()
        
        ax.hist(speed_data, bins=15, color='purple', alpha=0.7, edgecolor='black')
        ax.axvline(speed_data.mean(), color='red', linestyle='--', linewidth=2, 
                  label=f'Media: {speed_data.mean():.1f} km/h')
        ax.set_title('Distribuzione Velocità Media Stimata', fontsize=16, fontweight='bold')
        ax.set_xlabel('Velocità (km/h)')
        ax.set_ylabel('Frequenza')
        ax.legend()
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_time_trend(self):
        if self.df.empty:
            messagebox.showwarning("Attenzione", "Carica dei dati prima di creare i grafici!")
            return

        self.clear_graph_frame()
        
        try:
            # Converti le date
            dates = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce').dropna()
            
            if dates.empty:
                messagebox.showwarning("Attenzione", "Formato data non valido per il trend temporale!")
                return
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Raggruppa per mese
            monthly_counts = dates.dt.to_period('M').value_counts().sort_index()
            
            ax.plot(monthly_counts.index.astype(str), monthly_counts.values, 
                   marker='o', linewidth=2, markersize=6, color='green')
            ax.set_title('Trend Temporale degli Incidenti', fontsize=16, fontweight='bold')
            ax.set_xlabel('Mese')
            ax.set_ylabel('Numero di Incidenti')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione del trend temporale: {str(e)}")

if __name__ == "__main__":
    app = ExcelTableApp()
    app.mainloop()