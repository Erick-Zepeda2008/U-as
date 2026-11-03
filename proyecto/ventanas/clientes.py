# Módulo CLIENTES: permite ver, buscar, registrar, editar y eliminar clientas.
# Contiene el formulario (ventana emergente) y la página con la tabla.

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QHeaderView
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# datos contiene la lista compartida de clientas (datos.clientes).
from . import datos
# Se llama después de cada cambio para guardar en MySQL.
from .datos import guardar_en_mysql


class FormularioCliente(QDialog):
    """
    Ventana/formulario para registrar o editar una clienta.
    """

    # Si recibe 'cliente' se abre en modo edición; si es None, en modo registro.
    def __init__(self, cliente=None, parent=None):
        super().__init__(parent)

        self.cliente = cliente

        # El título de la ventana cambia según el modo.
        if cliente:
            self.setWindowTitle("Editar clienta")
        else:
            self.setWindowTitle("Nueva clienta")

        self.setMinimumWidth(400)

        self.crear_formulario()

    # Construye el título, los campos de texto y los botones Guardar/Cancelar.
    def crear_formulario(self):

        layout_principal = QVBoxLayout(self)

        titulo = QLabel(
            "Editar información de la clienta"
            if self.cliente
            else "Registrar nueva clienta"
        )

        fuente = QFont()
        fuente.setPointSize(18)
        fuente.setBold(True)

        titulo.setFont(fuente)
        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            color: #8e44ad;
            margin-bottom: 15px;
        """)

        layout_principal.addWidget(titulo)

        # QFormLayout alinea cada etiqueta con su campo.
        formulario = QFormLayout()

        # Campos de texto: nombre, teléfono, correo y dirección.
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")

        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("Número de teléfono")

        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico")

        self.direccion = QLineEdit()
        self.direccion.setPlaceholderText("Dirección")

        formulario.addRow("Nombre:", self.nombre)
        formulario.addRow("Teléfono:", self.telefono)
        formulario.addRow("Correo:", self.correo)
        formulario.addRow("Dirección:", self.direccion)

        layout_principal.addLayout(formulario)

        # Modo edición: rellena los campos con los datos actuales de la clienta.
        if self.cliente:

            self.nombre.setText(self.cliente["nombre"])
            self.telefono.setText(self.cliente["telefono"])
            self.correo.setText(self.cliente["correo"])
            self.direccion.setText(self.cliente["direccion"])

        # Botones estándar de Guardar y Cancelar.
        botones = QDialogButtonBox(
    QDialogButtonBox.Save |
    QDialogButtonBox.Cancel
)
        botones.button(QDialogButtonBox.Save).setText("Guardar")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")

        # Guardar valida los datos antes de cerrar; Cancelar cierra sin guardar.
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)

        layout_principal.addWidget(botones)

    # Comprueba que nombre y teléfono no estén vacíos (correo y dirección son
    # opcionales). Si falta algo, avisa y no cierra la ventana.
    def validar_y_aceptar(self):

        nombre = self.nombre.text().strip()
        telefono = self.telefono.text().strip()
        correo = self.correo.text().strip()
        direccion = self.direccion.text().strip()

        if not nombre:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el nombre de la clienta."
            )

            self.nombre.setFocus()

            return

        if not telefono:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el número de teléfono."
            )

            self.telefono.setFocus()

            return

        # Todo correcto: cierra el diálogo con resultado 'aceptado'.
        self.accept()

    # Devuelve lo escrito en el formulario como diccionario (sin espacios sobrantes).
    def obtener_datos(self):

        return {
            "nombre": self.nombre.text().strip(),
            "telefono": self.telefono.text().strip(),
            "correo": self.correo.text().strip(),
            "direccion": self.direccion.text().strip()
        }


class PaginaClientes(QWidget):
    """
    Página principal del módulo CLIENTES.
    """

    # Guarda una referencia a la lista compartida datos.clientes (no una copia) y
    # construye la interfaz.
    def __init__(self):
        super().__init__()

        self.clientes = datos.clientes

        self.crear_interfaz()

    # Construye la página: título, buscador, botón de nueva clienta y tabla.
    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout_principal.setSpacing(15)

        # Título y descripción de la sección.
        titulo = QLabel("CLIENTES")

        fuente_titulo = QFont()
        fuente_titulo.setPointSize(26)
        fuente_titulo.setBold(True)

        titulo.setFont(fuente_titulo)

        titulo.setStyleSheet("""
            color: #8e44ad;
        """)

        layout_principal.addWidget(titulo)

        descripcion = QLabel(
            "Registra, consulta, edita y administra "
            "la información de las clientas."
        )

        descripcion.setStyleSheet("""
            color: #777777;
            font-size: 13px;
        """)

        layout_principal.addWidget(descripcion)

        # Barra de búsqueda: la tabla se filtra mientras se escribe (textChanged); el
        # botón BUSCAR hace lo mismo.
        barra_busqueda = QHBoxLayout()

        self.buscar = QLineEdit()

        self.buscar.setPlaceholderText(
            "Buscar por nombre..."
        )

        self.buscar.setMinimumHeight(38)

        self.buscar.textChanged.connect(
            self.buscar_clientes
        )

        barra_busqueda.addWidget(self.buscar)

        boton_buscar = QPushButton("BUSCAR")

        boton_buscar.setCursor(
            Qt.PointingHandCursor
        )

        boton_buscar.setMinimumHeight(38)

        boton_buscar.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0px 20px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #732d91;
            }
        """)

        boton_buscar.clicked.connect(
            self.buscar_clientes
        )

        barra_busqueda.addWidget(boton_buscar)

        layout_principal.addLayout(barra_busqueda)

        # Fila con el botón de nueva clienta alineado a la derecha.
        fila_botones = QHBoxLayout()

        fila_botones.addStretch()

        boton_nueva = QPushButton(
            "+ NUEVA CLIENTA"
        )

        boton_nueva.setCursor(
            Qt.PointingHandCursor
        )

        boton_nueva.setMinimumHeight(40)

        boton_nueva.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0px 25px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #732d91;
            }
        """)

        boton_nueva.clicked.connect(
            self.nueva_clienta
        )

        fila_botones.addWidget(boton_nueva)

        layout_principal.addLayout(fila_botones)

        # Tabla de clientas: 4 columnas de datos más los botones Editar y Eliminar de
        # cada fila.
        self.tabla = QTableWidget()

        self.tabla.setColumnCount(6)

        self.tabla.setHorizontalHeaderLabels([
            "Nombre",
            "Teléfono",
            "Correo",
            "Dirección",
            "Editar",
            "Eliminar"
        ])

        # Las celdas son de solo lectura y al hacer clic se selecciona la fila
        # completa (una a la vez).
        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabla.verticalHeader().setVisible(False)

        # Ancho de columnas: Nombre, Correo y Dirección se estiran; las demás se
        # ajustan a su contenido.
        self.tabla.horizontalHeader().setStretchLastSection(
            False
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        layout_principal.addWidget(self.tabla)

        # Mensaje que aparece cuando la tabla está vacía o la búsqueda no encuentra
        # resultados.
        self.mensaje = QLabel(
            "No hay clientas registradas."
        )

        self.mensaje.setAlignment(
            Qt.AlignCenter
        )

        self.mensaje.setStyleSheet("""
            color: #999999;
            padding: 10px;
        """)

        layout_principal.addWidget(
            self.mensaje
        )

        # Actualizar tabla
        self.actualizar_tabla()

    # Abre el formulario vacío; si se guarda, agrega la clienta a la lista, respalda
    # en MySQL y refresca la tabla.
    def nueva_clienta(self):

        formulario = FormularioCliente(
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.clientes.append(datos)

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cliente registrada",
                "La clienta se ha registrado correctamente."
            )


    # Abre el formulario con los datos de la clienta en la posición 'indice' y
    # reemplaza sus datos al guardar.
    def editar_clienta(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.clientes):
            return

        cliente = self.clientes[indice]

        formulario = FormularioCliente(
            cliente=cliente,
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.clientes[indice] = datos

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cliente actualizada",
                "La información se ha actualizado correctamente."
            )


    # Pide confirmación y, si la respuesta es Sí, elimina la clienta de la lista y de
    # MySQL.
    def eliminar_clienta(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.clientes):
            return

        cliente = self.clientes[indice]

        respuesta = QMessageBox.question(
            self,
            "Eliminar clienta",
            (
                "¿Estás segura de que deseas eliminar a "
                f"{cliente['nombre']}?"
            ),
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:

            # Quita la clienta de la lista en memoria.
            del self.clientes[indice]

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cliente eliminada",
                "La clienta ha sido eliminada correctamente."
            )

    # Redibuja la tabla. Si recibe una lista filtrada (resultado de búsqueda) muestra
    # solo esa; si no, muestra todas las clientas.
    def actualizar_tabla(
        self,
        clientes_mostrar=None
    ):

        if clientes_mostrar is None:
            clientes_mostrar = self.clientes

        self.tabla.setRowCount(
            len(clientes_mostrar)
        )

        # Una fila por clienta: primero las 4 celdas de texto y luego los botones.
        for fila, cliente in enumerate(
            clientes_mostrar
        ):

            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    cliente["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    cliente["telefono"]
                )
            )

            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    cliente["correo"]
                )
            )

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    cliente["direccion"]
                )
            )

            # Botón de editar de esta fila.
            boton_editar = QPushButton("✏")

            boton_editar.setCursor(
                Qt.PointingHandCursor
            )

            boton_editar.setStyleSheet("""
                QPushButton {
                    border: none;
                    color: #8e44ad;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #732d91;
                }
            """)

            # Posición real en la lista completa (la fila de la tabla puede no
            # coincidir cuando hay un filtro activo).
            indice_real = self.clientes.index(
                cliente
            )

            boton_editar.clicked.connect(
                lambda checked=False,
                i=indice_real:
                self.editar_clienta(i)
            )

            self.tabla.setCellWidget(
                fila,
                4,
                boton_editar
            )

            # Botón de eliminar de esta fila.
            boton_eliminar = QPushButton("🗑")

            boton_eliminar.setCursor(
                Qt.PointingHandCursor
            )

            boton_eliminar.setStyleSheet("""
                QPushButton {
                    border: none;
                    color: #c0392b;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #922b21;
                }
            """)

            boton_eliminar.clicked.connect(
                lambda checked=False,
                i=indice_real:
                self.eliminar_clienta(i)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                boton_eliminar
            )

        # Muestra u oculta el mensaje de 'sin resultados' según haya filas o no.
        if len(clientes_mostrar) == 0:

            if len(self.clientes) == 0:

                self.mensaje.setText(
                    "No hay clientas registradas."
                )

            else:

                self.mensaje.setText(
                    "No se encontraron clientas."
                )

            self.mensaje.show()

        else:

            self.mensaje.hide()

    # Filtra las clientas cuyo nombre contenga el texto escrito (sin distinguir
    # mayúsculas de minúsculas).
    def buscar_clientes(self):

        texto = (
            self.buscar.text()
            .strip()
            .lower()
        )

        if not texto:

            self.actualizar_tabla()

            return

        clientes_filtrados = []

        for cliente in self.clientes:

            nombre = cliente["nombre"].lower()

            if texto in nombre:

                clientes_filtrados.append(
                    cliente
                )

        self.actualizar_tabla(
            clientes_filtrados
        )