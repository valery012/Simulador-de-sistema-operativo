
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QComboBox, QPushButton,
    QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QVBoxLayout,
    QHBoxLayout, QGridLayout
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

    def crear_interfaz(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        icono = QLabel("▣")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(48, 48)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()
        titulo = QLabel("Gestión de memoria RAM")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Asigna y libera memoria simulada respetando "
            "la capacidad disponible."
        )
        descripcion.setObjectName("descripcionModulo")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)
        principal.addLayout(encabezado)

        # TARJETAS
        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(10)

        self.valor_total, tarjeta_total = self.crear_tarjeta(
            "CAPACIDAD TOTAL"
        )
        self.valor_ocupada, tarjeta_ocupada = self.crear_tarjeta(
            "RAM OCUPADA"
        )
        self.valor_disponible, tarjeta_disponible = self.crear_tarjeta(
            "RAM DISPONIBLE"
        )

        tarjetas.addWidget(tarjeta_total)
        tarjetas.addWidget(tarjeta_ocupada)
        tarjetas.addWidget(tarjeta_disponible)
        principal.addLayout(tarjetas)

        # BARRA DE MEMORIA
        panel_barra = QFrame()
        panel_barra.setObjectName("panelFormulario")
        bloque = QVBoxLayout(panel_barra)

        cabecera = QHBoxLayout()

        etiqueta = QLabel("Uso de memoria")
        etiqueta.setObjectName("tituloSeccion")

        self.porcentaje = QLabel("0 %")
        self.porcentaje.setObjectName("contador")

        cabecera.addWidget(etiqueta)
        cabecera.addStretch()
        cabecera.addWidget(self.porcentaje)

        bloque.addLayout(cabecera)

        self.barra = QProgressBar()
        self.barra.setRange(0, self.gestor.capacidad)
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(13)

        bloque.addWidget(self.barra)
        principal.addWidget(panel_barra)

        # ASIGNACION DE MEMORIA
        panel_asignacion = QFrame()
        panel_asignacion.setObjectName("panelFormulario")

        formulario = QVBoxLayout(panel_asignacion)
        formulario.setSpacing(10)

        formulario.addWidget(
            QLabel("Selecciona un proceso registrado:")
        )

        seleccion = QHBoxLayout()

        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(
            self.actualizar_solicitud
        )

        self.boton_actualizar = QPushButton(
            "↻  Actualizar procesos"
        )
        self.boton_actualizar.setObjectName("botonSecundario")
        self.boton_actualizar.clicked.connect(
            self.actualizar_procesos
        )

        seleccion.addWidget(self.selector, 1)
        seleccion.addWidget(self.boton_actualizar)
        formulario.addLayout(seleccion)

        self.solicitud = QLabel(
            "Memoria solicitada: —"
        )
        self.solicitud.setObjectName("textoSecundario")
        formulario.addWidget(self.solicitud)

        self.boton_asignar = QPushButton(
            "＋  Asignar memoria"
        )
        self.boton_asignar.setObjectName("botonPrincipal")
        self.boton_asignar.clicked.connect(
            self.asignar_memoria
        )

        formulario.addWidget(self.boton_asignar)
        principal.addWidget(panel_asignacion)

        # TABLA
        cabecera_tabla = QHBoxLayout()

        titulo_tabla = QLabel("Asignaciones activas")
        titulo_tabla.setObjectName("tituloSeccion")

        self.contador = QLabel("0 asignaciones")
        self.contador.setObjectName("contador")

        cabecera_tabla.addWidget(titulo_tabla)
        cabecera_tabla.addStretch()
        cabecera_tabla.addWidget(self.contador)
        principal.addLayout(cabecera_tabla)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setObjectName("tablaMemoria")
        self.tabla.setHorizontalHeaderLabels([
            "PID", "Proceso", "Memoria", "Estado"
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

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)

        principal.addWidget(self.tabla, 1)

        self.boton_liberar = QPushButton(
            "Liberar memoria del proceso seleccionado en la tabla"
        )
        self.boton_liberar.setObjectName("botonSecundario")
        self.boton_liberar.clicked.connect(
            self.liberar_memoria
        )
        principal.addWidget(self.boton_liberar)

        self.estado = QLabel(
            "Selecciona un proceso para asignarle memoria."
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

        valor = QLabel("0 MB")
        valor.setObjectName("valorTarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)

        return valor, tarjeta

    def actualizar_procesos(self):
        anterior = self.selector.currentData()
        self.selector.clear()

        self.selector.addItem(
            "Seleccionar proceso", None
        )

        for proceso in self.gestor_procesos.consultar():
            self.selector.addItem(
                f"P{proceso.pid} - {proceso.nombre}",
                proceso.pid
            )

        indice = self.selector.findData(anterior)
        if indice >= 0:
            self.selector.setCurrentIndex(indice)

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
                "Memoria solicitada: —"
            )
            return

        estado = getattr(
            proceso.estado, "name", str(proceso.estado)
        )

        self.solicitud.setText(
            f"Memoria solicitada: {proceso.memoria} MB"
            f"  |  Estado: {estado.title()}"
        )

    def asignar_memoria(self):
        pid = self.selector.currentData()

        if pid is None:
            self.informar(
                "Selecciona un proceso.", "advertencia"
            )
            return

        proceso = self.buscar_proceso(pid)

        if proceso is None:
            self.informar(
                "El proceso ya no existe.", "error"
            )
            return

        estado = getattr(
            proceso.estado, "name", str(proceso.estado)
        )

        if estado == "FINALIZADO":
            self.informar(
                "No puedes asignar memoria a un proceso finalizado.",
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
                f"Asignados {proceso.memoria} MB al "
                f"proceso P{proceso.pid}.",
                "exito"
            )

        except ValueError as error:
            self.informar(str(error), "error")

    def liberar_memoria(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            self.informar(
                "Selecciona una asignación en la tabla.",
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

        except ValueError as error:
            self.informar(str(error), "error")

    def actualizar_estado(self):
        ocupada = self.gestor.ocupada
        disponible = self.gestor.disponible
        capacidad = self.gestor.capacidad

        porcentaje = (
            (ocupada / capacidad) * 100
            if capacidad else 0
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

        self.barra.setMaximum(capacidad)
        self.barra.setValue(ocupada)
        self.porcentaje.setText(
            f"{porcentaje:.1f} %"
        )

        asignaciones = self.gestor.consultar()
        procesos = {
            p.pid: p
            for p in self.gestor_procesos.consultar()
        }

        self.tabla.setRowCount(len(asignaciones))

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

            datos = [
                str(pid),
                nombre,
                f"{cantidad} MB",
                estado
            ]

            for columna, valor in enumerate(datos):
                item = QTableWidgetItem(valor)

                if columna != 1:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                if columna == 3:
                    item.setForeground(
                        QColor(
                            "#4ADE80"
                            if estado == "Listo"
                            else "#FBBF24"
                            if estado == "Ejecutando"
                            else "#94A3B8"
                        )
                    )

                self.tabla.setItem(
                    fila, columna, item
                )

        cantidad = len(asignaciones)
        self.contador.setText(
            f"{cantidad} asignaciones"
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
            QWidget#vistaMemoria {
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
            QFrame#tarjeta, QFrame#panelFormulario {
                background: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }
            QFrame#panelFormulario QLabel {
                color: #B7C7DC;
                background: transparent;
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
            QLabel#contador {
                color: #93C5FD;
                background: #1E3A5F;
                border-radius: 8px;
                padding: 6px 11px;
            }
            QLabel#textoSecundario {
                color: #93C5FD;
                font-size: 12px;
            }
            QComboBox {
                background: #0F1B2E;
                color: #F8FAFC;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 9px;
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
            QProgressBar {
                background: #344760;
                border: none;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background: #3B82F6;
                border-radius: 6px;
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
            QPushButton#botonSecundario {
                background: #24364F;
                color: #E5E7EB;
                border: 1px solid #3A5374;
                border-radius: 7px;
                padding: 9px 13px;
            }
            QPushButton#botonSecundario:hover {
                background: #345174;
            }
            QTableWidget#tablaMemoria {
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
                padding: 9px;
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

