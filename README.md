# Sistema de Gestión de Arriendo de Equipamiento Deportivo

## 1. Descripción del proyecto

Aplicación de escritorio desarrollada para la asignatura Programación II de la Universidad Católica de Temuco.

El sistema permite administrar categorías, equipamiento deportivo y clientes, gestionar arriendos y devoluciones, controlar la disponibilidad de equipos y visualizar estadísticas mediante gráficos.

La información se almacena de manera persistente en una base de datos SQLite utilizando SQLAlchemy ORM.

## 2. Integrantes

- Javier
- Sakin

## 3. Tecnologías utilizadas

| Tecnología | Propósito |
|---|---|
| Python 3 | Lenguaje de programación. |
| SQLAlchemy ORM 2.x | Modelamiento y acceso a la base de datos. |
| SQLite | Almacenamiento persistente de los datos. |
| Tkinter | Desarrollo de la interfaz gráfica. |
| Matplotlib | Generación y visualización de gráficos. |
| Factory Method | Patrón de diseño para la creación de equipos. |

## 4. Funcionalidades

### Categorías

- Crear, listar, actualizar y eliminar categorías.
- Validar nombres obligatorios y únicos.
- Impedir la eliminación de categorías vinculadas a equipos.

### Equipos

- Crear, listar, actualizar y eliminar equipos.
- Asociar equipos a categorías existentes.
- Gestionar precio diario, stock total y stock disponible.
- Consultar equipos con unidades disponibles.
- Impedir la eliminación de equipos vinculados a arriendos.

### Clientes

- Crear, listar, actualizar y eliminar clientes.
- Registrar nombre, correo electrónico y teléfono.
- Validar los datos ingresados.
- Impedir la eliminación de clientes vinculados a arriendos.

### Arriendos y devoluciones

- Registrar arriendos asociados a un cliente y un equipo.
- Validar cantidades, fechas y disponibilidad.
- Descontar el stock al registrar un arriendo.
- Restituir las unidades al registrar una devolución.
- Impedir devoluciones duplicadas.

### Consultas

- Equipos disponibles.
- Arriendos activos.
- Historial de arriendos.

### Estadísticas

- Cantidad de arriendos por categoría.
- Equipos con mayor número de arriendos.

Los gráficos se generan utilizando información almacenada en la base de datos y contabilizan operaciones de arriendo, no cantidades de unidades arrendadas.

## 5. Modelo de datos

### Categoria

- id: identificador único.
- nombre: nombre único de la categoría.
- descripcion: descripción de la categoría.

### Equipo

- id: identificador único.
- nombre: nombre del equipo.
- categoria_id: identificador de la categoría asociada.
- precio_diario: precio diario de arriendo.
- stock_total: cantidad total de unidades.
- stock_disponible: cantidad de unidades disponibles.

### Cliente

- id: identificador único.
- nombre: nombre del cliente.
- correo: correo electrónico único.
- telefono: número de contacto.

### Arriendo

- id: identificador único.
- equipo_id: identificador del equipo arrendado.
- cliente_id: identificador del cliente.
- fecha_inicio: fecha de inicio del arriendo.
- fecha_fin_prevista: fecha prevista de devolución.
- cantidad: cantidad de unidades arrendadas.
- estado: ACTIVO o DEVUELTO.

### Relaciones

- Una categoría puede tener muchos equipos.
- Un equipo pertenece a una categoría.
- Un equipo puede tener muchos arriendos.
- Un cliente puede tener muchos arriendos.
- Cada arriendo pertenece a un equipo y a un cliente.

Las relaciones se implementan mediante claves foráneas y relationship de SQLAlchemy ORM.

## 6. Estructura del proyecto

