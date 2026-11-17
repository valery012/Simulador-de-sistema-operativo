
import pytest

from simulador.comunicacion import ColaMensajes


def test_enviar_y_recibir():
    cola = ColaMensajes()

    cola.enviar("P1", "P2", "Hola")

    assert cola.pendientes() == 1

    mensaje = cola.recibir()

    assert mensaje.emisor == "P1"
    assert mensaje.receptor == "P2"
    assert mensaje.contenido == "Hola"
    assert cola.pendientes() == 0


def test_orden_fifo():
    cola = ColaMensajes()

    cola.enviar("P1", "P2", "Primero")
    cola.enviar("P2", "P1", "Segundo")

    assert cola.recibir().contenido == "Primero"
    assert cola.recibir().contenido == "Segundo"


def test_cola_vacia():
    cola = ColaMensajes()

    with pytest.raises(ValueError):
        cola.recibir()


def test_mensaje_vacio():
    cola = ColaMensajes()

    with pytest.raises(ValueError):
        cola.enviar("P1", "P2", "")
