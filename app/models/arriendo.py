from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#Estados posibles
class EstadoArriendo(str, Enum):
    ACTIVO = "ACTIVO"
    DEVUELTO = "DEVUELTO"

#Registro de un préstamo de equipos a un cliente durante un rango de fechas
class Arriendo(Base):
    __tablename__ = "arriendos"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_arriendo_cantidad_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin_prevista: Mapped[date] = mapped_column(Date)
    cantidad: Mapped[int] = mapped_column(Integer)

    estado: Mapped[EstadoArriendo] = mapped_column(
        SQLEnum(EstadoArriendo, name="estado_arriendo"),
        default=EstadoArriendo.ACTIVO,
    )

    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="arriendos")
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="arriendos")