```text
arriendo-deportivo/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── app/
│   ├── database.py
│   ├── models/
│   │   ├── categoria.py
│   │   ├── equipo.py
│   │   ├── cliente.py
│   │   └── arriendo.py
│   ├── factories/
│   │   └── equipo_factory.py
│   ├── services/
│   │   ├── categoria_service.py
│   │   ├── equipo_service.py
│   │   ├── consulta_service.py
│   │   ├── cliente_service.py
│   │   ├── arriendo_service.py
│   │   └── estadisticas_service.py
│   ├── gui/
│   │   ├── ventana_principal.py
│   │   ├── frame_categorias.py
│   │   ├── frame_equipos.py
│   │   ├── frame_clientes.py
│   │   ├── frame_arriendos.py
│   │   ├── frame_consultas.py
│   │   └── frame_graficos.py
│   └── utils/
│       └── excepciones.py
├── tests/
│   └── test_demo.py
├── docs/
│   └── capturas/
└── data/
    └── arriendos.db
```

## 7. Arquitectura

El proyecto separa sus responsabilidades en diferentes componentes:

- **Models:** define las entidades, atributos y relaciones de la base de datos mediante SQLAlchemy ORM.
- **Services:** contiene las operaciones CRUD, consultas, validaciones y reglas de negocio.
- **GUI:** contiene las ventanas, formularios, botones y tablas desarrollados con Tkinter.
- **Factories:** contiene las clases responsables de crear objetos de equipamiento.
- **Utils:** contiene las excepciones personalizadas utilizadas para informar errores.
- **Database:** configura la conexión a SQLite, las sesiones y la creación de las tablas.

El flujo general de la aplicación es:

```text
Usuario
   ↓
Interfaz gráfica (Tkinter)
   ↓
Servicios
   ↓
Modelos ORM (SQLAlchemy)
   ↓
Base de datos SQLite
```

Esta separación permite mantener la lógica de negocio independiente de la interfaz gráfica y facilita el mantenimiento del código.

## 8. Factory Method

El patrón Factory Method se utiliza para delegar la creación de objetos de equipamiento a clases especializadas.

Su implementación se encuentra en `app/factories/equipo_factory.py`.

Actualmente se utilizan las siguientes clases:

- EquipoFactory: clase base abstracta.
- BalonFactory: fábrica concreta para balones.
- RaquetaFactory: fábrica concreta para raquetas.
- EquipoGenericoFactory: fábrica concreta para otros equipos.

El servicio de equipos selecciona la fábrica correspondiente según la categoría del equipamiento.

```text
equipo_service.py
        ↓
Selección de fábrica
        ↓
crear_equipo()
        ↓
Objeto Equipo
        ↓
SQLAlchemy ORM
        ↓
SQLite
```

Las fábricas crean objetos compatibles con el modelo persistente Equipo. La validación de los datos y el almacenamiento en la base de datos son responsabilidad del servicio.

Esta implementación separa la construcción de objetos de las operaciones de persistencia y permite incorporar nuevas fábricas.

## 9. Interfaz gráfica

La interfaz gráfica se desarrolla mediante Tkinter y sus componentes ttk.

La ventana principal utiliza un Notebook para organizar las funcionalidades en seis pestañas:

1. Categorías.
2. Equipos.
3. Clientes.
4. Arriendos.
5. Consultas.
6. Estadísticas.

Se utilizan formularios para ingresar datos, Treeview para visualizar registros, Combobox para seleccionar opciones y messagebox para mostrar mensajes de confirmación y error.

## 10. Gráficos con Matplotlib

Matplotlib permite visualizar estadísticas obtenidas mediante consultas SQLAlchemy.

Los gráficos implementados son:

- Cantidad de arriendos por categoría.
- Equipos con mayor número de arriendos.

Para integrar los gráficos en Tkinter se utiliza FigureCanvasTkAgg, permitiendo visualizarlos dentro de la misma aplicación.

Las consultas utilizan funciones de agrupación y conteo para obtener resultados a partir de los registros almacenados.

## 11. Reglas de negocio

- El precio diario debe ser mayor que cero.
- El stock total y disponible no pueden ser negativos.
- El stock disponible no puede superar el stock total.
- La cantidad arrendada debe ser positiva.
- No se pueden arrendar más unidades que las disponibles.
- El equipo y el cliente deben existir.
- La fecha prevista de devolución no puede ser anterior a la fecha de inicio.
- Solo se pueden devolver arriendos activos.
- La devolución debe restituir exactamente las unidades arrendadas.
- No se permiten devoluciones duplicadas.
- Los registros vinculados se protegen frente a eliminaciones que comprometan la integridad de los datos.

