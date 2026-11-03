# Datos compartidos entre los módulos.
# Respaldados en MySQL a través de conexion.py.
#
# Mapeado: las filas de MySQL se convierten en objetos de modelos.py (Cliente,
# Personal, Insumo, Servicio, Cita) y de ahí a los diccionarios que usan las páginas.
# Hilos: guardar en MySQL se hace en un hilo aparte (hilos.py) para no congelar la UI.

from copy import deepcopy

# obtener_conexion abre la conexión a MySQL; Error es la excepción que lanza
# mysql.connector cuando algo falla.
from .conexion import obtener_conexion
from mysql.connector import Error

from .hilos import HiloGuardado
from .modelos import Cliente, Personal, Insumo, Servicio, Cita

# Listas en memoria compartidas por TODAS las páginas de la app. Cada elemento es un
# diccionario (una fila de la tabla).
# Las páginas modifican estas mismas listas y luego llaman a guardar_en_mysql() para
# respaldarlas.
clientes = []
personal = []
servicios = []
insumos = []
citas = []


def cargar_desde_mysql():
    """
    Carga todas las tablas de MySQL hacia las listas en
    memoria que usa el resto de la aplicación.

    Cada fila se mapea a su clase de modelos.py (que convierte los tipos:
    Decimal -> float, 0/1 -> bool, etc.) y se guarda como diccionario.

    Si no logra conectar (servidor apagado, credenciales
    mal puestas en conexion.py, etc.) deja las listas como
    estaban y solo avisa por consola, para que la app pueda
    seguir abriendo aunque la base de datos no esté lista.
    """
    try:
        conexion = obtener_conexion()
    except Error as error:
        print(f"[MySQL] No se pudo conectar: {error}")
        return

    try:
        # dictionary=True: cada fila llega como diccionario {columna: valor}.
        cursor = conexion.cursor(dictionary=True)

        # Con [:] se reemplaza el contenido de la lista EN SITIO, así las páginas
        # que ya guardaron una referencia ven los datos nuevos.
        cursor.execute(
            "SELECT nombre, telefono, correo, direccion FROM clientes"
        )
        clientes[:] = [Cliente.desde_fila(f).a_dict() for f in cursor.fetchall()]

        cursor.execute(
            "SELECT nombre, telefono, especialidad, carga FROM personal"
        )
        personal[:] = [Personal.desde_fila(f).a_dict() for f in cursor.fetchall()]

        cursor.execute(
            "SELECT nombre, categoria, cantidad, unidad, stock_minimo "
            "FROM insumos"
        )
        insumos[:] = [Insumo.desde_fila(f).a_dict() for f in cursor.fetchall()]

        # Los servicios se arman aparte porque cada uno lleva su lista de insumos
        # (tabla servicio_insumos).
        cursor.execute("SELECT id, nombre, duracion, precio FROM servicios")
        filas_servicios = cursor.fetchall()

        servicios[:] = []

        # Por cada servicio se buscan los insumos que consume y se mapea el
        # servicio completo.
        for fila in filas_servicios:

            cursor.execute(
                "SELECT insumo_nombre, cantidad FROM servicio_insumos "
                "WHERE servicio_id = %s",
                (fila["id"],)
            )

            fila["insumos"] = [
                {"nombre": r["insumo_nombre"], "cantidad": r["cantidad"]}
                for r in cursor.fetchall()
            ]

            servicios.append(Servicio.desde_fila(fila).a_dict())

        cursor.execute(
            "SELECT cliente, servicio, personal, fecha, hora, "
            "duracion, completada FROM citas"
        )
        citas[:] = [Cita.desde_fila(f).a_dict() for f in cursor.fetchall()]

        cursor.close()

    except Error as error:
        print(f"[MySQL] Error cargando datos: {error}")

    finally:
        # Siempre se cierra la conexión, haya habido error o no.
        conexion.close()


def _insertar(cursor, objeto):
    """Inserta un objeto del modelo en su tabla usando TABLA y COLUMNAS."""
    columnas = ", ".join(objeto.COLUMNAS)
    marcadores = ", ".join(["%s"] * len(objeto.COLUMNAS))
    cursor.execute(
        f"INSERT INTO {objeto.TABLA} ({columnas}) VALUES ({marcadores})",
        objeto.a_fila()
    )


