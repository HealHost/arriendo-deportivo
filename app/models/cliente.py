from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#Representa a una persona o empresa que arrienda
class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    arriendos: Mapped[List["Arriendo"]] = relationship(
        "Arriendo",
        back_populates="cliente",
    )
