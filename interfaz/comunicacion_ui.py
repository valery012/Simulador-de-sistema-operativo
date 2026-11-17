
from queue import Empty

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QComboBox,
    QPushButton, QPlainTextEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout
)


class ComunicacionUI(QWidget):

    def __init__(self, cola_mensajes, gestor_procesos=None):
        super().__init__()
        self.cola = cola_mensajes
        self.gestor_procesos = gestor_procesos

        self.setWindowTitle("Comunicación")
        self.setObjectName("vistaComunicacion")
        self.setMinimumSize(670, 490)

        self.crear_interfaz()
        self.aplicar_estilos()
        self.actualizar_procesos()
        self.actualizar_contador()

        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self.actualizar_contador)
        self.temporizador.start(1000)

    def crear_interfaz(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)

        # ENCABEZADO
        encabezado = QHBoxLayout()
        icono = QLabel("✉")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(48, 48)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()
        titulo = QLabel("Comunicación entre procesos")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Envía y recibe mensajes mediante una cola FIFO."
        )
        descripcion.setObjectName("descripcionModulo")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)
        principal.addLayout(encabezado)

        # FORMULARIO
        panel = QFrame()
        panel.setObjectName("panelFormulario")
        formulario = QGridLayout(panel)
        formulario.setContentsMargins(16, 15, 16, 15)
        formulario.setSpacing(11)

        if self.gestor_procesos is not None:
            self.emisor = QComboBox()
            self.receptor = QComboBox()
        else:
            self.emisor = QLineEdit()
            self.receptor = QLineEdit()
            self.emisor.setPlaceholderText("Ej. P1")
            self.receptor.setPlaceholderText("Ej. P2")

        self.mensaje_input = QLineEdit()
        self.mensaje_input.setPlaceholderText(
            "Escribe aquí el mensaje..."
        )

        formulario.addWidget(QLabel("Emisor:"), 0, 0)
        formulario.addWidget(self.emisor, 0, 1)
        formulario.addWidget(QLabel("Receptor:"), 1, 0)
        formulario.addWidget(self.receptor, 1, 1)
        formulario.addWidget(QLabel("Mensaje:"), 2, 0)
        formulario.addWidget(self.mensaje_input, 2, 1)
        formulario.setColumnStretch(1, 1)

        acciones = QHBoxLayout()
        acciones.setSpacing(10)

        self.enviar_btn = QPushButton("➤  Enviar mensaje")
        self.enviar_btn.setObjectName("botonPrincipal")
        self.enviar_btn.clicked.connect(self.enviar_mensaje)

        self.recibir_btn = QPushButton("Recibir mensaje")
        self.recibir_btn.setObjectName("botonSecundario")
        self.recibir_btn.clicked.connect(self.recibir_mensaje)

        acciones.addWidget(self.enviar_btn)
        acciones.addWidget(self.recibir_btn)

        if self.gestor_procesos is not None:
            self.actualizar_btn = QPushButton("↻")
            self.actualizar_btn.setObjectName("botonSecundario")
            self.actualizar_btn.setToolTip(
                "Actualizar procesos disponibles"
            )
            self.actualizar_btn.clicked.connect(
                self.actualizar_procesos
            )
            acciones.addWidget(self.actualizar_btn)

        formulario.addLayout(acciones, 3, 0, 1, 2)
        principal.addWidget(panel)

        # REGISTRO
        cabecera = QHBoxLayout()

        titulo_historial = QLabel("Registro de mensajes")
        titulo_historial.setObjectName("tituloSeccion")

        self.contador = QLabel("0 pendientes")
        self.contador.setObjectName("contador")

        cabecera.addWidget(titulo_historial)
        cabecera.addStretch()
        cabecera.addWidget(self.contador)
        principal.addLayout(cabecera)

        self.historial = QPlainTextEdit()
        self.historial.setReadOnly(True)
        self.historial.setPlaceholderText(
            "Los mensajes enviados y recibidos aparecerán aquí."
        )
        self.historial.setObjectName("historial")
        principal.addWidget(self.historial, 1)

        self.estado = QLabel(
            "FIFO: el primer mensaje enviado "
            "será el primero en recibirse."
        )
        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)
        principal.addWidget(self.estado)

    def actualizar_procesos(self):
        if self.gestor_procesos is None:
            return

        emisor_anterior = self.emisor.currentData()
        receptor_anterior = self.receptor.currentData()

        self.emisor.clear()
        self.receptor.clear()

        self.emisor.addItem("Seleccionar proceso", None)
        self.receptor.addItem("Seleccionar proceso", None)

        for proceso in self.gestor_procesos.consultar():
            estado = getattr(
                proceso.estado, "name", str(proceso.estado)
            )

            if estado == "FINALIZADO":
                continue

            etiqueta = f"P{proceso.pid} - {proceso.nombre}"
            identificador = f"P{proceso.pid}"

            self.emisor.addItem(etiqueta, identificador)
            self.receptor.addItem(etiqueta, identificador)

        for combo, anterior in (
            (self.emisor, emisor_anterior),
            (self.receptor, receptor_anterior)
        ):
            indice = combo.findData(anterior)
            if indice >= 0:
                combo.setCurrentIndex(indice)

    def obtener_participantes(self):
        if self.gestor_procesos is not None:
            return (
                self.emisor.currentData(),
                self.receptor.currentData()
            )

        return (
            self.emisor.text().strip(),
            self.receptor.text().strip()
        )

    def enviar_mensaje(self):
        emisor, receptor = self.obtener_participantes()
        contenido = self.mensaje_input.text().strip()

        if not emisor or not receptor or not contenido:
            self.informar(
                "Selecciona emisor, receptor y escribe un mensaje.",
                "advertencia"
            )
            return

        if emisor == receptor:
            self.informar(
                "Selecciona procesos diferentes para comunicarte.",
                "advertencia"
            )
            return

        try:
            self.cola.enviar(emisor, receptor, contenido)

            self.historial.appendPlainText(
                f"ENVIADO | {emisor} → {receptor}: {contenido}"
            )

            self.mensaje_input.clear()
            self.actualizar_contador()

            self.informar(
                "Mensaje agregado correctamente a la cola.",
                "exito"
            )

        except (ValueError, RuntimeError) as error:
            self.informar(str(error), "error")

    def recibir_mensaje(self):
        if self.cola.pendientes() == 0:
            self.informar(
                "No hay mensajes pendientes en la cola.",
                "advertencia"
            )
            return

        try:
            mensaje = self.cola.recibir()

            if mensaje is None:
                self.informar(
                    "La cola está vacía.", "advertencia"
                )
                return

            self.historial.appendPlainText(
                f"RECIBIDO | {mensaje.emisor} → "
                f"{mensaje.receptor}: {mensaje.contenido}"
            )

            self.actualizar_contador()
            self.informar("Mensaje recibido correctamente.", "exito")

        except (Empty, IndexError, ValueError) as error:
            self.informar(
                str(error) or "La cola está vacía.",
                "advertencia"
            )

    def actualizar_contador(self):
        pendientes = self.cola.pendientes()
        self.contador.setText(f"{pendientes} pendientes")

    def informar(self, texto, tipo="normal"):
        colores = {
            "normal": "#AFC2DA",
            "exito": "#4ADE80",
            "advertencia": "#FBBF24",
            "error": "#FB7185"
        }
        self.estado.setText(texto)
        self.estado.setStyleSheet(
            f"color: {colores.get(tipo, colores['normal'])};"
        )

    def aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget#vistaComunicacion {
                background: #111C30;
                color: #F8FAFC;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QLabel#iconoModulo {
                background: #25477E;
                color: #93C5FD;
                border-radius: 11px;
                font-size: 26px;
            }
            QLabel#tituloModulo {
                color: #F8FAFC;
                font-size: 21px;
                font-weight: bold;
            }
            QLabel#descripcionModulo {
                color: #94A3B8;
                font-size: 12px;
            }
            QFrame#panelFormulario {
                background: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }
            QFrame#panelFormulario QLabel {
                color: #B7C7DC;
                background: transparent;
            }
            QLineEdit, QComboBox, QPlainTextEdit {
                background: #0F1B2E;
                color: #F8FAFC;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 9px;
                selection-background-color: #2563EB;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #60A5FA;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox QAbstractItemView {
                background: #182A44;
                color: white;
                selection-background-color: #25477E;
            }
            QPushButton#botonPrincipal {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 11px 15px;
                font-weight: bold;
            }
            QPushButton#botonPrincipal:hover {
                background: #1D4ED8;
            }
            QPushButton#botonSecundario {
                background: #24364F;
                color: #E5E7EB;
                border: 1px solid #3A5374;
                border-radius: 7px;
                padding: 10px 15px;
            }
            QPushButton#botonSecundario:hover {
                background: #345174;
            }
            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }
            QLabel#contador {
                background: #1E3A5F;
                color: #93C5FD;
                border-radius: 8px;
                padding: 7px 11px;
            }
            QPlainTextEdit#historial {
                font-family: "Consolas";
                font-size: 12px;
            }
            QLabel#mensajeEstado {
                background: #182A44;
                color: #AFC2DA;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 11px;
            }
        """)