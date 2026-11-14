
"""Interfaz del planificador de CPU."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox,
    QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView,
    QMessageBox
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas
)

from simulador.planificacion import planificar


class PlanificadorUI(QWidget):

    def __init__(self, gestor):
        super().__init__()

        self.gestor = gestor

        layout = QVBoxLayout(self)

        titulo = QLabel("Planificador de CPU")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(titulo)

        controles = QHBoxLayout()

        controles.addWidget(QLabel("Algoritmo:"))

        self.algoritmo = QComboBox()
        self.algoritmo.addItems([
            "FCFS", "SJF", "Round Robin"
        ])
        controles.addWidget(self.algoritmo)

        controles.addWidget(QLabel("Quantum:"))

        self.quantum = QSpinBox()
        self.quantum.setRange(1, 100)
        self.quantum.setValue(2)
        self.quantum.setEnabled(False)
        controles.addWidget(self.quantum)

        self.algoritmo.currentTextChanged.connect(
            lambda texto: self.quantum.setEnabled(
                texto == "Round Robin"
            )
        )

        ejecutar = QPushButton("Ejecutar simulación")
        ejecutar.clicked.connect(self.ejecutar)
        controles.addWidget(ejecutar)

        layout.addLayout(controles)

        self.info = QLabel(
            "Registra procesos en el módulo Procesos."
        )
        layout.addWidget(self.info)

        # Diagrama de Gantt
        self.figura = Figure(
            figsize=(8, 2.5), tight_layout=True
        )
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setMinimumHeight(190)
        layout.addWidget(self.canvas)

        # Tabla de estadísticas
        self.tabla = QTableWidget(0, 7)
        self.tabla.setHorizontalHeaderLabels([
            "PID", "Nombre", "Llegada",
            "CPU", "Finalización", "Retorno", "Espera"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.tabla)

        self.promedios = QLabel(
            "Espera promedio: — | Retorno promedio: —"
        )
        layout.addWidget(self.promedios)

    def ejecutar(self):
        try:
            resultado = planificar(
                self.gestor.consultar(),
                self.algoritmo.currentText(),
                self.quantum.value()
            )
        except ValueError as error:
            QMessageBox.warning(
                self, "Planificación", str(error)
            )
            return

        self.info.setText(
            f"Algoritmo ejecutado: {resultado.algoritmo}"
        )

        self.mostrar_tabla(resultado)
        self.mostrar_gantt(resultado)

        self.promedios.setText(
            f"Espera promedio: "
            f"{resultado.promedio_espera:.2f} | "
            f"Retorno promedio: "
            f"{resultado.promedio_retorno:.2f}"
        )

    def mostrar_tabla(self, resultado):
        self.tabla.setRowCount(len(resultado.metricas))

        for fila, metrica in enumerate(resultado.metricas):
            datos = [
                metrica.pid,
                metrica.nombre,
                metrica.llegada,
                metrica.cpu,
                metrica.finalizacion,
                metrica.retorno,
                metrica.espera
            ]

            for columna, valor in enumerate(datos):
                self.tabla.setItem(
                    fila,
                    columna,
                    QTableWidgetItem(str(valor))
                )

    def mostrar_gantt(self, resultado):
        self.figura.clear()
        eje = self.figura.add_subplot(111)

        colores = [
            "#2563EB", "#0891B2",
            "#7C3AED", "#16A34A",
            "#EA580C"
        ]

        for tramo in resultado.tramos:
            duracion = tramo.fin - tramo.inicio

            if tramo.pid is None:
                color = "#64748B"
                etiqueta = "Libre"
            else:
                color = colores[
                    (tramo.pid - 1) % len(colores)
                ]
                etiqueta = f"P{tramo.pid}"

            eje.barh(
                0, duracion,
                left=tramo.inicio,
                height=0.55,
                color=color,
                edgecolor="white"
            )

            eje.text(
                tramo.inicio + duracion / 2,
                0,
                etiqueta,
                ha="center",
                va="center",
                color="white",
                fontsize=9
            )

        eje.set_yticks([])
        eje.set_xlabel("Tiempo de CPU")
        eje.set_title("Diagrama de Gantt")
        eje.set_xlim(
            0, max(t.fin for t in resultado.tramos)
        )
        eje.grid(axis="x", alpha=0.25)
        eje.set_axisbelow(True)

        self.canvas.draw()
