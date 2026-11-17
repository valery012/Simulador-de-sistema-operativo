
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QSpinBox,
    QPushButton, QPlainTextEdit, QVBoxLayout,
    QHBoxLayout
)

from simulador.concurrencia import ejecutar_concurrencia


class ConcurrenciaUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Concurrencia")
        self.setObjectName("vistaConcurrencia")
        self.setMinimumSize(650, 480)

        self.crear_interfaz()
        self.aplicar_estilos()

    def crear_interfaz(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        icono = QLabel("⇄")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(48, 48)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()

        titulo = QLabel("Concurrencia y sincronización")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Ejecuta dos hilos sobre un contador compartido "
            "y compara el uso de Lock."
        )
        descripcion.setObjectName("descripcionModulo")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)
        principal.addLayout(encabezado)

        # CONFIGURACION
        panel = QFrame()
        panel.setObjectName("panelFormulario")

        formulario = QVBoxLayout(panel)
        formulario.setContentsMargins(
            16, 15, 16, 15
        )
        formulario.setSpacing(12)

        etiqueta = QLabel(
            "Incrementos por hilo"
        )
        formulario.addWidget(etiqueta)

        self.repeticiones = QSpinBox()
        self.repeticiones.setRange(10, 500)
        self.repeticiones.setValue(100)
        formulario.addWidget(self.repeticiones)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        self.boton_sin = QPushButton(
            "Ejecutar sin Lock"
        )
        self.boton_sin.setObjectName(
            "botonSecundario"
        )

        self.boton_con = QPushButton(
            "✓  Ejecutar con Lock"
        )
        self.boton_con.setObjectName(
            "botonPrincipal"
        )

        self.boton_sin.clicked.connect(
            lambda: self.ejecutar(False)
        )

        self.boton_con.clicked.connect(
            lambda: self.ejecutar(True)
        )

        botones.addWidget(self.boton_sin)
        botones.addWidget(self.boton_con)

        formulario.addLayout(botones)
        principal.addWidget(panel)

        # RESULTADOS
        resumen = QHBoxLayout()
        resumen.setSpacing(10)

        tarjeta1, self.valor_esperado = self.crear_tarjeta(
            "RESULTADO ESPERADO"
        )
        tarjeta2, self.valor_obtenido = self.crear_tarjeta(
            "RESULTADO OBTENIDO"
        )
        tarjeta3, self.valor_perdidos = self.crear_tarjeta(
            "INCREMENTOS PERDIDOS"
        )

        resumen.addWidget(tarjeta1)
        resumen.addWidget(tarjeta2)
        resumen.addWidget(tarjeta3)
        principal.addLayout(resumen)

        titulo_registro = QLabel(
            "Detalle de ejecución"
        )
        titulo_registro.setObjectName("tituloSeccion")
        principal.addWidget(titulo_registro)

        self.registro = QPlainTextEdit()
        self.registro.setObjectName("registro")
        self.registro.setReadOnly(True)
        self.registro.setPlaceholderText(
            "Ejecuta una prueba para ver sus resultados."
        )

        principal.addWidget(self.registro, 1)

        self.estado = QLabel(
            "Sin Lock se provoca una condición de carrera "
            "para demostrar el problema. Con Lock se protege "
            "la sección crítica."
        )
        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)
        principal.addWidget(self.estado)

    def crear_tarjeta(self, titulo):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(13, 12, 13, 12)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("nombreTarjeta")

        valor = QLabel("—")
        valor.setObjectName("valorTarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)

        return tarjeta, valor

    def ejecutar(self, con_lock):
        repeticiones = self.repeticiones.value()

        try:
            resultado = ejecutar_concurrencia(
                con_lock=con_lock,
                repeticiones=repeticiones
            )

            self.valor_esperado.setText(
                str(resultado.esperado)
            )

            self.valor_obtenido.setText(
                str(resultado.obtenido)
            )

            self.valor_perdidos.setText(
                str(resultado.incrementos_perdidos)
            )

            modo = (
                "CON LOCK"
                if resultado.con_lock
                else "SIN LOCK"
            )

            self.registro.appendPlainText(
                f"\n{'=' * 40}\n"
                f"PRUEBA: {modo}\n"
                f"Incrementos por hilo: {repeticiones}\n"
                f"Resultado esperado: {resultado.esperado}\n"
                f"Resultado obtenido: {resultado.obtenido}\n"
                f"Incrementos perdidos: "
                f"{resultado.incrementos_perdidos}\n"
            )

            mensajes = resultado.mensajes

            if isinstance(mensajes, (list, tuple)):
                for mensaje in mensajes:
                    self.registro.appendPlainText(
                        str(mensaje)
                    )
            elif mensajes:
                self.registro.appendPlainText(
                    str(mensajes)
                )

            if con_lock:
                self.informar(
                    "La sección crítica quedó protegida "
                    "mediante threading.Lock.",
                    "exito"
                )
            else:
                self.informar(
                    "Ejecución sin Lock: se induce una "
                    "condición de carrera para comparar "
                    "los resultados.",
                    "advertencia"
                )

        except (ValueError, RuntimeError) as error:
            self.informar(str(error), "error")

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
            QWidget#vistaConcurrencia {
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
            QFrame#panelFormulario, QFrame#tarjeta {
                background: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }
            QFrame#panelFormulario QLabel {
                color: #B7C7DC;
                background: transparent;
            }
            QSpinBox {
                background: #0F1B2E;
                color: #F8FAFC;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 9px;
            }
            QSpinBox:focus {
                border: 1px solid #60A5FA;
            }
            QPushButton#botonPrincipal {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 11px 14px;
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
                padding: 10px 14px;
            }
            QPushButton#botonSecundario:hover {
                background: #345174;
            }
            QLabel#nombreTarjeta {
                color: #AFC2DA;
                font-size: 10px;
                font-weight: bold;
            }
            QLabel#valorTarjeta {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }
            QPlainTextEdit#registro {
                background: #0F1B2E;
                color: #E5E7EB;
                border: 1px solid #345071;
                border-radius: 8px;
                padding: 10px;
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
