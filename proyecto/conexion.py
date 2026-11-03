"""
Módulo encargado de la conexión a MySQL y de las operaciones
(CRUD) que usan las distintas ventanas del sistema Nail Bliss.
"""

# mysql-connector-python es la librería que permite hablar con MySQL (está en
# requirements.txt).
# NOTA: la aplicación actual NO usa este archivo; ventanas/datos.py usa
# ventanas/conexion.py. Este módulo queda como alternativa y para pruebas.
import mysql.connector
from mysql.connector import Error


class BaseDatos:
    """
    Maneja la conexión a MySQL y las operaciones sobre las tablas
    del sistema. Ajusta host, usuario, contraseña y base_datos
    según tu configuración local de MySQL.
    """

    def __init__(self, host="localhost", usuario="root", contraseña="", base_datos="chikys_nails"):
        self.host = host
        self.usuario = usuario
        self.contraseña = contraseña
        self.base_datos = base_datos
        # Todavía no hay conexión abierta; se asigna cuando se llama a conectar().
        self.conexion = None

    # ------------------------------------------------------------------
    # Conexión
    # ------------------------------------------------------------------
    def conectar(self):
        """Abre la conexión a MySQL. Devuelve la conexión o None si falla."""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.usuario,
                password=self.contraseña,
                database=self.base_datos
            )
            return self.conexion
        except Error as e:
            print(f"Error al conectar con MySQL: {e}")
            return None

    def cerrar(self):
        """Cierra la conexión si está abierta."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()

    # OJO: la tabla 'personal' que se crea aquí (apellido, puesto, correo) no coincide
    # con la que usa ventanas/datos.py (nombre, telefono, especialidad, carga). Si
    # usas este método, ajusta las columnas.
    def crear_tablas(self):
        """
        Crea la tabla 'personal' si no existe. Llama a esto una vez
        (por ejemplo al iniciar la app) para asegurarte de que la
        estructura exista en la base de datos.
        """
        conexion = self.conectar()
        if conexion is None:
            return False

        try:
            cursor = conexion.cursor()
            # Crea la tabla solo si todavía no existe (IF NOT EXISTS).
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal (
                    id_personal INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    puesto VARCHAR(100),
                    telefono VARCHAR(20),
                    correo VARCHAR(150),
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conexion.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error al crear las tablas: {e}")
            return False
        # Siempre se cierra la conexión, haya habido error o no (igual en los demás
        # métodos).
        finally:
            self.cerrar()

    # ------------------------------------------------------------------
    # Personal (empleados del salón)
    # ------------------------------------------------------------------
    def agregar_personal(self, nombre, apellido, puesto, telefono, correo):
        """Inserta un nuevo integrante del personal. Devuelve True/False."""
        conexion = self.conectar()
        if conexion is None:
            return False

        try:
            cursor = conexion.cursor()
            # Los %s son marcadores: MySQL los reemplaza por los valores de la tupla
            # de abajo, lo que evita inyección SQL.
            cursor.execute("""
                INSERT INTO personal (nombre, apellido, puesto, telefono, correo)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, apellido, puesto, telefono, correo))
            conexion.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error al agregar personal: {e}")
            return False
        finally:
            self.cerrar()

    def obtener_personal(self):
        """Devuelve una lista de tuplas con todo el personal registrado."""
        conexion = self.conectar()
        if conexion is None:
            return []

        try:
            cursor = conexion.cursor()
            # Trae todo el personal, del más reciente al más antiguo (id descendente).
            cursor.execute("""
                SELECT id_personal, nombre, apellido, puesto, telefono, correo
                FROM personal
                ORDER BY id_personal DESC
            """)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Error as e:
            print(f"Error al obtener personal: {e}")
            return []
        finally:
            self.cerrar()

    def eliminar_personal(self, id_personal):
        """Elimina un integrante del personal por su id. Devuelve True/False."""
        conexion = self.conectar()
        if conexion is None:
            return False

        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM personal WHERE id_personal = %s", (id_personal,))
            conexion.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error al eliminar personal: {e}")
            return False
        finally:
            self.cerrar()


# Prueba rápida: al ejecutar este archivo directamente se comprueba si MySQL responde.
if __name__ == "__main__":
    bd = BaseDatos()

    if bd.conectar():
        print("Conexión exitosa a MySQL")
        bd.cerrar()
    else:
        print("No se pudo conectar a MySQL")