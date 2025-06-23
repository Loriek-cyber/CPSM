# =============================================================================
# Software di Analisi Statistica Incidenti Stradali (Modifiche v6.0)
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
from datetime import datetime, timedelta
import collections

# Impostazioni UI
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Software di Analisi Statistica Incidenti Stradali")
        self.geometry("1200x850")
        self.df = None
        self.matplotlib_widgets = []

        # Frame caricamento
        frame = customtkinter.CTkFrame(self)
        frame.pack(fill='x', pady=10)
        self.label_file = customtkinter.CTkLabel(frame, text="Nessun dato caricato.", text_color="gray")
        self.label_file.pack(side='left', padx=10)
        customtkinter.CTkButton(frame, text="Carica CSV", command=self.carica_csv).pack(side='left', padx=5)
        customtkinter.CTkButton(frame, text="Dati Simulati", command=self.carica_dati_esempio).pack(side='left', padx=5)

        # Tabview
        self.tab_view = customtkinter.CTkTabview(self, command=self.on_tab_change)
        self.tab_view.pack(expand=True, fill='both', padx=10, pady=10)
        for name in ["Dati", "Descrittiva", "Bivariata"]:
            self.tab_view.add(name)
        self.setup_tab_dati()
        self.setup_tab_descrittiva()
        self.setup_tab_bivariata()
        self.tab_view.set("Dati")

    def carica_csv(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not fp: return
        df = pd.read_csv(fp, parse_dates=['Data_Ora_Incidente'], dayfirst=True)
        self.inizializza_dati(df, fp.split('/')[-1])

    def carica_dati_esempio(self):
        # genera dati come prima
        records=[]
        end, start = datetime.now(), datetime.now()-timedelta(days=365)
        for _ in range(300):
            dt = start + timedelta(seconds=random.randint(0,int((end-start).total_seconds())))
            records.append({'Data_Ora_Incidente': dt, 'Provincia': random.choice(['Milano','Roma','Napoli']),
                            'Numero_Feriti': random.randint(0,5), 'Numero_Morti': random.randint(0,2)})
        df=pd.DataFrame(records)
        self.inizializza_dati(df, 'Simulati')

    def inizializza_dati(self, df, nome):
        self.df = df.copy()
        self.df.dropna(subset=['Data_Ora_Incidente','Provincia'], inplace=True)
        self.df['Ora']=self.df['Data_Ora_Incidente'].dt.hour
        self.df['Giorno']=self.df['Data_Ora_Incidente'].dt.date
        self.label_file.configure(text=f"Caricati: {nome} ({len(self.df)}) record")
        self.popola_tab_dati()
        self.popola_selettori()

    def setup_tab_dati(self):
        tab = self.tab_view.tab("Dati")
        frame = customtkinter.CTkFrame(tab)
        frame.pack(expand=True, fill='both')
        self.tree = ttk.Treeview(frame, columns=('Data_Ora_Incidente','Provincia','Feriti','Morti','Ora'), show='headings')
        for c in self.tree['columns']:
            self.tree.heading(c, text=c)
        self.tree.pack(expand=True, fill='both')

    def popola_tab_dati(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for _,r in self.df.iterrows():
            self.tree.insert('', 'end', values=(r['Data_Ora_Incidente'].strftime('%Y-%m-%d %H:%M:%S'),r['Provincia'],r['Numero_Feriti'],r['Numero_Morti'],r['Ora']))

    def popola_selettori(self):
        tab=self.tab_view.tab("Descrittiva")
        self.cmb_var.configure(values=list(self.df.select_dtypes(include=[np.number,'datetime64']).columns))
        self.cmb_graf.configure(values=['Barre','Linee','Torta','Area'])
        if not self.cmb_var.get(): self.cmb_var.set(self.cmb_var.values[0])
        self.cmb_graf.set('Barre')
        self.on_tab_change()

    def setup_tab_descrittiva(self):
        tab=self.tab_view.tab("Descrittiva")
        frame=customtkinter.CTkFrame(tab)
        frame.pack(fill='x', pady=5)
        customtkinter.CTkLabel(frame, text="Variabile:").pack(side='left', padx=5)
        self.cmb_var=customtkinter.CTkComboBox(frame, values=[], command=lambda _:self.on_tab_change())
        self.cmb_var.pack(side='left', padx=5)
        customtkinter.CTkLabel(frame, text="Grafico:").pack(side='left', padx=5)
        self.cmb_graf=customtkinter.CTkComboBox(frame, values=[], command=lambda _:self.on_tab_change())
        self.cmb_graf.pack(side='left', padx=5)
        self.frame_res=customtkinter.CTkScrollableFrame(tab)
        self.frame_res.pack(expand=True, fill='both')

    def on_tab_change(self):
        if self.tab_view.get()=="Descrittiva" and self.df is not None:
            self.analisi_descrittiva()
        elif self.tab_view.get()=="Dati":
            self.popola_tab_dati()

    def analisi_descrittiva(self):
        var=self.cmb_var.get(); g=self.cmb_graf.get()
        for w in self.frame_res.winfo_children(): w.destroy()
        data=self.df[var].dropna()
        # Frequenze absolute, relative, cumulative
        if pd.api.types.is_numeric_dtype(data):
            freq=pd.cut(data, bins='sturges').value_counts().sort_index()
        else:
            freq=data.value_counts()
        rel=freq/len(data); cum=freq.cumsum()
        # Tabella
        df_freq=pd.DataFrame({'Assoluta':freq,'Relativa':rel,'Cumulata':cum})
        tree=ttk.Treeview(self.frame_res, columns=df_freq.columns, show='headings')
        for c in df_freq.columns:
            tree.heading(c,text=c)
            tree.column(c,width=100)
        for idx,row in df_freq.iterrows():
            tree.insert('','end',values=([str(idx)]+[f'{row[c]:.3f}' for c in df_freq.columns]))
        tree.pack(fill='x', pady=5)
        # Grafico
        fig,ax=plt.subplots(figsize=(5,3))
        if g=='Barre': freq.plot(kind='bar', ax=ax)
        elif g=='Linee': freq.plot(kind='line', ax=ax)
        elif g=='Torta': freq.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        elif g=='Area': freq.plot(kind='area', ax=ax)
        ax.set_title(f'{g} di {var}')
        canvas=FigureCanvasTkAgg(fig,master=self.frame_res)
        canvas.draw(); canvas.get_tk_widget().pack(expand=True,fill='both')
        plt.close(fig)

    def setup_tab_bivariata(self):
        tab=self.tab_view.tab("Bivariata")
        frame=customtkinter.CTkFrame(tab)
        frame.pack(fill='x', pady=5)
        customtkinter.CTkLabel(frame, text="X:").pack(side='left', padx=5)
        self.cmb_x=customtkinter.CTkComboBox(frame, values=[], command=lambda _:self.on_biv())
        self.cmb_x.pack(side='left', padx=5)
        customtkinter.CTkLabel(frame, text="Y:").pack(side='left', padx=5)
        self.cmb_y=customtkinter.CTkComboBox(frame, values=[], command=lambda _:self.on_biv())
        self.cmb_y.pack(side='left', padx=5)
        self.frame_b=customtkinter.CTkScrollableFrame(tab)
        self.frame_b.pack(expand=True, fill='both')

    def on_biv(self):
        for w in self.frame_b.winfo_children(): w.destroy()
        x=self.cmb_x.get(); y=self.cmb_y.get()
        df2=self.df[[x,y]].dropna()
        if df2.empty: return
        r=df2.corr().iloc[0,1]
        slope,intercept, *_=stats.linregress(df2[x],df2[y])
        customtkinter.CTkLabel(self.frame_b, text=f"r={r:.2f}, y={slope:.2f}x+{intercept:.2f}").pack()
        fig,ax=plt.subplots(figsize=(5,4))
        ax.scatter(df2[x],df2[y]); ax.plot(df2[x],slope*df2[x]+intercept,'r-')
        ax.set_xlabel(x); ax.set_ylabel(y)
        canvas=FigureCanvasTkAgg(fig,master=self.frame_b)
        canvas.draw(); canvas.get_tk_widget().pack(expand=True, fill='both')
        plt.close(fig)

if __name__ == '__main__':
    App().mainloop()
