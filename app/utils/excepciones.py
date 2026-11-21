
class ErrorSistema(Exception):
    pass


class DatosInvalidosError(ErrorSistema):
    pass


class RegistroNoEncontradoError(ErrorSistema):
    pass


class StockInsuficienteError(ErrorSistema):
    pass


class ArriendoYaDevueltoError(ErrorSistema):
    pass


class RegistroVinculadoError(ErrorSistema):
    pass