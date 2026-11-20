from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.arriendo import Arriendo, EstadoArriendo
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.utils.excepciones import (
    ArriendoYaDevueltoError,
    DatosInvalidosError,
    RegistroNoEncontradoError,
    StockInsuficienteError,
)

#Valida los datos de un arriendo nuevo antes de tocar la base de datos.
def _validar_datos_arriendo(cantidad, fecha_inicio, fecha_fin_prevista):
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        raise DatosInvalidosError("La cantidad debe ser un número entero mayor que cero.")
    if not isinstance(fecha_inicio, date) or not isinstance(fecha_fin_prevista, date):
        raise DatosInvalidosError("Las fechas deben ser fechas válidas.")
    if fecha_fin_prevista < fecha_inicio:
        raise DatosInvalidosError("La fecha de término no puede ser anterior a la fecha de inicio.")

#Registra un arriendo y descuenta el stock en la misma transacción.
def registrar_arriendo(equipo_id, cliente_id, fecha_inicio, fecha_fin_prevista, cantidad):

    _validar_datos_arriendo(cantidad, fecha_inicio, fecha_fin_prevista)

    with SessionLocal() as session:
        try:
            equipo = session.get(Equipo, equipo_id)
            if equipo is None:
                raise RegistroNoEncontradoError(f"No existe un equipo con id {equipo_id}.")

            cliente = session.get(Cliente, cliente_id)
            if cliente is None:
                raise RegistroNoEncontradoError(f"No existe un cliente con id {cliente_id}.")

            if cantidad > equipo.stock_disponible:
                raise StockInsuficienteError(
                    f"Solo hay {equipo.stock_disponible} unidad(es) disponible(s) de "
                    f"'{equipo.nombre}', y se pidieron {cantidad}."
                )

            equipo.stock_disponible -= cantidad

            arriendo = Arriendo(
                equipo_id=equipo_id,
                cliente_id=cliente_id,
                fecha_inicio=fecha_inicio,
                fecha_fin_prevista=fecha_fin_prevista,
                cantidad=cantidad,
                estado=EstadoArriendo.ACTIVO,
            )
            session.add(arriendo)
            session.commit()
            session.refresh(arriendo)
            return arriendo
        except Exception:
            session.rollback()
            raise

#Marca un arriendo como DEVUELTO y restituye exactamente las unidades prestadas.
def devolver_arriendo(arriendo_id):
    with SessionLocal() as session:
        try:
            arriendo = session.get(Arriendo, arriendo_id)
            if arriendo is None:
                raise RegistroNoEncontradoError(f"No existe un arriendo con id {arriendo_id}.")

            if arriendo.estado == EstadoArriendo.DEVUELTO:
                raise ArriendoYaDevueltoError("Este arriendo ya fue devuelto.")

            # Usamos la cantidad guardada en el arriendo, no un valor que venga de la pantalla.
            arriendo.equipo.stock_disponible += arriendo.cantidad
            arriendo.estado = EstadoArriendo.DEVUELTO
            session.commit()
            session.refresh(arriendo)
            return arriendo
        except Exception:
            session.rollback()
            raise

#Devuelve los arriendos, opcionalmente filtrados por estado.
def listar_arriendos(estado=None):
    with SessionLocal() as session:
        consulta = (
            select(Arriendo)
            .options(joinedload(Arriendo.equipo), joinedload(Arriendo.cliente))
            .order_by(Arriendo.fecha_inicio.desc(), Arriendo.id.desc())
        )
        if estado is not None:
            consulta = consulta.where(Arriendo.estado == estado)
        return list(session.scalars(consulta).unique().all())