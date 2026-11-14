
import pytest

from simulador.procesos import GestorProcesos
from simulador.planificacion import planificar


def preparar_procesos():
    gestor = GestorProcesos()

    gestor.crear("P1", 0, 5, 1, 128)
    gestor.crear("P2", 1, 3, 1, 128)
    gestor.crear("P3", 2, 1, 1, 128)

    return gestor


def test_fcfs():
    gestor = preparar_procesos()
    resultado = planificar(gestor.consultar(), "FCFS")

    assert [
        (t.pid, t.inicio, t.fin)
        for t in resultado.tramos
    ] == [
        (1, 0, 5),
        (2, 5, 8),
        (3, 8, 9)
    ]

    assert resultado.promedio_espera == pytest.approx(10 / 3)


def test_sjf():
    gestor = preparar_procesos()
    resultado = planificar(gestor.consultar(), "SJF")

    assert [t.pid for t in resultado.tramos] == [
        1, 3, 2
    ]

    assert resultado.promedio_espera == pytest.approx(8 / 3)


def test_round_robin():
    gestor = preparar_procesos()

    resultado = planificar(
        gestor.consultar(), "Round Robin", quantum=2
    )

    assert [
        (t.pid, t.inicio, t.fin)
        for t in resultado.tramos
    ] == [
        (1, 0, 2),
        (2, 2, 4),
        (3, 4, 5),
        (1, 5, 7),
        (2, 7, 8),
        (1, 8, 9)
    ]


def test_tiempo_ocioso_y_finalizados():
    gestor = GestorProcesos()

    primero = gestor.crear("P1", 3, 2, 1, 128)
    segundo = gestor.crear("P2", 5, 3, 1, 128)

    gestor.finalizar(segundo.pid)

    resultado = planificar(gestor.consultar(), "FCFS")

    assert [(t.pid, t.inicio, t.fin)
            for t in resultado.tramos] == [
        (None, 0, 3),
        (primero.pid, 3, 5)
    ]

    assert len(resultado.metricas) == 1
    assert primero.estado.value == "Listo"


def test_quantum_invalido():
    gestor = preparar_procesos()

    with pytest.raises(ValueError):
        planificar(
            gestor.consultar(), "Round Robin", quantum=0
        )
