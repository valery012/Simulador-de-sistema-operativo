
"""Comunicación mediante una cola de mensajes."""

from dataclasses import dataclass
from queue import Queue, Empty


@dataclass
class Mensaje:
    emisor: str
    receptor: str
    contenido: str


class ColaMensajes:

    def __init__(self):
        self._cola = Queue()

    def enviar(self, emisor, receptor, contenido):

        emisor = emisor.strip()
        receptor = receptor.strip()
        contenido = contenido.strip()

        if not emisor or not receptor or not contenido:
            raise ValueError(
                "Completa el emisor, receptor y mensaje."
            )

        mensaje = Mensaje(
            emisor=emisor,
            receptor=receptor,
            contenido=contenido
        )

        self._cola.put(mensaje)
        return mensaje

    def recibir(self):
        try:
            return self._cola.get_nowait()

        except Empty:
            raise ValueError(
                "La cola no tiene mensajes pendientes."
            )

    def pendientes(self):
        return self._cola.qsize()
