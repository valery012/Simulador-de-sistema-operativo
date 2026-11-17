
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QComboBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas
)
from matplotlib.ticker import MaxNLocator

from simulador.planificacion import planificar


class PlanificadorUI(QWidget):

    EXPLICACIONES = {
        "FCFS": (
            "FCFS: los procesos se ejecutan según "
            "su orden de llegada."
        ),
        "SJF": (
            "SJF no expulsivo: se selecciona el "
            "proceso disponible con menor ráfaga de CPU."
        ),
        "Round Robin": (
            "Round Robin: los procesos comparten la CPU "
            "en turnos definidos por el quantum."
        )
    }

    def __init__(self, gestor_procesos):
        super().__init__()

        self.gestor = gestor_procesos

        self.setWindowTitle("Planificador CPU")
        self.setObjectName("vistaPlanificador")
        self.setMinimumSize(720, 480)

        self.crear_interfaz()
        self.aplicar_estilos()
        self.actualizar_descripcion()

    def crear_interfaz(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("areaPlanificador")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        contenido = QWidget()
        contenido.setObjectName("contenidoPlanificador")

        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        icono = QLabel("◈")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(48, 48)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()

        titulo = QLabel("Planificador de CPU")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Compara FCFS, SJF no expulsivo y Round Robin."
        )
        descripcion.setObjectName("descripcionModulo")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)
        principal.addLayout(encabezado)

        # CONTROLES
        panel = QFrame()
        panel.setObjectName("panelFormulario")

        controles = QGridLayout(panel)
        controles.setContentsMargins(15, 13, 15, 13)
        controles.setSpacing(9)

        self.algoritmo = QComboBox()
        self.algoritmo.addItems([
            "FCFS",
            "SJF",
            "Round Robin"
        ])
        self.algoritmo.currentTextChanged.connect(
            self.actualizar_descripcion
        )

        self.quantum = QSpinBox()
        self.quantum.setRange(1, 1000)
        self.quantum.setValue(2)

        self.boton_ejecutar = QPushButton(
            "▶  Ejecutar planificación"
        )
        self.boton_ejecutar.setObjectName("botonPrincipal")
        self.boton_ejecutar.clicked.connect(
            self.ejecutar_planificacion
        )

        controles.addWidget(
            QLabel("Algoritmo:"), 0, 0
        )
        controles.addWidget(
            self.algoritmo, 1, 0
        )
        controles.addWidget(
            QLabel("Quantum:"), 0, 1
        )
        controles.addWidget(
            self.quantum, 1, 1
        )
        controles.addWidget(
            self.boton_ejecutar, 1, 2
        )

        controles.setColumnStretch(0, 2)
        controles.setColumnStretch(1, 1)
        controles.setColumnStretch(2, 2)

        self.explicacion = QLabel()
        self.explicacion.setObjectName("textoExplicacion")
        self.explicacion.setWordWrap(True)

        controles.addWidget(
            self.explicacion, 2, 0, 1, 3
        )

        principal.addWidget(panel)

        # GANTT
        titulo_gantt = QLabel("Diagrama de Gantt")
        titulo_gantt.setObjectName("tituloSeccion")
        principal.addWidget(titulo_gantt)

        self.figura = Figure(
            figsize=(8, 2.7),
            facecolor="#182A44"
        )

        self.canvas = FigureCanvas(self.figura)
        self.canvas.setMinimumHeight(225)

        panel_gantt = QFrame()
        panel_gantt.setObjectName("panelGrafico")

        layout_gantt = QVBoxLayout(panel_gantt)
        layout_gantt.setContentsMargins(
            10, 10, 10, 10
        )
        layout_gantt.addWidget(self.canvas)

        principal.addWidget(panel_gantt)

        # PROMEDIOS
        resumen = QHBoxLayout()

        tarjeta_espera, self.promedio_espera = (
            self.crear_tarjeta("ESPERA PROMEDIO")
        )
        tarjeta_retorno, self.promedio_retorno = (
            self.crear_tarjeta("RETORNO PROMEDIO")
        )

        resumen.addWidget(tarjeta_espera)
        resumen.addWidget(tarjeta_retorno)

        principal.addLayout(resumen)

        # TABLA
        titulo_tabla = QLabel(
            "Estadísticas por proceso"
        )
        titulo_tabla.setObjectName("tituloSeccion")
        principal.addWidget(titulo_tabla)

        self.tabla = QTableWidget(0, 7)
        self.tabla.setObjectName("tablaPlanificador")

        self.tabla.setHorizontalHeaderLabels([
            "PID",
            "Nombre",
            "Llegada",
            "CPU",
            "Finalización",
            "Retorno",
            "Espera"
        ])

        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(170)
        self.tabla.setShowGrid(False)

        principal.addWidget(self.tabla)

        self.estado = QLabel(
            "Crea procesos y ejecuta un algoritmo "
            "para visualizar los resultados."
        )
        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)
        principal.addWidget(self.estado)

        scroll.setWidget(contenido)
        raiz.addWidget(scroll)

        self.dibujar_gantt([])

    def crear_tarjeta(self, titulo):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(
            15, 10, 15, 10
        )

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("nombreTarjeta")

        valor = QLabel("—")
        valor.setObjectName("valorTarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)

        return tarjeta, valor

    def actualizar_descripcion(self, *args):
        algoritmo = self.algoritmo.currentText()

        self.quantum.setEnabled(
            algoritmo == "Round Robin"
        )

        self.explicacion.setText(
            self.EXPLICACIONES.get(algoritmo, "")
        )

    def ejecutar_planificacion(self):
        procesos = self.gestor.consultar()

        if not procesos:
            self.informar(
                "Primero debes crear procesos.",
                "advertencia"
            )
            return

        try:
            resultado = planificar(
                procesos,
                self.algoritmo.currentText(),
                quantum=self.quantum.value()
            )

            self.dibujar_gantt(resultado.tramos)
            self.actualizar_metricas(resultado)

            self.informar(
                f"Planificación {resultado.algoritmo} "
                "ejecutada correctamente.",
                "exito"
            )

        except ValueError as error:
            self.informar(str(error), "error")

    def dibujar_gantt(self, tramos):
        self.figura.clear()
        eje = self.figura.add_subplot(111)

        eje.set_facecolor("#111C30")

        eje.tick_params(
            axis="both",
            colors="#CBD5E1",
            labelsize=9
        )

        for borde in eje.spines.values():
            borde.set_color("#345071")

        eje.grid(
            axis="x",
            color="#345071",
            alpha=0.5,
            linestyle="--"
        )
        eje.set_axisbelow(True)

        eje.set_xlabel(
            "Tiempo de CPU",
            color="#CBD5E1",
            fontsize=10
        )

        if not tramos:
            eje.text(
                0.5, 0.5,
                "Sin planificación ejecutada",
                ha="center",
                va="center",
                color="#94A3B8",
                transform=eje.transAxes
            )
            eje.set_xticks([])
            eje.set_yticks([])

        else:
            pids = sorted({
                tramo.pid
                for tramo in tramos
                if tramo.pid is not None
            })

            posiciones = {
                pid: indice
                for indice, pid in enumerate(pids)
            }

            colores = [
                "#3B82F6",
                "#06B6D4",
                "#8B5CF6",
                "#22C55E",
                "#F59E0B",
                "#EC4899"
            ]

            for tramo in tramos:
                if tramo.pid is None:
                    continue

                inicio = tramo.inicio
                duracion = tramo.fin - tramo.inicio

                if duracion <= 0:
                    continue

                posicion = posiciones[tramo.pid]

                color = colores[
                    posicion % len(colores)
                ]

                eje.barh(
                    posicion,
                    duracion,
                    left=inicio,
                    height=0.60,
                    color=color,
                    edgecolor="#0B1220",
                    linewidth=1
                )

                eje.text(
                    inicio + duracion / 2,
                    posicion,
                    f"P{tramo.pid}",
                    color="white",
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold"
                )

            eje.set_yticks(
                list(posiciones.values())
            )
            eje.set_yticklabels([
                f"P{pid}" for pid in pids
            ])

            eje.invert_yaxis()
            eje.xaxis.set_major_locator(
                MaxNLocator(integer=True)
            )

            if tramos:
                eje.set_xlim(
                    left=0,
                    right=max(
                        tramo.fin for tramo in tramos
                    ) + 0.5
                )

        self.figura.tight_layout(pad=1.5)
        self.canvas.draw_idle()

    def actualizar_metricas(self, resultado):
        metricas = resultado.metricas

        self.tabla.setRowCount(
            len(metricas)
        )

        for fila, metrica in enumerate(metricas):
            valores = [
                metrica.pid,
                metrica.nombre,
                metrica.llegada,
                metrica.cpu,
                metrica.finalizacion,
                metrica.retorno,
                metrica.espera
            ]

            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(
                    str(valor)
                )

                if columna != 1:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabla.setItem(
                    fila, columna, item
                )

        self.promedio_espera.setText(
            f"{resultado.promedio_espera:.2f}"
        )

        self.promedio_retorno.setText(
            f"{resultado.promedio_retorno:.2f}"
        )

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
            QWidget#vistaPlanificador,
            QWidget#contenidoPlanificador,
            QScrollArea#areaPlanificador {
                background: #111C30;
                color: #F8FAFC;
                font-family: "Segoe UI";
                font-size: 13px;
                border: none;
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
            QFrame#panelFormulario,
            QFrame#panelGrafico,
            QFrame#tarjeta {
                background: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }
            QFrame#panelFormulario QLabel {
                color: #B7C7DC;
                background: transparent;
            }
            QComboBox, QSpinBox {
                background: #0F1B2E;
                color: white;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
                width: 22px;
            }
            QComboBox QAbstractItemView {
                background: #182A44;
                color: white;
                selection-background-color: #25477E;
            }
            QSpinBox:disabled {
                color: #64748B;
            }
            QLabel#textoExplicacion {
                color: #93C5FD;
                font-size: 12px;
                padding-top: 4px;
            }
            QPushButton#botonPrincipal {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 14px;
                font-weight: bold;
            }
            QPushButton#botonPrincipal:hover {
                background: #1D4ED8;
            }
            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }
            QLabel#nombreTarjeta {
                color: #AFC2DA;
                font-size: 11px;
            }
            QLabel#valorTarjeta {
                color: white;
                font-size: 23px;
                font-weight: bold;
            }
            QTableWidget#tablaPlanificador {
                background: #111C30;
                alternate-background-color: #16263E;
                color: #E5E7EB;
                border: 1px solid #2A405E;
                border-radius: 8px;
                selection-background-color: #25477E;
            }
            QHeaderView::section {
                background: #223753;
                color: #CBD5E1;
                border: none;
                padding: 9px 5px;
                font-weight: bold;
            }
            QLabel#mensajeEstado {
                background: #182A44;
                color: #AFC2DA;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 10px;
            }
        """)
