
"""Interfaz de comunicación de PyOS."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit,
    QPushButton, QPlainTextEdit,
    QMessageBox
)


class ComunicacionUI(QWidget):

    def __init__(self, cola):
        super().__init__()

        self.cola = cola
        self.construir_interfaz()

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Comunicación entre procesos")
        titulo.setObjectName("tituloModulo")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Envía mensajes entre identificadores "
            "de procesos simulados mediante una "
            "cola FIFO."
        )
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        formulario = QFormLayout()

        self.emisor = QLineEdit()
        self.emisor.setPlaceholderText("Ej.: P1")

        self.receptor = QLineEdit()
        self.receptor.setPlaceholderText("Ej.: P2")

        self.mensaje = QLineEdit()
        self.mensaje.setPlaceholderText(
            "Escribe un mensaje..."
        )

        formulario.addRow("Emisor:", self.emisor)
        formulario.addRow("Receptor:", self.receptor)
        formulario.addRow("Mensaje:", self.mensaje)

        layout.addLayout(formulario)

        botones = QHBoxLayout()

        enviar = QPushButton("Enviar mensaje")
        enviar.clicked.connect(self.enviar)

        recibir = QPushButton("Recibir mensaje")
        recibir.clicked.connect(self.recibir)

        botones.addWidget(enviar)
        botones.addWidget(recibir)
        layout.addLayout(botones)

        self.estado = QLabel()
        layout.addWidget(self.estado)

        self.salida = QPlainTextEdit()
        self.salida.setReadOnly(True)
        layout.addWidget(self.salida)

        explicacion = QLabel(
            "FIFO: el primer mensaje enviado "
            "será el primero en recibirse."
        )
        layout.addWidget(explicacion)

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

            QLineEdit, QPlainTextEdit {
                background-color: #111827;
                color: white;
                padding: 8px;
                border: 1px solid #475569;
                border-radius: 5px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 11px;
                border-radius: 6px;
            }
        """)

        self.actualizar_estado()

    def actualizar_estado(self):
        self.estado.setText(
            f"Mensajes pendientes: "
            f"{self.cola.pendientes()}"
        )

    def enviar(self):
        try:
            mensaje = self.cola.enviar(
                self.emisor.text(),
                self.receptor.text(),
                self.mensaje.text()
            )

        except ValueError as error:
            QMessageBox.warning(
                self, "Error", str(error)
            )
            return

        self.salida.appendPlainText(
            f"ENVIADO | {mensaje.emisor} -> "
            f"{mensaje.receptor}: {mensaje.contenido}"
        )

        self.mensaje.clear()
        self.actualizar_estado()

    def recibir(self):
        try:
            mensaje = self.cola.recibir()

        except ValueError as error:
            QMessageBox.warning(
                self, "Cola vacía", str(error)
            )
            return

        self.salida.appendPlainText(
            f"RECIBIDO | {mensaje.emisor} -> "
            f"{mensaje.receptor}: {mensaje.contenido}"
        )

        self.actualizar_estado()
