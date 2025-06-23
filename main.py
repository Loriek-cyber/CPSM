import tkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import os

# --- CLASSE BACKEND PER L'ANALISI (Leggermente modificata per il GUI) ---

class AnalisiDatiIncidenti:
    """
    Classe di backend per eseguire le analisi statistiche.
    Restituisce dati e stringhe formattate invece di stampare a console.
    """
    def __init__(self, dataframe):
        self.df = dataframe
        # Prepara le colonne numeriche e categoriali
        self.colonne_numeriche = self.df.select_dtypes(include=np.number).columns.tolist()
        self.colonne_categoriali = self.df.select_dtypes(include=['object', 'category']).columns.tolist()

    def calcola_frequenze(self, colonna):
        if colonna not in self.colonne_categoriali:
            return f"Errore: La colonna '{colonna}' non è di tipo categoriale."
        
        freq_assoluta = self.df[colonna].value_counts()
        freq_relativa = self.df[colonna].value_counts(normalize=True)
        freq_cum_assoluta = freq_assoluta.cumsum()
        freq_cum_relativa = freq_relativa.cumsum()

        tabella = pd.DataFrame({
            'Frequenza Assoluta': freq_assoluta,
            'Frequenza Relativa (%)': freq_relativa * 100,
            'Cumulata Assoluta': freq_cum_assoluta,
            'Cumulata Relativa (%)': freq_cum_relativa * 100
        })
        return f"--- Tabella di Frequenza per '{colonna}' ---\n\n" + tabella.round(2).to_string()

    def calcola_indici_univariati(self, colonna):
        if colonna not in self.colonne_numeriche:
            return f"Errore: La colonna '{colonna}' non è di tipo numerico."
        
        data = self.df[colonna].dropna()
        if data.empty:
            return f"La colonna '{colonna}' non contiene dati validi."
        
        media = data.mean()
        mediana = data.median()
        moda = data.mode().to_list()
        varianza = data.var(ddof=1)
        dev_std = data.std(ddof=1)
        campo_variazione = data.max() - data.min()
        coeff_variazione = (dev_std / media) if media != 0 else float('inf')
        asimmetria = data.skew()
        curtosi = data.kurt()
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        
        output = f"--- Indici Statistici per '{colonna}' ---\n\n"
        output += f">> Indici di Posizione:\n"
        output += f"   - Media Campionaria: {media:.4f}\n"
        output += f"   - Mediana: {mediana:.4f}\n"
        output += f"   - Moda: {moda}\n\n"
        output += f">> Indici di Variabilità:\n"
        output += f"   - Varianza Campionaria: {varianza:.4f}\n"
        output += f"   - Deviazione Standard: {dev_std:.4f}\n"
        output += f"   - Campo di Variazione: {campo_variazione:.4f}\n"
        output += f"   - Coeff. di Variazione: {coeff_variazione:.4f}\n\n"
        output += f">> Indici di Forma:\n"
        output += f"   - Asimmetria: {asimmetria:.4f}\n"
        output += f"   - Curtosi: {curtosi:.4f}\n\n"
        output += f">> Quartili e Intervalli:\n"
        output += f"   - Q1 (25° percentile): {q1:.2f}\n"
        output += f"   - Q3 (75° percentile): {q3:.2f}\n"
        output += f"   - Intervallo Interquartile (IQR): {q3-q1:.2f}\n"
        return output

    def analisi_bivariata(self, var1, var2):
        if var1 not in self.colonne_numeriche or var2 not in self.colonne_numeriche:
            return "Errore: Entrambe le colonne devono essere numeriche."
        
        correlazione = self.df[var1].corr(self.df[var2])
        slope, intercept, r_value, p_value, std_err = linregress(self.df[var1], self.df[var2])
        
        output = f"--- Analisi Bivariata tra '{var1}' e '{var2}' ---\n\n"
        output += f"Coefficiente di Correlazione di Pearson (r): {correlazione:.4f}\n"
        output += "\nRetta di Regressione Stimata:\n"
        output += f"   - Equazione: {var2} = {slope:.4f} * {var1} + {intercept:.4f}\n"
        return output

    def plot_categoriali(self):
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))
        fig.suptitle('Analisi Variabili Categoriali', fontsize=16)
        
        # Grafico a Barre per Provincia
        sns.countplot(y=self.df['Provincia'], ax=axes[0], order=self.df['Provincia'].value_counts().index, palette='crest')
        axes[0].set_title('Numero di Incidenti per Provincia')
        
        # Grafico a Torta per Tipo Strada
        tipo_strada_counts = self.df['Tipo_Strada'].value_counts()
        axes[1].pie(tipo_strada_counts, labels=tipo_strada_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('magma'))
        axes[1].set_title('Distribuzione per Tipo di Strada')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    def plot_numerici(self, colonna):
        if colonna not in self.colonne_numeriche:
            messagebox.showerror("Errore", f"La colonna '{colonna}' non è numerica.")
            return

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f'Analisi della variabile: {colonna}', fontsize=16)
        
        sns.histplot(self.df[colonna], kde=True, ax=axes[0], bins=20)
        axes[0].set_title(f'Istogramma di {colonna}')
        
        sns.boxplot(x=self.df[colonna], ax=axes[1])
        axes[1].set_title(f'Box Plot di {colonna}')

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    def plot_bivariato(self, var1, var2):
        if var1 not in self.colonne_numeriche or var2 not in self.colonne_numeriche:
            messagebox.showerror("Errore", "Entrambe le variabili devono essere numeriche.")
            return

        plt.figure(figsize=(10, 7))
        sns.regplot(x=var1, y=var2, data=self.df, scatter_kws={'alpha':0.5}, line_kws={'color': 'red'})
        plt.title(f'Diagramma a Dispersione e Regressione: {var1} vs {var2}', fontsize=14)
        plt.show()

