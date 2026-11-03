# Punto de entrada de la aplicación Chikys Nails.
# Para abrir el sistema ejecuta este archivo: python Main.py

import sys
from PySide6.QtWidgets import QApplication
from ventanas.inicio import NailBliss


# Crea la aplicación de Qt (sys.argv permite recibir argumentos de consola).
app = QApplication(sys.argv)

# Crea la ventana principal (la clase está en ventanas/inicio.py).
ventana = NailBliss()
# Muestra la ventana en pantalla.
ventana.show()

# Inicia el bucle de eventos (la app queda esperando clics y teclas) y termina el
# programa cuando se cierra la ventana.
sys.exit(app.exec())