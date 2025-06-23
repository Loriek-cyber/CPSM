import pandas as pd
import customtkinter as ctk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Funzione per caricare il CSV
def carica_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        return df
    return None

# Funzioni per i grafici
def grafico_incidenti_per_provincia(df):
    counts = df['Provincia'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='bar', ax=ax, color="#3B8ED0")
    ax.set_title('Incidenti per Provincia')
    ax.set_xlabel('Provincia')
    ax.set_ylabel('Numero Incidenti')
    plt.tight_layout()
    return fig

def grafico_incidenti_per_giorno(df):
    counts = df['Giorno_Settimana'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='bar', ax=ax, color="#3B8ED0")
    ax.set_title('Incidenti per Giorno della Settimana')
    ax.set_xlabel('Giorno della Settimana')
    ax.set_ylabel('Numero Incidenti')
    plt.tight_layout()
    return fig

def grafico_tipo_strada(df):
    counts = df['Tipo_Strada'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_title('Distribuzione Tipo Strada')
    ax.set_ylabel('')
    plt.tight_layout()
    return fig

def grafico_feriti_morti(df):
    fig, ax = plt.subplots()
    df[['Numero_Feriti', 'Numero_Morti']].sum().plot(kind='bar', ax=ax, color=["#3B8ED0", "#E07A5F"])
    ax.set_title('Totale Feriti e Morti')
    ax.set_ylabel('Numero')
    plt.tight_layout()
    return fig

def grafico_velocita_media(df):
    fig, ax = plt.subplots()
    df['Velocita_Media_Stimata'].plot(kind='hist', bins=20, ax=ax, color="#3B8ED0")
    ax.set_title('Distribuzione Velocità Media Stimata')
    ax.set_xlabel('Velocità Media Stimata')
    ax.set_ylabel('Frequenza')
    plt.tight_layout()
    return fig

GRAFICI = {
    "Incidenti per Provincia": grafico_incidenti_per_provincia,
    "Incidenti per Giorno della Settimana": grafico_incidenti_per_giorno,
    "Distribuzione Tipo Strada": grafico_tipo_strada,
    "Totale Feriti e Morti": grafico_feriti_morti,
    "Distribuzione Velocità Media": grafico_velocita_media,
}

# Funzione per tabelle di frequenza
def tabella_frequenze(df, colonna):
    freq_ass = df[colonna].value_counts().sort_index()
    freq_rel = freq_ass / freq_ass.sum()
    freq_cum = freq_ass.cumsum()
    freq_rel_cum = freq_rel.cumsum()
    tabella = pd.DataFrame({
        'Frequenza Assoluta': freq_ass,
        'Frequenza Relativa': freq_rel,
        'Frequenza Cumulata': freq_cum,
        'Frequenza Relativa Cumulata': freq_rel_cum
    })
    return tabella

# Funzione per indici di posizione
def indici_posizione(df, colonna):
    media = df[colonna].mean()
    mediana = df[colonna].median()
    moda = df[colonna].mode().iloc[0] if not df[colonna].mode().empty else np.nan
    return {'Media': media, 'Mediana': mediana, 'Moda': moda}

# Funzione per indici di variabilità
def indici_varianza(df, colonna):
    varianza = df[colonna].var()
    std = df[colonna].std()
    scarto_medio = df[colonna].mad()
    ampiezza = df[colonna].max() - df[colonna].min()
    coeff_var = std / df[colonna].mean() if df[colonna].mean() != 0 else np.nan
    return {
        'Varianza': varianza,
        'Deviazione Standard': std,
        'Scarto Medio Assoluto': scarto_medio,
        'Ampiezza': ampiezza,
        'Coeff. di Variazione': coeff_var
    }

# Funzione per indici di forma
def indici_forma(df, colonna):
    skew = df[colonna].skew()
    kurt = df[colonna].kurtosis()
    return {'Asimmetria': skew, 'Curtosi': kurt}

# Quartili e boxplot
def boxplot_quartili(df, colonna):
    quartili = df[colonna].quantile([0.25, 0.5, 0.75])
    fig, ax = plt.subplots()
    ax.boxplot(df[colonna].dropna(), vert=False, patch_artist=True)
    ax.set_title(f'Boxplot di {colonna}')
    return fig, quartili

# Intervalli rappresentativi
def intervalli_rappresentativi(df, colonna):
    q1 = df[colonna].quantile(0.25)
    q3 = df[colonna].quantile(0.75)
    iqr = q3 - q1
    media = df[colonna].mean()
    std = df[colonna].std()
    chebyshev = (media - 2*std, media + 2*std)
    return {'Intervallo Quartili': (q1, q3), 'Chebyshev (±2σ)': chebyshev}

# Dati bivariati: scatter, correlazione, regressione
def scatter_correlazione(df, x, y):
    fig, ax = plt.subplots()
    ax.scatter(df[x], df[y], alpha=0.6)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f'Scatter: {x} vs {y}')
    # Regressione
    if df[x].dtype != 'O' and df[y].dtype != 'O':
        slope, intercept, r_value, _, _ = stats.linregress(df[x], df[y])
        ax.plot(df[x], intercept + slope*df[x], color='red')
        correlazione = r_value
    else:
        correlazione = np.nan
    return fig, correlazione

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisi Incidenti Stradali")
        self.geometry("800x500")
        self.df = None

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.logo = ctk.CTkLabel(self.sidebar, text="CPSM", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=(20, 10))

        self.tabview = ctk.CTkTabview(self, width=600)
        self.tabview.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.tabview.add("Caricamento")
        self.tabview.add("Grafici")
        self.tabview.add("Info")
        self.tabview.add("Statistica")

        # Caricamento Tab
        self.btn_carica = ctk.CTkButton(self.tabview.tab("Caricamento"), text="Carica CSV", command=self.carica)
        self.btn_carica.pack(pady=30)
        self.label_file = ctk.CTkLabel(self.tabview.tab("Caricamento"), text="Nessun file caricato")
        self.label_file.pack()

        # Grafici Tab
        self.combo = ctk.CTkComboBox(self.tabview.tab("Grafici"), values=list(GRAFICI.keys()), state="readonly")
        self.combo.pack(pady=10)
        self.btn_mostra = ctk.CTkButton(self.tabview.tab("Grafici"), text="Mostra Grafico", command=self.mostra_grafico, state="disabled")
        self.btn_mostra.pack(pady=10)
        self.canvas_frame = ctk.CTkFrame(self.tabview.tab("Grafici"))
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Info Tab
        info_text = (
            "Analisi Incidenti Stradali\n"
            "Carica un file CSV e visualizza i grafici statistici.\n"
            "Sviluppato con CustomTkinter."
        )
        self.info_label = ctk.CTkLabel(self.tabview.tab("Info"), text=info_text, justify="left")
        self.info_label.pack(padx=10, pady=10)

        # Statistica Tab
        self.stat_col_combo = ctk.CTkComboBox(self.tabview.tab("Statistica"), values=[], state="readonly")
        self.stat_col_combo.pack(pady=10)
        self.btn_stat = ctk.CTkButton(self.tabview.tab("Statistica"), text="Calcola Statistiche", command=self.mostra_statistiche, state="disabled")
        self.btn_stat.pack(pady=10)
        self.stat_text = ctk.CTkTextbox(self.tabview.tab("Statistica"), height=200)
        self.stat_text.pack(fill="both", expand=True, padx=10, pady=10)

    def carica(self):
        self.df = carica_csv()
        if self.df is not None:
            self.label_file.configure(text="File caricato correttamente!")
            self.btn_mostra.configure(state="normal")
            # Aggiorna colonne disponibili per la statistica
            numeriche = self.df.select_dtypes(include=np.number).columns.tolist()
            self.stat_col_combo.configure(values=numeriche)
            self.btn_stat.configure(state="normal")
        else:
            self.label_file.configure(text="Nessun file caricato")
            self.btn_mostra.configure(state="disabled")
            self.btn_stat.configure(state="disabled")

    def mostra_grafico(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        if self.df is not None and self.combo.get():
            fig = GRAFICI[self.combo.get()](self.df)
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def mostra_statistiche(self):
        col = self.stat_col_combo.get()
        if col and self.df is not None:
            pos = indici_posizione(self.df, col)
            var = indici_varianza(self.df, col)
            forma = indici_forma(self.df, col)
            interv = intervalli_rappresentativi(self.df, col)
            self.stat_text.delete("0.0", "end")
            self.stat_text.insert("end", f"Indici di posizione:\n{pos}\n\n")
            self.stat_text.insert("end", f"Indici di variabilità:\n{var}\n\n")
            self.stat_text.insert("end", f"Indici di forma:\n{forma}\n\n")
            self.stat_text.insert("end", f"Intervalli rappresentativi:\n{interv}\n\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()