# --- CLASSE FRONTEND (INTERFACCIA GRAFICA) ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analizzatore Statistico di Incidenti Stradali")
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")

        self.df = None
        self.analyzer = None

        # Crea la struttura a schede (tabs)
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        # Aggiungi le schede
        self.tab_data = self.tab_view.add("1. Carica/Genera Dati")
        self.tab_uni = self.tab_view.add("2. Analisi Univariata")
        self.tab_bi = self.tab_view.add("3. Analisi Bivariata")
        self.tab_plot = self.tab_view.add("4. Visualizzazione Grafica")
        
        self.crea_tab_data()
        self.crea_tab_uni()
        self.crea_tab_bi()
        self.crea_tab_plot()

    def crea_tab_data(self):
        # Frame per generazione
        gen_frame = ctk.CTkFrame(self.tab_data)
        gen_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(gen_frame, text="Numero righe da generare:").pack(side="left", padx=5)
        self.entry_righe = ctk.CTkEntry(gen_frame, width=80)
        self.entry_righe.insert(0, "500")
        self.entry_righe.pack(side="left", padx=5)
        ctk.CTkButton(gen_frame, text="Genera e Carica Dati", command=self.generate_and_load_data).pack(side="left", padx=5)

        # Frame per caricamento
        load_frame = ctk.CTkFrame(self.tab_data)
        load_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(load_frame, text="Carica File CSV Esistente", command=self.load_existing_data).pack(side="left", padx=5)
        self.status_label = ctk.CTkLabel(load_frame, text="Nessun dato caricato.", text_color="yellow")
        self.status_label.pack(side="left", padx=10)

        # Frame per anteprima dati
        preview_frame = ctk.CTkFrame(self.tab_data)
        preview_frame.pack(pady=10, padx=10, expand=True, fill="both")
        ctk.CTkLabel(preview_frame, text="Anteprima Dati:").pack(anchor="w")
        self.preview_textbox = ctk.CTkTextbox(preview_frame, state="disabled", font=("Courier New", 10))
        self.preview_textbox.pack(expand=True, fill="both", pady=5)
        
    def crea_tab_uni(self):
        # Frame controlli
        control_frame = ctk.CTkFrame(self.tab_uni)
        control_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(control_frame, text="Seleziona Colonna:").pack(side="left", padx=5)
        self.uni_col_menu = ctk.CTkOptionMenu(control_frame, values=["...caricare i dati..."])
        self.uni_col_menu.pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Calcola Frequenze (per categorie)", command=self.run_frequency_analysis).pack(side="left", padx=10)
        ctk.CTkButton(control_frame, text="Calcola Indici Statistici (per numeri)", command=self.run_statistical_indices).pack(side="left", padx=10)
        
        # Textbox risultati
        self.uni_results_textbox = ctk.CTkTextbox(self.tab_uni, state="disabled", font=("Courier New", 11))
        self.uni_results_textbox.pack(pady=10, padx=10, expand=True, fill="both")

    def crea_tab_bi(self):
        # Frame controlli
        control_frame = ctk.CTkFrame(self.tab_bi)
        control_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(control_frame, text="Variabile 1 (X):").pack(side="left", padx=(5,0))
        self.bi_col1_menu = ctk.CTkOptionMenu(control_frame, values=["..."])
        self.bi_col1_menu.pack(side="left", padx=(0,15))
        
        ctk.CTkLabel(control_frame, text="Variabile 2 (Y):").pack(side="left", padx=(5,0))
        self.bi_col2_menu = ctk.CTkOptionMenu(control_frame, values=["..."])
        self.bi_col2_menu.pack(side="left", padx=(0,15))
        
        ctk.CTkButton(control_frame, text="Calcola Correlazione e Regressione", command=self.run_bivariate_analysis).pack(side="left", padx=10)

        # Textbox risultati
        self.bi_results_textbox = ctk.CTkTextbox(self.tab_bi, state="disabled", font=("Courier New", 11))
        self.bi_results_textbox.pack(pady=10, padx=10, expand=True, fill="both")

    def crea_tab_plot(self):
        plot_frame = ctk.CTkFrame(self.tab_plot)
        plot_frame.pack(pady=20, padx=20)
        
        ctk.CTkLabel(plot_frame, text="Genera Grafici (si apriranno in una nuova finestra)", font=("", 14, "bold")).pack(pady=10, padx=10)

        ctk.CTkButton(plot_frame, text="Grafici Variabili Categoriali (Barre e Torta)", command=self.show_categorical_plots).pack(fill="x", pady=5)

        # Frame per grafici numerici
        num_plot_frame = ctk.CTkFrame(plot_frame)
        num_plot_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(num_plot_frame, text="Seleziona variabile numerica:").pack(side="left", padx=5)
        self.plot_num_menu = ctk.CTkOptionMenu(num_plot_frame, values=["..."])
        self.plot_num_menu.pack(side="left", padx=5)
        ctk.CTkButton(num_plot_frame, text="Mostra Istogramma e Box Plot", command=self.show_numerical_plots).pack(side="left", padx=5)
        
        # Frame per grafici bivariati
        bi_plot_frame = ctk.CTkFrame(plot_frame)
        bi_plot_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(bi_plot_frame, text="Var 1 (X):").pack(side="left", padx=5)
        self.plot_bi1_menu = ctk.CTkOptionMenu(bi_plot_frame, values=["..."])
        self.plot_bi1_menu.pack(side="left", padx=5)
        ctk.CTkLabel(bi_plot_frame, text="Var 2 (Y):").pack(side="left", padx=5)
        self.plot_bi2_menu = ctk.CTkOptionMenu(bi_plot_frame, values=["..."])
        self.plot_bi2_menu.pack(side="left", padx=5)
        ctk.CTkButton(bi_plot_frame, text="Mostra Grafico a Dispersione", command=self.show_bivariate_plot).pack(side="left", padx=5)

    def _load_data_into_app(self, filepath):
        try:
            self.df = pd.read_csv(filepath)
            self.df['Data_Ora_Incidente'] = pd.to_datetime(self.df['Data_Ora_Incidente'])
            self.analyzer = AnalisiDatiIncidenti(self.df)
            
            # Aggiorna UI
            self.status_label.configure(text=f"Caricato: {os.path.basename(filepath)} ({len(self.df)} righe)", text_color="lightgreen")
            
            self.preview_textbox.configure(state="normal")
            self.preview_textbox.delete("1.0", "end")
            self.preview_textbox.insert("1.0", self.df.head(10).to_string())
            self.preview_textbox.configure(state="disabled")
            
            self._update_option_menus()
            messagebox.showinfo("Successo", "Dati caricati e analizzatore pronto.")
        except Exception as e:
            messagebox.showerror("Errore di Caricamento", f"Impossibile caricare o processare il file.\nErrore: {e}")
            self.df = None
            self.analyzer = None

    def _update_option_menus(self):
        all_cols = self.df.columns.tolist()
        num_cols = self.analyzer.colonne_numeriche
        
        self.uni_col_menu.configure(values=all_cols)
        self.uni_col_menu.set(all_cols[0] if all_cols else "...")
        
        self.bi_col1_menu.configure(values=num_cols)
        self.bi_col2_menu.configure(values=num_cols)
        if len(num_cols) > 1:
            self.bi_col1_menu.set(num_cols[0])
            self.bi_col2_menu.set(num_cols[1])

        self.plot_num_menu.configure(values=num_cols)
        self.plot_num_menu.set(num_cols[0] if num_cols else "...")
        self.plot_bi1_menu.configure(values=num_cols)
        self.plot_bi2_menu.configure(values=num_cols)
        if len(num_cols) > 1:
            self.plot_bi1_menu.set(num_cols[0])
            self.plot_bi2_menu.set(num_cols[1])


    def generate_and_load_data(self):
        try:
            num_righe = int(self.entry_righe.get())
            if num_righe <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un numero di righe valido (intero e positivo).")
            return
            
        filepath = "incidenti_generati.csv"
        # Funzione di generazione dati
        np.random.seed(42)
        date = pd.to_datetime(pd.date_range(start='2024-01-01', periods=num_righe))
        data = {
            'Data_Ora_Incidente': date,
            'Provincia': np.random.choice(['Milano', 'Roma', 'Napoli', 'Torino', 'Bologna'], num_righe, p=[0.3, 0.2, 0.2, 0.15, 0.15]),
            'Giorno_Settimana': [d.strftime('%A') for d in date],
            'Tipo_Strada': np.random.choice(['Autostrada', 'Strada Statale', 'Strada Comunale'], num_righe),
            'Numero_Feriti': np.random.poisson(lam=1.2, size=num_righe),
            'Numero_Morti': np.random.choice([0, 1, 2], size=num_righe, p=[0.96, 0.03, 0.01]),
            'Velocita_Media_Stimata': np.clip(np.random.normal(loc=80, scale=30, size=num_righe), 20, 160).astype(int)
        }
        df_esempio = pd.DataFrame(data)
        df_esempio.to_csv(filepath, index=False)
        
        self._load_data_into_app(filepath)

    def load_existing_data(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filepath:
            self._load_data_into_app(filepath)

    def run_frequency_analysis(self):
        if not self.analyzer:
            messagebox.showwarning("Attenzione", "Caricare prima i dati.")
            return
        col = self.uni_col_menu.get()
        result = self.analyzer.calcola_frequenze(col)
        self.uni_results_textbox.configure(state="normal")
        self.uni_results_textbox.delete("1.0", "end")
        self.uni_results_textbox.insert("1.0", result)
        self.uni_results_textbox.configure(state="disabled")

    def run_statistical_indices(self):
        if not self.analyzer:
            messagebox.showwarning("Attenzione", "Caricare prima i dati.")
            return
        col = self.uni_col_menu.get()
        result = self.analyzer.calcola_indici_univariati(col)
        self.uni_results_textbox.configure(state="normal")
        self.uni_results_textbox.delete("1.0", "end")
        self.uni_results_textbox.insert("1.0", result)
        self.uni_results_textbox.configure(state="disabled")
    
    def run_bivariate_analysis(self):
        if not self.analyzer:
            messagebox.showwarning("Attenzione", "Caricare prima i dati.")
            return
        var1 = self.bi_col1_menu.get()
        var2 = self.bi_col2_menu.get()
        result = self.analyzer.analisi_bivariata(var1, var2)
        self.bi_results_textbox.configure(state="normal")
        self.bi_results_textbox.delete("1.0", "end")
        self.bi_results_textbox.insert("1.0", result)
        self.bi_results_textbox.configure(state="disabled")
        
    def show_categorical_plots(self):
        if self.analyzer: self.analyzer.plot_categoriali()
        else: messagebox.showwarning("Attenzione", "Caricare prima i dati.")

    def show_numerical_plots(self):
        if self.analyzer: self.analyzer.plot_numerici(self.plot_num_menu.get())
        else: messagebox.showwarning("Attenzione", "Caricare prima i dati.")

    def show_bivariate_plot(self):
        if self.analyzer: self.analyzer.plot_bivariato(self.plot_bi1_menu.get(), self.plot_bi2_menu.get())
        else: messagebox.showwarning("Attenzione", "Caricare prima i dati.")


if __name__ == "__main__":
    app = App()
    app.mainloop()