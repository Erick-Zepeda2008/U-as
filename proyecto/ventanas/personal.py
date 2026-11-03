# Módulo PERSONAL: permite ver, buscar, registrar, editar y eliminar al personal del
# salón.
# Contiene el formulario (ventana emergente) y la página con la tabla.

import PySide6.QtWidgets

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# datos contiene la lista compartida del personal (datos.personal).
from . import datos
# Se llama después de cada cambio para guardar en MySQL.
from .datos import guardar_en_mysql


# Diálogo (ventana emergente) para registrar o editar a un integrante del personal.
class FormularioPersonal(PySide6.QtWidgets.QDialog):

    # Si recibe 'personal' se abre en modo edición; si es None, en modo registro.
    def __init__(self, personal=None, parent=None):
        super().__init__(parent)

        self.personal = personal

        if personal:
            self.setWindowTitle("Editar personal")
        else:
            self.setWindowTitle("Nuevo personal")

        self.setMinimumWidth(400)

        self.crear_formulario()

    # Construye el título, los campos y los botones Guardar/Cancelar.
    def crear_formulario(self):

        layout_principal = PySide6.QtWidgets.QVBoxLayout(self)

        titulo = PySide6.QtWidgets.QLabel(
            "Editar información del personal"
            if self.personal
            else "Registrar nuevo personal"
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

        formulario = PySide6.QtWidgets.QFormLayout()

        # Campos de texto: nombre, teléfono y especialidad.
        self.nombre = PySide6.QtWidgets.QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")

        self.telefono = PySide6.QtWidgets.QLineEdit()
        self.telefono.setPlaceholderText("Número de teléfono")

        self.especialidad = PySide6.QtWidgets.QLineEdit()
        self.especialidad.setPlaceholderText(
            "Ej. Manicure, pedicure, uñas acrílicas..."
        )

        # Lista desplegable que indica qué tan ocupada está la persona.
        self.carga = PySide6.QtWidgets.QComboBox()
        self.carga.addItems([
            "Disponible",
            "Carga baja",
            "Carga media",
            "Carga alta"
        ])

        formulario.addRow("Nombre:", self.nombre)
        formulario.addRow("Teléfono:", self.telefono)
        formulario.addRow("Especialidad:", self.especialidad)
        formulario.addRow("Carga de trabajo:", self.carga)

        layout_principal.addLayout(formulario)

        # Modo edición: rellena los campos con los datos actuales y selecciona la
        # carga de trabajo guardada.
        if self.personal:

            self.nombre.setText(self.personal["nombre"])
            self.telefono.setText(self.personal["telefono"])
            self.especialidad.setText(self.personal["especialidad"])

            indice = self.carga.findText(
                self.personal["carga"]
            )

            if indice >= 0:
                self.carga.setCurrentIndex(indice)

        botones = PySide6.QtWidgets.QDialogButtonBox(
            PySide6.QtWidgets.QDialogButtonBox.Save |
            PySide6.QtWidgets.QDialogButtonBox.Cancel
        )

        botones.button(
            PySide6.QtWidgets.QDialogButtonBox.Save
        ).setText("Guardar")

        botones.button(
            PySide6.QtWidgets.QDialogButtonBox.Cancel
        ).setText("Cancelar")

        # Guardar valida los datos antes de cerrar; Cancelar cierra sin guardar.
        botones.accepted.connect(
            self.validar_y_aceptar
        )

        botones.rejected.connect(
            self.reject
        )

        layout_principal.addWidget(botones)

    # Exige nombre, teléfono y especialidad. Si falta alguno, avisa y no cierra la
    # ventana.
    def validar_y_aceptar(self):

        nombre = self.nombre.text().strip()
        telefono = self.telefono.text().strip()
        especialidad = self.especialidad.text().strip()

        if not nombre:

            PySide6.QtWidgets.QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el nombre del personal."
            )

            self.nombre.setFocus()

            return

        if not telefono:

            PySide6.QtWidgets.QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el número de teléfono."
            )

            self.telefono.setFocus()

            return

        if not especialidad:

            PySide6.QtWidgets.QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar la especialidad."
            )

            self.especialidad.setFocus()

            return

        # Datos completos: cierra el diálogo con resultado 'aceptado'.
        self.accept()

    # Devuelve lo escrito en el formulario como diccionario.
    def obtener_datos(self):

        return {
            "nombre": self.nombre.text().strip(),
            "telefono": self.telefono.text().strip(),
            "especialidad": self.especialidad.text().strip(),
            "carga": self.carga.currentText()
        }


