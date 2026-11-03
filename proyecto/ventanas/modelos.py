# Mapeado objeto-relacional sencillo (sin librerías externas).
#
# Cada tabla de MySQL se representa con una clase de Python (una dataclass):
#   tabla clientes   <-> clase Cliente
#   tabla personal   <-> clase Personal
#   tabla insumos    <-> clase Insumo
#   tabla servicios  <-> clase Servicio (con sus InsumoServicio de servicio_insumos)
#   tabla citas      <-> clase Cita
#
# Cada clase sabe convertirse en los dos sentidos:
#   - desde_fila(fila): convierte una fila de MySQL (o un diccionario de las
#     páginas) en un objeto, ya con los tipos correctos (float, int, bool, str).
#   - a_fila(): devuelve los valores en el orden de las columnas, listos para un
#     INSERT.
#   - a_dict(): devuelve un diccionario, que es el formato que usan las páginas.

from dataclasses import dataclass, field, fields, asdict
from typing import ClassVar


def _convertir(tipo, valor):
    """Convierte 'valor' al tipo indicado; si viene vacío (None) usa el valor neutro."""
    if valor is None:
        return "" if tipo is str else tipo()      # 0.0, 0, False o lista vacía
    if tipo is bool:
        return bool(valor)                         # MySQL guarda 0/1
    return tipo(valor)                             # float(Decimal), int(...), str(...)


@dataclass
class Modelo:
    """Clase base: aquí vive la lógica de mapeo que comparten todas las tablas."""

    # Nombre de la tabla y columnas (en orden) que se guardan en MySQL.
    TABLA: ClassVar[str] = ""
    COLUMNAS: ClassVar[tuple] = ()

    @classmethod
    def desde_fila(cls, fila):
        """Crea un objeto a partir de una fila (diccionario) de MySQL o de la app."""
        valores = {}
        for campo in fields(cls):
            valores[campo.name] = _convertir(campo.type, fila.get(campo.name))
        return cls(**valores)

    def a_fila(self):
        """Valores en el orden de COLUMNAS, listos para un INSERT."""
        return tuple(getattr(self, columna) for columna in self.COLUMNAS)

    def a_dict(self):
        """Diccionario con todos los campos (formato que usan las páginas)."""
        return asdict(self)


@dataclass
class Cliente(Modelo):
    nombre: str = ""
    telefono: str = ""
    correo: str = ""
    direccion: str = ""

    TABLA: ClassVar[str] = "clientes"
    COLUMNAS: ClassVar[tuple] = ("nombre", "telefono", "correo", "direccion")


@dataclass
class Personal(Modelo):
    nombre: str = ""
    telefono: str = ""
    especialidad: str = ""
    carga: str = "Disponible"

    TABLA: ClassVar[str] = "personal"
    COLUMNAS: ClassVar[tuple] = ("nombre", "telefono", "especialidad", "carga")


@dataclass
class Insumo(Modelo):
    nombre: str = ""
    categoria: str = ""
    cantidad: float = 0.0
    unidad: str = ""
    stock_minimo: float = 0.0

    TABLA: ClassVar[str] = "insumos"
    COLUMNAS: ClassVar[tuple] = (
        "nombre", "categoria", "cantidad", "unidad", "stock_minimo"
    )


@dataclass
class InsumoServicio(Modelo):
    """Un insumo que consume un servicio (fila de servicio_insumos)."""

    nombre: str = ""
    cantidad: float = 0.0


@dataclass
class Servicio(Modelo):
    nombre: str = ""
    duracion: int = 0
    precio: float = 0.0
    insumos: list = field(default_factory=list)   # lista de InsumoServicio

    TABLA: ClassVar[str] = "servicios"
    COLUMNAS: ClassVar[tuple] = ("nombre", "duracion", "precio")

    @classmethod
    def desde_fila(cls, fila):
        # Primero se mapean los campos simples y luego los insumos anidados.
        servicio = super().desde_fila(fila)
        servicio.insumos = [
            InsumoServicio.desde_fila(insumo)
            for insumo in (fila.get("insumos") or [])
        ]
        return servicio


@dataclass
class Cita(Modelo):
    cliente: str = ""
    servicio: str = ""
    personal: str = ""
    fecha: str = ""          # texto dd/MM/yyyy
    hora: str = ""           # texto hh:mm
    duracion: int = 0
    completada: bool = False

    TABLA: ClassVar[str] = "citas"
    COLUMNAS: ClassVar[tuple] = (
        "cliente", "servicio", "personal", "fecha", "hora",
        "duracion", "completada"
    )
