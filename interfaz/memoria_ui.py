
"""Interfaz de memoria simulada de PyOS."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QProgressBar, QTableWidget,
    QTableWidgetItem, QMessageBox,
    QHeaderView
)

from simulador.procesos import EstadoProceso


class MemoriaUI(QWidget):

    def __init__(self, memoria, procesos):
        super().__init__()

        self.memoria = memoria
        self.procesos = procesos

        self.construir_interfaz()
        self.actualizar()

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Gestión de memoria RAM")
        titulo.setObjectName("tituloModulo")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Selecciona un proceso registrado "
            "y asígnale la memoria solicitada. "
            "Capacidad simulada: 1024 MB."
        )
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        layout.addWidget(QLabel("Proceso:"))

        seleccion = QHBoxLayout()

        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(
            self.actualizar_solicitud
        )

        seleccion.addWidget(self.selector)

        recargar = QPushButton("Actualizar procesos")
        recargar.clicked.connect(self.actualizar)
        seleccion.addWidget(recargar)

        layout.addLayout(seleccion)

        self.solicitud = QLabel()
        layout.addWidget(self.solicitud)

        botones = QHBoxLayout()

        asignar = QPushButton("Asignar memoria")
        asignar.clicked.connect(self.asignar)

        liberar = QPushButton("Liberar memoria")
        liberar.clicked.connect(self.liberar)

        botones.addWidget(asignar)
        botones.addWidget(liberar)
        layout.addLayout(botones)

        self.resumen = QLabel()
        layout.addWidget(self.resumen)

        self.barra = QProgressBar()
        self.barra.setRange(
            0, self.memoria.capacidad
        )
        layout.addWidget(self.barra)

        self.tabla = QTableWidget(0, 3)

        self.tabla.setHorizontalHeaderLabels([
            "PID", "Proceso", "Memoria asignada"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.tabla)

        self.estado = QLabel(
            "Selecciona un proceso para comenzar."
        )
        layout.addWidget(self.estado)

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
                font-size: 14px;
            }

            QLabel#tituloModulo {
                font-size: 22px;
                font-weight: bold;
            }

            QComboBox, QTableWidget {
                background-color: #111827;
                color: white;
                border: 1px solid #475569;
                padding: 7px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }

            QProgressBar {
                background-color: #111827;
                color: white;
                border: 1px solid #475569;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #16A34A;
            }
        """)

    def proceso_seleccionado(self):
        pid = self.selector.currentData()

        for proceso in self.procesos.consultar():
            if proceso.pid == pid:
                return proceso

        return None

    def actualizar_solicitud(self):
        proceso = self.proceso_seleccionado()

        if proceso:
            self.solicitud.setText(
                f"Memoria solicitada: "
                f"{proceso.memoria} MB"
            )
        else:
            self.solicitud.setText(
                "No hay procesos registrados."
            )

    def actualizar(self):
        pid_anterior = self.selector.currentData()

        self.selector.blockSignals(True)
        self.selector.clear()

        for proceso in self.procesos.consultar():
            self.selector.addItem(
                f"P{proceso.pid} - {proceso.nombre} "
                f"({proceso.estado.value})",
                proceso.pid
            )

        indice = self.selector.findData(pid_anterior)

        if indice >= 0:
            self.selector.setCurrentIndex(indice)

        self.selector.blockSignals(False)

        self.actualizar_solicitud()

        self.resumen.setText(
            f"Total: {self.memoria.capacidad} MB | "
            f"Ocupada: {self.memoria.ocupada} MB | "
            f"Disponible: {self.memoria.disponible} MB"
        )

        self.barra.setValue(
            self.memoria.ocupada
        )

        asignaciones = self.memoria.consultar()

        nombres = {
            p.pid: p.nombre
            for p in self.procesos.consultar()
        }

        self.tabla.setRowCount(
            len(asignaciones)
        )

        for fila, (pid, cantidad) in enumerate(
            sorted(asignaciones.items())
        ):
            datos = [
                pid,
                nombres.get(pid, "Desconocido"),
                f"{cantidad} MB"
            ]

            for columna, valor in enumerate(datos):
                self.tabla.setItem(
                    fila,
                    columna,
                    QTableWidgetItem(str(valor))
                )

    def asignar(self):
        proceso = self.proceso_seleccionado()

        if proceso is None:
            QMessageBox.warning(
                self, "Atención",
                "Primero crea un proceso."
            )
            return

        if proceso.estado == EstadoProceso.FINALIZADO:
            QMessageBox.warning(
                self, "Atención",
                "No puedes asignar memoria a "
                "un proceso finalizado."
            )
            return

        try:
            self.memoria.asignar(
                proceso.pid,
                proceso.memoria
            )

        except ValueError as error:
            QMessageBox.warning(
                self, "Memoria", str(error)
            )
            return

        self.estado.setText(
            f"Se asignaron {proceso.memoria} MB "
            f"al proceso P{proceso.pid}."
        )

        self.actualizar()

    def liberar(self):
        proceso = self.proceso_seleccionado()

        if proceso is None:
            QMessageBox.warning(
                self, "Atención",
                "Selecciona un proceso."
            )
            return

        try:
            cantidad = self.memoria.liberar(
                proceso.pid
            )

        except ValueError as error:
            QMessageBox.warning(
                self, "Memoria", str(error)
            )
            return

        self.estado.setText(
            f"Se liberaron {cantidad} MB "
            f"del proceso P{proceso.pid}."
        )

        self.actualizar()
