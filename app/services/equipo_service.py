from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import SessionLocal, registrar_modelos
from app.models.categoria import Categoria
from app.models.equipo import Equipo
from app.utils.excepciones import DatosInvalidosError, RegistroNoEncontradoError, RegistroVinculadoError
from app.factories.equipo_factory import BalonFactory, RaquetaFactory, EquipoGenericoFactory

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


def _seleccionar_fabrica(nombre_categoria):
    nombre_categoria = nombre_categoria.strip().lower()
    if nombre_categoria in ("balón", "balones", "balon"):
        return BalonFactory()
    if nombre_categoria in ("raqueta", "raquetas"):
        return RaquetaFactory()
    return EquipoGenericoFactory()


def crear_equipo(nombre, categoria_id, precio_diario, stock_total):
    nombre, precio_diario, stock_total = _validar_datos(
        nombre, precio_diario, stock_total
    )

    with SessionLocal() as session:
        categoria = session.get(Categoria, categoria_id)

        if categoria is None:
            raise RegistroNoEncontradoError("La categoría seleccionada no existe.")

        fabrica = _seleccionar_fabrica(categoria.nombre)

        equipo = fabrica.crear_equipo(
            nombre=nombre,
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
        )

        try:
            session.add(equipo)
            session.commit()
        except Exception:
            session.rollback()
            raise

        return equipo


def listar_equipos(solo_disponibles=False):
    consulta = (
        select(Equipo).options(joinedload(Equipo.categoria)).order_by(Equipo.nombre)
    )

    if solo_disponibles:
        consulta = consulta.where(Equipo.stock_disponible > 0)
    with SessionLocal() as session:
        return list(session.scalars(consulta))


def obtener_equipo(equipo_id):
    consulta = (select(Equipo).options(joinedload(Equipo.categoria)).where(Equipo.id == equipo_id))
    with SessionLocal() as session:
        equipo = session.scalars(consulta).first()

        if equipo is None:
            raise RegistroNoEncontradoError("El equipo seleccionado no existe.")
        return equipo


def actualizar_equipo(equipo_id, nombre, categoria_id, precio_diario, stock_total):
    nombre, precio_diario, stock_total = _validar_datos(
        nombre, precio_diario, stock_total
    )

    with SessionLocal() as session:
        equipo = session.get(Equipo, equipo_id)
        if equipo is None:
            raise RegistroNoEncontradoError("El equipo no existe.")

        if session.get(Categoria, categoria_id) is None:
            raise RegistroNoEncontradoError("La categoría seleccionada no existe.")

        arrendadas = equipo.stock_total - equipo.stock_disponible
        if stock_total < arrendadas:
            raise DatosInvalidosError(
                f"El stock total no puede ser menor a {arrendadas}, "
                "que son las unidades actualmente arrendadas."
            )

        equipo.nombre = nombre
        equipo.categoria_id = categoria_id
        equipo.precio_diario = precio_diario
        equipo.stock_total = stock_total
        equipo.stock_disponible = stock_total - arrendadas

        session.commit()
        return equipo


def eliminar_equipo(equipo_id):
    with SessionLocal() as session:
        equipo = session.get(Equipo, equipo_id)
        if equipo is None:
            raise RegistroNoEncontradoError("El equipo no existe.")

        if equipo.arriendos:
            raise RegistroVinculadoError(
                f"No se puede eliminar '{equipo.nombre}': tiene "
                f"{len(equipo.arriendos)} arriendo(s) asociado(s)."
            )

        session.delete(equipo)
        session.commit()