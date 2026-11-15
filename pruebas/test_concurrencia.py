
import pytest

from simulador.concurrencia import ejecutar_concurrencia


def test_con_lock():
    resultado = ejecutar_concurrencia(
        con_lock=True, repeticiones=100
    )

    assert resultado.esperado == 200
    assert resultado.obtenido == 200
    assert resultado.incrementos_perdidos == 0


def test_sin_lock():
    resultado = ejecutar_concurrencia(
        con_lock=False, repeticiones=100
    )

    assert resultado.esperado == 200
    assert resultado.obtenido < 200
    assert resultado.incrementos_perdidos > 0


def test_dos_hilos():
    resultado = ejecutar_concurrencia(
        con_lock=True, repeticiones=10
    )

    assert len(resultado.mensajes) == 2
    assert resultado.obtenido == 20


def test_repeticiones_invalidas():
    with pytest.raises(ValueError):
        ejecutar_concurrencia(
            con_lock=True, repeticiones=0
        )
