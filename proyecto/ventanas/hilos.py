# Hilo de segundo plano para guardar en MySQL sin congelar la ventana.
#
# Guardar en MySQL puede tardar (borra e inserta todas las tablas). Si se hiciera
# en el hilo principal, la interfaz se quedaría "pegada" unos instantes.
# Con HiloGuardado el guardado ocurre en un hilo aparte (QThread).

import threading

from PySide6.QtCore import QThread


class HiloGuardado(QThread):
    """
    Hilo que ejecuta la función de guardado con una COPIA de los datos.

    - Usa un único hilo: los guardados se hacen de uno en uno, nunca dos a la vez.
    - Si llegan varios guardados mientras uno está en curso, solo se conserva el más
      reciente (contiene todos los cambios anteriores), así no se acumula trabajo.
    """

    def __init__(self, funcion_guardar):
        super().__init__()
        self._guardar = funcion_guardar     # función que recibe la copia de los datos
        self._candado = threading.Lock()    # protege _pendiente y _activo
        self._pendiente = None              # copia más reciente por guardar
        self._activo = False                # True mientras run() esté trabajando

    def encolar(self, copia):
        """Pide guardar 'copia'. Se llama desde el hilo principal; no bloquea."""
        with self._candado:
            self._pendiente = copia
            if self._activo:
                return                      # el hilo ya la recogerá en su ciclo
            self._activo = True
        self.wait()                         # por si el hilo anterior termina de salir
        self.start()                        # arranca run() en el hilo nuevo

    def run(self):
        """Se ejecuta en el hilo secundario: guarda mientras haya algo pendiente."""
        while True:
            with self._candado:
                copia = self._pendiente
                self._pendiente = None
                if copia is None:
                    self._activo = False    # no queda nada: el hilo termina
                    return
            self._guardar(copia)            # trabajo lento, fuera del candado

    def esperar(self):
        """Bloquea hasta terminar todos los guardados pendientes (al cerrar la app)."""
        self.wait()
