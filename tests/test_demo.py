import unittest
from datetime import date
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.arriendo import Arriendo, EstadoArriendo
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.services import arriendo_service, cliente_service
from app.utils.excepciones import (
    ArriendoYaDevueltoError,
    DatosInvalidosError,
    RegistroVinculadoError,
    StockInsuficienteError,
)

#Cada prueba arranca con una base de datos vacía y nueva.
class TestServicios(unittest.TestCase):
    def setUp(self):
        self.motor = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.motor)
        self.SesionPrueba = sessionmaker(bind=self.motor)

        self.parches = [
            patch("app.services.cliente_service.SessionLocal", self.SesionPrueba),
            patch("app.services.arriendo_service.SessionLocal", self.SesionPrueba),
        ]
        for parche in self.parches:
            parche.start()

    def tearDown(self):
        for parche in self.parches:
            parche.stop()
        Base.metadata.drop_all(self.motor)
        self.motor.dispose()

    #Prepara datos
    #Inserta una categoría y un equipo directamente.
    #sin pasar por los servicios.
    def _crear_equipo(self, nombre="Bicicleta", stock=3):
        with self.SesionPrueba() as sesion:
            categoria = Categoria(nombre="Ciclismo", descripcion="Bicicletas y accesorios")
            sesion.add(categoria)
            sesion.flush()            #Genera el id de la categoría antes de usarlo.
            equipo = Equipo(
                nombre=nombre,
                categoria_id=categoria.id,
                precio_diario=10000,
                stock_total=stock,
                stock_disponible=stock,
            )
            sesion.add(equipo)
            sesion.commit()
            return equipo.id

    def _stock_actual(self, equipo_id):
        with self.SesionPrueba() as sesion:
            return sesion.get(Equipo, equipo_id).stock_disponible

    #Clientes
    def test_crear_cliente_normaliza_correo(self):
        cliente = cliente_service.crear_cliente("  Ana Pérez ", "ANA@Mail.CL", "+56 9 1234")
        self.assertEqual(cliente.nombre, "Ana Pérez")
        self.assertEqual(cliente.correo, "ana@mail.cl")
        self.assertIsNotNone(cliente.id)

    def test_correo_duplicado_lanza_datos_invalidos(self):
        cliente_service.crear_cliente("Ana", "ana@mail.cl")
        with self.assertRaises(DatosInvalidosError):
            cliente_service.crear_cliente("Otra Ana", "ANA@mail.cl")

    def test_correo_sin_formato_lanza_datos_invalidos(self):
        with self.assertRaises(DatosInvalidosError):
            cliente_service.crear_cliente("Ana", "ana-sin-arroba")

    def test_no_se_puede_eliminar_cliente_con_arriendos(self):
        equipo_id = self._crear_equipo()
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")
        arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 1), date(2026, 1, 3), 1)

        with self.assertRaises(RegistroVinculadoError):
            cliente_service.eliminar_cliente(cliente.id)

    #Arriendos
    def test_registrar_arriendo_descuenta_stock(self):
        equipo_id = self._crear_equipo(stock=3)
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")

        arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 1), date(2026, 1, 3), 2)

        self.assertEqual(self._stock_actual(equipo_id), 1)

    def test_stock_insuficiente_no_crea_arriendo_ni_descuenta(self):
        equipo_id = self._crear_equipo(stock=1)
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")

        with self.assertRaises(StockInsuficienteError):
            arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 1), date(2026, 1, 3), 2)

        self.assertEqual(self._stock_actual(equipo_id), 1)
        self.assertEqual(arriendo_service.listar_arriendos(), [])

    def test_fecha_fin_anterior_a_inicio_lanza_datos_invalidos(self):
        equipo_id = self._crear_equipo()
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")

        with self.assertRaises(DatosInvalidosError):
            arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 5), date(2026, 1, 1), 1)

    def test_devolver_restituye_stock_exacto(self):
        equipo_id = self._crear_equipo(stock=3)
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")
        arriendo = arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 1), date(2026, 1, 3), 2)

        arriendo_service.devolver_arriendo(arriendo.id)

        self.assertEqual(self._stock_actual(equipo_id), 3)
        devuelto = arriendo_service.listar_arriendos(EstadoArriendo.DEVUELTO)
        self.assertEqual(len(devuelto), 1)

    def test_segunda_devolucion_no_suma_stock(self):
        equipo_id = self._crear_equipo(stock=3)
        cliente = cliente_service.crear_cliente("Luis", "luis@mail.cl")
        arriendo = arriendo_service.registrar_arriendo(equipo_id, cliente.id, date(2026, 1, 1), date(2026, 1, 3), 2)
        arriendo_service.devolver_arriendo(arriendo.id)

        with self.assertRaises(ArriendoYaDevueltoError):
            arriendo_service.devolver_arriendo(arriendo.id)

        self.assertEqual(self._stock_actual(equipo_id), 3)


if __name__ == "__main__":
    unittest.main()