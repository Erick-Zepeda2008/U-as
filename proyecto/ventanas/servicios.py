# Módulo SERVICIOS: permite ver, buscar, registrar, editar y eliminar los servicios
# del salón
# (manicura, pedicura, etc.) y definir qué insumos consume cada uno.

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QDialog,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QHeaderView
)

from . import datos
# Se llama después de cada cambio para guardar en MySQL.
from .datos import guardar_en_mysql


# Catálogo de servicios con su duración (en minutos) y su precio (en córdobas, C$).
# El formulario solo permite elegir de aquí y rellena duración y precio
# automáticamente.
SERVICIOS_PREDEFINIDOS = {
    "Manicura clásica": {
        "duracion": 60,
        "precio": 350.00
    },
    "Manicura semipermanente": {
        "duracion": 90,
        "precio": 500.00
    },
    "Uñas acrílicas": {
        "duracion": 120,
        "precio": 800.00
    },
    "Pedicura": {
        "duracion": 60,
        "precio": 400.00
    }
}

# Diálogo para registrar o editar un servicio: se elige del catálogo y se le asignan
# los insumos que consume.
class FormularioServicio(QDialog):


    # Si recibe 'servicio' se abre en modo edición; si es None, en modo registro.
    def __init__(self, servicio=None, parent=None):
        super().__init__(parent)

        # Insumos que consume el servicio: lista de diccionarios {nombre, cantidad}.
        self.insumos_seleccionados = []

        if servicio:
            # En modo edición se copian los insumos del servicio (copy) para no
            # alterar el original hasta que se guarde.
            self.insumos_seleccionados = [
                insumo.copy()
                for insumo in servicio.get("insumos", [])
            ]

        # Texto que muestra los insumos agregados.
        self.lista_insumos = QLabel(
            "No hay insumos agregados."
        )

        self.setWindowTitle(
            "Editar servicio" if servicio else "Registrar servicio"
        )

        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        titulo = QLabel(
            "Editar servicio" if servicio else "Registrar servicio"
        )

        titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #9145b6;
            margin-bottom: 8px;
        """)

        layout.addWidget(titulo)

        layout.addWidget(QLabel("Servicio:"))

        # Lista desplegable con los servicios del catálogo.
        self.combo_servicio = QComboBox()

        for nombre in SERVICIOS_PREDEFINIDOS:
            self.combo_servicio.addItem(nombre)

        layout.addWidget(self.combo_servicio)

        layout.addWidget(QLabel("Duración:"))

        # Duración en minutos (de 1 a 480); se llena sola al elegir el servicio.
        self.duracion = QSpinBox()
        self.duracion.setRange(1, 480)
        self.duracion.setSuffix(" minutos")
        self.duracion.setReadOnly(True)

        layout.addWidget(self.duracion)

        layout.addWidget(QLabel("Precio:"))

        # Precio en córdobas (C$); es de solo lectura porque viene del catálogo.
        self.precio = QDoubleSpinBox()
        self.precio.setRange(0, 100000)
        self.precio.setDecimals(2)
        self.precio.setPrefix("C$ ")
        self.precio.setReadOnly(True)

        layout.addWidget(self.precio)

        layout.addWidget(
       QLabel("Insumos utilizados:")
    )

        layout.addWidget(
        self.lista_insumos
    )

        # Abre una ventanita para elegir un insumo del inventario y su cantidad.
        btn_agregar_insumo = QPushButton(
        "+ Agregar insumo"
    )

        btn_agregar_insumo.clicked.connect(
        self.agregar_insumo
    )

        layout.addWidget(
        btn_agregar_insumo
   )
        
        botones = QHBoxLayout()

        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")

        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #9145b6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #7d379f;
            }
        """)

        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                color: #333333;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #dcdcdc;
            }
        """)

        # Guardar cierra el diálogo como aceptado; Cancelar lo cierra sin guardar.
        btn_guardar.clicked.connect(self.accept)
        btn_cancelar.clicked.connect(self.reject)

        botones.addStretch()
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)

        layout.addLayout(botones)

        self.setLayout(layout)

        # Muestra la lista de insumos inicial.
        self.actualizar_lista_insumos()

        # Cuando cambia el servicio elegido, se actualizan la duración y el precio.
        self.combo_servicio.currentTextChanged.connect(
            self.actualizar_datos
        )

        # Modo edición: selecciona en la lista el servicio que se está editando.
        if servicio:

            indice = self.combo_servicio.findText(
                servicio["nombre"]
            )

            if indice >= 0:
                self.combo_servicio.setCurrentIndex(indice)

        self.actualizar_datos(
            self.combo_servicio.currentText()
        )

    # Rellena duración y precio con los valores del catálogo para el servicio elegido.
    def actualizar_datos(self, nombre):

        if nombre in SERVICIOS_PREDEFINIDOS:

            datos = SERVICIOS_PREDEFINIDOS[nombre]

            self.duracion.setValue(
                datos["duracion"]
            )

            self.precio.setValue(
                datos["precio"]
            )

    # Refresca el texto que lista los insumos agregados (o muestra 'No hay insumos
    # agregados.').
    def actualizar_lista_insumos(self):

        if not self.insumos_seleccionados:

            self.lista_insumos.setText(
                "No hay insumos agregados."
            )

            return

        texto = ""

        for insumo in self.insumos_seleccionados:

            texto += (
                f'• {insumo["nombre"]} — '
                f'{insumo["cantidad"]:.2f}\n'
            )

        self.lista_insumos.setText(
            texto.strip()
        )       

    # Abre una ventana emergente para elegir un insumo del inventario (datos.insumos)
    # y la cantidad que usa el servicio.
    def agregar_insumo(self):

        ventana = QDialog(self)

        ventana.setWindowTitle(
            "Agregar insumo"
        )

        ventana.setMinimumWidth(350)

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Insumo:")
        )

        combo_insumo = QComboBox()

        combo_insumo.addItem(
            "Seleccionar insumo"
        )

        # Llena la lista con los insumos registrados en el inventario.
        for insumo in datos.insumos:

            combo_insumo.addItem(
                insumo["nombre"]
            )

        layout.addWidget(
            combo_insumo
        )

        layout.addWidget(
            QLabel("Cantidad:")
        )

        cantidad = QDoubleSpinBox()

        cantidad.setRange(
            0.01,
            100000
        )

        cantidad.setDecimals(2)

        cantidad.setValue(
            1.00
        )

        layout.addWidget(
            cantidad
        )

        botones = QHBoxLayout()

        btn_cancelar = QPushButton(
            "Cancelar"
        )

        btn_agregar = QPushButton(
            "Agregar"
        )

        botones.addStretch()

        botones.addWidget(
            btn_cancelar
        )

        botones.addWidget(
            btn_agregar
        )

        layout.addLayout(
            botones
        )

        ventana.setLayout(
            layout
        )

        # Función interna: valida la selección. Si el insumo ya estaba agregado
        # actualiza su cantidad; si no, lo añade.
        def guardar_insumo():

            if combo_insumo.currentIndex() == 0:

                QMessageBox.warning(
                    ventana,
                    "Insumo",
                    "Selecciona un insumo."
                )

                return

            nombre_insumo = combo_insumo.currentText()
            cantidad_insumo = cantidad.value()

            insumo_existente = None

            for insumo in self.insumos_seleccionados:

                if insumo["nombre"] == nombre_insumo:
                    insumo_existente = insumo
                    break

            if insumo_existente:

                insumo_existente["cantidad"] = cantidad_insumo

            else:

                self.insumos_seleccionados.append({
                    "nombre": nombre_insumo,
                    "cantidad": cantidad_insumo
                })
           
            self.actualizar_lista_insumos()

            ventana.accept()

        btn_cancelar.clicked.connect(
            ventana.reject
        )

        btn_agregar.clicked.connect(
            guardar_insumo
        )

        # Muestra la ventanita y espera a que el usuario la cierre.
        ventana.exec()

    # Devuelve los datos del servicio como diccionario (nombre, duración, precio e
    # insumos).
    def obtener_datos(self):

        return {
            "nombre": self.combo_servicio.currentText(),
            "duracion": self.duracion.value(),
            "precio": self.precio.value(),
            "insumos": self.insumos_seleccionados.copy()
        }
    
# Página principal del módulo SERVICIOS: buscador, botón de nuevo servicio y tabla.
class PaginaServicios(QWidget):

    # Usa la lista compartida datos.servicios, que se respalda en MySQL con
    # guardar_en_mysql().
    def __init__(self):
        super().__init__()

        # Datos temporales mientras no usamos base de datos
        self.servicios = datos.servicios

        self.construir_interfaz()

    # Construye la página: título, buscador, botón de registrar y tabla.
    def construir_interfaz(self):

        layout_principal = QVBoxLayout()

        layout_principal.setContentsMargins(
            25, 25, 25, 25
        )

        layout_principal.setSpacing(15)

        titulo = QLabel("Servicios")

        titulo.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #9145b6;
            margin-bottom: 5px;
        """)

        layout_principal.addWidget(titulo)

        barra = QHBoxLayout()

        barra.setSpacing(10)

        # Buscador por nombre: la tabla se filtra mientras se escribe.
        self.buscar = QLineEdit()

        self.buscar.setPlaceholderText(
            "Buscar servicio..."
        )

        self.buscar.textChanged.connect(
            self.buscar_servicio
        )

        btn_nuevo = QPushButton(
            "Registrar servicio"
        )

        btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #9145b6;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #7d379f;
            }
        """)

        # Abre el formulario para registrar un servicio.
        btn_nuevo.clicked.connect(
            self.registrar_servicio
        )

        barra.addWidget(self.buscar)
        barra.addWidget(btn_nuevo)

        layout_principal.addLayout(barra)
        
        # Tabla de servicios: nombre, duración, precio e insumos, más los botones de
        # editar y eliminar.
        self.tabla = QTableWidget()

        self.tabla.setColumnCount(6)

        self.tabla.setHorizontalHeaderLabels([
            "Servicio",
            "Duración",
            "Precio",
            "Insumos",
            "Editar",
            "Eliminar"
        ])

        self.tabla.setAlternatingRowColors(True)

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #faf7fb;
                border: 1px solid #dddddd;
                gridline-color: #eeeeee;
            }

            QHeaderView::section {
                background-color: #9145b6;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 6px;
            }
        """)

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

        layout_principal.addWidget(self.tabla)

        self.setLayout(layout_principal)

        self.actualizar_tabla()

    # Redibuja la tabla con 'lista' (resultado de búsqueda) o con todos los servicios.
    def actualizar_tabla(self, lista=None):

        if lista is None:
            lista = self.servicios

        self.tabla.setRowCount(0)

        for fila, servicio in enumerate(lista):

            self.tabla.insertRow(fila)

            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    servicio["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    f'{servicio["duracion"]} minutos'
                )
            )

            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    f'C$ {servicio["precio"]:.2f}'
                )
            )

            # Junta los insumos del servicio para mostrarlos todos en una sola celda.
            insumos = servicio.get(
                "insumos",
                []
            )

            if insumos:

                texto_insumos = ""

                for insumo in insumos:

                    texto_insumos += (
                        f'{insumo["nombre"]} '
                        f'({insumo["cantidad"]:.2f})\n'
                    )

                texto_insumos = texto_insumos.strip()

            else:

                texto_insumos = "Sin insumos"

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    texto_insumos
                )
            )

            btn_editar = QPushButton("Editar")

            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #9145b6;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                }

                QPushButton:hover {
                    background-color: #7d379f;
                }
            """)

            # Botón de editar de esta fila.
            btn_editar.clicked.connect(
                lambda checked=False, s=servicio:
                self.editar_servicio(s)
            )

            self.tabla.setCellWidget(
                fila,
                4,
                btn_editar
            )

            btn_eliminar = QPushButton("Eliminar")

            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #d96b8b;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                }

                QPushButton:hover {
                    background-color: #c65375;
                }
            """)

            # Botón de eliminar de esta fila.
            btn_eliminar.clicked.connect(
                lambda checked=False, s=servicio:
                self.eliminar_servicio(s)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                btn_eliminar
            )

    # Abre el formulario para un servicio nuevo. No permite repetir un servicio con el
    # mismo nombre; si todo está bien, lo agrega, guarda en MySQL y refresca la tabla.
    def registrar_servicio(self):

        formulario = FormularioServicio(
            parent=self
        )

        if formulario.exec():

            datos = formulario.obtener_datos()

            for servicio in self.servicios:

                if servicio["nombre"] == datos["nombre"]:

                    QMessageBox.warning(
                        self,
                        "Servicio existente",
                        "Ese servicio ya está registrado."
                    )

                    return

            self.servicios.append(datos)

            guardar_en_mysql()

            self.actualizar_tabla()

    # NOTA: este método está repetido (idéntico al anterior). Python solo usa la
    # última definición, así que puedes borrar una de las dos.
    def registrar_servicio(self):

        formulario = FormularioServicio(
            parent=self
        )

        if formulario.exec():

            datos = formulario.obtener_datos()

            for servicio in self.servicios:

                if servicio["nombre"] == datos["nombre"]:

                    QMessageBox.warning(
                        self,
                        "Servicio existente",
                        "Ese servicio ya está registrado."
                    )

                    return

            self.servicios.append(datos)

            guardar_en_mysql()

            self.actualizar_tabla()

    # Abre el formulario con el servicio elegido; verifica que el nuevo nombre no
    # choque con otro servicio y actualiza sus datos.
    def editar_servicio(self, servicio):

        formulario = FormularioServicio(
            servicio,
            self
        )

        if formulario.exec():

            nuevos_datos = (
                formulario.obtener_datos()
            )

            for otro in self.servicios:

                if (
                    otro is not servicio
                    and
                    otro["nombre"] == nuevos_datos["nombre"]
                ):

                    QMessageBox.warning(
                        self,
                        "Servicio existente",
                        "Ese servicio ya está registrado."
                    )

                    return

            # Copia los valores nuevos al servicio existente (se edita en el sitio).
            servicio["nombre"] = (
                nuevos_datos["nombre"]
            )

            servicio["duracion"] = (
                nuevos_datos["duracion"]
            )

            servicio["precio"] = (
                nuevos_datos["precio"]
            )
            servicio["insumos"] = nuevos_datos["insumos"]

            guardar_en_mysql()

            self.actualizar_tabla()

    # Pide confirmación y, si la respuesta es Sí, elimina el servicio de la lista y de
    # MySQL.
    def eliminar_servicio(self, servicio):

        respuesta = QMessageBox.question(
            self,
            "Eliminar servicio",
            f'¿Deseas eliminar "{servicio["nombre"]}"?',
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:

            self.servicios.remove(servicio)

            guardar_en_mysql()

            self.actualizar_tabla()

    # Filtra los servicios cuyo nombre contenga el texto y actualiza la tabla.
    def buscar_servicio(self, texto):

        texto = texto.lower()

        resultados = [
            servicio
            for servicio in self.servicios
            if texto in servicio["nombre"].lower()
        ]

        self.actualizar_tabla(resultados)