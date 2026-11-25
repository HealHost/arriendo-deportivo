from tkinter import messagebox, ttk
from app.services import consulta_service
from app.utils.excepciones import ErrorSistema


class FrameConsultas(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)

        self.consulta_actual = self.mostrar_disponibles
        self._crear_botones()
        self._crear_tabla()
        self.refrescar()
        self.bind("<Map>", self._al_mostrar)


    def _crear_botones(self):
        botones = ttk.LabelFrame(
            self, text="Consultas disponibles", padding=10
        )
        botones.pack(fill="x")

        ttk.Button(
            botones,
            text="Equipos disponibles",
            command=self.mostrar_disponibles,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Arriendos activos",
            command=self.mostrar_activos,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Historial de arriendos",
            command=self.mostrar_historial,
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Refrescar",
            command=self.refrescar,
        ).pack(side="right", padx=5)


    def _crear_tabla(self):
        self.titulo = ttk.Label(
            self, text="", font=("Arial", 12, "bold")
        )
        self.titulo.pack(anchor="w", pady=10)

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(
            contenedor,
            show="headings",
        )

        scroll_vertical = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview,
        )

        scroll_horizontal = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=self.tabla.xview,
        )

        self.tabla.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_vertical.grid(row=0, column=1, sticky="ns")
        scroll_horizontal.grid(row=1, column=0, sticky="ew")

        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        self.lbl_resultados = ttk.Label(self, text="")
        self.lbl_resultados.pack(anchor="w", pady=5)


    def _configurar_tabla(self, columnas, encabezados):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        self.tabla["columns"] = columnas

        for columna, encabezado in zip(columnas, encabezados):
            self.tabla.heading(columna, text=encabezado)
            self.tabla.column(
                columna, width=130, anchor="center"
            )


    def mostrar_disponibles(self):
        self.consulta_actual = self.mostrar_disponibles

        try:
            equipos = consulta_service.consultar_equipos_disponibles()
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        self.titulo.config(text="Equipos disponibles")

        columnas = (
            "id",
            "nombre",
            "categoria",
            "precio",
            "stock_total",
            "stock_disponible",
        )

        encabezados = (
            "ID",
            "Nombre",
            "Categoría",
            "Precio diario",
            "Stock total",
            "Disponible",
        )

        self._configurar_tabla(columnas, encabezados)

        for equipo in equipos:
            self.tabla.insert(
                "",
                "end",
                values=(
                    equipo.id,
                    equipo.nombre,
                    equipo.categoria.nombre,
                    equipo.precio_diario,
                    equipo.stock_total,
                    equipo.stock_disponible,
                ),
            )

        self.lbl_resultados.config(
            text=f"Equipos disponibles encontrados: {len(equipos)}"
        )


    def _mostrar_arriendos(self, arriendos, titulo):
        self.titulo.config(text=titulo)

        columnas = (
            "id",
            "equipo",
            "cliente",
            "fecha_inicio",
            "fecha_fin",
            "cantidad",
            "estado",
        )

        encabezados = (
            "ID",
            "Equipo",
            "Cliente",
            "Fecha de inicio",
            "Término previsto",
            "Cantidad",
            "Estado",
        )

        self._configurar_tabla(columnas, encabezados)

        for arriendo in arriendos:
            self.tabla.insert(
                "",
                "end",
                values=(
                    arriendo.id,
                    arriendo.equipo.nombre,
                    arriendo.cliente.nombre,
                    arriendo.fecha_inicio.strftime("%d/%m/%Y"),
                    arriendo.fecha_fin_prevista.strftime("%d/%m/%Y"),
                    arriendo.cantidad,
                    arriendo.estado.value,
                ),
            )

        self.lbl_resultados.config(
            text=f"Arriendos encontrados: {len(arriendos)}"
        )


    def mostrar_activos(self):
        self.consulta_actual = self.mostrar_activos
        try:
            arriendos = consulta_service.consultar_arriendos_activos()
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        self._mostrar_arriendos(arriendos, "Arriendos activos")


    def mostrar_historial(self):
        self.consulta_actual = self.mostrar_historial
        try:
            arriendos = consulta_service.consultar_historial_arriendos()
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        self._mostrar_arriendos(arriendos, "Historial de arriendos")


    def refrescar(self):
        self.consulta_actual()


    def _al_mostrar(self, _evento):
        self.refrescar()