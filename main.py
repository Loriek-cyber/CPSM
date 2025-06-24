import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tksheet import Sheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
from functools import wraps
from typing import Optional, Tuple, List

warnings.filterwarnings('ignore')

# --- Global Style Configuration ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
sns.set_theme(style="darkgrid", palette="deep")

# Update matplotlib plot styles to match the dark theme
plt.rcParams.update({
    "axes.facecolor": "#2B2B2B",
    "figure.facecolor": "#2B2B2B",
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "text.color": "white",
    "legend.facecolor": "#333333",
})

# --- Decorators ---
def requires_data(func):
    """Decorator to check if data is loaded before executing a function."""
    @wraps(func)
    def wrapper(self: 'ExcelTableApp', *args, **kwargs):
        if self.df.empty:
            messagebox.showwarning("Dati Mancanti", "Caricare o creare dei dati prima di eseguire questa operazione.")
            return None
        return func(self, *args, **kwargs)
    return wrapper


class ExcelTableApp(ctk.CTk):
    # --- Constants ---
    EXPECTED_COLUMNS = [
        "Data_Ora_Incidente", "Provincia", "Giorno_Settimana",
        "Tipo_Strada", "Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"
    ]
    NUMERIC_COLUMNS = ["Numero_Feriti", "Numero_Morti", "Velocita_Media_Stimata"]
    WEEKDAY_ORDER = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

    def __init__(self):
        super().__init__()
        self.title("Analisi Statistiche Dati Incidenti Stradali")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # DataFrame per memorizzare i dati
        self.df = pd.DataFrame()
        
        # --- Main UI Structure ---
        self.setup_ui()

    def setup_ui(self) -> None:
        """Initializes the main UI components, including the tab view."""
        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("Dati")
        self.tab_view.add("Grafici")
        self.tab_view.add("Analisi Statistiche")
        self.tab_view.add("Analisi Bivariata")

        # Setup each tab
        self.setup_data_tab(self.tab_view.tab("Dati"))
        self.setup_visual_tab(self.tab_view.tab("Grafici"))
        self.setup_stats_tab(self.tab_view.tab("Analisi Statistiche"))
        self.setup_bivariate_tab(self.tab_view.tab("Analisi Bivariata"))

    def setup_data_tab(self, tab: ctk.CTkFrame) -> None:
        """Sets up the UI for the 'Dati' tab."""
        # Frame per i pulsanti
        buttons_frame = ctk.CTkFrame(tab)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        # Pulsanti per operazioni sui dati
        upload_btn = ctk.CTkButton(buttons_frame, text="Carica CSV", command=self.upload_csv)
        upload_btn.pack(side="left", padx=5, pady=5)

        save_btn = ctk.CTkButton(buttons_frame, text="Salva CSV", command=self.save_csv)
        save_btn.pack(side="left", padx=5, pady=5)

        add_row_btn = ctk.CTkButton(buttons_frame, text="Aggiungi Riga", command=self.add_row)
        add_row_btn.pack(side="left", padx=5, pady=5)

        delete_row_btn = ctk.CTkButton(buttons_frame, text="Elimina Riga", command=self.delete_row)
        delete_row_btn.pack(side="left", padx=5, pady=5)

        create_sample_btn = ctk.CTkButton(buttons_frame, text="Crea Dati Esempio", command=self.create_sample_data)
        create_sample_btn.pack(side="left", padx=5, pady=5)

        # Tabella modificabile
        self.sheet = Sheet(
            tab,
            data=[[]], 
            headers=self.EXPECTED_COLUMNS,
            width=1300, 
            height=600
        )
        
        # Abilita tutte le funzionalità di modifica
        self.sheet.enable_bindings([
            "single_select", "row_select", "column_select", "drag_select",
            "column_width_resize", "double_click_column_resize",
            "row_height_resize",
            "arrowkeys", "right_click_popup_menu", "rc_select",
            "rc_insert_column", "rc_delete_column", "rc_insert_row", "rc_delete_row",
            "copy", "cut", "paste", "delete", "undo", "edit_cell"
        ])
        
        self.sheet.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.sheet.bind("<<SheetModified>>", self.on_sheet_modified)

    def setup_visual_tab(self, tab: ctk.CTkFrame) -> None:
        """Sets up the UI for the 'Grafici' tab."""
        # Frame per i controlli dei grafici
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=10, pady=10)

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
            btn = ctk.CTkButton(controls_frame, text=text, command=command)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")
        
        for i in range(3):
            controls_frame.grid_columnconfigure(i, weight=1)

        # Frame per i grafici
        self.graph_frame = ctk.CTkFrame(tab)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial label
        self.no_data_label = ctk.CTkLabel(
            self.graph_frame, 
            text="Carica dei dati per visualizzare i grafici",
            font=ctk.CTkFont(size=16)
        )
        self.no_data_label.pack(expand=True)

    def setup_stats_tab(self, tab: ctk.CTkFrame) -> None:
        """Sets up the UI for the 'Analisi Statistiche' tab."""
        # Frame di controllo
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Selezione variabile
        ctk.CTkLabel(control_frame, text="Seleziona Variabile:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        self.stats_var = ctk.StringVar(value=self.NUMERIC_COLUMNS[0])
        self.stats_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=self.NUMERIC_COLUMNS,
            variable=self.stats_var,
            width=200
        )
        self.stats_dropdown.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="w")

        # Pulsanti per analisi
        stats_buttons = [
            ("Tabelle Frequenze", self.show_frequency_tables), ("Indici Posizione", self.show_position_indices),
            ("Indici Variabilità", self.show_variability_indices), ("Indici Forma", self.show_shape_indices),
            ("Box Plot", self.show_boxplot), ("Quartili e Outlier", self.show_quartiles_analysis)
        ]

        for i, (text, command) in enumerate(stats_buttons):
            btn = ctk.CTkButton(control_frame, text=text, command=command)
            btn.grid(row=1, column=i, padx=5, pady=5, sticky="ew")
        
        control_frame.grid_columnconfigure(list(range(len(stats_buttons))), weight=1)

        # Frame per risultati statistici
        self.stats_result_frame = ctk.CTkFrame(tab)
        self.stats_result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.stats_result_frame.grid_columnconfigure(0, weight=1)
        self.stats_result_frame.grid_columnconfigure(1, weight=1)
        self.stats_result_frame.grid_rowconfigure(0, weight=1)

        # Textbox per risultati
        self.stats_textbox = ctk.CTkTextbox(self.stats_result_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.stats_textbox.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="nsew")

        # Frame per grafici statistici
        self.stats_graph_frame = ctk.CTkFrame(self.stats_result_frame)
        self.stats_graph_frame.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="nsew")

    def setup_bivariate_tab(self, tab: ctk.CTkFrame) -> None:
        """Sets up the UI for the 'Analisi Bivariata' tab."""
        # Frame di controllo
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Selezione variabili
        ctk.CTkLabel(control_frame, text="Variabile X:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        self.bivar_x = ctk.StringVar(value=self.NUMERIC_COLUMNS[0])
        self.bivar_x_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=self.NUMERIC_COLUMNS,
            variable=self.bivar_x,
            width=150
        )
        self.bivar_x_dropdown.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="w")

        ctk.CTkLabel(control_frame, text="Variabile Y:", font=ctk.CTkFont(size=14)).grid(row=0, column=2, padx=(10, 5), pady=10, sticky="w")
        
        self.bivar_y = ctk.StringVar(value=self.NUMERIC_COLUMNS[2])
        self.bivar_y_dropdown = ctk.CTkComboBox(
            control_frame, 
            values=self.NUMERIC_COLUMNS,
            variable=self.bivar_y,
            width=150
        )
        self.bivar_y_dropdown.grid(row=0, column=3, padx=(0, 20), pady=10, sticky="w")

        # Pulsanti analisi bivariata
        bivar_buttons = [
            ("Diagramma Dispersione", self.show_scatter_plot), ("Correlazione", self.show_correlation),
            ("Regressione Lineare", self.show_regression)
        ]

        for i, (text, command) in enumerate(bivar_buttons):
            btn = ctk.CTkButton(control_frame, text=text, command=command)
            btn.grid(row=1, column=i, columnspan=2, padx=5, pady=5, sticky="ew")

        control_frame.grid_columnconfigure(list(range(4)), weight=1)

        # Frame per risultati bivariati
        self.bivar_result_frame = ctk.CTkFrame(tab)
        self.bivar_result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.bivar_result_frame.grid_columnconfigure(0, weight=1)
        self.bivar_result_frame.grid_columnconfigure(1, weight=1)
        self.bivar_result_frame.grid_rowconfigure(0, weight=1)

        # Textbox per risultati
        self.bivar_textbox = ctk.CTkTextbox(self.bivar_result_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.bivar_textbox.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="nsew")

        # Frame per grafici bivariati
        self.bivar_graph_frame = ctk.CTkFrame(self.bivar_result_frame)
        self.bivar_graph_frame.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="nsew")

    def upload_csv(self) -> None:
        """Opens a file dialog to load a CSV file into the DataFrame and sheet."""
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

    @requires_data
    def save_csv(self) -> None:
        """Opens a file dialog to save the current DataFrame to a CSV file."""
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

    def add_row(self) -> None:
        """Adds a new empty row to the sheet."""
        self.sheet.insert_row()
        self.update_df_from_sheet()

    @requires_data
    def delete_row(self) -> None:
        """Deletes the selected row(s) from the sheet."""
        selected = self.sheet.get_selected_rows()
        if selected:
            for row in sorted(selected, reverse=True):
                self.sheet.delete_row(row)
            self.update_df_from_sheet()
        else:
            messagebox.showwarning("Attenzione", "Seleziona una riga da eliminare!")

    def create_sample_data(self) -> None:
        """Generates a realistic sample dataset of 100 incidents."""
        try:
            provinces = ["Milano", "Roma", "Napoli", "Torino", "Palermo", "Genova", "Bologna", "Firenze", "Venezia", "Bari"]
            road_types = ["Urbana", "Extraurbana", "Autostrada"]
            
            np.random.seed(42)
            sample_data = []
            start_date = datetime.now() - timedelta(days=365)

            for _ in range(100):
                random_date = start_date + timedelta(
                    days=np.random.randint(0, 365),
                    hours=np.random.randint(0, 24),
                    minutes=np.random.randint(0, 60)
                )
                
                feriti = np.random.poisson(2)
                morti = np.random.binomial(feriti, 0.1) if feriti > 0 else 0
                
                road_type = np.random.choice(road_types)
                if road_type == "Urbana":
                    velocita = np.random.normal(50, 10)
                elif road_type == "Extraurbana":
                    velocita = np.random.normal(90, 15)
                else:  # Autostrada
                    velocita = np.random.normal(120, 20)
                velocita = round(max(20, min(180, velocita)), 1)

                sample_data.append([
                    random_date.strftime('%Y-%m-%d %H:%M:%S'),
                    np.random.choice(provinces),
                    self.WEEKDAY_ORDER[random_date.weekday()],
                    road_type,
                    feriti,
                    morti,
                    velocita
                ])
            
            self.df = pd.DataFrame(sample_data, columns=self.EXPECTED_COLUMNS)
            self.update_sheet_from_df()
            messagebox.showinfo("Successo", "100 righe di dati di esempio sono state create.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione dei dati di esempio: {e}")

    def update_sheet_from_df(self) -> None:
        """Populates the tksheet with data from the DataFrame."""
        if not self.df.empty:
            self.sheet.set_sheet_data(self.df.values.tolist())
            self.sheet.headers(list(self.df.columns))

    def update_df_from_sheet(self) -> None:
        """Updates the DataFrame with the current data from the tksheet."""
        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()
        if data and headers:
            filtered_data = [row for row in data if any(str(cell).strip() for cell in row)]
            self.df = pd.DataFrame(filtered_data, columns=headers)

    def on_sheet_modified(self, event: tk.Event) -> None:
        """Callback function for when the sheet is modified."""
        self.update_df_from_sheet()

    def get_numeric_data(self, column_name: str) -> Optional[pd.Series]:
        """Extracts numeric data from a DataFrame column, handling errors."""
        return pd.to_numeric(self.df[column_name], errors='coerce').dropna()

    # --- Helper Methods for Analysis ---

    def _get_univariate_data(self) -> Tuple[Optional[str], Optional[pd.Series]]:
        """Gets the selected variable and its numeric data for univariate analysis."""
        variable = self.stats_var.get()
        data = self.get_numeric_data(variable)
        if data is None or data.empty:
            messagebox.showwarning("Dati non validi", f"Nessun dato numerico valido per '{variable}'.")
            return None, None
        return variable, data

    def _get_bivariate_data(self) -> Tuple[Optional[str], Optional[pd.Series], Optional[str], Optional[pd.Series]]:
        """Gets the selected variables and their numeric data for bivariate analysis."""
        var_x, var_y = self.bivar_x.get(), self.bivar_y.get()
        data_x, data_y = self.get_numeric_data(var_x), self.get_numeric_data(var_y)

        if data_x is None or data_y is None or data_x.empty or data_y.empty:
            messagebox.showwarning("Dati non validi", "Dati numerici non validi per una o entrambe le variabili.")
            return None, None, None, None
        
        common_index = data_x.index.intersection(data_y.index)
        return var_x, data_x.loc[common_index], var_y, data_y.loc[common_index]

    def _display_figure(self, fig: plt.Figure, parent_frame: ctk.CTkFrame) -> None:
        """Clears a frame and displays a matplotlib figure in it."""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- Statistical Analysis Methods ---

    @requires_data
    def show_frequency_tables(self) -> None:
        """Calculates and displays frequency tables for the selected variable."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Costruisci le classi
        n_classes = min(10, int(np.sqrt(len(data))))
        hist, bin_edges = np.histogram(data, bins=n_classes)
        
        result = f"--- TABELLE FREQUENZE: {variable} ---\n"
        result += "=" * 75 + "\n"
        result += f"{'Classe':<20} {'Freq. Ass.':>12} {'Freq. Rel.':>12} {'Freq. Ass. Cum.':>15} {'Freq. Rel. Cum.':>15}\n"
        result += "-" * 75 + "\n"
        
        cum_freq = 0
        cum_rel = 0
        
        for i in range(len(hist)):
            freq_abs = hist[i]
            freq_rel = freq_abs / len(data)
            cum_freq += freq_abs
            cum_rel += freq_rel
            
            class_label = f"[{bin_edges[i]:.1f}, {bin_edges[i+1]:.1f})"
            result += f"{class_label:<20} {freq_abs:>12} {freq_rel:>12.4f} {cum_freq:>15} {cum_rel:>15.4f}\n"
        
        result += f"\nTotale: {len(data)} osservazioni\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(data, bins=n_classes, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title(f'Istogramma - {variable}', fontsize=14, fontweight='bold')
        ax.set_xlabel(variable)
        ax.set_ylabel('Frequenza')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._display_figure(fig, self.stats_graph_frame)

    @requires_data
    def show_position_indices(self) -> None:
        """Calculates and displays position indices for the selected variable."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Calcola indici di posizione
        mean_val = data.mean()
        median_val = data.median()
        mode_val = data.mode()
        
        result = f"--- INDICI DI POSIZIONE: {variable} ---\n"
        result += "=" * 50 + "\n\n"
        result += f"{'Media campionaria:':<28} {mean_val:>10.4f}\n"
        result += f"{'Mediana campionaria:':<28} {median_val:>10.4f}\n"
        
        if not mode_val.empty:
            if len(mode_val) == 1:
                result += f"{'Moda campionaria:':<28} {mode_val.iloc[0]:>10.4f}\n"
            else:
                result += f"{'Mode campionarie:':<28} {', '.join([f'{x:.2f}' for x in mode_val])}\n"
        else:
            result += f"{'Moda campionaria:':<28} {'Non presente':>10}\n"
        
        result += "\n" + "-"*50 + "\n"
        result += f"{'Numero di osservazioni:':<28} {len(data):>10}\n"
        result += f"{'Valore minimo:':<28} {data.min():>10.4f}\n"
        result += f"{'Valore massimo:':<28} {data.max():>10.4f}\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    @requires_data
    def show_variability_indices(self) -> None:
        """Calculates and displays variability indices."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Calcola indici di variabilità
        var_sample = data.var(ddof=1)
        std_sample = data.std(ddof=1)
        mean_val = data.mean()
        mad = np.mean(np.abs(data - mean_val))
        range_val = data.max() - data.min()
        cv = (std_sample / mean_val) * 100 if mean_val != 0 else 0
        
        result = f"--- INDICI DI VARIABILITÀ: {variable} ---\n"
        result += "=" * 50 + "\n\n"
        result += f"{'Varianza campionaria:':<28} {var_sample:>10.4f}\n"
        result += f"{'Deviazione standard camp.:':<28} {std_sample:>10.4f}\n"
        result += f"{'Scarto medio assoluto:':<28} {mad:>10.4f}\n"
        result += f"{'Ampiezza campo variazione:':<28} {range_val:>10.4f}\n"
        result += f"{'Coefficiente di variazione:':<28} {cv:>9.2f}%\n"
        
        result += "\n" + "-"*50 + "\n"
        result += f"{'Media:':<28} {mean_val:>10.4f}\n"
        result += f"{'Numero di osservazioni:':<28} {len(data):>10}\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    @requires_data
    def show_shape_indices(self) -> None:
        """Calculates and displays shape indices (skewness, kurtosis)."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Calcola indici di forma
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        result = f"--- INDICI DI FORMA: {variable} ---\n"
        result += "=" * 50 + "\n\n"
        result += f"{'Indice di asimmetria:':<28} {skewness:>10.4f}\n"
        
        if skewness > 0.5:
            result += "  → Distribuzione asimmetrica positiva (coda a destra)\n"
        elif skewness < -0.5:
            result += "  → Distribuzione asimmetrica negativa (coda a sinistra)\n"
        else:
            result += "  → Distribuzione approssimativamente simmetrica\n"
        
        result += f"\n{'Indice di curtosi:':<28} {kurtosis:>10.4f}\n"
        
        if kurtosis > 0:
            result += "  → Distribuzione leptocurtica (più piccata della normale)\n"
        elif kurtosis < 0:
            result += "  → Distribuzione platicurtica (più piatta della normale)\n"
        else:
            result += "  → Distribuzione mesocurtica (simile alla normale)\n"
        
        self.stats_textbox.delete("1.0", "end")
        self.stats_textbox.insert("1.0", result)

    @requires_data
    def show_boxplot(self) -> None:
        """Displays a box plot for the selected variable."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Crea box plot
        fig, ax = plt.subplots(figsize=(6, 6))
        
        box_plot = ax.boxplot(data, patch_artist=True, labels=[variable])
        box_plot['boxes'][0].set_facecolor('lightblue')
        
        ax.set_title(f'Box Plot - {variable}', fontsize=14, fontweight='bold')
        ax.set_ylabel(variable)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._display_figure(fig, self.stats_graph_frame)

    @requires_data
    def show_quartiles_analysis(self) -> None:
        """Performs and displays quartile and outlier analysis."""
        variable, data = self._get_univariate_data()
        if data is None:
            return

        # Calcola quartili
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
        
        result = f"--- ANALISI QUARTILI E OUTLIER: {variable} ---\n"
        result += "=" * 60 + "\n\n"
        result += f"{'Primo quartile (Q1):':<28} {Q1:>10.4f}\n"
        result += f"{'Secondo quartile (Q2):':<28} {Q2:>10.4f} (Mediana)\n"
        result += f"{'Terzo quartile (Q3):':<28} {Q3:>10.4f}\n"
        result += f"{'Differenza interquartile:':<28} {IQR:>10.4f}\n"
        
        result += f"\nLimiti per outlier:\n"
        result += f"{'Limite inferiore:':<28} {lower_bound:>10.4f}\n"
        result += f"{'Limite superiore:':<28} {upper_bound:>10.4f}\n"
        result += f"{'Numero di outlier:':<28} {len(outliers):>10}\n"
        
        if len(outliers) > 0:
            result += f"{'Valori outlier (primi 5):':<28} {', '.join([f'{x:.2f}' for x in outliers.head(5)])}\n"
            if len(outliers) > 5:
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

    # --- Bivariate Analysis Methods ---

    @requires_data
    def show_scatter_plot(self) -> None:
        """Displays a scatter plot for the two selected variables."""
        var_x, data_x, var_y, data_y = self._get_bivariate_data()
        if data_x is None:
            return

        # Crea diagramma a dispersione
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(data_x, data_y, alpha=0.6, color='blue')
        ax.set_xlabel(var_x)
        ax.set_ylabel(var_y)
        ax.set_title(f'Diagramma a Dispersione: {var_x} vs {var_y}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._display_figure(fig, self.bivar_graph_frame)

    @requires_data
    def show_correlation(self) -> None:
        """Calculates and displays correlation analysis results."""
        var_x, data_x, var_y, data_y = self._get_bivariate_data()
        if data_x is None:
            return

        # Calcola coefficiente di correlazione
        correlation = np.corrcoef(data_x, data_y)[0, 1]
        
        # Test di significatività
        n = len(data_x)
        t_stat = correlation * np.sqrt((n-2)/(1-correlation**2)) if correlation != 1 else float('inf')
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n-2)) if correlation != 1 else 0

        result = f"--- ANALISI DI CORRELAZIONE ---\n"
        result += "=" * 50 + "\n\n"
        result += f"Variabile X: {var_x}\n"
        result += f"Variabile Y: {var_y}\n"
        result += f"Numero di osservazioni: {n}\n\n"
        
        result += f"{'Coefficiente di Pearson (r):':<35} {correlation:.4f}\n\n"
        
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
        result += f"{'Statistica t:':<35} {t_stat:.4f}\n"
        result += f"{'P-value:':<35} {p_value:.4f}\n"
        result += f"{'Significativo al 5% (p < 0.05):':<35} {'Sì' if p_value < 0.05 else 'No'}\n\n"
        
        # Covarianza
        covariance = np.cov(data_x, data_y)[0, 1]
        result += f"{'Covarianza:':<35} {covariance:.4f}\n"
        
        # Coefficiente di determinazione
        r_squared = correlation**2
        result += f"{'Coefficiente di determinazione (R²):':<35} {r_squared:.4f}\n"
        result += f"{'Varianza spiegata:':<35} {r_squared*100:.2f}%\n"

        self.bivar_textbox.delete("1.0", "end")
        self.bivar_textbox.insert("1.0", result)

    @requires_data
    def show_regression(self) -> None:
        """Performs and displays linear regression analysis."""
        var_x, data_x, var_y, data_y = self._get_bivariate_data()
        if data_x is None:
            return

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
        
        result = f"--- REGRESSIONE LINEARE ---\n"
        result += "=" * 50 + "\n\n"
        result += f"Variabile indipendente (X): {var_x}\n"
        result += f"Variabile dipendente (Y): {var_y}\n"
        result += f"Numero di osservazioni: {n}\n\n"
        
        result += f"EQUAZIONE DELLA RETTA:\n"
        result += f"Y = {intercept:.4f} + {slope:.4f} * X\n\n"
        
        result += f"PARAMETRI:\n"
        result += f"{'Intercetta (a):':<35} {intercept:.4f}\n"
        result += f"{'Coefficiente angolare (b):':<35} {slope:.4f}\n\n"
        
        result += f"BONTÀ DEL MODELLO:\n"
        result += f"{'Coefficiente di correlazione (r):':<35} {correlation:.4f}\n"
        result += f"{'Coefficiente di determinazione (R²):':<35} {r_squared:.4f}\n"
        result += f"{'Varianza spiegata:':<35} {r_squared*100:.2f}%\n"
        result += f"{'Errore quadratico medio (MSE):':<35} {mse:.4f}\n"
        result += f"{'Radice errore quadratico medio (RMSE):':<35} {rmse:.4f}\n\n"
        
        result += f"INTERPRETAZIONE:\n"
        if slope > 0:
            result += f"Per ogni unità di aumento di {var_x}, {var_y} aumenta di {slope:.4f} unità\n"
        else:
            result += f"Per ogni unità di aumento di {var_x}, {var_y} diminuisce di {abs(slope):.4f} unità\n"

        self.bivar_textbox.delete("1.0", "end")
        self.bivar_textbox.insert("1.0", result)

        # Crea grafico di regressione
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
        self._display_figure(fig, self.bivar_graph_frame)

    # --- Visualization Tab Plotting Methods ---

    @requires_data
    def plot_incidents_by_province(self) -> None:
        """Plots the number of incidents per province."""
        fig, ax = plt.subplots(figsize=(10, 6))
        province_counts = self.df['Provincia'].value_counts()
        sns.barplot(x=province_counts.index, y=province_counts.values, ax=ax)
        ax.set_title('Numero di Incidenti per Provincia', fontsize=16, fontweight='bold')
        ax.set_xlabel('Provincia')
        ax.set_ylabel('Numero di Incidenti')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        self._display_figure(fig, self.graph_frame)

    @requires_data
    def plot_incidents_by_day(self) -> None:
        """Plots the number of incidents per day of the week."""
        fig, ax = plt.subplots(figsize=(10, 6))
        day_counts = self.df['Giorno_Settimana'].value_counts().reindex(self.WEEKDAY_ORDER, fill_value=0)
        sns.barplot(x=day_counts.index, y=day_counts.values, ax=ax, palette='viridis')
        ax.set_title('Numero di Incidenti per Giorno della Settimana', fontsize=16, fontweight='bold')
        ax.set_xlabel('Giorno della Settimana')
        ax.set_ylabel('Numero di Incidenti')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        self._display_figure(fig, self.graph_frame)

    @requires_data
    def plot_casualties(self) -> None:
        """Plots histograms for the number of injured and deceased."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        feriti = pd.to_numeric(self.df['Numero_Feriti'], errors='coerce').dropna()
        sns.histplot(feriti, bins=10, ax=ax1, kde=True, color='orange')
        ax1.set_title('Distribuzione Numero Feriti', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Numero Feriti')
        
        morti = pd.to_numeric(self.df['Numero_Morti'], errors='coerce').dropna()
        sns.histplot(morti, bins=max(1, morti.nunique()), ax=ax2, kde=True, color='red')
        ax2.set_title('Distribuzione Numero Morti', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Numero Morti')
        plt.tight_layout()
        self._display_figure(fig, self.graph_frame)

    @requires_data
    def plot_road_type(self) -> None:
        """Plots a pie chart for incident distribution by road type."""
        fig, ax = plt.subplots(figsize=(8, 8))
        road_counts = self.df['Tipo_Strada'].value_counts()
        ax.pie(road_counts, labels=road_counts.index, autopct='%1.1f%%', startangle=140,
               wedgeprops={'edgecolor': 'white', 'linewidth': 1})
        ax.set_title('Distribuzione Incidenti per Tipo di Strada', fontsize=16, fontweight='bold')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        self._display_figure(fig, self.graph_frame)

    @requires_data
    def plot_speed_distribution(self) -> None:
        """Plots a histogram for the estimated average speed."""
        fig, ax = plt.subplots(figsize=(10, 6))
        speed_data = pd.to_numeric(self.df['Velocita_Media_Stimata'], errors='coerce').dropna()
        sns.histplot(speed_data, bins=20, ax=ax, kde=True, color='purple')
        ax.axvline(speed_data.mean(), color='red', linestyle='--', linewidth=2, 
                  label=f'Media: {speed_data.mean():.1f} km/h')
        ax.set_title('Distribuzione Velocità Media Stimata', fontsize=16, fontweight='bold')
        ax.set_xlabel('Velocità (km/h)')
        ax.set_ylabel('Frequenza')
        ax.legend()
        plt.tight_layout()
        self._display_figure(fig, self.graph_frame)

    @requires_data
    def plot_time_trend(self) -> None:
        """Plots the monthly trend of incidents over time."""
        try:
            # Converti le date
            dates = pd.to_datetime(self.df['Data_Ora_Incidente'], errors='coerce').dropna()
            
            if dates.empty:
                messagebox.showwarning("Attenzione", "Formato data non valido per il trend temporale!")
                return
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            monthly_counts = dates.dt.to_period('M').value_counts().sort_index()
            monthly_counts.plot(kind='line', ax=ax, marker='o', style='-g',
                                title='Trend Temporale degli Incidenti')
            ax.set_title('Trend Temporale degli Incidenti', fontsize=16, fontweight='bold')
            ax.set_xlabel('Mese')
            ax.set_ylabel('Numero di Incidenti')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            self._display_figure(fig, self.graph_frame)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione del trend temporale: {str(e)}")

if __name__ == "__main__":
    app = ExcelTableApp()
    app.mainloop()