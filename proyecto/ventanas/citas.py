# Módulo CITAS: permite agendar, editar, cancelar y completar citas.
# Evita que una misma persona tenga dos citas que se crucen y, al completar una cita,
# descuenta los insumos del inventario.

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTimeEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QHeaderView
)

# QDate y QTime manejan fechas y horas.
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont

# datos da acceso a las listas compartidas: clientes, servicios, personal, insumos y
# citas.
from . import datos
# Se llama después de cada cambio para guardar en MySQL.
from .datos import guardar_en_mysql


class FormularioCita(QDialog):
    """
    Formulario para registrar o editar una cita.
    """

    # Si recibe 'cita' se abre en modo edición; si es None, en modo registro.
    def __init__(self, cita=None, parent=None):
        super().__init__(parent)

        self.cita = cita

        if cita:
            self.setWindowTitle("Editar cita")
        else:
            self.setWindowTitle("Nueva cita")

        self.setMinimumWidth(430)

        self.crear_formulario()

    # Construye el formulario: clienta, servicio, personal, fecha y hora.
    def crear_formulario(self):

        layout_principal = QVBoxLayout(self)

        titulo = QLabel(
            "Editar cita"
            if self.cita
            else "Registrar nueva cita"
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


        formulario = QFormLayout()
    
        # Listas desplegables llenadas con lo ya registrado (clientas, servicios y
        # personal).
        # La primera opción es un texto guía ('Seleccionar ...') que no cuenta como
        # elección válida.
        self.cliente = QComboBox()

        self.cliente.addItem("Seleccionar clienta")

        for cliente in datos.clientes:
            self.cliente.addItem(cliente["nombre"])

       
        self.servicio = QComboBox()

        self.servicio.addItem("Seleccionar servicio")

        for servicio in datos.servicios:
           self.servicio.addItem(servicio["nombre"])

        self.personal = QComboBox()

        self.personal.addItem("Seleccionar personal")

        for persona in datos.personal:
          self.personal.addItem(persona["nombre"])


        # Selector de fecha con calendario emergente (formato dd/MM/yyyy); empieza en
        # el día de hoy.
        self.fecha = QDateEdit()

        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setDisplayFormat("dd/MM/yyyy")

        # Selector de hora (formato hh:mm); empieza en la hora actual.
        self.hora = QTimeEdit()

        self.hora.setTime(
            QTime.currentTime()
        )

        self.hora.setDisplayFormat(
            "hh:mm"
        )

        formulario.addRow(
            "Clienta:",
            self.cliente
        )

        formulario.addRow(
            "Servicio:",
            self.servicio
        )

        formulario.addRow(
            "Personal:",
            self.personal
        )

        formulario.addRow(
            "Fecha:",
            self.fecha
        )

        formulario.addRow(
            "Hora:",
            self.hora
        )

        layout_principal.addLayout(
            formulario
        )

        # Modo edición: selecciona en cada lista los valores de la cita y coloca su
        # fecha y hora.
        if self.cita:

            self.seleccionar_combo(
                self.cliente,
                self.cita["cliente"]
            )

            self.seleccionar_combo(
                self.servicio,
                self.cita["servicio"]
            )

            self.seleccionar_combo(
                self.personal,
                self.cita["personal"]
            )

            # Convierte los textos guardados ('dd/MM/yyyy' y 'hh:mm') otra vez a fecha
            # y hora.
            fecha = QDate.fromString(
                self.cita["fecha"],
                "dd/MM/yyyy"
            )

            hora = QTime.fromString(
                self.cita["hora"],
                "hh:mm"
            )

            if fecha.isValid():
                self.fecha.setDate(fecha)

            if hora.isValid():
                self.hora.setTime(hora)

        botones = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        # Guardar valida los datos antes de cerrar; Cancelar cierra sin guardar.
        botones.accepted.connect(
            self.validar_y_aceptar
        )

        botones.rejected.connect(
            self.reject
        )

        layout_principal.addWidget(
            botones
        )

    # Selecciona en una lista desplegable el elemento que tenga ese texto, si existe.
    def seleccionar_combo(
        self,
        combo,
        texto
    ):

        indice = combo.findText(
            texto
        )

        if indice >= 0:
            combo.setCurrentIndex(
                indice
            )

    # Exige elegir clienta, servicio y personal (la posición 0 es el texto guía). Si
    # falta algo, avisa y no cierra.
    def validar_y_aceptar(self):

        if self.cliente.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes seleccionar una clienta."
            )

            return

        if self.servicio.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes seleccionar un servicio."
            )

            return

        if self.personal.currentIndex() == 0:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes seleccionar al personal que atenderá."
            )

            return

        # Todo correcto: cierra el diálogo con resultado 'aceptado'.
        self.accept()

    # Devuelve la cita como diccionario. La duración se toma del servicio elegido y
    # sirve para detectar choques de horario.
    def obtener_datos(self):

        nombre_servicio = self.servicio.currentText()

        duracion = 0

        # Busca la duración del servicio elegido.
        for servicio in datos.servicios:
           if servicio["nombre"] == nombre_servicio:
            duracion = servicio["duracion"]
            break

        return {
        "cliente": self.cliente.currentText(),
        "servicio": nombre_servicio,
        "personal": self.personal.currentText(),
        "fecha": self.fecha.date().toString(
            "dd/MM/yyyy"
        ),
        "hora": self.hora.time().toString(
            "hh:mm"
        ),
        "duracion": duracion
    }

