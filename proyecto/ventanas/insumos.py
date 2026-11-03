# Módulo INSUMOS: inventario de materiales del salón (esmaltes, herramientas, etc.).
# Permite ver, buscar, registrar, editar y eliminar insumos, y avisa cuando el stock
# está bajo.

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
    QHeaderView,
    QComboBox,
    QDoubleSpinBox
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from . import datos
# Se llama después de cada cambio para guardar en MySQL.
from .datos import guardar_en_mysql


# Diálogo para registrar o editar un insumo: nombre, categoría, cantidad, unidad y
# stock mínimo.
class FormularioInsumo(QDialog):

    # Si recibe 'insumo' se abre en modo edición; si es None, en modo registro.
    def __init__(self, insumo=None, parent=None):
        super().__init__(parent)

        self.insumo = insumo

        if insumo:
            self.setWindowTitle("Editar insumo")
        else:
            self.setWindowTitle("Nuevo insumo")

        self.setMinimumWidth(400)

        self.crear_formulario()

    # Construye el título, los campos y los botones del diálogo.
    def crear_formulario(self):

        layout_principal = QVBoxLayout(self)

        # ==================================================
        # TÍTULO
        # ==================================================

        titulo = QLabel(
            "Editar información del insumo"
            if self.insumo
            else "Registrar nuevo insumo"
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

        # ==================================================
        # FORMULARIO
        # ==================================================

        formulario = QFormLayout()

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre del insumo")

        # Categorías para clasificar el insumo.
        self.categoria = QComboBox()

        self.categoria.addItems([
            "Esmaltes",
            "Herramientas",
            "Limpieza",
            "Decoración",
            "Desechables",
            "Otros"
        ])

        # Cantidad en existencia (admite decimales, de 0 a 999999).
        self.cantidad = QDoubleSpinBox()
        self.cantidad.setRange(0, 999999)
        self.cantidad.setDecimals(2)
        self.cantidad.setSingleStep(1)

        # Unidad en que se mide la cantidad.
        self.unidad = QComboBox()

        self.unidad.addItems([
            "Unidades",
            "Paquetes",
            "Frascos",
            "Mililitros",
            "Litros"
        ])

        # Stock mínimo: si la cantidad baja a este valor o menos, la tabla marca el
        # insumo con ⚠.
        self.stock_minimo = QDoubleSpinBox()
        self.stock_minimo.setRange(0, 999999)
        self.stock_minimo.setDecimals(2)
        self.stock_minimo.setSingleStep(1)

        formulario.addRow(
            "Nombre:",
            self.nombre
        )

        formulario.addRow(
            "Categoría:",
            self.categoria
        )

        formulario.addRow(
            "Cantidad:",
            self.cantidad
        )

        formulario.addRow(
            "Unidad:",
            self.unidad
        )

        formulario.addRow(
            "Stock mínimo:",
            self.stock_minimo
        )

        layout_principal.addLayout(formulario)

        # ==================================================
        # CARGAR DATOS SI ES EDICIÓN
        # ==================================================

        if self.insumo:

            self.nombre.setText(
                self.insumo["nombre"]
            )

            indice_categoria = self.categoria.findText(
                self.insumo["categoria"]
            )

            if indice_categoria >= 0:
                self.categoria.setCurrentIndex(
                    indice_categoria
                )

            self.cantidad.setValue(
                self.insumo["cantidad"]
            )

            indice_unidad = self.unidad.findText(
                self.insumo["unidad"]
            )

            if indice_unidad >= 0:
                self.unidad.setCurrentIndex(
                    indice_unidad
                )

            self.stock_minimo.setValue(
                self.insumo["stock_minimo"]
            )

        # ==================================================
        # BOTONES
        # ==================================================

        botones = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        # Solo cambiamos el texto visible.
        # Los nombres internos de PySide6 se mantienen.
        botones.button(
            QDialogButtonBox.Save
        ).setText("Guardar")

        botones.button(
            QDialogButtonBox.Cancel
        ).setText("Cancelar")

        botones.accepted.connect(
            self.validar_y_aceptar
        )

        botones.rejected.connect(
            self.reject
        )

        layout_principal.addWidget(
            botones
        )

    # ==================================================
    # VALIDAR FORMULARIO
    # ==================================================

    # Solo exige que el nombre no esté vacío; si lo está, avisa y no cierra.
    def validar_y_aceptar(self):

        nombre = self.nombre.text().strip()

        if not nombre:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debes ingresar el nombre del insumo."
            )

            self.nombre.setFocus()

            return

        self.accept()

    # ==================================================
    # OBTENER DATOS
    # ==================================================

    # Devuelve lo escrito en el formulario como diccionario.
    def obtener_datos(self):

        return {
            "nombre": self.nombre.text().strip(),
            "categoria": self.categoria.currentText(),
            "cantidad": self.cantidad.value(),
            "unidad": self.unidad.currentText(),
            "stock_minimo": self.stock_minimo.value()
        }


