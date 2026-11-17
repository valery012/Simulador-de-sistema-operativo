from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QComboBox,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
)

class MemoriaUI(QWidget):

    def __init__(self, gestor_memoria, gestor_procesos):
        super().__init__()

        self.gestor = gestor_memoria
        self.gestor_procesos = gestor_procesos

        self.setWindowTitle("Memoria")
        self.setObjectName("vistaMemoria")
        self.setMinimumSize(700, 490)

        self.crear_interfaz()
        self.aplicar_estilos()

        self.actualizar_procesos()
        self.actualizar_estado()

    
    # INTERFAZ
    

    def crear_interfaz(self):

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("areaMemoria")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        contenido = QWidget()
        contenido.setObjectName("contenidoMemoria")

        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(17, 15, 17, 15)
        principal.setSpacing(12)

        
        # ENCABEZADO
        

        encabezado = QHBoxLayout()
        encabezado.setSpacing(11)

        icono = QLabel("▣")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(45, 45)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()
        textos.setSpacing(3)

        titulo = QLabel("Gestión de memoria RAM")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Asigna memoria a los procesos y "
            "consulta cuánto espacio queda disponible."
        )
        descripcion.setObjectName("descripcionModulo")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)

        principal.addLayout(encabezado)

    
        # RESUMEN GENERAL
        

        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(9)

        tarjeta_total, self.valor_total = (
            self.crear_tarjeta("CAPACIDAD TOTAL")
        )

        tarjeta_ocupada, self.valor_ocupada = (
            self.crear_tarjeta("RAM OCUPADA")
        )

        tarjeta_disponible, self.valor_disponible = (
            self.crear_tarjeta("RAM LIBRE")
        )

        tarjetas.addWidget(tarjeta_total)
        tarjetas.addWidget(tarjeta_ocupada)
        tarjetas.addWidget(tarjeta_disponible)

        principal.addLayout(tarjetas)

        
        # BARRA DE OCUPACION
        

        panel_barra = QFrame()
        panel_barra.setObjectName("panelResumen")

        bloque_barra = QVBoxLayout(panel_barra)
        bloque_barra.setContentsMargins(14, 10, 14, 10)
        bloque_barra.setSpacing(9)

        fila_barra = QHBoxLayout()

        titulo_barra = QLabel("Uso de memoria")
        titulo_barra.setObjectName("tituloSeccion")

        self.porcentaje = QLabel("0 %")
        self.porcentaje.setObjectName("textoAzul")

        fila_barra.addWidget(titulo_barra)
        fila_barra.addStretch()
        fila_barra.addWidget(self.porcentaje)

        bloque_barra.addLayout(fila_barra)

        self.barra = QProgressBar()
        self.barra.setObjectName("barraMemoria")
        self.barra.setRange(
            0, max(1, self.gestor.capacidad)
        )
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(12)

        bloque_barra.addWidget(self.barra)

        principal.addWidget(panel_barra)

        
        # DOS AREAS DE TRABAJO
        

        trabajo = QHBoxLayout()
        trabajo.setSpacing(12)

        
        # IZQUIERDA: ASIGNAR
        

        panel_asignar = QFrame()
        panel_asignar.setObjectName("panelTrabajo")

        izquierda = QVBoxLayout(panel_asignar)
        izquierda.setContentsMargins(14, 13, 14, 13)
        izquierda.setSpacing(10)

        paso_1 = QLabel("PASO 1")
        paso_1.setObjectName("etiquetaPaso")

        titulo_asignar = QLabel("Asignar memoria")
        titulo_asignar.setObjectName("tituloSeccion")

        izquierda.addWidget(paso_1)
        izquierda.addWidget(titulo_asignar)

        instruccion = QLabel(
            "Selecciona un proceso activo."
        )
        instruccion.setObjectName("textoSecundario")
        instruccion.setWordWrap(True)

        izquierda.addWidget(instruccion)

        self.selector = QComboBox()
        self.selector.setObjectName("selectorProceso")
        self.selector.currentIndexChanged.connect(
            self.actualizar_solicitud
        )

        izquierda.addWidget(self.selector)

        self.boton_actualizar = QPushButton(
            "↻  Actualizar procesos"
        )
        self.boton_actualizar.setObjectName(
            "botonSecundario"
        )
        self.boton_actualizar.clicked.connect(
            self.actualizar_procesos
        )

        izquierda.addWidget(self.boton_actualizar)

        self.solicitud = QLabel(
            "RAM solicitada: —"
        )
        self.solicitud.setObjectName("detalleProceso")

        self.asignada = QLabel(
            "RAM asignada: —"
        )
        self.asignada.setObjectName("detalleProceso")

        izquierda.addWidget(self.solicitud)
        izquierda.addWidget(self.asignada)

        self.boton_asignar = QPushButton(
            "＋  Asignar RAM"
        )
        self.boton_asignar.setObjectName(
            "botonPrincipal"
        )
        self.boton_asignar.clicked.connect(
            self.asignar_memoria
        )

        izquierda.addWidget(self.boton_asignar)
        izquierda.addStretch()

        # =====================================
        # DERECHA: LIBERAR
        # =====================================

        panel_liberar = QFrame()
        panel_liberar.setObjectName("panelTrabajo")

        derecha = QVBoxLayout(panel_liberar)
        derecha.setContentsMargins(14, 13, 14, 13)
        derecha.setSpacing(10)

        paso_2 = QLabel("PASO 2")
        paso_2.setObjectName("etiquetaPaso")

        titulo_liberar = QLabel("Liberar memoria")
        titulo_liberar.setObjectName("tituloSeccion")

        derecha.addWidget(paso_2)
        derecha.addWidget(titulo_liberar)

        fila_contador = QHBoxLayout()

        instruccion_tabla = QLabel(
            "Selecciona una asignación de la tabla."
        )
        instruccion_tabla.setObjectName(
            "textoSecundario"
        )
        instruccion_tabla.setWordWrap(True)

        self.contador = QLabel("0 asignaciones")
        self.contador.setObjectName("contador")

        fila_contador.addWidget(
            instruccion_tabla, 1
        )
        fila_contador.addWidget(
            self.contador
        )

        derecha.addLayout(fila_contador)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setObjectName("tablaMemoria")

        self.tabla.setHorizontalHeaderLabels([
            "PID",
            "Proceso",
            "RAM asignada",
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
        self.tabla.setShowGrid(False)

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(31)

        cabecera = self.tabla.horizontalHeader()

        cabecera.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        cabecera.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabla.setMinimumHeight(140)

        self.tabla.itemSelectionChanged.connect(
            self.actualizar_boton_liberar
        )

        derecha.addWidget(self.tabla, 1)

        self.boton_liberar = QPushButton(
            "Liberar RAM seleccionada"
        )
        self.boton_liberar.setObjectName(
            "botonSecundario"
        )

        self.boton_liberar.clicked.connect(
            self.liberar_memoria
        )

        derecha.addWidget(self.boton_liberar)

        trabajo.addWidget(panel_asignar, 1)
        trabajo.addWidget(panel_liberar, 2)

        principal.addLayout(trabajo)

        
        # MENSAJE INFERIOR
        

        self.ayuda = QLabel(
            "Registrar un proceso no ocupa RAM "
            "automáticamente. Debes asignarla aquí."
        )
        self.ayuda.setObjectName("textoAyuda")
        self.ayuda.setWordWrap(True)

        principal.addWidget(self.ayuda)

        self.estado = QLabel(
            "Sistema de memoria listo."
        )
        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)

        principal.addWidget(self.estado)

        scroll.setWidget(contenido)
        raiz.addWidget(scroll)

    
    # TARJETAS
    

    def crear_tarjeta(self, titulo):

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(5)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("nombreTarjeta")

        valor = QLabel("0 MB")
        valor.setObjectName("valorTarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)

        return tarjeta, valor

    
    # PROCESOS DISPONIBLES
    

    def actualizar_procesos(self):

        anterior = self.selector.currentData()

        self.selector.blockSignals(True)
        self.selector.clear()

        activos = []

        for proceso in self.gestor_procesos.consultar():

            estado = getattr(
                proceso.estado,
                "name",
                str(proceso.estado)
            )

            if estado != "FINALIZADO":
                activos.append(proceso)

        if activos:

            self.selector.addItem(
                "Seleccionar proceso...",
                None
            )

            for proceso in activos:

                self.selector.addItem(
                    f"P{proceso.pid} - {proceso.nombre}",
                    proceso.pid
                )

            indice = self.selector.findData(anterior)

            if indice >= 0:
                self.selector.setCurrentIndex(indice)

            self.ayuda.setText(
                "La memoria solicitada es la que definiste "
                "al crear el proceso. Solo se ocupa RAM "
                "cuando pulsas Asignar RAM."
            )

        else:

            self.selector.addItem(
                "No hay procesos activos",
                None
            )

            self.ayuda.setText(
                "No hay procesos activos para asignar RAM. "
                "Ve al módulo Procesos y crea uno."
            )

        self.selector.blockSignals(False)

        self.selector.setEnabled(bool(activos))

        self.actualizar_solicitud()
        self.actualizar_estado()

    def buscar_proceso(self, pid):

        for proceso in self.gestor_procesos.consultar():

            if proceso.pid == pid:
                return proceso

        return None

    def actualizar_solicitud(self, *args):

        pid = self.selector.currentData()
        proceso = self.buscar_proceso(pid)

        if proceso is None:

            self.solicitud.setText(
                "RAM solicitada: —"
            )

            self.asignada.setText(
                "RAM asignada: —"
            )

            self.boton_asignar.setEnabled(False)
            return

        asignaciones = self.gestor.consultar()

        cantidad_asignada = asignaciones.get(
            pid, 0
        )

        self.solicitud.setText(
            f"RAM solicitada: {proceso.memoria} MB"
        )

        self.asignada.setText(
            f"RAM asignada actualmente: "
            f"{cantidad_asignada} MB"
        )

        # Evitar asignaciones duplicadas.
        self.boton_asignar.setEnabled(
            pid not in asignaciones
        )

    
    # ASIGNAR MEMORIA
    

    def asignar_memoria(self):

        pid = self.selector.currentData()

        if pid is None:

            self.informar(
                "Primero selecciona un proceso activo.",
                "advertencia"
            )
            return

        proceso = self.buscar_proceso(pid)

        if proceso is None:

            self.informar(
                "No se encontró el proceso.",
                "error"
            )
            return

        estado = getattr(
            proceso.estado,
            "name",
            str(proceso.estado)
        )

        if estado == "FINALIZADO":

            self.informar(
                "No se puede asignar RAM a "
                "un proceso finalizado.",
                "advertencia"
            )
            return

        try:

            self.gestor.asignar(
                proceso.pid,
                proceso.memoria
            )

            self.actualizar_estado()

            self.informar(
                f"Se asignaron {proceso.memoria} MB "
                f"al proceso P{pid}.",
                "exito"
            )

        except (ValueError, RuntimeError) as error:

            self.informar(
                f"No se pudo asignar RAM: {error}",
                "error"
            )

    
    # LIBERAR MEMORIA
    

    def actualizar_boton_liberar(self):

        fila = self.tabla.currentRow()

        seleccionado = (
            fila >= 0
            and self.tabla.item(fila, 0) is not None
        )

        self.boton_liberar.setEnabled(
            seleccionado
        )

    def liberar_memoria(self):

        fila = self.tabla.currentRow()

        if fila < 0:

            self.informar(
                "Selecciona una fila de la tabla.",
                "advertencia"
            )
            return

        item = self.tabla.item(fila, 0)

        if item is None:
            return

        pid = int(item.text())

        try:

            self.gestor.liberar(pid)

            self.actualizar_estado()

            self.informar(
                f"Memoria del proceso P{pid} liberada.",
                "exito"
            )

        except (ValueError, RuntimeError) as error:

            self.informar(
                f"No se pudo liberar RAM: {error}",
                "error"
            )

    
    # ACTUALIZAR ESTADISTICAS Y TABLA
    

    def actualizar_estado(self):

        capacidad = self.gestor.capacidad
        ocupada = self.gestor.ocupada
        disponible = self.gestor.disponible

        porcentaje = (
            ocupada / capacidad * 100
            if capacidad > 0 else 0
        )

        self.valor_total.setText(
            f"{capacidad} MB"
        )

        self.valor_ocupada.setText(
            f"{ocupada} MB"
        )

        self.valor_disponible.setText(
            f"{disponible} MB"
        )

        self.barra.setMaximum(
            max(1, capacidad)
        )
        self.barra.setValue(ocupada)

        self.porcentaje.setText(
            f"{porcentaje:.1f} %"
        )

        asignaciones = self.gestor.consultar()

        procesos = {
            p.pid: p
            for p in self.gestor_procesos.consultar()
        }

        # Recordar selección previa, si existe.
        pid_seleccionado = None
        fila_anterior = self.tabla.currentRow()

        if fila_anterior >= 0:
            item = self.tabla.item(
                fila_anterior, 0
            )
            if item is not None:
                pid_seleccionado = int(
                    item.text()
                )

        self.tabla.blockSignals(True)
        self.tabla.clearSelection()
        self.tabla.setRowCount(
            len(asignaciones)
        )

        fila_restaurar = -1

        for fila, (pid, cantidad) in enumerate(
            sorted(asignaciones.items())
        ):

            proceso = procesos.get(pid)

            nombre = (
                proceso.nombre
                if proceso is not None
                else "Desconocido"
            )

            estado = (
                getattr(
                    proceso.estado,
                    "name",
                    str(proceso.estado)
                ).title()
                if proceso is not None
                else "Sin registro"
            )

            valores = [
                str(pid),
                nombre,
                f"{cantidad} MB",
                estado,
            ]

            for columna, valor in enumerate(valores):

                item = QTableWidgetItem(valor)

                if columna != 1:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                if columna == 3:

                    color = (
                        "#4ADE80"
                        if estado == "Listo"
                        else "#FBBF24"
                        if estado == "Ejecutando"
                        else "#94A3B8"
                    )

                    item.setForeground(
                        QColor(color)
                    )

                self.tabla.setItem(
                    fila, columna, item
                )

            if pid == pid_seleccionado:
                fila_restaurar = fila

        self.tabla.blockSignals(False)

        if fila_restaurar >= 0:
            self.tabla.selectRow(
                fila_restaurar
            )

        cantidad = len(asignaciones)

        self.contador.setText(
            f"{cantidad} "
            f"{'asignación' if cantidad == 1 else 'asignaciones'}"
        )

        self.actualizar_boton_liberar()
        self.actualizar_solicitud()

    
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
            QWidget#vistaMemoria,
            QWidget#contenidoMemoria,
            QScrollArea#areaMemoria {
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

            QFrame#tarjeta,
            QFrame#panelResumen,
            QFrame#panelTrabajo {
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 10px;
            }

            QLabel#nombreTarjeta {
                color: #AFC2DA;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#valorTarjeta {
                color: #FFFFFF;
                font-size: 23px;
                font-weight: bold;
            }

            QLabel#tituloSeccion {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#etiquetaPaso {
                color: #60A5FA;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#textoAzul {
                color: #93C5FD;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#textoSecundario {
                color: #AFC2DA;
                font-size: 11px;
            }

            QLabel#detalleProceso {
                color: #E5E7EB;
                background-color: #111C30;
                border: 1px solid #345071;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }

            QLabel#contador {
                color: #93C5FD;
                background-color: #1E3A5F;
                border-radius: 7px;
                padding: 6px 9px;
                font-size: 10px;
            }

            QComboBox#selectorProceso {
                background-color: #0F1B2E;
                color: #FFFFFF;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 9px;
                min-height: 18px;
            }

            QComboBox#selectorProceso:focus {
                border: 1px solid #60A5FA;
            }

            QComboBox#selectorProceso:disabled {
                color: #94A3B8;
                background-color: #162238;
            }

            QComboBox::drop-down {
                border: none;
                width: 23px;
            }

            QComboBox QAbstractItemView {
                background-color: #182A44;
                color: white;
                selection-background-color: #25477E;
            }

            QPushButton#botonPrincipal {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 10px 12px;
                font-weight: bold;
            }

            QPushButton#botonPrincipal:hover {
                background-color: #1D4ED8;
            }

            QPushButton#botonSecundario {
                background-color: #24364F;
                color: #E5E7EB;
                border: 1px solid #3A5374;
                border-radius: 7px;
                padding: 9px 12px;
            }

            QPushButton#botonSecundario:hover {
                background-color: #345174;
            }

            QPushButton#botonPrincipal:disabled,
            QPushButton#botonSecundario:disabled {
                background-color: #25354B;
                color: #8295AF;
                border: 1px solid #33465F;
            }

            QProgressBar#barraMemoria {
                background-color: #344760;
                border: none;
                border-radius: 6px;
            }

            QProgressBar#barraMemoria::chunk {
                background-color: #3B82F6;
                border-radius: 6px;
            }

            QTableWidget#tablaMemoria {
                background-color: #111C30;
                alternate-background-color: #16263E;
                color: #E5E7EB;
                border: 1px solid #345071;
                border-radius: 7px;
                outline: none;
                selection-background-color: #25477E;
                selection-color: #FFFFFF;
            }

            QTableWidget#tablaMemoria::item {
                padding: 4px;
            }

            QTableWidget#tablaMemoria::item:selected {
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

            QLabel#textoAyuda {
                background-color: #153047;
                color: #A5D7F0;
                border: 1px solid #285271;
                border-radius: 7px;
                padding: 9px;
                font-size: 11px;
            }

            QLabel#mensajeEstado {
                background-color: #182A44;
                color: #AFC2DA;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 10px;
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
