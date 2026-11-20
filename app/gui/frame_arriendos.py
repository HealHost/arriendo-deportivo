import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from app.models.arriendo import EstadoArriendo
from app.services import arriendo_service, cliente_service, equipo_service
from app.utils.excepciones import (
    ArriendoYaDevueltoError,
    DatosInvalidosError,
    RegistroNoEncontradoError,
    StockInsuficienteError,
)

FORMATO_FECHA = "%Y-%m-%d"

# Texto del combobox de filtro -> valor que entiende arriendo_service.listar_arriendos.
OPCIONES_ESTADO = {
    "Todos": None,
    "Activos": EstadoArriendo.ACTIVO,
    "Devueltos": EstadoArriendo.DEVUELTO,
}

#Frame de arriendos. Se incrusta en la ventana principal, igual que FrameClientes.

class FrameArriendos(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)

        #Estos diccionarios hacen la traducción de texto a id.
        self._equipos = {}
        self._clientes = {}

        self._var_equipo = tk.StringVar()
        self._var_cliente = tk.StringVar()
        self._var_inicio = tk.StringVar(value=date.today().strftime(FORMATO_FECHA))
        self._var_fin = tk.StringVar()
        self._var_cantidad = tk.StringVar(value="1")
        self._var_estado = tk.StringVar(value="Todos")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._construir_formulario()
        self._construir_filtro()
        self._construir_tabla()
        self._cargar_combos()
        self._cargar_tabla()

    def _construir_formulario(self):
        marco = ttk.LabelFrame(self, text="Nuevo arriendo", padding=10)
        marco.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        marco.columnconfigure(1, weight=1)

        #El usuario solo elige de la lista.
        self._combo_equipo = ttk.Combobox(marco, textvariable=self._var_equipo, state="readonly")
        self._combo_cliente = ttk.Combobox(marco, textvariable=self._var_cliente, state="readonly")

        campos = [
            ("Equipo:", self._combo_equipo),
            ("Cliente:", self._combo_cliente),
            ("Fecha inicio (AAAA-MM-DD):", ttk.Entry(marco, textvariable=self._var_inicio)),
            ("Fecha fin prevista (AAAA-MM-DD):", ttk.Entry(marco, textvariable=self._var_fin)),
            ("Cantidad:", ttk.Entry(marco, textvariable=self._var_cantidad)),
        ]
        for fila, (etiqueta, widget) in enumerate(campos):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=3)
            widget.grid(row=fila, column=1, sticky="ew", padx=5, pady=3)

        botones = ttk.Frame(marco)
        botones.grid(row=len(campos), column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(botones, text="Registrar arriendo", command=self._registrar).pack(side="left", padx=4)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_formulario).pack(side="left", padx=4)

    def _construir_filtro(self):
        marco = ttk.Frame(self)
        marco.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(marco, text="Mostrar:").pack(side="left")
        combo_estado = ttk.Combobox(
            marco,
            textvariable=self._var_estado,
            values=list(OPCIONES_ESTADO),
            state="readonly",
            width=12,
        )
        combo_estado.pack(side="left", padx=5)
        #Al cambiar el filtro se recarga la tabla de inmediato.
        combo_estado.bind("<<ComboboxSelected>>", lambda evento: self._cargar_tabla())

        ttk.Button(marco, text="Devolver seleccionado", command=self._devolver).pack(side="right")

    def _construir_tabla(self):
        marco = ttk.Frame(self)
        marco.grid(row=2, column=0, sticky="nsew")

        columnas = [
            ("id", "ID", 50),
            ("equipo", "Equipo", 180),
            ("cliente", "Cliente", 180),
            ("cantidad", "Cant.", 70),
            ("inicio", "Inicio", 100),
            ("fin", "Fin prevista", 110),
            ("estado", "Estado", 100),
        ]
        self.tabla = ttk.Treeview(
            marco,
            columns=[columna for columna, _, _ in columnas],
            show="headings",
            selectmode="browse",
        )
        for columna, titulo, ancho in columnas:
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="w")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    #Llena los combobox de equipos y clientes. 
    #Se llama al abrir y tras cada cambio de stock.
    def _cargar_combos(self):
        # El stock aparece en el texto para que el usuario vea cuántas unidades quedan.
        self._equipos = {
            f"{equipo.id} - {equipo.nombre} (disp.: {equipo.stock_disponible})": equipo.id
            for equipo in equipo_service.listar_equipos()
        }
        self._clientes = {
            f"{cliente.id} - {cliente.nombre}": cliente.id
            for cliente in cliente_service.listar_clientes()
        }
        self._combo_equipo.configure(values=list(self._equipos))
        self._combo_cliente.configure(values=list(self._clientes))

    #Vuelve a llenar la tabla según el filtro de estado elegido.
    def _cargar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        estado = OPCIONES_ESTADO[self._var_estado.get()]
        for arriendo in arriendo_service.listar_arriendos(estado):
            self.tabla.insert(
                "",
                tk.END,
                iid=str(arriendo.id),
                values=(
                    arriendo.id,
                    arriendo.equipo.nombre,
                    arriendo.cliente.nombre,
                    arriendo.cantidad,
                    arriendo.fecha_inicio.strftime(FORMATO_FECHA),
                    arriendo.fecha_fin_prevista.strftime(FORMATO_FECHA),
                    arriendo.estado.value,
                ),
            )

    #Lee el formulario, lo convierte a tipos de Python y pide al servicio registrar el arriendo.
    def _registrar(self):
        #Primera etapa de convertir el texto. Si algo no se puede leer, no se llama al servicio.
        try:
            equipo_id = self._leer_id(self._var_equipo, self._equipos, "un equipo")
            cliente_id = self._leer_id(self._var_cliente, self._clientes, "un cliente")
            cantidad = self._leer_entero(self._var_cantidad.get())
            inicio = self._leer_fecha(self._var_inicio.get(), "inicio")
            fin = self._leer_fecha(self._var_fin.get(), "fin prevista")
        except DatosInvalidosError as error:
            messagebox.showwarning("Datos no válidos", str(error), parent=self)
            return

        #Segunda etapa de el servicio valida stock, fechas y existencia, y descuenta el stock.
        try:
            arriendo_service.registrar_arriendo(equipo_id, cliente_id, inicio, fin, cantidad)
        except (DatosInvalidosError, StockInsuficienteError) as error:
            messagebox.showwarning("No se pudo registrar", str(error), parent=self)
            return
        except RegistroNoEncontradoError as error:
            messagebox.showerror("No encontrado", str(error), parent=self)
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"No se pudo registrar el arriendo.\n{error}", parent=self)
            return

        messagebox.showinfo("Listo", "Arriendo registrado correctamente.", parent=self)
        self._limpiar_formulario()
        #El stock cambió, así que los combobox y la tabla deben reflejarlo.
        self._cargar_combos()
        self._cargar_tabla()

    def _devolver(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Sin selección", "Selecciona un arriendo en la tabla.", parent=self)
            return

        # El iid de cada fila es el id del arriendo (lo pusimos en _cargar_tabla).
        arriendo_id = int(seleccion[0])

        confirmado = messagebox.askyesno(
            "Confirmar devolución",
            "¿Registrar la devolución completa de este arriendo?",
            parent=self,
        )
        if not confirmado:
            return

        try:
            arriendo_service.devolver_arriendo(arriendo_id)
        except ArriendoYaDevueltoError as error:
            messagebox.showwarning("Ya devuelto", str(error), parent=self)
            return
        except RegistroNoEncontradoError as error:
            messagebox.showerror("No encontrado", str(error), parent=self)
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"No se pudo devolver el arriendo.\n{error}", parent=self)
            return

        messagebox.showinfo("Listo", "Devolución registrada. El stock fue restituido.", parent=self)
        self._cargar_combos()
        self._cargar_tabla()

    def _limpiar_formulario(self):
        self._var_equipo.set("")
        self._var_cliente.set("")
        self._var_inicio.set(date.today().strftime(FORMATO_FECHA))
        self._var_fin.set("")
        self._var_cantidad.set("1")

    #convertir texto a tipos de python.
    @staticmethod
    def _leer_id(variable, opciones, nombre_campo):
        texto = variable.get()
        if texto not in opciones:
            raise DatosInvalidosError(f"Debes seleccionar {nombre_campo}.")
        return opciones[texto]

    @staticmethod
    def _leer_entero(texto):
        try:
            return int(texto)
        except ValueError:
            raise DatosInvalidosError("La cantidad debe ser un número entero.") from None

    @staticmethod
    def _leer_fecha(texto, nombre_campo):
        try:
            return datetime.strptime(texto.strip(), FORMATO_FECHA).date()
        except ValueError:
            raise DatosInvalidosError(
                f"La fecha de {nombre_campo} debe tener el formato AAAA-MM-DD."
            ) from None