## 12. Instalación y ejecución

### Requisitos

- Python 3.
- pip.
- Tkinter disponible en la instalación de Python.

En algunas distribuciones Linux es necesario instalar Tkinter por separado. Por ejemplo, en Ubuntu o Debian:

```bash
sudo apt install python3-tk
```

### Crear un entorno virtual

Desde la carpeta raíz del proyecto:

```bash
python -m venv .venv
```

Activar el entorno virtual en Linux:

```bash
source .venv/bin/activate
```

En Windows:

```bash
.venv\Scripts\activate
```

### Instalar las dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación

```bash
python main.py
```

La aplicación genera automáticamente la carpeta data y la base de datos SQLite `data/arriendos.db` si no existen.

Los datos se conservan al cerrar y volver a abrir la aplicación.

## 13. Pruebas de demostración

Las siguientes pruebas corresponden a los casos mínimos establecidos en la pauta del proyecto.

| Prueba | Acción | Resultado esperado |
|---|---|---|
| 1 | Crear categoría y equipo con stock de 5 unidades. | Stock disponible: 5. |
| 2 | Crear cliente y arrendar 2 unidades. | Stock disponible: 3 y estado ACTIVO. |
| 3 | Intentar arrendar 4 unidades adicionales. | Operación rechazada. Stock: 3. |
| 4 | Devolver el arriendo de 2 unidades. | Stock disponible: 5 y estado DEVUELTO. |
| 5 | Intentar devolver nuevamente el mismo arriendo. | Operación rechazada. Stock: 5. |
| 6 | Cerrar y reabrir la aplicación. | Datos persistentes y gráficos generados desde la BD. |

### Resultados

Pendiente de registrar los resultados de las pruebas ejecutadas sobre la versión final del proyecto.

## 14. Capturas de pantalla

Agregar capturas reales de las siguientes funcionalidades:

- Gestión de categorías.
- Gestión de equipos.
- Gestión de clientes.
- Registro de arriendos y devoluciones.
- Consultas.
- Gráficos estadísticos.
- Mensajes de validación y errores.

Las capturas se almacenarán en `docs/capturas/`.

## 15. Distribución de responsabilidades

### Javier

- Configuración de la base de datos.
- Modelos Categoria y Equipo.
- Servicios de categorías, equipos y consultas.
- Interfaces gráficas de categorías, equipos y consultas.
- Implementación de Factory Method.
- Excepciones personalizadas.
- Archivo requirements.txt.
- Archivo .gitignore.

### Sakin

- Modelos Cliente y Arriendo.
- Servicios de clientes, arriendos y estadísticas.
- Interfaces gráficas de clientes, arriendos y gráficos.
- Ventana principal e integración de pestañas.
- Archivo main.py.
- Pruebas de demostración.
- Documentación README.md.

## 16. Fuentes y documentación técnica

### Python

- Documentación oficial: https://docs.python.org/es/3/
- Clases abstractas ABC: https://docs.python.org/es/3/library/abc.html

### SQLAlchemy ORM

- Documentación oficial: https://docs.sqlalchemy.org/en/20/orm/
- Tutorial de SQLAlchemy: https://docs.sqlalchemy.org/en/20/tutorial/

### SQLite

- Documentación oficial: https://www.sqlite.org/docs.html

### Tkinter

- Documentación oficial: https://docs.python.org/es/3/library/tkinter.html
- Componentes ttk: https://docs.python.org/es/3/library/tkinter.ttk.html
- Cuadros de diálogo messagebox: https://docs.python.org/es/3/library/tkinter.messagebox.html

### Matplotlib

- Documentación oficial: https://matplotlib.org/stable/
- Integración de Matplotlib con Tkinter: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html

### Factory Method

- Refactoring Guru: https://refactoring.guru/es/design-patterns/factory-method

---

Universidad Católica de Temuco — Programación II.

Proyecto Final, Evaluación 3 — 2026.