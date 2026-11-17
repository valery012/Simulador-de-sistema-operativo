
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)


class ProcesosUI(QWidget):

    def __init__(self, gestor_procesos):
        super().__init__()

        self.gestor = gestor_procesos

        self.setObjectName("vistaProcesos")
        self.setWindowTitle("Procesos")
        self.setMinimumSize(700, 460)

        self.crear_interfaz()
        self.aplicar_estilos()
        self.actualizar_tabla()


    def crear_interfaz(self):

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)


        encabezado = QHBoxLayout()
        encabezado.setSpacing(12)

        icono = QLabel("⚙")
        icono.setObjectName("iconoModulo")
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono.setFixedSize(48, 48)

        encabezado.addWidget(icono)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("Gestión de procesos")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Crea, consulta y finaliza procesos simulados "
            "del sistema operativo."
        )
        descripcion.setObjectName("descripcionModulo")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addLayout(textos, 1)

        principal.addLayout(encabezado)


        panel = QFrame()
        panel.setObjectName("panelFormulario")

        formulario = QGridLayout(panel)
        formulario.setContentsMargins(16, 14, 16, 14)
        formulario.setHorizontalSpacing(17)
        formulario.setVerticalSpacing(8)

        formulario.setColumnStretch(0, 1)
        formulario.setColumnStretch(1, 1)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText(
            "Ej. Editor de texto"
        )

        self.llegada = self.crear_campo_numerico(
            minimo=0,
            maximo=9999,
            valor=0
        )

        self.cpu = self.crear_campo_numerico(
            minimo=1,
            maximo=9999,
            valor=5
        )

        self.prioridad = self.crear_campo_numerico(
            minimo=0,
            maximo=9999,
            valor=1
        )

        self.memoria = self.crear_campo_numerico(
            minimo=1,
            maximo=65536,
            valor=128
        )
        self.memoria.setSuffix(" MB")

        formulario.addWidget(
            self.crear_etiqueta("Nombre del proceso"),
            0, 0
        )
        formulario.addWidget(
            self.crear_etiqueta("Tiempo de llegada"),
            0, 1
        )

        formulario.addWidget(self.nombre, 1, 0)
        formulario.addWidget(self.llegada, 1, 1)

        formulario.addWidget(
            self.crear_etiqueta("CPU requerida"),
            2, 0
        )
        formulario.addWidget(
            self.crear_etiqueta("Prioridad"),
            2, 1
        )

        formulario.addWidget(self.cpu, 3, 0)
        formulario.addWidget(self.prioridad, 3, 1)

        formulario.addWidget(
            self.crear_etiqueta("Memoria solicitada"),
            4, 0
        )
        formulario.addWidget(
            self.crear_etiqueta("Estado inicial"),
            4, 1
        )

        formulario.addWidget(self.memoria, 5, 0)

        estado_inicial = QLabel("●  LISTO")
        estado_inicial.setObjectName("estadoInicial")
        estado_inicial.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
            | Qt.AlignmentFlag.AlignLeft
        )

        formulario.addWidget(estado_inicial, 5, 1)

        # Botones
        acciones = QHBoxLayout()
        acciones.setSpacing(10)

        self.boton_crear = QPushButton(
            "＋  Crear proceso"
        )
        self.boton_crear.setObjectName(
            "botonPrincipal"
        )

        self.boton_finalizar = QPushButton(
            "Finalizar seleccionado"
        )
        self.boton_finalizar.setObjectName(
            "botonSecundario"
        )

        self.boton_crear.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.boton_finalizar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.boton_crear.clicked.connect(
            self.crear_proceso
        )
        self.boton_finalizar.clicked.connect(
            self.finalizar_proceso
        )

        acciones.addWidget(self.boton_crear)
        acciones.addWidget(self.boton_finalizar)
        acciones.addStretch()

        formulario.addLayout(
            acciones, 6, 0, 1, 2
        )

        principal.addWidget(panel)


        cabecera_tabla = QHBoxLayout()

        titulo_tabla = QLabel(
            "Procesos del sistema"
        )
        titulo_tabla.setObjectName(
            "tituloSeccion"
        )

        self.contador = QLabel(
            "0 procesos"
        )
        self.contador.setObjectName(
            "contadorProcesos"
        )

        cabecera_tabla.addWidget(titulo_tabla)
        cabecera_tabla.addStretch()
        cabecera_tabla.addWidget(self.contador)

        principal.addLayout(cabecera_tabla)


        self.tabla = QTableWidget(0, 7)

        self.tabla.setObjectName(
            "tablaProcesos"
        )

        self.tabla.setHorizontalHeaderLabels([
            "PID",
            "Nombre",
            "Llegada",
            "CPU",
            "Prioridad",
            "Memoria",
            "Estado",
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

        self.tabla.setAlternatingRowColors(True)

        self.tabla.verticalHeader().setVisible(
            False
        )

        self.tabla.verticalHeader().setDefaultSectionSize(
            36
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla.horizontalHeader().setMinimumSectionSize(
            60
        )

        self.tabla.setShowGrid(False)

        principal.addWidget(
            self.tabla, 1
        )


        self.mensaje = QLabel(
            "Sistema listo para gestionar procesos."
        )

        self.mensaje.setObjectName(
            "mensajeEstado"
        )

        self.mensaje.setWordWrap(True)

        principal.addWidget(self.mensaje)


    def crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName(
            "etiquetaCampo"
        )
        return etiqueta

    def crear_campo_numerico(
        self, minimo, maximo, valor
    ):
        campo = QSpinBox()
        campo.setRange(minimo, maximo)
        campo.setValue(valor)
        return campo

    def informar(self, texto, tipo="normal"):

        colores = {
            "normal": "#AFC2DA",
            "exito": "#4ADE80",
            "advertencia": "#FBBF24",
            "error": "#FB7185",
        }

        color = colores.get(
            tipo, colores["normal"]
        )

        self.mensaje.setText(texto)
        self.mensaje.setStyleSheet(
            f"color: {color};"
        )


    def crear_proceso(self):

        nombre = self.nombre.text().strip()

        if not nombre:
            self.informar(
                "Debes escribir el nombre del proceso.",
                "advertencia"
            )
            return

        try:
            proceso = self.gestor.crear(
                nombre=nombre,
                llegada=self.llegada.value(),
                cpu_requerida=self.cpu.value(),
                prioridad=self.prioridad.value(),
                memoria=self.memoria.value(),
            )

            self.actualizar_tabla()
            self.nombre.clear()

            pid = getattr(
                proceso, "pid", None
            )

            if pid is not None:
                mensaje = (
                    f"Proceso P{pid} creado correctamente."
                )
            else:
                mensaje = (
                    f"Proceso '{nombre}' creado correctamente."
                )

            self.informar(
                mensaje,
                "exito"
            )

        except (ValueError, RuntimeError) as error:
            self.informar(
                f"No se pudo crear el proceso: {error}",
                "error"
            )


    def finalizar_proceso(self):

        fila = self.tabla.currentRow()

        if fila < 0:
            self.informar(
                "Selecciona un proceso de la tabla.",
                "advertencia"
            )
            return

        elemento = self.tabla.item(
            fila, 0
        )

        if elemento is None:
            return

        pid = int(
            elemento.text()
        )

        try:
            self.gestor.finalizar(pid)

            self.actualizar_tabla()

            self.informar(
                f"Proceso P{pid} finalizado. "
                "Si tiene memoria asignada, "
                "puedes liberarla desde Memoria.",
                "exito"
            )

        except (ValueError, RuntimeError) as error:
            self.informar(
                f"No se pudo finalizar el proceso: {error}",
                "error"
            )


    def actualizar_tabla(self):

        procesos = self.gestor.consultar()

        self.tabla.setRowCount(
            len(procesos)
        )

        for fila, proceso in enumerate(procesos):

            estado = getattr(
                proceso.estado,
                "name",
                str(proceso.estado)
            )

            estado = estado.replace(
                "_", " "
            ).title()

            valores = [
                str(proceso.pid),
                str(proceso.nombre),
                str(proceso.llegada),
                str(proceso.cpu_requerida),
                str(proceso.prioridad),
                f"{proceso.memoria} MB",
                estado,
            ]

            for columna, valor in enumerate(valores):

                item = QTableWidgetItem(
                    valor
                )

                if columna != 1:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                if columna == 6:

                    if estado == "Listo":
                        item.setForeground(
                            QColor("#4ADE80")
                        )

                    elif estado == "Ejecutando":
                        item.setForeground(
                            QColor("#FBBF24")
                        )

                    elif estado == "Finalizado":
                        item.setForeground(
                            QColor("#94A3B8")
                        )

                self.tabla.setItem(
                    fila,
                    columna,
                    item
                )

        cantidad = len(procesos)

        self.contador.setText(
            f"{cantidad} "
            f"{'proceso' if cantidad == 1 else 'procesos'}"
        )

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QWidget#vistaProcesos {
                background-color: #111C30;
                color: #F8FAFC;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLabel#iconoModulo {
                background-color: #25477E;
                color: #93C5FD;
                border: 1px solid #365D98;
                border-radius: 11px;
                font-size: 27px;
                font-weight: bold;
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
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }

            QLabel#etiquetaCampo {
                color: #B7C7DC;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
            }

            QLineEdit, QSpinBox {
                background-color: #0F1B2E;
                color: #F8FAFC;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 7px 10px;
                min-height: 18px;
                selection-background-color: #2563EB;
            }

            QLineEdit:hover, QSpinBox:hover {
                border: 1px solid #4C729C;
            }

            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #60A5FA;
            }

            QLabel#estadoInicial {
                color: #4ADE80;
                background-color: #15332D;
                border: 1px solid #23594A;
                border-radius: 7px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton#botonPrincipal {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 10px 16px;
                font-weight: bold;
            }

            QPushButton#botonPrincipal:hover {
                background-color: #1D4ED8;
            }

            QPushButton#botonPrincipal:pressed {
                background-color: #1E40AF;
            }

            QPushButton#botonSecundario {
                background-color: #24364F;
                color: #E5E7EB;
                border: 1px solid #3A5374;
                border-radius: 7px;
                padding: 9px 16px;
            }

            QPushButton#botonSecundario:hover {
                background-color: #345174;
            }

            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#contadorProcesos {
                color: #93C5FD;
                background-color: #1E3A5F;
                border: 1px solid #335682;
                border-radius: 8px;
                padding: 6px 11px;
                font-size: 11px;
            }

            QTableWidget#tablaProcesos {
                background-color: #111C30;
                alternate-background-color: #16263E;
                color: #E5E7EB;
                border: 1px solid #2A405E;
                border-radius: 8px;
                outline: none;
                gridline-color: #24364F;
                selection-background-color: #25477E;
                selection-color: white;
            }

            QTableWidget#tablaProcesos::item {
                padding: 5px;
            }

            QTableWidget#tablaProcesos::item:selected {
                background-color: #25477E;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #223753;
                color: #CBD5E1;
                border: none;
                border-bottom: 1px solid #345071;
                padding: 9px 5px;
                font-weight: bold;
            }

            QLabel#mensajeEstado {
                color: #AFC2DA;
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 9px 12px;
                font-size: 12px;
            }

            QScrollBar:vertical {
                background-color: #111C30;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background-color: #3A5374;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)