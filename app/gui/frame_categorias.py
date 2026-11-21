import tkinter as tk
from tkinter import messagebox, ttk

from app.services import categoria_service
from app.utils.excepciones import ErrorSistema


class FrameCategorias(ttk.Frame):

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.categoria_id = None 

        self._crear_formulario()
        self._crear_tabla()
        self.refrescar()


    def _crear_formulario(self):
        formulario = ttk.LabelFrame(self, text="Datos de la categoría", padding=10)
        formulario.pack(fill="x")

        ttk.Label(formulario, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        self.var_nombre = tk.StringVar()
        ttk.Entry(formulario, textvariable=self.var_nombre, width=40).grid(
            row=0, column=1, padx=5, pady=3
        )

        ttk.Label(formulario, text="Descripción:").grid(
            row=1, column=0, sticky="w", pady=3
        )
        self.var_descripcion = tk.StringVar()
        ttk.Entry(formulario, textvariable=self.var_descripcion, width=40).grid(
            row=1, column=1, padx=5, pady=3
        )

        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(botones, text="Crear", command=self.crear).pack(side="left", padx=3)
        ttk.Button(botones, text="Actualizar", command=self.actualizar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(
            side="left", padx=3
        )

    def _crear_tabla(self):
        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True, pady=(10, 0))

        columnas = ("id", "nombre", "descripcion")
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings")
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=200)
        self.tabla.column("descripcion", width=350)

        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)


    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for c in categoria_service.listar_categorias():
            self.tabla.insert("", "end", values=(c.id, c.nombre, c.descripcion or ""))

    def crear(self):
        try:
            categoria_service.crear_categoria(
                self.var_nombre.get(), self.var_descripcion.get()
            )
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo("Listo", "Categoría creada correctamente.", parent=self)
        self.limpiar()
        self.refrescar()

    def actualizar(self):
        if self.categoria_id is None:
            messagebox.showwarning(
                "Atención", "Selecciona una categoría de la tabla.", parent=self
            )
            return
        try:
            categoria_service.actualizar_categoria(
                self.categoria_id, self.var_nombre.get(), self.var_descripcion.get()
            )
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo(
            "Listo", "Categoría actualizada correctamente.", parent=self
        )
        self.limpiar()
        self.refrescar()

    def eliminar(self):
        if self.categoria_id is None:
            messagebox.showwarning(
                "Atención", "Selecciona una categoría de la tabla.", parent=self
            )
            return
        if not messagebox.askyesno(
            "Confirmar", "¿Eliminar la categoría seleccionada?", parent=self
        ):
            return
        try:
            categoria_service.eliminar_categoria(self.categoria_id)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo("Listo", "Categoría eliminada.", parent=self)
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        self.categoria_id = None
        self.var_nombre.set("")
        self.var_descripcion.set("")
        self.tabla.selection_remove(self.tabla.selection())

    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        id_, nombre, descripcion = self.tabla.item(seleccion[0], "values")
        self.categoria_id = int(id_)
        self.var_nombre.set(nombre)
        self.var_descripcion.set(descripcion)