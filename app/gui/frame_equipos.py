import tkinter as tk
from tkinter import messagebox, ttk
from app.services import categoria_service, equipo_service
from app.utils.excepciones import ErrorSistema


class FrameEquipos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)

        self.equipo_id = None
        self.categorias = {}
        self._crear_formulario()
        self._crear_tabla()
        self.refrescar()
        self.bind("<Map>", self._al_mostrar)

    def _crear_formulario(self):
        formulario = ttk.LabelFrame(
            self, text="Datos del equipo", padding=10
        )
        formulario.pack(fill="x")

        ttk.Label(formulario, text="Nombre:").grid(
            row=0, column=0, sticky="w", pady=3
        )
        self.var_nombre = tk.StringVar()

        ttk.Entry(
            formulario, textvariable=self.var_nombre, width=40
        ).grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(formulario, text="Categoría:").grid(
            row=1, column=0, sticky="w", pady=3
        )
        self.var_categoria = tk.StringVar()

        self.combo_categoria = ttk.Combobox(
            formulario,
            textvariable=self.var_categoria,
            state="readonly",
            width=37,
        )
        self.combo_categoria.grid(
            row=1, column=1, padx=5, pady=3
        )

        ttk.Label(formulario, text="Precio diario:").grid(
            row=2, column=0, sticky="w", pady=3
        )
        self.var_precio = tk.StringVar()

        ttk.Entry(
            formulario, textvariable=self.var_precio, width=40
        ).grid(row=2, column=1, padx=5, pady=3)

        ttk.Label(formulario, text="Stock total:").grid(
            row=3, column=0, sticky="w", pady=3
        )
        self.var_stock = tk.StringVar()

        ttk.Entry(
            formulario, textvariable=self.var_stock, width=40
        ).grid(row=3, column=1, padx=5, pady=3)

        botones = ttk.Frame(formulario)
        botones.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            botones, text="Crear", command=self.crear
        ).pack(side="left", padx=3)

        ttk.Button(
            botones, text="Actualizar", command=self.actualizar
        ).pack(side="left", padx=3)

        ttk.Button(
            botones, text="Eliminar", command=self.eliminar
        ).pack(side="left", padx=3)

        ttk.Button(
            botones, text="Limpiar", command=self.limpiar
        ).pack(side="left", padx=3)

    def _crear_tabla(self):
        filtros = ttk.Frame(self)
        filtros.pack(fill="x", pady=(10, 0))

        self.var_disponibles = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            filtros,
            text="Mostrar solo equipos disponibles",
            variable=self.var_disponibles,
            command=self.refrescar,
        ).pack(side="left")

        ttk.Button(
            filtros, text="Refrescar", command=self.refrescar
        ).pack(side="right")

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True, pady=(10, 0))

        columnas = (
            "id",
            "nombre",
            "categoria",
            "precio",
            "stock_total",
            "stock_disponible",
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )

        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("precio", text="Precio diario")
        self.tabla.heading("stock_total", text="Stock total")
        self.tabla.heading("stock_disponible", text="Disponible")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=180)
        self.tabla.column("categoria", width=150)
        self.tabla.column("precio", width=110, anchor="center")
        self.tabla.column("stock_total", width=100, anchor="center")
        self.tabla.column(
            "stock_disponible", width=100, anchor="center"
        )

        scroll = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview,
        )

        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _cargar_categorias(self):
        categorias = categoria_service.listar_categorias()

        self.categorias = {
            categoria.nombre: categoria.id
            for categoria in categorias
        }

        self.combo_categoria["values"] = list(self.categorias.keys())

        if self.var_categoria.get() not in self.categorias:
            self.var_categoria.set("")

    def refrescar(self):
        self._cargar_categorias()

        equipos = equipo_service.listar_equipos(
            solo_disponibles=self.var_disponibles.get()
        )

        self.limpiar()

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

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

    def crear(self):
        categoria_id = self.categorias.get(self.var_categoria.get())

        try:
            equipo_service.crear_equipo(
                nombre=self.var_nombre.get(),
                categoria_id=categoria_id,
                precio_diario=self.var_precio.get(),
                stock_total=self.var_stock.get(),
            )

        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        messagebox.showinfo("Listo", "Equipo creado correctamente.", parent=self)

        self.refrescar()

    def actualizar(self):
        if self.equipo_id is None:
            messagebox.showwarning(
                "Atención",
                "Selecciona un equipo de la tabla.",
                parent=self,
            )
            return

        categoria_id = self.categorias.get(
            self.var_categoria.get()
        )

        try:
            equipo_service.actualizar_equipo(
                equipo_id=self.equipo_id,
                nombre=self.var_nombre.get(),
                categoria_id=categoria_id,
                precio_diario=self.var_precio.get(),
                stock_total=self.var_stock.get(),
            )

        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        messagebox.showinfo("Listo", "Equipo actualizado correctamente.", parent=self)

        self.refrescar()

    def eliminar(self):
        if self.equipo_id is None:
            messagebox.showwarning(
                "Atención",
                "Selecciona un equipo de la tabla.",
                parent=self,
            )
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar el equipo seleccionado?",
            parent=self,
        ):
            return

        try:
            equipo_service.eliminar_equipo(self.equipo_id)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        messagebox.showinfo("Listo", "Equipo eliminado correctamente.", parent=self)
        self.refrescar()


    def limpiar(self):
        self.equipo_id = None
        self.var_nombre.set("")
        self.var_categoria.set("")
        self.var_precio.set("")
        self.var_stock.set("")
        self.tabla.selection_remove(self.tabla.selection())


    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.equipo_id = int(valores[0])
        self.var_nombre.set(valores[1])
        self.var_categoria.set(valores[2])
        self.var_precio.set(valores[3])
        self.var_stock.set(valores[4])


    def _al_mostrar(self, _evento):
        self.refrescar()