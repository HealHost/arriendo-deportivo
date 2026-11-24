from abc import ABC, abstractmethod
from app.models.equipo import Equipo


class EquipoFactory(ABC):
    @abstractmethod
    def crear_equipo(self, nombre, categoria_id, precio_diario, stock_total):
        pass


class BalonFactory(EquipoFactory):
    def crear_equipo(self, nombre, categoria_id, precio_diario, stock_total):
        return Equipo(
            nombre=nombre or "Balón",
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
            stock_disponible=stock_total,
        )


class RaquetaFactory(EquipoFactory):

    def crear_equipo(self, nombre, categoria_id, precio_diario, stock_total):
        return Equipo(
            nombre=nombre or "Raqueta",
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
            stock_disponible=stock_total,
        )


class EquipoGenericoFactory(EquipoFactory):
    def crear_equipo(self, nombre, categoria_id, precio_diario, stock_total):
        return Equipo(
            nombre=nombre,
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
            stock_disponible=stock_total,
        )