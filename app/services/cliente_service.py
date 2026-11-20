from sqlalchemy import func, or_, select

from app.database import SessionLocal
from app.models.arriendo import Arriendo
from app.models.cliente import Cliente
from app.utils.excepciones import (
    DatosInvalidosError,
    RegistroNoEncontradoError,
    RegistroVinculadoError,
)

#limites del largo de las columnas del modelo
LARGO_MAX_NOMBRE = 100
LARGO_MAX_CORREO = 120
LARGO_MAX_TELEFONO = 20

# Caracteres permitidos en el teléfono
CARACTERES_TELEFONO = set("0123456789+- ")

#Limpia los datos y valida sus regla y devuelve listos para guardar.
def _normalizar_datos(nombre, correo, telefono):
    nombre = (nombre or "").strip()
    correo = (correo or "").strip().lower()
    telefono = (telefono or "").strip() or None

    if not nombre:  
        raise DatosInvalidosError("El nombre del cliente es obligatorio.")
    if len(nombre) > LARGO_MAX_NOMBRE:
        raise DatosInvalidosError(f"El nombre no puede superar los {LARGO_MAX_NOMBRE} caracteres.")

    partes = correo.split("@")
    if len(partes) != 2 or not partes[0] or "." not in partes[1]:
        raise DatosInvalidosError("El correo no tiene un formato válido (ejemplo: nombre@dominio.cl).")
    if len(correo) > LARGO_MAX_CORREO:
        raise DatosInvalidosError(f"El correo no puede superar los {LARGO_MAX_CORREO} caracteres.")

    if telefono is not None:
        if any(caracter not in CARACTERES_TELEFONO for caracter in telefono):
            raise DatosInvalidosError("El teléfono solo puede contener números, espacios, '+' y '-'.")
        if len(telefono) > LARGO_MAX_TELEFONO:
            raise DatosInvalidosError(f"El teléfono no puede superar los {LARGO_MAX_TELEFONO} caracteres.")

    return nombre, correo, telefono

#Lanza error si otro cliente ya usa ese correo.
def _verificar_correo_libre(session, correo, ignorar_id=None):
    consulta = select(Cliente.id).where(Cliente.correo == correo)
    if ignorar_id is not None:
        consulta = consulta.where(Cliente.id != ignorar_id)
    if session.scalar(consulta) is not None:
        raise DatosInvalidosError(f"Ya existe un cliente registrado con el correo {correo}.")

#Crea un cliente nuevo y lo devuelve.
def crear_cliente(nombre, correo, telefono=None):
    nombre, correo, telefono = _normalizar_datos(nombre, correo, telefono)

    with SessionLocal() as session:
        try:
            _verificar_correo_libre(session, correo)
            cliente = Cliente(nombre=nombre, correo=correo, telefono=telefono)
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente
        except Exception:
            session.rollback()
            raise

#Devuelve los clientes ordenados por nombre. 
#Si hay filtro, busca en nombre y correo.
def listar_clientes(filtro=""):
    texto = (filtro or "").strip()

    with SessionLocal() as session:
        consulta = select(Cliente).order_by(Cliente.nombre)
        if texto:
            patron = f"%{texto}%"
            consulta = consulta.where(
                or_(Cliente.nombre.ilike(patron), Cliente.correo.ilike(patron))
            )

        return list(session.scalars(consulta).all())

#Devuelve un cliente por su id.
def obtener_cliente(cliente_id):
    with SessionLocal() as session:
        cliente = session.get(Cliente, cliente_id)
        if cliente is None:
            raise RegistroNoEncontradoError(f"No existe un cliente con id {cliente_id}.")
        return cliente

#Modifica los datos de un cliente existente y lo devuelve.
def actualizar_cliente(cliente_id, nombre, correo, telefono=None):
    nombre, correo, telefono = _normalizar_datos(nombre, correo, telefono)

    with SessionLocal() as session:
        try:
            cliente = session.get(Cliente, cliente_id)
            if cliente is None:
                raise RegistroNoEncontradoError(f"No existe un cliente con id {cliente_id}.")

            _verificar_correo_libre(session, correo, ignorar_id=cliente_id)

            cliente.nombre = nombre
            cliente.correo = correo
            cliente.telefono = telefono
            session.commit()
            session.refresh(cliente)
            return cliente
        except Exception:
            session.rollback()
            raise

#Elimina un cliente, 
####solo si no tiene arriendos registrados.
###
##
#
def eliminar_cliente(cliente_id):
    with SessionLocal() as session:
        try:
            cliente = session.get(Cliente, cliente_id)
            if cliente is None:
                raise RegistroNoEncontradoError(f"No existe un cliente con id {cliente_id}.")

            cantidad_arriendos = session.scalar(
                select(func.count(Arriendo.id)).where(Arriendo.cliente_id == cliente_id)
            )
            if cantidad_arriendos > 0:
                raise RegistroVinculadoError(
                    "No se puede eliminar el cliente porque tiene arriendos registrados."
                )

            session.delete(cliente)
            session.commit()
        except Exception:
            session.rollback()
            raise