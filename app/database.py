from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ / "data"
RUTA_BD = CARPETA_DATOS / "arriendos.db"
CARPETA_DATOS.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{RUTA_BD}")


class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def registrar_modelos():
    from app.models.categoria import Categoria
    from app.models.equipo import Equipo
    from app.models.cliente import Cliente
    from app.models.arriendo import Arriendo


def init_db():
    registrar_modelos()
    Base.metadata.create_all(engine)