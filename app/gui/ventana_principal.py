import tkinter as tk
from tkinter import ttk

from app.gui.frame_arriendos import FrameArriendos
from app.gui.frame_categorias import FrameCategorias
from app.gui.frame_clientes import FrameClientes
from app.gui.frame_consultas import FrameConsultas
from app.gui.frame_equipos import FrameEquipos
from app.gui.frame_graficos import FrameGraficos

#Ventana raíz.
#Cada pestaña es un frame independiente.
class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arriendo de equipamiento deportivo")
        self.geometry("1000x650")
        self.minsize(900, 600)

        #contenedor de pestañas.
        self._noteCook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=8, pady=8)

        #Creamos los frames y los guardamos en atributos para poder
        #refrescarlos después desde _al_cambiar_pestana.
        self._frame_graficos = FrameGraficos(self._notebook)

        self._notebook.add(FrameCategorias(self._notebook), text="Categorías")
        self._notebook.add(FrameEquipos(self._notebook), text="Equipos")
        self._notebook.add(FrameClientes(self._notebook), text="Clientes")
        self._notebook.add(FrameArriendos(self._notebook), text="Arriendos")
        self._notebook.add(FrameConsultas(self._notebook), text="Consultas")
        self._notebook.add(self._frame_graficos, text="Estadísticas")

        self._notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)

    #Refresca la pestaña recién abierta para mostrar datos actuales.
    def _al_cambiar_pestana(self, evento=None):

        pestana_actual = self._notebook.nametowidget(self._notebook.select())
        if pestana_actual is self._frame_graficos:
            pestana_actual.actualizar()