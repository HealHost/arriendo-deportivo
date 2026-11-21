from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.arriendo import Arriendo


class Equipo(Base):
    __tablename__ = "equipos"

    __table_args__ = (
        CheckConstraint("precio_diario > 0", name="ck_equipo_precio_positivo"),
        CheckConstraint("stock_total >= 0", name="ck_equipo_stock_total"),
        CheckConstraint("stock_disponible >= 0", name="ck_equipo_stock_disp_no_negativo"),
        CheckConstraint("stock_disponible <= stock_total", name="ck_equipo_disp_menor_total"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    precio_diario: Mapped[float] = mapped_column(nullable=False)
    stock_total: Mapped[int] = mapped_column(nullable=False)
    stock_disponible: Mapped[int] = mapped_column(nullable=False)
    categoria: Mapped["Categoria"] = relationship(back_populates="equipos")
    arriendos: Mapped[list["Arriendo"]] = relationship(back_populates="equipo")