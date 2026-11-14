"""Interfaz visual para administrar procesos simulados."""

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSpinBox,
)

from simulador.procesos import GestorProcesos


class ProcesosUI(QWidget):
    """Panel para crear, consultar y finalizar procesos."""

    def __init__(self, gestor: GestorProcesos | None = None) -> None:
        super().__init__()
        self.gestor = gestor or GestorProcesos()
        self._construir_ui()
        self._actualizar_tabla()

    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)

        formulario = QFormLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej. Editor de texto")
        formulario.addRow("Nombre:", self.nombre_input)
        self.llegada_input = QSpinBox()
        self.llegada_input.setRange(0, 10000)

        self.cpu_input = QSpinBox()
        self.cpu_input.setRange(1, 9999)
        self.cpu_input.setValue(5)

        self.prioridad_input = QSpinBox()
        self.prioridad_input.setRange(0, 20)
        self.prioridad_input.setValue(1)

        self.memoria_input = QSpinBox()
        self.memoria_input.setRange(1, 1024)
        self.memoria_input.setValue(128)
        self.memoria_input.setSuffix(" MB")

        formulario.addRow("Llegada:", self.llegada_input)
        formulario.addRow("CPU requerida:", self.cpu_input)
        formulario.addRow("Prioridad:", self.prioridad_input)
        formulario.addRow("Memoria:", self.memoria_input)

        layout.addLayout(formulario)

        acciones = QHBoxLayout()
        crear = QPushButton("Crear proceso")
        crear.clicked.connect(self._crear_proceso)
        acciones.addWidget(crear)

        finalizar = QPushButton("Finalizar seleccionado")
        finalizar.clicked.connect(self._finalizar_seleccionado)
        acciones.addWidget(finalizar)
        acciones.addStretch()
        layout.addLayout(acciones)

        self.mensaje = QLabel()
        layout.addWidget(self.mensaje)

        self.tabla = QTableWidget(0, 7)
        self.tabla.setHorizontalHeaderLabels([
            "PID",
            "Nombre",
            "Llegada",
            "CPU",
            "Prioridad",
            "Memoria",
            "Estado"])
        
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.tabla)

    def _crear_proceso(self) -> None:
        try:
            
            proceso = self.gestor.crear(self.nombre_input.text(), self.llegada_input.value(),self.cpu_input.value(),
                self.prioridad_input.value(),
                self.memoria_input.value()
            )

        except ValueError as error:
            self.mensaje.setText(str(error))
            return

        self.nombre_input.clear()
        self.mensaje.setText(f"Proceso {proceso.pid} creado.")
        self._actualizar_tabla()

    def _finalizar_seleccionado(self) -> None:
        fila = self.tabla.currentRow()
        if fila < 0:
            self.mensaje.setText("Selecciona un proceso.")
            return

        pid = int(self.tabla.item(fila, 0).text())
        proceso = self.gestor.finalizar(pid)
        self.mensaje.setText(f"Proceso {proceso.pid} finalizado.")
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        procesos = self.gestor.consultar()
        self.tabla.setRowCount(len(procesos))

        for fila, proceso in enumerate(procesos):
            datos = [
                proceso.pid,
                proceso.nombre,
                proceso.llegada,
                proceso.cpu_requerida,
                proceso.prioridad,
                proceso.memoria,
                proceso.estado.value,
            ]
            for columna, valor in enumerate(datos):
                self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

        self.tabla.resizeColumnsToContents()

