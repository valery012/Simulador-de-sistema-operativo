
import pytest

from simulador.memoria import GestorMemoria


def test_asignar_memoria():
    memoria = GestorMemoria(1024)

    memoria.asignar(1, 256)

    assert memoria.ocupada == 256
    assert memoria.disponible == 768


def test_memoria_insuficiente():
    memoria = GestorMemoria(1024)

    memoria.asignar(1, 700)

    with pytest.raises(ValueError):
        memoria.asignar(2, 400)

    assert memoria.disponible == 324


def test_liberar_memoria():
    memoria = GestorMemoria(1024)

    memoria.asignar(1, 500)
    memoria.liberar(1)

    assert memoria.disponible == 1024
    assert memoria.consultar() == {}


def test_evitar_duplicados():
    memoria = GestorMemoria(1024)

    memoria.asignar(1, 100)

    with pytest.raises(ValueError):
        memoria.asignar(1, 100)
