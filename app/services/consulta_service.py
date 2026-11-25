from app.services.equipo_service import listar_equipos
from app.services.arriendo_service import listar_arriendos
from app.models.arriendo import EstadoArriendo


def consultar_equipos_disponibles():
    return listar_equipos(solo_disponibles=True)


def consultar_arriendos_activos():
    return listar_arriendos(estado=EstadoArriendo.ACTIVO)


def consultar_historial_arriendos():
    return listar_arriendos()