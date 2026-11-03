# Prototipo ANTIGUO de la pantalla de inicio (con el nombre 'Nail Bliss').
# La aplicación actual usa ventanas/inicio.py; Main.py no importa este archivo.
# Si lo ejecutas solo, abre una ventana con el diseño de la portada.

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

# Ventana de prueba con encabezado (logo y menú), banner principal y tarjeta para
# agendar cita.
class NailBliss(QWidget):

    # Configura el título y el tamaño mínimo de la ventana y construye la interfaz.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nail Bliss")
        self.setMinimumSize(1000, 650)
        self.crear_interfaz()

    # Construye toda la pantalla de arriba hacia abajo: encabezado, banner (hero) y
    # tarjeta de cita.
    def crear_interfaz(self):

        # Layout vertical que apila las tres secciones, sin márgenes ni espacios.
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- ENCABEZADO: logo, subtítulo y botones del menú ---
        encabezado = QFrame()
        encabezado.setFixedHeight(145)
        encabezado.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)

        layout_encabezado = QVBoxLayout()
        layout_encabezado.setContentsMargins(20, 10, 20, 0)
        layout_encabezado.setSpacing(5)

        # Nombre del salón: texto grande, centrado y en cursiva.
        logo = QLabel("Nails Bliss")
        logo.setAlignment(Qt.AlignCenter)

        fuente_logo = QFont()
        fuente_logo.setPointSize(27)
        fuente_logo.setItalic(True)

        logo.setFont(fuente_logo)

        logo.setStyleSheet("""
            QLabel {
                color: #c39ac5;
                padding-top: 5px;
            }
        """)

        layout_encabezado.addWidget(logo)

        # Subtítulo pequeño debajo del logo.
        subtitulo_logo = QLabel("Salón de uñas")
        subtitulo_logo.setAlignment(Qt.AlignCenter)

        fuente_subtitulo = QFont()
        fuente_subtitulo.setPointSize(8)
        fuente_subtitulo.setItalic(True)

        subtitulo_logo.setFont(fuente_subtitulo)

        subtitulo_logo.setStyleSheet("""
            QLabel {
                color: #b8a5b8;
            }
        """)

        layout_encabezado.addWidget(subtitulo_logo)

        # Fila horizontal con los botones del menú (en este prototipo no hacen nada al
        # hacer clic).
        menu = QHBoxLayout()
        menu.setContentsMargins(50, 25, 50, 5)
        menu.setSpacing(40)

        botones_menu = [
            "INICIO",
            "SERVICIOS",
            "PROMOCIONES",
            "SOBRE NOSOTROS",
            "CONTACTOS"
        ]

        # Crea un botón de texto por cada opción; cambia de color al pasar el mouse
        # (:hover).
        for texto in botones_menu:

            boton = QPushButton(texto)

            boton.setCursor(Qt.PointingHandCursor)

            boton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #555555;
                    font-size: 11px;
                    font-weight: bold;
                }

                QPushButton:hover {
                    color: #c58bc5;
                }
            """)

            menu.addWidget(boton)

        layout_encabezado.addLayout(menu)

        encabezado.setLayout(layout_encabezado)

        layout_principal.addWidget(encabezado)

        # --- BANNER PRINCIPAL (hero): texto a la izquierda e imagen a la derecha ---
        hero = QFrame()
        hero.setFixedHeight(320)

        layout_hero = QHBoxLayout()
        layout_hero.setContentsMargins(0, 0, 0, 0)
        layout_hero.setSpacing(0)

        # Panel izquierdo de color morado con los textos de bienvenida.
        izquierda = QFrame()

        izquierda.setStyleSheet("""
            QFrame {
                background-color: #d9a7d6;
            }
        """)

        layout_izquierda = QVBoxLayout()
        layout_izquierda.setContentsMargins(70, 25, 40, 20)
        layout_izquierda.setSpacing(8)

        pequeno = QLabel("REALZA TU BELLEZA")

        fonte_pequeno = QFont()
        fonte_pequeno.setPointSize(10)
        fonte_pequeno.setItalic(True)

        pequeno.setFont(fonte_pequeno)

        pequeno.setStyleSheet("""
            QLabel {
                color: #765f73;
            }
        """)

        layout_izquierda.addWidget(pequeno)

        titulo = QLabel("BELLEZAS EN TUS UÑAS")

        fuente_titulo = QFont()
        fuente_titulo.setPointSize(20)
        fuente_titulo.setBold(True)
        fuente_titulo.setItalic(True)

        titulo.setFont(fuente_titulo)

        titulo.setStyleSheet("""
            QLabel {
                color: white;
            }
        """)

        layout_izquierda.addWidget(titulo)

        confianza = QLabel("CONFÍA EN TI")

        fuente_confianza = QFont()
        fuente_confianza.setPointSize(21)
        fuente_confianza.setItalic(True)

        confianza.setFont(fuente_confianza)

        confianza.setStyleSheet("""
            QLabel {
                color: #4e414d;
            }
        """)

        layout_izquierda.addWidget(confianza)

        # Línea horizontal decorativa entre el título y la descripción.
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("""
            QFrame {
                color: #a879a5;
                background-color: #a879a5;
            }
        """)

        layout_izquierda.addWidget(linea)

        descripcion = QLabel(
            "Manicuras modernas, elegantes y hechas\n"
            "con amor."
        )

        descripcion.setAlignment(Qt.AlignCenter)

        fuente_descripcion = QFont()
        fuente_descripcion.setPointSize(10)
        fuente_descripcion.setItalic(True)

        descripcion.setFont(fuente_descripcion)

        descripcion.setStyleSheet("""
            QLabel {
                color: #6d596b;
            }
        """)

        layout_izquierda.addWidget(descripcion)

        layout_izquierda.addStretch()

        izquierda.setLayout(layout_izquierda)

        # Panel derecho: muestra la foto de uñas.
        derecha = QLabel()

        derecha.setAlignment(Qt.AlignCenter)

        # Pon aquí la imagen de las uñas
        pixmap = QPixmap("recursos/uñas.jpg")

        # Si la imagen se cargó bien, se escala para llenar el espacio; si no se
        # encontró, se muestra un texto de reemplazo.
        if not pixmap.isNull():

            pixmap = pixmap.scaled(
                550,
                320,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            derecha.setPixmap(pixmap)

        else:

            derecha.setText("IMAGEN DE UÑAS")
            derecha.setStyleSheet("""
                QLabel {
                    background-color: #d8c1ad;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)

        # El número 1 es el factor de estiramiento: ambas mitades ocupan el mismo
        # ancho.
        layout_hero.addWidget(izquierda, 1)
        layout_hero.addWidget(derecha, 1)

        hero.setLayout(layout_hero)

        layout_principal.addWidget(hero)

        # --- TARJETA 'AGENDA TU CITA' ---
        contenedor_cita = QFrame()

        contenedor_cita.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)

        layout_cita = QHBoxLayout()
        layout_cita.setContentsMargins(100, 20, 100, 20)

        tarjeta = QFrame()

        tarjeta.setFixedHeight(85)

        tarjeta.setStyleSheet("""
            QFrame {
                background-color: #e7c2e3;
                border-radius: 10px;
            }
        """)

        layout_tarjeta = QHBoxLayout()
        layout_tarjeta.setContentsMargins(25, 10, 30, 10)

        # Texto
        textos = QVBoxLayout()

        momento = QLabel("Tu momento importante")

        fuente_momento = QFont()
        fuente_momento.setPointSize(9)
        fuente_momento.setItalic(True)

        momento.setFont(fuente_momento)

        momento.setStyleSheet("""
            QLabel {
                color: #765f73;
            }
        """)

        textos.addWidget(momento)

        agenda = QLabel("AGENDA TU CITA")

        fuente_agenda = QFont()
        fuente_agenda.setPointSize(17)
        fuente_agenda.setBold(True)

        agenda.setFont(fuente_agenda)

        agenda.setStyleSheet("""
            QLabel {
                color: #654f62;
            }
        """)

        textos.addWidget(agenda)

        elegir = QLabel("ELIGE EL SERVICIO QUE MÁS TE GUSTE")

        fuente_elegir = QFont()
        fuente_elegir.setPointSize(8)

        elegir.setFont(fuente_elegir)

        elegir.setStyleSheet("""
            QLabel {
                color: #8c7489;
            }
        """)

        textos.addWidget(elegir)

        layout_tarjeta.addLayout(textos)

        layout_tarjeta.addStretch()

        # Botón
        # Botón redondeado; cambia de color al pasar el mouse (:hover) y al
        # presionarlo (:pressed).
        boton_cita = QPushButton("AGENDA TU CITA AHORA")

        boton_cita.setFixedSize(220, 40)

        boton_cita.setCursor(Qt.PointingHandCursor)

        boton_cita.setStyleSheet("""
            QPushButton {
                background-color: #d8a6d4;
                color: #765d72;
                border: none;
                border-radius: 20px;
                font-size: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #c88fc4;
                color: white;
            }

            QPushButton:pressed {
                background-color: #b879b5;
            }
        """)

        layout_tarjeta.addWidget(boton_cita)

        tarjeta.setLayout(layout_tarjeta)

        layout_cita.addWidget(tarjeta)

        contenedor_cita.setLayout(layout_cita)

        layout_principal.addWidget(contenedor_cita)

        # Aplica el layout principal a la ventana.
        self.setLayout(layout_principal)


# Arranque del prototipo: crea la app, muestra la ventana y entra al bucle de eventos.
app = QApplication(sys.argv)

ventana = NailBliss()
ventana.show()

sys.exit(app.exec())