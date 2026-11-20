from sqlalchemy import desc, func, select

from app.database import SessionLocal
from app.models.arriendo import Arriendo
from app.models.categoria import Categoria
from app.models.equipo import Equipo

#Devuelve una lista.
def arriendos_por_categoria():
    with SessionLocal() as session:
        consulta = (
            select(Categoria.nombre, func.count(Arriendo.id))
            .select_from(Categoria)
            .outerjoin(Equipo, Equipo.categoria_id == Categoria.id)
            .outerjoin(Arriendo, Arriendo.equipo_id == Equipo.id)
            # Agrupamos por id y nombre: dos categorías podrían tener el mismo nombre.
            .group_by(Categoria.id, Categoria.nombre)
            .order_by(Categoria.nombre)
        )
        # Convertimos a tuplas normales para que la sesión pueda cerrarse sin problemas.
        return [(nombre, cantidad) for nombre, cantidad in session.execute(consulta).all()]

#Devuelve hasta limite pares de mayor a menor.
def equipos_mas_arrendados(limite=10):
    with SessionLocal() as session:
        consulta = (
            select(Equipo.nombre, func.count(Arriendo.id).label("total"))
            .join(Arriendo, Arriendo.equipo_id == Equipo.id)
            .group_by(Equipo.id, Equipo.nombre)
            .order_by(desc("total"), Equipo.nombre)
            .limit(limite)
        )
        return [(nombre, total) for nombre, total in session.execute(consulta).all()]