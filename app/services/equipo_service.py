"""Lógica de negocio del CRUD de equipos."""

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import SessionLocal, registrar_modelos
from app.models.categoria import Categoria
from app.models.equipo import Equipo
from app.utils.excepciones import DatosInvalidosError, RegistroNoEncontradoError, RegistroVinculadoError

registrar_modelos()


def _validar_datos(nombre, precio_diario, stock_total):
    nombre = (nombre or "").strip()
    if not nombre:
        raise DatosInvalidosError("El nombre del equipo es obligatorio.")

    try:
        precio_diario = float(precio_diario)
    except (TypeError, ValueError):
        raise DatosInvalidosError("El precio diario debe ser un número.") from None
    if precio_diario <= 0:
        raise DatosInvalidosError("El precio diario debe ser mayor que 0.")

    try:
        stock_total = int(stock_total)
    except (TypeError, ValueError):
        raise DatosInvalidosError("El stock total debe ser un número entero.") from None
    if stock_total < 0:
        raise DatosInvalidosError("El stock total no puede ser negativo.")

    return nombre, precio_diario, stock_total

def crear_equipo(nombre, categoria_id, precio_diario, stock_total):
    nombre, precio_diario, stock_total = _validar_datos(nombre, precio_diario, stock_total)
    
    with SessionLocal() as session:
        if session.get(Categoria, categoria_id) is None:
            raise RegistroNoEncontradoError("La categoria seleccionada no existe.")

        equipo = Equipo(
            nombre=nombre,
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
            stock_disponible=stock_total
        )
        session.add(equipo)
        session.commit()
        return equipo

