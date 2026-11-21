from sqlalchemy import select
from app.database import SessionLocal, registrar_modelos
from app.models.categoria import Categoria
from app.utils.excepciones import DatosInvalidosError, RegistroNoEncontradoError, RegistroVinculadoError
registrar_modelos()


def crear_categoria(nombre, descripcion=None):
    nombre = (nombre or "").strip()
    if not nombre:
        raise DatosInvalidosError("El nombre de la categoría es obligatorio.")

    with SessionLocal() as session:
        existe = session.scalar(select(Categoria).where(Categoria.nombre == nombre))
        if existe:
            raise DatosInvalidosError(f"Ya existe una categoría llamada '{nombre}'.")

        categoria = Categoria(
            nombre=nombre, 
            descripcion=(descripcion or "").strip() or None
        )
        session.add(categoria)
        session.commit()
        return categoria


def listar_categorias():
    with SessionLocal() as session:
        return list(session.scalars(select(Categoria).order_by(Categoria.nombre)))


def obtener_categoria(categoria_id):
    with SessionLocal() as session:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None:
            raise RegistroNoEncontradoError("La categoría no existe.")
        return categoria


def actualizar_categoria(categoria_id, nombre, descripcion=None):
    nombre = (nombre or "").strip()
    if not nombre:
        raise DatosInvalidosError("El nombre de la categoría es obligatorio.")

    with SessionLocal() as session:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None:
            raise RegistroNoEncontradoError("La categoría no existe.")

        repetida = session.scalar(
            select(Categoria).where(
                Categoria.nombre == nombre, Categoria.id != categoria_id
            )
        )
        if repetida:
            raise DatosInvalidosError(f"Ya existe una categoría llamada '{nombre}'.")

        categoria.nombre = nombre
        categoria.descripcion = (descripcion or "").strip() or None
        session.commit()
        return categoria


def eliminar_categoria(categoria_id):
    with SessionLocal() as session:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None:
            raise RegistroNoEncontradoError("La categoría no existe.")

        if categoria.equipos:
            raise RegistroVinculadoError(
                f"No se puede eliminar '{categoria.nombre}': tiene "
                f"{len(categoria.equipos)} equipo(s) asociado(s)."
            )

        session.delete(categoria)
        session.commit()