class PaginaCitas(QWidget):
    """
    Página principal del módulo CITAS.
    """

    # Guarda una referencia a la lista compartida datos.citas y construye la interfaz.
    def __init__(self):
        super().__init__()

        # Las citas ahora se comparten a través de datos.py
        # y quedan respaldadas en MySQL.
        self.citas = datos.citas

        self.crear_interfaz()

    # Construye la página: título, botón para agendar y tabla de citas.
    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout_principal.setSpacing(15)


        titulo = QLabel("CITAS")

        fuente_titulo = QFont()
        fuente_titulo.setPointSize(26)
        fuente_titulo.setBold(True)

        titulo.setFont(fuente_titulo)

        titulo.setStyleSheet("""
            color: #8e44ad;
        """)

        layout_principal.addWidget(
            titulo
        )


        descripcion = QLabel(
            "Programa, consulta, modifica y administra "
            "las citas de Chikys Nails."
        )

        descripcion.setStyleSheet("""
            color: #777777;
            font-size: 13px;
        """)

        layout_principal.addWidget(
            descripcion
        )


        fila_botones = QHBoxLayout()

        fila_botones.addStretch()

        boton_nueva = QPushButton(
            "+ NUEVA CITA"
        )

        boton_nueva.setCursor(
            Qt.PointingHandCursor
        )

        boton_nueva.setMinimumHeight(
            40
        )

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
            self.nueva_cita
        )

        fila_botones.addWidget(
            boton_nueva
        )

        layout_principal.addLayout(
            fila_botones
        )


        # Tabla de citas: Clienta, Servicio, Personal, Fecha y Hora, más los botones
        # Editar, Cancelar y Completar de cada fila.
        self.tabla = QTableWidget()

        self.tabla.setColumnCount(8)

        self.tabla.setHorizontalHeaderLabels([
            "Clienta",
            "Servicio",
            "Personal",
            "Fecha",
            "Hora",
            "Editar",
            "Cancelar",
            "Completar"
        ])

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabla.verticalHeader().setVisible(
            False
        )

      
        # Ajuste del ancho de cada columna.
        header = self.tabla.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        layout_principal.addWidget(
            self.tabla
        )

        # Mensaje que aparece cuando no hay citas registradas.
        self.mensaje = QLabel(
            "No hay citas registradas."
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


    # Abre el formulario; antes de guardar verifica que la persona no tenga otra cita
    # que se cruce en horario.
    def nueva_cita(self):

        formulario = FormularioCita(
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()


            # Evita dobles reservas para la misma persona.
            if self.existe_cita(
                datos["fecha"],
                datos["hora"],
                datos["personal"],
                datos["duracion"]
            ):

                QMessageBox.warning(
                    self,
                    "Horario ocupado",
                    (
                        "El personal seleccionado ya "
                        "tiene una cita en esa fecha y hora."
                    )
                )

                return

            # Toda cita nueva empieza como pendiente.
            datos["completada"] = False

            self.citas.append(datos)

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cita registrada",
                "La cita se ha registrado correctamente."
            )

    # Edita una cita existente. Al comprobar choques de horario se ignora la propia
    # cita (indice_excluir).
    def editar_cita(self, indice):

        if indice < 0 or indice >= len(
            self.citas
        ):
            return

        cita = self.citas[indice]

        formulario = FormularioCita(
            cita=cita,
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()

            # Evita dobles reservas para la misma persona.
            if self.existe_cita(
                datos["fecha"],
                datos["hora"],
                datos["personal"],
                datos["duracion"],
                indice_excluir=indice
            ):

                QMessageBox.warning(
                    self,
                    "Horario ocupado",
                    (
                        "El personal seleccionado ya "
                        "tiene otra cita en esa fecha y hora."
                    )
                )

                return

            self.citas[indice] = datos

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cita actualizada",
                "La cita se ha actualizado correctamente."
            )

    # Pide confirmación y, si la respuesta es Sí, elimina la cita de la lista y de
    # MySQL.
    def cancelar_cita(self, indice):

        if indice < 0 or indice >= len(
            self.citas
        ):
            return

        cita = self.citas[indice]

        respuesta = QMessageBox.question(
            self,
            "Cancelar cita",
            (
                "¿Deseas cancelar la cita de "
                f"{cita['cliente']}?"
            ),
            QMessageBox.Yes |
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:

            del self.citas[indice]

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Cita cancelada",
                "La cita ha sido cancelada correctamente."
            )

  
    # Marca la cita como completada y descuenta del inventario los insumos que usa el
    # servicio.
    # Primero verifica que haya existencias suficientes de TODOS los insumos, para no
    # descontar a medias.
    def completar_cita(self, cita):

        # Si la cita ya estaba completada, solo avisa y no hace nada más.
        if cita.get("completada", False):

            QMessageBox.information(
                self,
                "Cita completada",
                "Esta cita ya fue completada."
            )

            return

        servicio_encontrado = None

        # Busca el servicio de la cita para saber qué insumos consume.
        for servicio in datos.servicios:

            if servicio["nombre"] == cita["servicio"]:

                servicio_encontrado = servicio

                break

        if servicio_encontrado is None:

            QMessageBox.warning(
                self,
                "Servicio no encontrado",
                "No se encontró el servicio asociado a esta cita."
            )

            return

        insumos = servicio_encontrado.get(
            "insumos",
            []
        )

        # Servicio sin insumos: solo se marca la cita como completada.
        if not insumos:

            cita["completada"] = True

            guardar_en_mysql()

            QMessageBox.information(
                self,
                "Cita completada",
                "La cita se ha completado correctamente."
            )

            self.actualizar_tabla()

            return

        # PASO 1 (verificar): comprueba que cada insumo exista y alcance. Si algo
        # falla, se cancela sin descontar nada.
        for insumo_servicio in insumos:

            insumo_encontrado = None

            for insumo in datos.insumos:

                if insumo["nombre"] == insumo_servicio["nombre"]:

                    insumo_encontrado = insumo

                    break

            if insumo_encontrado is None:

                QMessageBox.warning(
                    self,
                    "Insumo no encontrado",
                    f'No se encontró el insumo '
                    f'"{insumo_servicio["nombre"]}" '
                    f'en el inventario.'
                )

                return

            cantidad_necesaria = insumo_servicio["cantidad"]

            if insumo_encontrado["cantidad"] < cantidad_necesaria:

                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f'No hay suficiente stock de '
                    f'"{insumo_encontrado["nombre"]}".\n\n'
                    f'Disponible: '
                    f'{insumo_encontrado["cantidad"]}\n'
                    f'Necesario: '
                    f'{cantidad_necesaria}'
                )

                return

        # PASO 2 (descontar): ya está todo verificado, ahora sí se resta cada insumo
        # del inventario.
        for insumo_servicio in insumos:

            for insumo in datos.insumos:

                if insumo["nombre"] == insumo_servicio["nombre"]:

                    insumo["cantidad"] -= (
                        insumo_servicio["cantidad"]
                    )

                    break

        cita["completada"] = True

        guardar_en_mysql()

        QMessageBox.information(
            self,
            "Cita completada",
            "La cita se ha completado y los insumos "
            "han sido descontados del inventario."
        )

        self.actualizar_tabla()


    # Devuelve True si la persona ya tiene otra cita que se cruza con el horario dado
    # (misma fecha, mismo personal y horas que se solapan). 'indice_excluir' omite una
    # cita, la que se está editando.
    def existe_cita(
    self,
    fecha,
    hora,
    personal,
    duracion,
    indice_excluir=None
):

     nueva_hora_inicio = QTime.fromString(
        hora,
        "hh:mm"
    )

     # Hora de fin = hora de inicio + duración (los minutos se pasan a segundos con *
     # 60).
     nueva_hora_fin = nueva_hora_inicio.addSecs(
        duracion * 60
    )

     for indice, cita in enumerate(
        self.citas
    ):

        # Omite la cita que se está editando.
        if indice == indice_excluir:
            continue

        if (
            cita["fecha"] != fecha
            or cita["personal"] != personal
        ):
            continue

        # Inicio y fin de la cita que ya existe.
        hora_inicio = QTime.fromString(
            cita["hora"],
            "hh:mm"
        )

        hora_fin = hora_inicio.addSecs(
            cita["duracion"] * 60
        )

        if (
            nueva_hora_inicio < hora_fin
            and nueva_hora_fin > hora_inicio
        ):
            # Hay cruce: la nueva cita empieza antes de que termine la otra y termina
            # después de que la otra empieza.
            return True

     return False

    # Redibuja la tabla con todas las citas.
    def actualizar_tabla(self):

        self.tabla.setRowCount(
            len(self.citas)
        )

        for fila, cita in enumerate(
            self.citas
        ):

            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    cita["cliente"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    cita["servicio"]
                )
            )

            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    cita["personal"]
                )
            )

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    cita["fecha"]
                )
            )

            self.tabla.setItem(
                fila,
                4,
                QTableWidgetItem(
                    cita["hora"]
                )
            )

            # Botones de cada fila: ✏ editar, 🗑 cancelar y ✓ completar.
            boton_editar = QPushButton(
                "✏"
            )

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

            boton_editar.clicked.connect(
                lambda checked=False,
                i=fila:
                self.editar_cita(i)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                boton_editar
            )

            boton_cancelar = QPushButton(
                "🗑"
            )

            boton_cancelar.setCursor(
                Qt.PointingHandCursor
            )

            boton_cancelar.setStyleSheet("""
                QPushButton {
                    border: none;
                    color: #c0392b;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #922b21;
                }
            """)

            boton_cancelar.clicked.connect(
                lambda checked=False,
                i=fila:
                self.cancelar_cita(i)
            )

            self.tabla.setCellWidget(
                fila,
                6,
                boton_cancelar
            )

            boton_completar = QPushButton(
                "✓"
            )

            boton_completar.setCursor(
                Qt.PointingHandCursor
            )

            boton_completar.setStyleSheet("""
                QPushButton {
                    border: none;
                    color: #27ae60;
                    font-size: 16px;
                }

                QPushButton:hover {
                    color: #1e8449;
                }
            """)

            boton_completar.clicked.connect(
                lambda checked=False,
                i=fila:
                self.completar_cita(self.citas[i])
            )

            self.tabla.setCellWidget(
                fila,
                7,
                boton_completar
            )

            # Una cita completada ya no se puede editar, cancelar ni completar de
            # nuevo (sus botones se deshabilitan).
            if cita.get("completada", False):

                boton_editar.setEnabled(False)
                boton_cancelar.setEnabled(False)
                boton_completar.setEnabled(False)

        # Muestra u oculta el mensaje de 'no hay citas' según haya filas o no.
        if len(self.citas) == 0:

            self.mensaje.show()

        else:

            self.mensaje.hide()