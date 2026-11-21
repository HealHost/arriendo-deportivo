import tkinter as tk
from tkinter import messagebox, ttk

from app.services import cliente_service
from app.utils.excepciones import (
    DatosInvalidosError,
    RegistroNoEncontradoError,
    RegistroVinculadoError,
)

#Frame que se incrusta en la ventana principal.
class FrameClientes(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)

        #None significa crear uno nuevo.
        self._id_seleccionado = None

        # StringVar permite leer y escribir los campos desde código con .get y .set.
        self._var_nombre = tk.StringVar()
        self._var_correo = tk.StringVar()
        self._var_telefono = tk.StringVar()
        self._var_filtro = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._construir_formulario()
        self._construir_busqueda()
        self._construir_tabla()
        self._cargar_tabla()

    def _construir_formulario(self):
        marco = ttk.LabelFrame(self, text="Datos del cliente", padding=10)
        marco.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        marco.columnconfigure(1, weight=1)

        campos = [
            ("Nombre:", self._var_nombre),
            ("Correo:", self._var_correo),
            ("Teléfono:", self._var_telefono),
        ]
        for fila, (etiqueta, variable) in enumerate(campos):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=3)
            ttk.Entry(marco, textvariable=variable).grid(row=fila, column=1, sticky="ew", padx=5, pady=3)

        botones = ttk.Frame(marco)
        botones.grid(row=len(campos), column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_formulario).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(side="left", padx=4)

    def _construir_busqueda(self):
        marco = ttk.Frame(self)
        marco.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(marco, text="Buscar (nombre o correo):").pack(side="left")
        entrada = ttk.Entry(marco, textvariable=self._var_filtro, width=30)
        entrada.pack(side="left", padx=5)
        #Enter en la caja de búsqueda hace lo mismo que el botón.
        entrada.bind("<Return>", lambda evento: self._cargar_tabla())

        ttk.Button(marco, text="Buscar", command=self._cargar_tabla).pack(side="left")
        ttk.Button(marco, text="Ver todos", command=self._ver_todos).pack(side="left", padx=5)

    def _construir_tabla(self):
        marco = ttk.Frame(self)
        marco.grid(row=2, column=0, sticky="nsew")

        columnas = [("id", "ID", 50), ("nombre", "Nombre", 200), ("correo", "Correo", 220), ("telefono", "Teléfono", 130)]
        self.tabla = ttk.Treeview(
            marco,
            columns=[columna for columna, _, _ in columnas],
            show="headings",
            selectmode="browse",  #Solo se puede seleccionar una fila a la vez.
        )
        for columna, titulo, ancho in columnas:
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="w")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        #evento que Tk dispara cuando cambia la selección.
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    #Vuelve a llenar la tabla con los clientes que coinciden con el filtro.
    def _cargar_tabla(self):
        """Vuelve a llenar la tabla con los clientes que coinciden con el filtro."""
        self.tabla.delete(*self.tabla.get_children())
        clientes = cliente_service.listar_clientes(self._var_filtro.get())
        for cliente in clientes:
            # iid usa el id del cliente, así al seleccionar una fila sabemos a quién corresponde.
            self.tabla.insert(
                "",
                tk.END,
                iid=str(cliente.id),
                values=(cliente.id, cliente.nombre, cliente.correo, cliente.telefono or ""),
            )

    def _ver_todos(self):
        self._var_filtro.set("")
        self._cargar_tabla()

    #Copia la fila seleccionada al formulario para poder editarla.
    def _al_seleccionar(self, evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        cliente_id, nombre, correo, telefono = self.tabla.item(seleccion[0], "values")
        self._id_seleccionado = int(cliente_id)
        self._var_nombre.set(nombre)
        self._var_correo.set(correo)
        self._var_telefono.set(telefono)

    def _limpiar_formulario(self):
        self._id_seleccionado = None
        for variable in (self._var_nombre, self._var_correo, self._var_telefono):
            variable.set("")
        self.tabla.selection_remove(self.tabla.selection())

    #Crea un cliente nuevo o actualiza el seleccionado, según corresponda.
    def _guardar(self):
        """Crea un cliente nuevo o actualiza el seleccionado, según corresponda."""
        nombre = self._var_nombre.get()
        correo = self._var_correo.get()
        telefono = self._var_telefono.get()
        try:
            if self._id_seleccionado is None:
                cliente_service.crear_cliente(nombre, correo, telefono)
                mensaje = "Cliente registrado correctamente."
            else:
                cliente_service.actualizar_cliente(self._id_seleccionado, nombre, correo, telefono)
                mensaje = "Cliente actualizado correctamente."
        except DatosInvalidosError as error:
            # El usuario corrige los datos, así que el formulario se mantiene como está.
            messagebox.showwarning("Datos no válidos", str(error), parent=self)
            return
        except RegistroNoEncontradoError as error:
            messagebox.showerror("Cliente no encontrado", str(error), parent=self)
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"No se pudo guardar el cliente.\n{error}", parent=self)
            return

        messagebox.showinfo("Listo", mensaje, parent=self)
        self._limpiar_formulario()
        self._cargar_tabla()

    def _eliminar(self):
        if self._id_seleccionado is None:
            messagebox.showinfo("Sin selección", "Selecciona un cliente en la tabla para eliminarlo.", parent=self)
            return

        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Eliminar el cliente seleccionado? Esta acción no se puede deshacer.",
            parent=self,
        )
        if not confirmado:
            return

        try:
            cliente_service.eliminar_cliente(self._id_seleccionado)
        except RegistroVinculadoError as error:
            #Tiene arriendos: no se borra y no hay nada más que hacer aquí.
            messagebox.showwarning("No se puede eliminar", str(error), parent=self)
            return
        except RegistroNoEncontradoError as error:
            messagebox.showerror("Cliente no encontrado", str(error), parent=self)
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"No se pudo eliminar el cliente.\n{error}", parent=self)
            return

        self._limpiar_formulario()
        self._cargar_tabla()