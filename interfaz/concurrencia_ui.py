
"""Interfaz gráfica de concurrencia para PyOS."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QMessageBox
)

from simulador.concurrencia import ejecutar_concurrencia


class ConcurrenciaUI(QWidget):

    def __init__(self):
        super().__init__()

        self.construir_interfaz()

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("Concurrencia y sincronización")
        titulo.setObjectName("tituloConcurrencia")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Dos hilos comparten un contador. "
            "Cada hilo intenta incrementarlo 100 veces."
        )
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        botones = QHBoxLayout()

        sin_lock = QPushButton("Ejecutar sin Lock")
        sin_lock.clicked.connect(
            lambda: self.ejecutar(False)
        )

        con_lock = QPushButton("Ejecutar con Lock")
        con_lock.clicked.connect(
            lambda: self.ejecutar(True)
        )

        botones.addWidget(sin_lock)
        botones.addWidget(con_lock)
        layout.addLayout(botones)

        self.estado = QLabel(
            "Selecciona una prueba para comenzar."
        )
        layout.addWidget(self.estado)

        self.salida = QPlainTextEdit()
        self.salida.setReadOnly(True)
        self.salida.setPlaceholderText(
            "Aquí aparecerán los resultados."
        )

        layout.addWidget(self.salida)

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
                font-size: 14px;
            }

            QLabel#tituloConcurrencia {
                font-size: 22px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 12px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPlainTextEdit {
                background-color: #111827;
                color: #E5E7EB;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px;
                font-family: Consolas;
            }
        """)

    def ejecutar(self, con_lock):
        try:
            resultado = ejecutar_concurrencia(
                con_lock=con_lock,
                repeticiones=100
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error de concurrencia",
                str(error)
            )
            return

        modo = "CON LOCK" if con_lock else "SIN LOCK"

        texto = [
            f"PRUEBA: {modo}",
            "-" * 35,
            *resultado.mensajes,
            "",
            f"Valor esperado: {resultado.esperado}",
            f"Valor obtenido: {resultado.obtenido}",
            (
                "Incrementos perdidos: "
                f"{resultado.incrementos_perdidos}"
            ),
            ""
        ]

        if resultado.incrementos_perdidos == 0:
            texto.append(
                "Resultado: contador correcto."
            )
        else:
            texto.append(
                "Resultado: condición de carrera "
                "demostrada."
            )

        self.salida.appendPlainText(
            "\n".join(texto) + "\n"
        )

        self.estado.setText(
            f"Última prueba: {modo} | "
            f"Resultado: {resultado.obtenido}"
        )
