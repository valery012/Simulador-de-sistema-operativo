
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
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
            "FCFS: los procesos se ejecutan "
            "según su orden de llegada."
        ),
        "SJF": (
            "SJF no expulsivo: selecciona el proceso "
            "disponible con menor ráfaga de CPU."
        ),
        "Round Robin": (
            "Round Robin: los procesos comparten "
            "la CPU en turnos definidos por el quantum."
        ),
    }

    def __init__(self, gestor_procesos):
        super().__init__()

        self.gestor = gestor_procesos

        self.setWindowTitle("Planificador CPU")
        self.setObjectName("vistaPlanificador")
        self.setMinimumSize(680, 460)

        # Evita que el encabezado aparezca cortado
        # la primera vez que se abre la ventana.
        self.primer_inicio = True

        self.crear_interfaz()
        self.aplicar_estilos()
        self.actualizar_descripcion()

    
    # CONSTRUCCION DE LA INTERFAZ
    

    def crear_interfaz(self):

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # Un único scroll general para pantallas pequeñas
        self.scroll = QScrollArea()
        self.scroll.setObjectName("areaPlanificador")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        contenido = QWidget()
        contenido.setObjectName("contenidoPlanificador")

        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(17, 14, 17, 14)
        principal.setSpacing(9)

        
        # ENCABEZADO
        

        encabezado = QHBoxLayout()
        encabezado.setSpacing(11)

        icono = QLabel("◈")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(43, 43)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()
        textos.setSpacing(3)

        titulo = QLabel("Planificador de CPU")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Compara FCFS, SJF no expulsivo "
            "y Round Robin."
        )
        descripcion.setObjectName("descripcionModulo")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)

        principal.addLayout(encabezado)

        
        # PANEL DE CONFIGURACION
        

        panel = QFrame()
        panel.setObjectName("panelFormulario")

        controles = QGridLayout(panel)
        controles.setContentsMargins(14, 11, 14, 11)
        controles.setHorizontalSpacing(10)
        controles.setVerticalSpacing(7)

        etiqueta_algoritmo = QLabel("Algoritmo:")
        etiqueta_quantum = QLabel("Quantum:")

        self.algoritmo = QComboBox()
        self.algoritmo.addItems([
            "FCFS",
            "SJF",
            "Round Robin",
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
        self.boton_ejecutar.setObjectName(
            "botonPrincipal"
        )

        self.boton_ejecutar.clicked.connect(
            self.ejecutar_planificacion
        )

        controles.addWidget(
            etiqueta_algoritmo, 0, 0
        )
        controles.addWidget(
            etiqueta_quantum, 0, 1
        )

        controles.addWidget(
            self.algoritmo, 1, 0
        )
        controles.addWidget(
            self.quantum, 1, 1
        )
        controles.addWidget(
            self.boton_ejecutar, 1, 2
        )

        controles.setColumnStretch(0, 3)
        controles.setColumnStretch(1, 2)
        controles.setColumnStretch(2, 3)

        self.explicacion = QLabel()
        self.explicacion.setObjectName(
            "textoExplicacion"
        )
        self.explicacion.setWordWrap(True)

        controles.addWidget(
            self.explicacion, 2, 0, 1, 3
        )

        principal.addWidget(panel)

        
        # DIAGRAMA DE GANTT
        

        titulo_gantt = QLabel(
            "Diagrama de Gantt"
        )
        titulo_gantt.setObjectName(
            "tituloSeccion"
        )

        principal.addWidget(titulo_gantt)

        panel_gantt = QFrame()
        panel_gantt.setObjectName("panelGrafico")

        layout_gantt = QVBoxLayout(panel_gantt)
        layout_gantt.setContentsMargins(9, 8, 9, 8)
        layout_gantt.setSpacing(0)

        self.figura = Figure(
            figsize=(8, 2.3),
            dpi=100,
            facecolor="#182A44"
        )

        self.canvas = FigureCanvas(self.figura)

        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # Altura fija para evitar que el Gantt
        # empuje el resto de la ventana.
        self.canvas.setFixedHeight(205)
        self.canvas.setMinimumWidth(0)

        layout_gantt.addWidget(self.canvas)

        principal.addWidget(panel_gantt)

        
        # ESTADISTICAS PROMEDIO
        

        resumen = QHBoxLayout()
        resumen.setSpacing(10)

        tarjeta_espera, self.promedio_espera = (
            self.crear_tarjeta(
                "ESPERA PROMEDIO"
            )
        )

        tarjeta_retorno, self.promedio_retorno = (
            self.crear_tarjeta(
                "RETORNO PROMEDIO"
            )
        )

        resumen.addWidget(tarjeta_espera)
        resumen.addWidget(tarjeta_retorno)

        principal.addLayout(resumen)

        
        # ESTADISTICAS INDIVIDUALES
        

        titulo_tabla = QLabel(
            "Estadísticas por proceso"
        )
        titulo_tabla.setObjectName(
            "tituloSeccion"
        )

        principal.addWidget(titulo_tabla)

        self.tabla = QTableWidget(0, 7)
        self.tabla.setObjectName(
            "tablaPlanificador"
        )

        self.tabla.setHorizontalHeaderLabels([
            "PID",
            "Nombre",
            "Llegada",
            "CPU",
            "Finalización",
            "Retorno",
            "Espera",
        ])

        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(31)

        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)

        # La tabla ocupa una zona controlada.
        # Si hay muchos procesos, se desplaza
        # dentro de la propia tabla.
        self.tabla.setMinimumHeight(130)
        self.tabla.setMaximumHeight(170)

        principal.addWidget(self.tabla)

        
        # ESTADO INFERIOR
        

        self.estado = QLabel(
            "Crea procesos y ejecuta un algoritmo "
            "para visualizar sus resultados."
        )

        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)

        principal.addWidget(self.estado)

        self.scroll.setWidget(contenido)
        raiz.addWidget(self.scroll)

        self.dibujar_gantt([])

    
    # EVITAR ENCABEZADO OCULTO
    

    def showEvent(self, evento):
        super().showEvent(evento)

        if self.primer_inicio:
            self.primer_inicio = False

            QTimer.singleShot(
                0,
                self.mostrar_desde_arriba
            )

    def mostrar_desde_arriba(self):
        self.scroll.verticalScrollBar().setValue(0)

    
    # TARJETAS

    def crear_tarjeta(self, titulo):

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(13, 9, 13, 9)
        layout.setSpacing(3)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("nombreTarjeta")

        valor = QLabel("—")
        valor.setObjectName("valorTarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)

        return tarjeta, valor

    
    # DESCRIPCION DE ALGORITMOS

    def actualizar_descripcion(self, *args):

        algoritmo = self.algoritmo.currentText()

        self.quantum.setEnabled(
            algoritmo == "Round Robin"
        )

        self.explicacion.setText(
            self.EXPLICACIONES.get(
                algoritmo, ""
            )
        )

    
    # EJECUTAR PLANIFICACION

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

            self.dibujar_gantt(
                resultado.tramos
            )

            self.actualizar_metricas(
                resultado
            )

            self.informar(
                f"Planificación {resultado.algoritmo} "
                "ejecutada correctamente.",
                "exito"
            )

        except (ValueError, RuntimeError) as error:
            self.informar(
                f"No se pudo planificar: {error}",
                "error"
            )

    # DIBUJAR DIAGRAMA DE GANTT
    

    def dibujar_gantt(self, tramos):

        self.figura.clear()

        eje = self.figura.add_subplot(111)
        eje.set_facecolor("#111C30")

        # Dejar espacio para los nombres y el eje X.
        self.figura.subplots_adjust(
            left=0.08,
            right=0.98,
            top=0.94,
            bottom=0.26
        )

        eje.tick_params(
            axis="both",
            colors="#CBD5E1",
            labelsize=9
        )

        # Eliminamos bordes decorativos que
        # parecían barras dentro del gráfico.
        eje.spines["top"].set_visible(False)
        eje.spines["right"].set_visible(False)

        eje.spines["left"].set_color("#345071")
        eje.spines["bottom"].set_color("#345071")

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
            fontsize=9
        )

        if not tramos:

            eje.text(
                0.5,
                0.5,
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
                "#EC4899",
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
                    color="#FFFFFF",
                    ha="center",
                    va="center",
                    fontsize=8,
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

            eje.set_xlim(
                left=0,
                right=max(
                    tramo.fin for tramo in tramos
                ) + 0.5
            )

        self.canvas.draw_idle()

    
    # ESTADISTICAS

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
                metrica.espera,
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

    
    # MENSAJES

    def informar(self, texto, tipo="normal"):

        colores = {
            "normal": "#AFC2DA",
            "exito": "#4ADE80",
            "advertencia": "#FBBF24",
            "error": "#FB7185",
        }

        self.estado.setText(texto)

        self.estado.setStyleSheet(
            f"color: {colores.get(tipo, colores['normal'])};"
        )

    
    # ESTILOS MIDNIGHT TECH
    
    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget#vistaPlanificador,
            QWidget#contenidoPlanificador,
            QScrollArea#areaPlanificador {
                background-color: #111C30;
                color: #F8FAFC;
                font-family: "Segoe UI";
                font-size: 13px;
                border: none;
            }

            QLabel#iconoModulo {
                background-color: #25477E;
                color: #93C5FD;
                border-radius: 11px;
                font-size: 25px;
            }

            QLabel#tituloModulo {
                color: #F8FAFC;
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#descripcionModulo {
                color: #94A3B8;
                font-size: 12px;
            }

            QFrame#panelFormulario,
            QFrame#panelGrafico,
            QFrame#tarjeta {
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 10px;
            }

            QFrame#panelFormulario QLabel {
                color: #B7C7DC;
                background: transparent;
            }

            QComboBox,
            QSpinBox {
                background-color: #0F1B2E;
                color: #FFFFFF;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 7px;
                min-height: 20px;
            }

            QComboBox:focus,
            QSpinBox:focus {
                border: 1px solid #60A5FA;
            }

            QComboBox::drop-down {
                border: none;
                width: 22px;
            }

            QComboBox QAbstractItemView {
                background-color: #182A44;
                color: #FFFFFF;
                selection-background-color: #25477E;
            }

            QSpinBox:disabled {
                color: #64748B;
            }

            QLabel#textoExplicacion {
                color: #93C5FD;
                font-size: 11px;
                padding-top: 2px;
            }

            QPushButton#botonPrincipal {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 9px 12px;
                font-weight: bold;
            }

            QPushButton#botonPrincipal:hover {
                background-color: #1D4ED8;
            }

            QPushButton#botonPrincipal:pressed {
                background-color: #1E40AF;
            }

            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 14px;
                font-weight: bold;
            }

            QLabel#nombreTarjeta {
                color: #AFC2DA;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#valorTarjeta {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
            }

            QTableWidget#tablaPlanificador {
                background-color: #111C30;
                alternate-background-color: #16263E;
                color: #E5E7EB;
                border: 1px solid #2A405E;
                border-radius: 7px;
                outline: none;
                selection-background-color: #25477E;
                selection-color: #FFFFFF;
            }

            QTableWidget#tablaPlanificador::item {
                padding: 4px;
            }

            QTableWidget#tablaPlanificador::item:selected {
                background-color: #25477E;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #223753;
                color: #CBD5E1;
                border: none;
                border-bottom: 1px solid #345071;
                padding: 7px 4px;
                font-weight: bold;
            }

            QLabel#mensajeEstado {
                background-color: #182A44;
                color: #AFC2DA;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 8px 10px;
                font-size: 12px;
            }

            QScrollBar:vertical {
                background-color: #111C30;
                width: 9px;
            }

            QScrollBar::handle:vertical {
                background-color: #3A5374;
                border-radius: 4px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
