# Ventana principal de Chikys Nails: encabezado con logo y menú, y una zona central
# que cambia de página
# (Inicio, Clientes, Citas, Servicios, Personal, Insumos).

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QStackedWidget
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

# Cada módulo define una página completa del sistema.
from .clientes import PaginaClientes
from .citas import PaginaCitas
from .servicios import PaginaServicios
from .personal import PaginaPersonal
from .insumos import PaginaInsumos
# Guarda en MySQL todos los datos en memoria y espera a que el hilo de guardado termine.
from .datos import guardar_en_mysql_y_esperar


# Ventana principal. Tiene el menú superior y un QStackedWidget, que muestra una sola
# página a la vez.
class NailBliss(QWidget):

    # Configura el título y el tamaño mínimo de la ventana y construye la interfaz.
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chikys Nails")
        self.setMinimumSize(1000, 650)

        self.crear_interfaz()

    # Arma el encabezado (logo + menú) y el contenedor con todas las páginas.
    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- ENCABEZADO: logo, subtítulo y menú de navegación ---
        header = QFrame()
        header.setFixedHeight(145)

        header.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)

        layout_header = QVBoxLayout(header)
        layout_header.setContentsMargins(30, 15, 30, 15)
        layout_header.setSpacing(8)

        # Nombre del negocio, grande y centrado.
        logo = QLabel("Chikys Nails")
        logo.setAlignment(Qt.AlignCenter)

        fuente_logo = QFont()
        fuente_logo.setPointSize(28)
        fuente_logo.setBold(True)

        logo.setFont(fuente_logo)

        logo.setStyleSheet("""
            color: #8e44ad;
        """)

        layout_header.addWidget(logo)

        # Subtítulo
        subtitulo = QLabel("Salón de uñas")
        subtitulo.setAlignment(Qt.AlignCenter)

        fuente_subtitulo = QFont()
        fuente_subtitulo.setPointSize(11)

        subtitulo.setFont(fuente_subtitulo)

        subtitulo.setStyleSheet("""
            color: #777777;
        """)

        layout_header.addWidget(subtitulo)

        # Fila horizontal con los botones de navegación.
        menu = QHBoxLayout()
        menu.setContentsMargins(0, 5, 0, 0)
        menu.setSpacing(15)

        # El orden de esta lista coincide con el orden de las páginas del
        # QStackedWidget:
        # 0 = INICIO, 1 = CLIENTES, 2 = CITAS, 3 = SERVICIOS, 4 = PERSONAL, 5 =
        # INSUMOS.
        nombres_menu = [
            "INICIO",
            "CLIENTES",
            "CITAS",
            "SERVICIOS",
            "PERSONAL",
            "INSUMOS"
        ]

        # Crea un botón por cada opción; al hacer clic se muestra la página con ese
        # índice.
        for indice, nombre in enumerate(nombres_menu):

            boton = QPushButton(nombre)

            boton.setCursor(Qt.PointingHandCursor)

            boton.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: #555555;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 8px 5px;
                }

                QPushButton:hover {
                    color: #8e44ad;
                }
            """)

            # 'i=indice' fija el índice de ESTE botón; sin eso todos usarían el valor
            # del último.
            boton.clicked.connect(
                lambda checked=False, i=indice:
                self.cambiar_pagina(i)
            )

            menu.addWidget(boton)

        layout_header.addLayout(menu)

        layout_principal.addWidget(header)

        # Contenedor de páginas: solo se ve una a la vez. Se agregan en el mismo orden
        # que el menú.
        self.paginas = QStackedWidget()

        self.paginas.addWidget(self.crear_pagina_inicio())

        self.paginas.addWidget(PaginaClientes())

        self.paginas.addWidget(PaginaCitas())

        self.paginas.addWidget(PaginaServicios())

        self.paginas.addWidget(PaginaPersonal())

        self.paginas.addWidget(PaginaInsumos())

        layout_principal.addWidget(self.paginas)

    # Muestra la página indicada por su posición en el menú.
    def cambiar_pagina(self, indice):

        self.paginas.setCurrentIndex(indice)

    # Qt ejecuta este método automáticamente al cerrar la ventana.
    def closeEvent(self, event):

        # Guardado de seguridad al cerrar la aplicación,
        # por si algo no se guardó en el camino.
        guardar_en_mysql_y_esperar()

        super().closeEvent(event)

    # Construye la página de bienvenida (banner con texto e imagen y tarjeta para
    # agendar cita) y la devuelve.
    def crear_pagina_inicio(self):

        pagina = QWidget()

        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- BANNER PRINCIPAL ---
        hero = QFrame()
        hero.setFixedHeight(320)

        layout_hero = QHBoxLayout(hero)
        layout_hero.setContentsMargins(0, 0, 0, 0)
        layout_hero.setSpacing(0)

        # Panel izquierdo: mensajes de bienvenida sobre fondo de color.
        izquierda = QFrame()

        izquierda.setStyleSheet("""
            QFrame {
                background-color: #8e44ad;
            }
        """)

        layout_izquierda = QVBoxLayout(izquierda)
        layout_izquierda.setContentsMargins(50, 35, 50, 35)

        titulo1 = QLabel("REALZA TU BELLEZA")

        fuente1 = QFont()
        fuente1.setPointSize(13)
        fuente1.setBold(True)

        titulo1.setFont(fuente1)

        titulo1.setStyleSheet("""
            color: white;
        """)

        layout_izquierda.addWidget(titulo1)

        titulo2 = QLabel("BELLEZAS EN TUS UÑAS")

        fuente2 = QFont()
        fuente2.setPointSize(24)
        fuente2.setBold(True)

        titulo2.setFont(fuente2)

        titulo2.setStyleSheet("""
            color: white;
        """)

        layout_izquierda.addWidget(titulo2)

        titulo3 = QLabel("CONFÍA EN TI")

        fuente3 = QFont()
        fuente3.setPointSize(24)
        fuente3.setBold(True)

        titulo3.setFont(fuente3)

        titulo3.setStyleSheet("""
            color: white;
        """)

        layout_izquierda.addWidget(titulo3)

        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("""
            color: white;
        """)

        layout_izquierda.addWidget(linea)

        descripcion = QLabel(
            "Manicuras modernas, elegantes y hechas\n"
            "con amor."
        )

        descripcion.setStyleSheet("""
            color: white;
            font-size: 12px;
        """)

        layout_izquierda.addWidget(descripcion)

        layout_izquierda.addStretch()

        layout_hero.addWidget(izquierda, 1)

        # Panel derecho: imagen del salón.
        derecha = QLabel()
        derecha.setAlignment(Qt.AlignCenter)

        # Ruta a recursos/uñas.jpg calculada desde la ubicación de este archivo
        # (Path), para que funcione sin importar desde dónde se ejecute el programa.
        ruta_imagen = (
            Path(__file__).parent.parent
            / "recursos"
            / "uñas.jpg"
        )

        pixmap = QPixmap(str(ruta_imagen))

        # Si la imagen existe se escala para llenar el panel; si no, se muestra un
        # aviso.
        if not pixmap.isNull():

            derecha.setPixmap(
                pixmap.scaled(
                    500,
                    320,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        else:

            derecha.setText("Imagen no encontrada")

            derecha.setStyleSheet("""
                background-color: #eeeeee;
                color: #777777;
            """)

        layout_hero.addWidget(derecha, 1)

        layout.addWidget(hero)

        # --- TARJETA INFERIOR: invita a agendar una cita ---
        tarjeta = QFrame()

        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(30, 25, 30, 25)
        layout_tarjeta.setSpacing(8)

        texto1 = QLabel("Tu momento importante")
        texto1.setAlignment(Qt.AlignCenter)

        fuente = QFont()
        fuente.setPointSize(14)
        fuente.setBold(True)

        texto1.setFont(fuente)

        texto1.setStyleSheet("""
            color: #8e44ad;
        """)

        layout_tarjeta.addWidget(texto1)

        texto2 = QLabel("AGENDA TU CITA")
        texto2.setAlignment(Qt.AlignCenter)

        fuente2 = QFont()
        fuente2.setPointSize(20)
        fuente2.setBold(True)

        texto2.setFont(fuente2)

        layout_tarjeta.addWidget(texto2)

        texto3 = QLabel(
            "ELIGE EL SERVICIO QUE MÁS TE GUSTE"
        )

        texto3.setAlignment(Qt.AlignCenter)

        texto3.setStyleSheet("""
            color: #777777;
        """)

        layout_tarjeta.addWidget(texto3)

        # Botón que lleva directamente a la página de Citas (índice 2).
        boton_cita = QPushButton("AGENDA TU CITA AHORA")

        boton_cita.setCursor(Qt.PointingHandCursor)

        boton_cita.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 25px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #732d91;
            }
        """)

        boton_cita.clicked.connect(
            lambda: self.cambiar_pagina(2)
        )

        layout_tarjeta.addWidget(
            boton_cita,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(tarjeta)

        return pagina