
import os

# Permite ejecutar pruebas de interfaz sin
# necesidad de abrir ventanas visibles.
os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen"
)

import pytest

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from interfaz.procesos_ui import ProcesosUI
from simulador.procesos import (
    GestorProcesos,
    EstadoProceso,
)
from simulador.memoria import GestorMemoria


@pytest.fixture(scope="module")
def aplicacion():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    yield app


@pytest.fixture
def escenario(aplicacion):

    gestor_procesos = GestorProcesos()
    gestor_memoria = GestorMemoria(1024)

    proceso = gestor_procesos.crear(
        nombre="Proceso de prueba",
        llegada=0,
        cpu_requerida=5,
        prioridad=1,
        memoria=128
    )

    ventana = ProcesosUI(
        gestor_procesos,
        gestor_memoria
    )

    ventana.tabla.selectRow(0)

    yield (
        ventana,
        gestor_procesos,
        gestor_memoria,
        proceso
    )

    ventana.close()


def test_cancelar_no_finaliza_ni_libera(
    escenario,
    monkeypatch
):
    ventana, procesos, memoria, proceso = escenario

    memoria.asignar(proceso.pid, 128)

    monkeypatch.setattr(
        QMessageBox,
        "exec",
        lambda self: QMessageBox.StandardButton.No
    )

    ventana.finalizar_proceso()

    assert (
        procesos.consultar()[0].estado
        != EstadoProceso.FINALIZADO
    )

    assert memoria.ocupada == 128


def test_finalizar_libera_memoria(
    escenario,
    monkeypatch
):
    ventana, procesos, memoria, proceso = escenario

    memoria.asignar(proceso.pid, 128)

    monkeypatch.setattr(
        QMessageBox,
        "exec",
        lambda self: QMessageBox.StandardButton.Yes
    )

    notificaciones = []

    ventana.procesos_cambiados.connect(
        lambda: notificaciones.append(True)
    )

    ventana.finalizar_proceso()

    assert (
        procesos.consultar()[0].estado
        == EstadoProceso.FINALIZADO
    )

    assert memoria.ocupada == 0
    assert memoria.disponible == 1024
    assert len(notificaciones) == 1


def test_finalizar_sin_memoria_no_pide_confirmacion(
    escenario,
    monkeypatch
):
    ventana, procesos, memoria, proceso = escenario

    def no_debe_preguntar(self):
        raise AssertionError(
            "No debe pedir confirmación si no hay RAM."
        )

    monkeypatch.setattr(
        QMessageBox,
        "exec",
        no_debe_preguntar
    )

    ventana.finalizar_proceso()

    assert (
        procesos.consultar()[0].estado
        == EstadoProceso.FINALIZADO
    )

    assert memoria.ocupada == 0


def test_proceso_finalizado_no_se_finaliza_dos_veces(
    escenario,
    monkeypatch
):
    ventana, procesos, memoria, proceso = escenario

    procesos.finalizar(proceso.pid)
    ventana.actualizar_tabla()
    ventana.tabla.selectRow(0)

    def no_debe_preguntar(self):
        raise AssertionError(
            "Un proceso finalizado no debe "
            "mostrar confirmación."
        )

    monkeypatch.setattr(
        QMessageBox,
        "exec",
        no_debe_preguntar
    )

    ventana.finalizar_proceso()

    assert (
        procesos.consultar()[0].estado
        == EstadoProceso.FINALIZADO
    )

    assert memoria.ocupada == 0
    assert "ya está finalizado" in ventana.mensaje.text()
