
"""Interfaz dinámica de concurrencia para PyOS."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QMessageBox,
    QSpinBox,
    QFormLayout
)

from simulador.concurrencia import ejecutar_concurrencia


class ConcurrenciaUI(QWidget):

    def __init__(self):
        super().__init__()
        self.construir_interfaz()

    def construir_interfaz(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # TITULO
        titulo = QLabel("Concurrencia y sincronización")
        titulo.setObjectName("tituloConcurrencia")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Dos hilos reales de Python comparten "
            "un contador. Configura cuántas veces "
            "cada hilo intentará incrementarlo."
        )
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        # CONFIGURACION
        formulario = QFormLayout()

        self.repeticiones = QSpinBox()
        self.repeticiones.setRange(10, 500)
        self.repeticiones.setValue(100)
        self.repeticiones.setSuffix(" incrementos")

        formulario.addRow(
            "Incrementos por hilo:",
            self.repeticiones
        )

        layout.addLayout(formulario)

        # INFORMACION DINAMICA
        self.informacion = QLabel()
        layout.addWidget(self.informacion)

        # BOTONES
        botones = QHBoxLayout()

        self.boton_sin_lock = QPushButton(
            "Ejecutar sin Lock"
        )

        self.boton_sin_lock.clicked.connect(
            lambda: self.ejecutar(False)
        )

        self.boton_con_lock = QPushButton(
            "Ejecutar con Lock"
        )

        self.boton_con_lock.clicked.connect(
            lambda: self.ejecutar(True)
        )

        botones.addWidget(self.boton_sin_lock)
        botones.addWidget(self.boton_con_lock)

        layout.addLayout(botones)

        # ESTADO DE LA SIMULACION
        self.estado = QLabel(
            "Configura las repeticiones y ejecuta una prueba."
        )

        layout.addWidget(self.estado)

        # CONSOLA DE RESULTADOS
        self.salida = QPlainTextEdit()
        self.salida.setReadOnly(True)

        self.salida.setPlaceholderText(
            "Aquí aparecerán los resultados "
            "de cada simulación."
        )

        layout.addWidget(self.salida)

        # EXPLICACION PEDAGOGICA
        self.explicacion = QLabel(
            "Sin Lock: ambos hilos pueden sobrescribir "
            "actualizaciones del contador.\n"
            "Con Lock: solo un hilo modifica el "
            "contador a la vez."
        )

        self.explicacion.setWordWrap(True)
        layout.addWidget(self.explicacion)

        # EVENTOS
        self.repeticiones.valueChanged.connect(
            self.actualizar_configuracion
        )

        self.actualizar_configuracion(
            self.repeticiones.value()
        )

        # ESTILOS
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

            QSpinBox {
                background-color: #303030;
                color: white;
                border: 1px solid #475569;
                padding: 8px;
                border-radius: 5px;
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

    def actualizar_configuracion(self, repeticiones):

        esperado = repeticiones * 2

        self.informacion.setText(
            f"Hilos: 2 | "
            f"Incrementos por hilo: {repeticiones} | "
            f"Total esperado: {esperado}"
        )

        self.estado.setText(
            "Configuración actualizada. "
            "Ejecuta una nueva prueba."
        )

        self.salida.clear()

    def ejecutar(self, con_lock):

        cantidad = self.repeticiones.value()

        try:
            resultado = ejecutar_concurrencia(
                con_lock=con_lock,
                repeticiones=cantidad
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
            "",
            f"PRUEBA: {modo}",
            "-" * 40,
            f"Hilos ejecutados: 2",
            f"Incrementos por hilo: {cantidad}",
            "",
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

        if con_lock:
            texto.append(
                "EXPLICACION:"
            )
            texto.append(
                "Lock protege la seccion critica."
            )
            texto.append(
                "Los incrementos se realizaron correctamente."
            )

        elif resultado.incrementos_perdidos > 0:
            texto.append(
                "EXPLICACION:"
            )
            texto.append(
                "Se produjo una condicion de carrera."
            )
            texto.append(
                "Algunas actualizaciones se sobrescribieron."
            )

        else:
            texto.append(
                "EXPLICACION:"
            )
            texto.append(
                "No se perdieron incrementos en esta ejecucion."
            )
            texto.append(
                "Esto no significa que sea seguro trabajar sin Lock."
            )

        self.salida.appendPlainText(
            "\n".join(texto) + "\n"
        )

        self.estado.setText(
            f"Ultima prueba: {modo} | "
            f"Resultado: {resultado.obtenido} "
            f"de {resultado.esperado}"
        )