# Página principal del módulo INSUMOS: buscador, botón de nuevo insumo y tabla del
# inventario.
class PaginaInsumos(QWidget):

    # Guarda una referencia a la lista compartida datos.insumos y construye la
    # interfaz.
    def __init__(self):

        super().__init__()

        self.insumos = datos.insumos

        self.crear_interfaz()

    # Qt lo ejecuta cada vez que la página se muestra: refresca la tabla, porque al
    # completar citas se pueden haber descontado insumos.
    def showEvent(self, event):

        self.actualizar_tabla()

        super().showEvent(event)

    # Construye la página: título, buscador, botón de nuevo insumo y tabla.
    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout_principal.setSpacing(15)

        titulo = QLabel("INSUMOS")

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
            "Registra, consulta, edita y administra "
            "el inventario de insumos."
        )

        descripcion.setStyleSheet("""
            color: #777777;
            font-size: 13px;
        """)

        layout_principal.addWidget(
            descripcion
        )

        barra_busqueda = QHBoxLayout()

        # Buscador por nombre: la tabla se filtra mientras se escribe.
        self.buscar = QLineEdit()

        self.buscar.setPlaceholderText(
            "Buscar por nombre..."
        )

        self.buscar.setMinimumHeight(38)

        self.buscar.textChanged.connect(
            self.buscar_insumos
        )

        barra_busqueda.addWidget(
            self.buscar
        )

        boton_buscar = QPushButton(
            "BUSCAR"
        )

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
            self.buscar_insumos
        )

        barra_busqueda.addWidget(
            boton_buscar
        )

        layout_principal.addLayout(
            barra_busqueda
        )

        fila_botones = QHBoxLayout()

        fila_botones.addStretch()

        boton_nuevo = QPushButton(
            "+ NUEVO INSUMO"
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
            self.nuevo_insumo
        )

        fila_botones.addWidget(
            boton_nuevo
        )

        layout_principal.addLayout(
            fila_botones
        )

        # Tabla de inventario: Insumo, Categoría, Cantidad, Unidad y Stock mínimo, más
        # los botones Editar y Eliminar.
        self.tabla = QTableWidget()

        self.tabla.setColumnCount(7)

        self.tabla.setHorizontalHeaderLabels([
            "Insumo",
            "Categoría",
            "Cantidad",
            "Unidad",
            "Stock mínimo",
            "Editar",
            "Eliminar"
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
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        layout_principal.addWidget(
            self.tabla
        )

        # Mensaje que aparece cuando la tabla está vacía o la búsqueda no encuentra
        # resultados.
        self.mensaje = QLabel(
            "No hay insumos registrados."
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

    # Abre el formulario vacío; si se guarda, agrega el insumo a la lista, respalda en
    # MySQL y refresca la tabla.
    def nuevo_insumo(self):

        formulario = FormularioInsumo(
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.insumos.append(
                datos
            )

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Insumo registrado",
                "El insumo se ha registrado correctamente."
            )

    # Abre el formulario con el insumo de la posición 'indice' y reemplaza sus datos
    # al guardar.
    def editar_insumo(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.insumos):
            return

        insumo = self.insumos[indice]

        formulario = FormularioInsumo(
            insumo=insumo,
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            datos = formulario.obtener_datos()

            self.insumos[indice] = datos

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Insumo actualizado",
                "La información se ha actualizado correctamente."
            )

    # Pide confirmación y, si la respuesta es Sí, elimina el insumo de la lista y de
    # MySQL.
    def eliminar_insumo(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.insumos):
            return

        insumo = self.insumos[indice]

        respuesta = QMessageBox.question(
            self,
            "Eliminar insumo",
            (
                "¿Estás segura de que deseas eliminar "
                f"el insumo {insumo['nombre']}?"
            ),
            QMessageBox.Yes |
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:

            # Quita el insumo de la lista en memoria.
            del self.insumos[indice]

            guardar_en_mysql()

            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Insumo eliminado",
                "El insumo ha sido eliminado correctamente."
            )

    # Resta una cantidad al insumo (por ejemplo, por uso manual); la cantidad se pide
    # con pedir_cantidad().
    # NOTA: por ahora ningún botón de la tabla llama a este método.
    def descontar_insumo(self, indice):

        # Seguridad: ignora posiciones que no existen en la lista.
        if indice < 0 or indice >= len(self.insumos):
            return

        insumo = self.insumos[indice]

        cantidad_actual = insumo["cantidad"]

        # No se puede descontar si ya no hay existencias.
        if cantidad_actual <= 0:

            QMessageBox.warning(
                self,
                "Sin existencias",
                "Este insumo no tiene existencias disponibles."
            )

            return

        cantidad, ok = self.pedir_cantidad(
            insumo["nombre"],
            cantidad_actual
        )

        if not ok:
            return

        # Resta la cantidad indicada y respalda en MySQL.
        insumo["cantidad"] -= cantidad

        guardar_en_mysql()

        self.actualizar_tabla()

    # Ventana pequeña que pregunta cuánto descontar (mínimo 0.01 y máximo lo que hay).
    # Devuelve (cantidad, True/False según si el usuario aceptó).
    def pedir_cantidad(
        self,
        nombre,
        cantidad_maxima
    ):

        dialogo = QDialog(self)

        dialogo.setWindowTitle(
            "Descontar insumo"
        )

        dialogo.setMinimumWidth(350)

        layout = QVBoxLayout(
            dialogo
        )

        titulo = QLabel(
            f"¿Cuánto deseas descontar de {nombre}?"
        )

        titulo.setWordWrap(True)

        layout.addWidget(
            titulo
        )

        cantidad = QDoubleSpinBox()

        cantidad.setRange(
            0.01,
            cantidad_maxima
        )

        cantidad.setDecimals(2)

        cantidad.setSingleStep(1)

        layout.addWidget(
            cantidad
        )

        botones = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        botones.button(
            QDialogButtonBox.Save
        ).setText("Aceptar")

        botones.button(
            QDialogButtonBox.Cancel
        ).setText("Cancelar")

        botones.accepted.connect(
            dialogo.accept
        )

        botones.rejected.connect(
            dialogo.reject
        )

        layout.addWidget(
            botones
        )

        resultado = dialogo.exec()

        return (
            cantidad.value(),
            resultado == QDialog.Accepted
        )

    # Redibuja la tabla con 'insumos_mostrar' (resultado de búsqueda) o con todos los
    # insumos.
    def actualizar_tabla(
        self,
        insumos_mostrar=None
    ):

        if insumos_mostrar is None:
            insumos_mostrar = self.insumos

        self.tabla.setRowCount(
            len(insumos_mostrar)
        )

        for fila, insumo in enumerate(
            insumos_mostrar
        ):

            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    insumo["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    insumo["categoria"]
                )
            )

            cantidad = insumo["cantidad"]

            # El formato :g quita ceros sobrantes (5.0 se muestra como 5).
            item_cantidad = QTableWidgetItem(
                f"{cantidad:g}"
            )

            self.tabla.setItem(
                fila,
                2,
                item_cantidad
            )

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    insumo["unidad"]
                )
            )

            stock_minimo = insumo[
                "stock_minimo"
            ]

            self.tabla.setItem(
                fila,
                4,
                QTableWidgetItem(
                    f"{stock_minimo:g}"
                )
            )

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

            # Posición real en la lista completa (la fila de la tabla puede no
            # coincidir cuando hay un filtro activo).
            indice_real = self.insumos.index(
                insumo
            )

            boton_editar.clicked.connect(
                lambda checked=False,
                i=indice_real:
                self.editar_insumo(i)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                boton_editar
            )

            boton_eliminar = QPushButton(
                "🗑"
            )

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
                self.eliminar_insumo(i)
            )

            self.tabla.setCellWidget(
                fila,
                6,
                boton_eliminar
            )

            # Alerta de stock bajo: agrega ⚠ a la cantidad y un mensaje al pasar el
            # mouse.
            if cantidad <= stock_minimo:

                item_cantidad.setText(
                    f"{cantidad:g} ⚠"
                )

                item_cantidad.setToolTip(
                    "Stock bajo"
                )

        # Muestra u oculta el mensaje de 'sin resultados' según haya filas o no.
        if len(insumos_mostrar) == 0:

            if len(self.insumos) == 0:

                self.mensaje.setText(
                    "No hay insumos registrados."
                )

            else:

                self.mensaje.setText(
                    "No se encontraron insumos."
                )

            self.mensaje.show()

        else:

            self.mensaje.hide()

    # Filtra los insumos cuyo nombre contenga el texto escrito (sin distinguir
    # mayúsculas de minúsculas).
    def buscar_insumos(self):

        texto = (
            self.buscar.text()
            .strip()
            .lower()
        )

        if not texto:

            self.actualizar_tabla()

            return

        insumos_filtrados = []

        for insumo in self.insumos:

            nombre = insumo[
                "nombre"
            ].lower()

            if texto in nombre:

                insumos_filtrados.append(
                    insumo
                )

        self.actualizar_tabla(
            insumos_filtrados
        )