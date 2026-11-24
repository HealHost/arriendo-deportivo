from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from app.services import estadisticas_service

#Cantidad máxima de equipos en el gráfico.
LIMITE_EQUIPOS = 10

#Frame con dos gráficos, arriendos por categoría y equipos más arrendados.
class FrameGraficos(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._construir_barra()
        self._construir_graficos()
        self.actualizar()

    def _construir_barra(self):
        barra = ttk.Frame(self)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(barra, text="Actualizar gráficos", command=self.actualizar).pack(side="left")

    def _construir_graficos(self):
        contenedor = ttk.Frame(self)
        contenedor.grid(row=1, column=0, sticky="nsew")
        contenedor.columnconfigure((0, 1), weight=1)
        contenedor.rowconfigure(0, weight=1)

        self._figura_categorias = Figure(figsize=(5, 4), dpi=100)
        self._ax_categorias = self._figura_categorias.add_subplot(111)
        self._canvas_categorias = FigureCanvasTkAgg(self._figura_categorias, master=contenedor)
        self._canvas_categorias.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5)

        self._figura_equipos = Figure(figsize=(5, 4), dpi=100)
        self._ax_equipos = self._figura_equipos.add_subplot(111)
        self._canvas_equipos = FigureCanvasTkAgg(self._figura_equipos, master=contenedor)
        self._canvas_equipos.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=5)

    #Pide los datos al servicio y redibuja ambos gráficos.
    def actualizar(self):
        try:
            datos_categorias = estadisticas_service.arriendos_por_categoria()
            datos_equipos = estadisticas_service.equipos_mas_arrendados(LIMITE_EQUIPOS)
        except Exception as error:
            messagebox.showerror("Error al cargar estadísticas", f"No se pudieron leer los datos.\n{error}", parent=self)
            return

        self._dibujar_categorias(datos_categorias)
        self._dibujar_equipos(datos_equipos)

    def _dibujar_categorias(self, datos):
        ax = self._ax_categorias
        ax.clear() 
        ax.set_title("Arriendos por categoría")
        ax.set_ylabel("Operaciones de arriendo")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        if datos:
            nombres = [nombre for nombre, _ in datos]
            valores = [cantidad for _, cantidad in datos]
            ax.bar(nombres, valores, color="#4C72B0")
            ax.tick_params(axis="x", labelrotation=30)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ax.transAxes)

        self._figura_categorias.tight_layout()
        self._canvas_categorias.draw()

    def _dibujar_equipos(self, datos):
        ax = self._ax_equipos
        ax.clear()
        ax.set_title(f"Top {LIMITE_EQUIPOS} equipos más arrendados")
        ax.set_xlabel("Operaciones de arriendo")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if datos:
            nombres = [nombre for nombre, _ in datos]
            valores = [total for _, total in datos]
            ax.barh(nombres, valores, color="#55A868")
            ax.invert_yaxis()
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ax.transAxes)

        self._figura_equipos.tight_layout()
        self._canvas_equipos.draw()