# Página principal del módulo PERSONAL: buscador, botón de nuevo personal y tabla.
class PaginaPersonal(PySide6.QtWidgets.QWidget):

    # Guarda una referencia a la lista compartida datos.personal y construye la
    # interfaz.
    # (Nota: ahora los datos se respaldan en MySQL con guardar_en_mysql(), aunque el
    # comentario de abajo diga 'en memoria'.)
    def __init__(self):

        super().__init__()

        # Por ahora el personal se almacena
        # temporalmente en memoria.
        self.personal = datos.personal

        self.crear_interfaz()

    # Construye la página: título, buscador, botón de nuevo personal y tabla.
    def crear_interfaz(self):

        layout_principal = PySide6.QtWidgets.QVBoxLayout(self)

        layout_principal.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout_principal.setSpacing(15)

        titulo = PySide6.QtWidgets.QLabel("PERSONAL")

        fuente_titulo = QFont()
        fuente_titulo.setPointSize(26)
        fuente_titulo.setBold(True)

        titulo.setFont(fuente_titulo)

        titulo.setStyleSheet("""
            color: #8e44ad;
        """)

        layout_principal.addWidget(titulo)

        descripcion = PySide6.QtWidgets.QLabel(
            "Registra, consulta, edita y administra "
            "la información del personal."
        )

        descripcion.setStyleSheet("""
            color: #777777;
            font-size: 13px;
        """)

        layout_principal.addWidget(descripcion)

        barra_busqueda = PySide6.QtWidgets.QHBoxLayout()

        # Buscador por nombre: la tabla se filtra mientras se escribe.
        self.buscar = PySide6.QtWidgets.QLineEdit()

        self.buscar.setPlaceholderText(
            "Buscar por nombre..."
        )

        self.buscar.setMinimumHeight(38)

        self.buscar.textChanged.connect(
            self.buscar_personal
        )

        barra_busqueda.addWidget(
            self.buscar
        )

        boton_buscar = PySide6.QtWidgets.QPushButton("BUSCAR")

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
            self.buscar_personal
        )

        barra_busqueda.addWidget(
            boton_buscar
        )

        layout_principal.addLayout(
            barra_busqueda
        )

        fila_botones = PySide6.QtWidgets.QHBoxLayout()

        fila_botones.addStretch()

        boton_nuevo = PySide6.QtWidgets.QPushButton(
            "+ NUEVO PERSONAL"
        )

        boton_nuevo.setCursor(
            Qt.PointingHandCursor
        )

        boton_nuevo.setMinimumHeight(40)

        boton_nuevo.setStyleSheet("""
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

        boton_nuevo.clicked.connect(
            self.nuevo_personal
        )

        fila_botones.addWidget(
            boton_nuevo
        )

        layout_principal.addLayout(
            fila_botones
        )

        # Tabla del personal: Nombre, Teléfono, Especialidad y Carga de trabajo, más
        # los botones Editar y Eliminar de cada fila.
        self.tabla = PySide6.QtWidgets.QTableWidget()

        self.tabla.setColumnCount(6)

        self.tabla.setHorizontalHeaderLabels([
            "Nombre",
            "Teléfono",
            "Especialidad",
            "Carga de trabajo",
            "Editar",
            "Eliminar"
        ])

        self.tabla.setEditTriggers(
            PySide6.QtWidgets.QTableWidget.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            PySide6.QtWidgets.QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            PySide6.QtWidgets.QTableWidget.SingleSelection
        )

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.horizontalHeader().setStretchLastSection(
            False
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            0,
            PySide6.QtWidgets.QHeaderView.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            1,
            PySide6.QtWidgets.QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            2,
            PySide6.QtWidgets.QHeaderView.Stretch
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            3,
            PySide6.QtWidgets.QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            4,
            PySide6.QtWidgets.QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            5,
            PySide6.QtWidgets.QHeaderView.ResizeToContents
        )

        layout_principal.addWidget(
            self.tabla
        )

        # Mensaje que aparece cuando la tabla está vacía o la búsqueda no encuentra
        # resultados.
        self.mensaje = PySide6.QtWidgets.QLabel(
            "No hay personal registrado."
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

        self.actualizar_tabla()

    # Abre el formulario vacío; si se guarda, agrega a la persona a la lista, respalda
    # en MySQL y refresca la tabla.
    def nuevo_personal(self):

        formulario = FormularioPersonal(
            parent=self
        )

        resultado = formulario.exec()

        if resultado == PySide6.QtWidgets.QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.personal.append(datos)

            guardar_en_mysql()

            self.actualizar_tabla()

            PySide6.QtWidgets.QMessageBox.information(
                self,
                "Personal registrado",
                "El personal se ha registrado correctamente."
            )

    # Abre el formulario con los datos de la persona en la posición 'indice' y
    # reemplaza sus datos al guardar.
    def editar_personal(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.personal):
            return

        persona = self.personal[indice]

        formulario = FormularioPersonal(
            personal=persona,
            parent=self
        )

        resultado = formulario.exec()

        if resultado == PySide6.QtWidgets.QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.personal[indice] = datos

            guardar_en_mysql()

            self.actualizar_tabla()

            PySide6.QtWidgets.QMessageBox.information(
                self,
                "Personal actualizado",
                "La información se ha actualizado correctamente."
            )

    # Pide confirmación y, si la respuesta es Sí, elimina a la persona de la lista y
    # de MySQL.
    def eliminar_personal(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.personal):
            return

        persona = self.personal[indice]

        respuesta = PySide6.QtWidgets.QMessageBox.question(
            self,
            "Eliminar personal",
            (
                "¿Estás segura de que deseas eliminar a "
                f"{persona['nombre']}?"
            ),
            PySide6.QtWidgets.QMessageBox.Yes |
            PySide6.QtWidgets.QMessageBox.No
        )

        if respuesta == PySide6.QtWidgets.QMessageBox.Yes:

            # Quita a la persona de la lista en memoria.
            del self.personal[indice]

            guardar_en_mysql()

            self.actualizar_tabla()

            PySide6.QtWidgets.QMessageBox.information(
                self,
                "Personal eliminado",
                "El personal ha sido eliminado correctamente."
            )

    # Redibuja la tabla. Si recibe una lista filtrada (resultado de búsqueda) muestra
    # solo esa; si no, muestra a todo el personal.
    def actualizar_tabla(
        self,
        personal_mostrar=None
    ):

        if personal_mostrar is None:
            personal_mostrar = self.personal

        self.tabla.setRowCount(
            len(personal_mostrar)
        )

        # Una fila por persona: primero las 4 celdas de texto y luego los botones de
        # editar y eliminar.
        for fila, persona in enumerate(
            personal_mostrar
        ):

            self.tabla.setItem(
                fila,
                0,
                PySide6.QtWidgets.QTableWidgetItem(
                    persona["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                PySide6.QtWidgets.QTableWidgetItem(
                    persona["telefono"]
                )
            )

            self.tabla.setItem(
                fila,
                2,
                PySide6.QtWidgets.QTableWidgetItem(
                    persona["especialidad"]
                )
            )

            self.tabla.setItem(
                fila,
                3,
                PySide6.QtWidgets.QTableWidgetItem(
                    persona["carga"]
                )
            )

            boton_editar = PySide6.QtWidgets.QPushButton("✏")

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
            indice_real = self.personal.index(
                persona
            )

            boton_editar.clicked.connect(
                lambda checked=False,
                i=indice_real:
                self.editar_personal(i)
            )

            self.tabla.setCellWidget(
                fila,
                4,
                boton_editar
            )

            boton_eliminar = PySide6.QtWidgets.QPushButton("🗑")

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
                self.eliminar_personal(i)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                boton_eliminar
            )

        # Muestra u oculta el mensaje de 'sin resultados' según haya filas o no.
        if len(personal_mostrar) == 0:

            if len(self.personal) == 0:

                self.mensaje.setText(
                    "No hay personal registrado."
                )

            else:

                self.mensaje.setText(
                    "No se encontró personal."
                )

            self.mensaje.show()

        else:

            self.mensaje.hide()

    # Filtra al personal cuyo nombre contenga el texto escrito (sin distinguir
    # mayúsculas de minúsculas).
    def buscar_personal(self):

        texto = (
            self.buscar.text()
            .strip()
            .lower()
        )

        if not texto:

            self.actualizar_tabla()

            return

        personal_filtrado = []

        for persona in self.personal:

            nombre = persona["nombre"].lower()

            if texto in nombre:

                personal_filtrado.append(
                    persona
                )

        self.actualizar_tabla(
            personal_filtrado
        )