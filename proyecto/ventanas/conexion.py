# Configuración y función de conexión a MySQL que usa ventanas/datos.py.
# Si cambias el usuario, la contraseña o el nombre de la base de datos, hazlo en las
# constantes de abajo.

import mysql.connector
from mysql.connector import Error


# ============================================================
# CONFIGURACIÓN DE MYSQL
# ============================================================

HOST = "localhost"
USUARIO = "root"
CONTRASEÑA = ""
BASE_DATOS = "chikys_nails"


# ============================================================
# CONEXIÓN
# ============================================================

def obtener_conexion():
    """
    Crea y devuelve una conexión a MySQL.
    """

    try:
        conexion = mysql.connector.connect(
            host=HOST,
            user=USUARIO,
            password=CONTRASEÑA,
            database=BASE_DATOS
        )

        return conexion

    except Error as error:
        print(f"[MySQL] No se pudo conectar: {error}")
        # Se vuelve a lanzar el error para que quien llamó a esta función (datos.py)
        # decida qué hacer.
        raise


# ============================================================
# PRUEBA DE CONEXIÓN
# ============================================================

# Prueba rápida: al ejecutar este archivo directamente se comprueba la conexión a
# MySQL.
if __name__ == "__main__":

    try:

        conexion = obtener_conexion()

        if conexion.is_connected():
            print("Conexión exitosa a MySQL")

        conexion.close()

    except Error:

        print("No se pudo conectar a MySQL")