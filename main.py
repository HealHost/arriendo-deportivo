from app.database import init_db
from app.models.arriendo import *
from app.models.cliente import * 
from app.gui.ventana_principal import VentanaPrincipal


def main():
    init_db()

    ventana = VentanaPrincipal()
    ventana.mainloop()


if __name__ == "__main__":
    main()