def _guardar_copia(copia):
    """
    Guarda en MySQL una COPIA de las listas (clientes, personal, servicios,
    insumos, citas). Reemplaza el contenido completo de cada tabla (borra e
    inserta de nuevo). Para el volumen de datos de un salón esto es simple,
    rápido y evita tener que llevar IDs sincronizados en cada lista.

    Esta función corre en el hilo de HiloGuardado, no en el hilo de la interfaz.
    Devuelve True si se guardó correctamente, False si hubo un error.
    """
    lista_clientes, lista_personal, lista_servicios, lista_insumos, lista_citas = copia

    try:
        conexion = obtener_conexion()
    except Error as error:
        print(f"[MySQL] No se pudo conectar para guardar: {error}")
        return False

    try:
        cursor = conexion.cursor()

        # Estrategia: se borra cada tabla y se vuelve a insertar todo lo que hay
        # en memoria.
        # ATENCIÓN: si las listas están vacías porque no se pudo cargar al iniciar
        # (MySQL apagado), un guardado posterior dejaría las tablas vacías.
        cursor.execute("DELETE FROM clientes")
        for c in lista_clientes:
            _insertar(cursor, Cliente.desde_fila(c))

        cursor.execute("DELETE FROM personal")
        for p in lista_personal:
            _insertar(cursor, Personal.desde_fila(p))

        cursor.execute("DELETE FROM insumos")
        for i in lista_insumos:
            _insertar(cursor, Insumo.desde_fila(i))

        # Primero se borra servicio_insumos (depende de servicios) y después servicios.
        cursor.execute("DELETE FROM servicio_insumos")
        cursor.execute("DELETE FROM servicios")
        for s in lista_servicios:
            servicio = Servicio.desde_fila(s)
            _insertar(cursor, servicio)

            # lastrowid es el id que MySQL le asignó al servicio recién insertado;
            # sirve para ligar sus insumos.
            servicio_id = cursor.lastrowid

            for ins in servicio.insumos:
                cursor.execute(
                    "INSERT INTO servicio_insumos "
                    "(servicio_id, insumo_nombre, cantidad) "
                    "VALUES (%s, %s, %s)",
                    (servicio_id, ins.nombre, ins.cantidad)
                )

        cursor.execute("DELETE FROM citas")
        for cita in lista_citas:
            _insertar(cursor, Cita.desde_fila(cita))

        # Confirma todos los cambios juntos. Si algo falló antes, no se aplica
        # nada (ver rollback más abajo).
        conexion.commit()
        cursor.close()
        return True

    except Error as error:
        print(f"[MySQL] Error guardando datos: {error}")
        # Revierte los cambios a medias para no dejar la base de datos inconsistente.
        conexion.rollback()
        return False

    finally:
        conexion.close()


# Hilo de guardado. Se crea la primera vez que se necesita (ya con la aplicación
# de Qt creada), no al importar este módulo.
_hilo_guardado = None


def _obtener_hilo():
    global _hilo_guardado
    if _hilo_guardado is None:
        _hilo_guardado = HiloGuardado(_guardar_copia)
    return _hilo_guardado


def guardar_en_mysql():
    """
    Pide guardar el estado actual de las listas en MySQL, SIN bloquear la interfaz.

    Se toma una copia de las listas en este momento (hilo principal) y el hilo
    secundario la guarda. Así, si el usuario sigue editando mientras se guarda,
    el hilo no ve listas a medio modificar.
    """
    copia = (
        deepcopy(clientes),
        deepcopy(personal),
        deepcopy(servicios),
        deepcopy(insumos),
        deepcopy(citas),
    )
    _obtener_hilo().encolar(copia)


def guardar_en_mysql_y_esperar():
    """
    Igual que guardar_en_mysql(), pero espera a que el hilo termine.
    Se usa al cerrar la aplicación para no perder el último guardado.
    """
    guardar_en_mysql()
    _obtener_hilo().esperar()


# Al importar este módulo (que ocurre al arrancar la app),
# cargamos automáticamente lo que ya exista en MySQL.
cargar_desde_mysql()
