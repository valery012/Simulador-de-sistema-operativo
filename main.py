
import sys

from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMdiArea,
    QMenu,
    QStackedWidget,
    QScrollArea,
    QProgressBar,
)

from simulador.procesos import (
    GestorProcesos,
    EstadoProceso,
)
from simulador.comunicacion import ColaMensajes
from simulador.memoria import GestorMemoria
from simulador.archivos import GestorArchivos

from interfaz.procesos_ui import ProcesosUI
from interfaz.planificador_ui import PlanificadorUI
from interfaz.concurrencia_ui import ConcurrenciaUI
from interfaz.comunicacion_ui import ComunicacionUI
from interfaz.memoria_ui import MemoriaUI
from interfaz.archivos_ui import ArchivosUI


class PyOS(QMainWindow):

    MODULOS = {
        "Procesos": "Crear, consultar y finalizar procesos.",
        "Planificador CPU": "Ejecutar FCFS, SJF y Round Robin.",
        "Concurrencia": "Demostrar hilos y sincronización.",
        "Comunicación": "Enviar mensajes mediante una cola FIFO.",
        "Memoria": "Asignar y liberar memoria simulada.",
        "Archivos": "Administrar archivos de texto.",
    }

    ICONOS = {
        "Inicio": "⌂",
        "Procesos": "⚙",
        "Planificador CPU": "◈",
        "Concurrencia": "⇄",
        "Comunicación": "✉",
        "Memoria": "▣",
        "Archivos": "▤",
    }

    def __init__(self):
        super().__init__()

        # Gestores únicos, compartidos por todos los módulos.
        self.gestor_procesos = GestorProcesos()
        self.cola_mensajes = ColaMensajes()
        self.gestor_memoria = GestorMemoria(1024)
        self.gestor_archivos = GestorArchivos()

        self.setWindowTitle(
            "PyOS Simulator | Midnight Tech Edition"
        )
        self.resize(1280, 800)
        self.setMinimumSize(850, 550)

        self.botones_nav = {}

        self.crear_escritorio()
        self.aplicar_estilos()
        self.mostrar_inicio()

        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(
            self.actualizar_indicadores
        )
        self.temporizador.start(1000)


    def crear_escritorio(self):

        principal = QWidget()
        self.setCentralWidget(principal)

        layout = QVBoxLayout(principal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ENCABEZADO SUPERIOR
        encabezado = QFrame()
        encabezado.setObjectName("encabezado")

        barra = QHBoxLayout(encabezado)
        barra.setContentsMargins(22, 12, 22, 12)
        barra.setSpacing(12)

        logo = QLabel("◈")
        logo.setObjectName("logo")
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        barra.addWidget(logo)

        identidad = QVBoxLayout()
        identidad.setSpacing(3)

        titulo = QLabel("PyOS Simulator")
        titulo.setObjectName("tituloPrincipal")

        subtitulo = QLabel("MIDNIGHT TECH EDITION")
        subtitulo.setObjectName("subtituloPrincipal")

        identidad.addWidget(titulo)
        identidad.addWidget(subtitulo)

        barra.addLayout(identidad)
        barra.addStretch()

        indicador = QLabel("●  SIMULADOR ACTIVO")
        indicador.setObjectName("indicadorActivo")
        barra.addWidget(indicador)

        layout.addWidget(encabezado)

        # CUERPO
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)

        # MENU LATERAL
        lateral = QFrame()
        lateral.setObjectName("lateral")
        lateral.setFixedWidth(220)

        navegacion = QVBoxLayout(lateral)
        navegacion.setContentsMargins(13, 22, 13, 15)
        navegacion.setSpacing(7)

        general = QLabel("GENERAL")
        general.setObjectName("seccion")
        navegacion.addWidget(general)

        self.agregar_boton(
            navegacion,
            "Inicio",
            self.mostrar_inicio
        )

        navegacion.addSpacing(18)

        modulos = QLabel("MODULOS DEL SISTEMA")
        modulos.setObjectName("seccion")
        navegacion.addWidget(modulos)

        for nombre in self.MODULOS:
            self.agregar_boton(
                navegacion,
                nombre,
                lambda n=nombre: self.abrir_modulo(n)
            )

        navegacion.addStretch()

        nota = QLabel(
            "PYOS 1.0\nSimulación académica"
        )
        nota.setObjectName("notaLateral")
        navegacion.addWidget(nota)

        cuerpo.addWidget(lateral)

        # VISTAS
        self.vistas = QStackedWidget()
        self.vistas.setObjectName("vistas")

        self.dashboard = self.crear_dashboard()

        self.escritorio = QMdiArea()
        self.escritorio.setObjectName("escritorio")

        self.escritorio.setBackground(
            QBrush(QColor("#0F1B2E"))
        )

        self.escritorio.setViewMode(
            QMdiArea.ViewMode.SubWindowView
        )

        self.escritorio.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.escritorio.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.escritorio.subWindowActivated.connect(
            self.ventana_activada
        )

        self.vistas.addWidget(self.dashboard)
        self.vistas.addWidget(self.escritorio)

        cuerpo.addWidget(self.vistas, 1)
        layout.addLayout(cuerpo, 1)

        # BARRA INFERIOR
        inferior = QFrame()
        inferior.setObjectName("barraInferior")

        tareas = QHBoxLayout(inferior)
        tareas.setContentsMargins(14, 7, 16, 7)
        tareas.setSpacing(12)

        boton_inicio = QPushButton("⌂  Inicio")
        boton_inicio.setObjectName("botonInicio")
        boton_inicio.clicked.connect(
            self.mostrar_inicio
        )
        tareas.addWidget(boton_inicio)

        boton_aplicaciones = QPushButton(
            "☰  Aplicaciones"
        )
        boton_aplicaciones.setObjectName(
            "botonAplicaciones"
        )

        menu = QMenu(self)

        for nombre in self.MODULOS:
            accion = menu.addAction(nombre)
            accion.triggered.connect(
                lambda checked=False, n=nombre:
                self.abrir_modulo(n)
            )

        boton_aplicaciones.setMenu(menu)
        tareas.addWidget(boton_aplicaciones)

        self.estado_sistema = QLabel()
        self.estado_sistema.setObjectName("estadoSistema")
        tareas.addWidget(self.estado_sistema, 1)

        self.reloj = QLabel()
        self.reloj.setObjectName("reloj")
        tareas.addWidget(self.reloj)

        layout.addWidget(inferior)

    def agregar_boton(self, layout, nombre, funcion):

        icono = self.ICONOS.get(nombre, "●")

        boton = QPushButton(
            f"{icono}    {nombre}"
        )
        boton.setObjectName("botonNavegacion")
        boton.setCheckable(True)

        boton.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        boton.setToolTip(
            self.MODULOS.get(
                nombre,
                "Ver resumen del simulador."
            )
        )

        boton.clicked.connect(
            lambda checked=False: funcion()
        )

        layout.addWidget(boton)
        self.botones_nav[nombre] = boton

    def marcar_activo(self, nombre):

        for modulo, boton in self.botones_nav.items():
            boton.setChecked(modulo == nombre)


    def crear_dashboard(self):

        area = QScrollArea()
        area.setObjectName("dashboardArea")
        area.setWidgetResizable(True)

        area.setFrameShape(
            QFrame.Shape.NoFrame
        )

        contenido = QWidget()
        contenido.setObjectName("dashboard")

        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(27, 24, 27, 24)
        layout.setSpacing(15)

        etiqueta = QLabel("CENTRO DE CONTROL")
        etiqueta.setObjectName("etiquetaSuperior")
        layout.addWidget(etiqueta)

        titulo = QLabel("Panel del sistema")
        titulo.setObjectName("tituloDashboard")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Consulta el estado de los recursos "
            "y accede a los módulos de simulación."
        )
        descripcion.setObjectName("descripcionDashboard")
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        # TARJETAS
        tarjetas = QGridLayout()
        tarjetas.setSpacing(13)

        (
            tarjeta_procesos,
            self.valor_procesos,
            self.detalle_procesos
        ) = self.crear_tarjeta(
            "PROCESOS REGISTRADOS", "⚙"
        )

        (
            tarjeta_memoria,
            self.valor_memoria,
            self.detalle_memoria
        ) = self.crear_tarjeta(
            "MEMORIA UTILIZADA", "▣"
        )

        (
            tarjeta_mensajes,
            self.valor_mensajes,
            self.detalle_mensajes
        ) = self.crear_tarjeta(
            "MENSAJES PENDIENTES", "✉"
        )

        (
            tarjeta_archivos,
            self.valor_archivos,
            self.detalle_archivos
        ) = self.crear_tarjeta(
            "ARCHIVOS GUARDADOS", "▤"
        )

        tarjetas.addWidget(tarjeta_procesos, 0, 0)
        tarjetas.addWidget(tarjeta_memoria, 0, 1)
        tarjetas.addWidget(tarjeta_mensajes, 1, 0)
        tarjetas.addWidget(tarjeta_archivos, 1, 1)

        layout.addLayout(tarjetas)

        # MEMORIA
        panel_ram = QFrame()
        panel_ram.setObjectName("panelResumen")

        bloque = QVBoxLayout(panel_ram)
        bloque.setContentsMargins(18, 16, 18, 16)
        bloque.setSpacing(11)

        titulo_ram = QLabel("Estado de memoria RAM")
        titulo_ram.setObjectName("tituloPanel")
        bloque.addWidget(titulo_ram)

        self.barra_memoria = QProgressBar()
        self.barra_memoria.setObjectName("barraMemoria")

        self.barra_memoria.setRange(
            0,
            self.gestor_memoria.capacidad
        )
        self.barra_memoria.setTextVisible(False)
        self.barra_memoria.setFixedHeight(12)

        bloque.addWidget(self.barra_memoria)

        self.resumen_memoria = QLabel()
        self.resumen_memoria.setObjectName("textoSecundario")
        bloque.addWidget(self.resumen_memoria)

        layout.addWidget(panel_ram)

        # ACCESOS RAPIDOS
        accesos = QHBoxLayout()
        accesos.setSpacing(12)

        boton_procesos = QPushButton(
            "⚙  Administrar procesos"
        )
        boton_procesos.setObjectName("accesoRapido")
        boton_procesos.clicked.connect(
            lambda: self.abrir_modulo("Procesos")
        )

        boton_cpu = QPushButton(
            "◈  Planificador CPU"
        )
        boton_cpu.setObjectName("accesoRapido")
        boton_cpu.clicked.connect(
            lambda: self.abrir_modulo(
                "Planificador CPU"
            )
        )

        accesos.addWidget(boton_procesos)
        accesos.addWidget(boton_cpu)

        layout.addLayout(accesos)

        ayuda = QLabel(
            "PyOS es un simulador educativo. "
            "Los procesos, la planificación de CPU "
            "y la RAM son modelos simulados. "
            "Los hilos y las operaciones sobre archivos "
            "utilizan mecanismos reales de Python."
        )
        ayuda.setObjectName("textoAyuda")
        ayuda.setWordWrap(True)

        layout.addWidget(ayuda)
        layout.addStretch()

        area.setWidget(contenido)
        return area

    def crear_tarjeta(self, nombre, icono):

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaResumen")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(17, 13, 17, 13)
        layout.setSpacing(6)

        superior = QHBoxLayout()

        etiqueta = QLabel(nombre)
        etiqueta.setObjectName("nombreTarjeta")

        simbolo = QLabel(icono)
        simbolo.setObjectName("iconoTarjeta")

        superior.addWidget(etiqueta)
        superior.addStretch()
        superior.addWidget(simbolo)

        layout.addLayout(superior)

        valor = QLabel("0")
        valor.setObjectName("valorTarjeta")
        layout.addWidget(valor)

        detalle = QLabel("Sin datos")
        detalle.setObjectName("detalleTarjeta")
        layout.addWidget(detalle)

        return tarjeta, valor, detalle


    def actualizar_indicadores(self):

        procesos = self.gestor_procesos.consultar()
        total = len(procesos)

        finalizados = sum(
            1 for proceso in procesos
            if proceso.estado == EstadoProceso.FINALIZADO
        )

        ocupada = self.gestor_memoria.ocupada
        disponible = self.gestor_memoria.disponible
        capacidad = self.gestor_memoria.capacidad

        mensajes = self.cola_mensajes.pendientes()

        try:
            archivos = str(
                len(self.gestor_archivos.listar())
            )
        except OSError:
            archivos = "—"

        self.valor_procesos.setText(str(total))
        self.detalle_procesos.setText(
            f"{finalizados} finalizados"
        )

        self.valor_memoria.setText(
            f"{ocupada} MB"
        )
        self.detalle_memoria.setText(
            f"{disponible} MB disponibles"
        )

        self.valor_mensajes.setText(str(mensajes))
        self.detalle_mensajes.setText("En cola FIFO")

        self.valor_archivos.setText(archivos)
        self.detalle_archivos.setText(
            "Carpeta archivos_prueba"
        )

        self.barra_memoria.setMaximum(
            max(1, capacidad)
        )
        self.barra_memoria.setValue(ocupada)

        porcentaje = (
            ocupada / capacidad * 100
            if capacidad else 0
        )

        self.resumen_memoria.setText(
            f"{ocupada} MB ocupados  |  "
            f"{disponible} MB libres  |  "
            f"{porcentaje:.1f}% utilizado"
        )

        self.estado_sistema.setText(
            f"Procesos: {total}  |  "
            f"RAM: {ocupada}/{capacidad} MB  |  "
            f"Mensajes: {mensajes}"
        )

        self.reloj.setText(
            QDateTime.currentDateTime().toString(
                "hh:mm:ss"
            )
        )


    def procesos_actualizados(self):

        # Actualizar inmediatamente el dashboard.
        self.actualizar_indicadores()

        # Avisar a los módulos que están abiertos.
        for ventana in self.escritorio.subWindowList():

            panel = ventana.widget()

            if isinstance(panel, MemoriaUI):
                panel.actualizar_procesos()
                panel.actualizar_estado()

            elif isinstance(panel, ComunicacionUI):
                panel.actualizar_procesos()
                panel.actualizar_contador()

    def refrescar_modulo(self, panel):

        if isinstance(panel, MemoriaUI):
            panel.actualizar_procesos()
            panel.actualizar_estado()

        elif isinstance(panel, ComunicacionUI):
            panel.actualizar_procesos()
            panel.actualizar_contador()

        elif isinstance(panel, ProcesosUI):
            panel.actualizar_tabla()


    def mostrar_inicio(self):

        self.vistas.setCurrentWidget(
            self.dashboard
        )

        self.marcar_activo("Inicio")
        self.actualizar_indicadores()

    def ventana_activada(self, ventana):

        if ventana is not None:
            nombre = ventana.windowTitle()

            if nombre in self.MODULOS:
                self.marcar_activo(nombre)


    def centrar_ventana(self, ventana):

        area = self.escritorio.viewport().rect()
        margen = 28

        ancho_disponible = max(
            300,
            area.width() - 2 * margen
        )

        alto_disponible = max(
            250,
            area.height() - 2 * margen
        )

        ancho = min(920, ancho_disponible)
        alto = min(620, alto_disponible)

        ventana.resize(ancho, alto)

        posicion_x = max(
            0,
            (area.width() - ventana.width()) // 2
        )

        posicion_y = max(
            0,
            (area.height() - ventana.height()) // 2
        )

        ventana.move(posicion_x, posicion_y)

    def mantener_ventana_visible(self, ventana):

        if ventana.isMaximized():
            return

        area = self.escritorio.viewport().rect()

        fuera_de_area = (
            ventana.x() < 0
            or ventana.y() < 0
            or ventana.x() + ventana.width() > area.width()
            or ventana.y() + ventana.height() > area.height()
        )

        if fuera_de_area:
            self.centrar_ventana(ventana)

    def abrir_modulo(self, nombre):

        self.vistas.setCurrentWidget(
            self.escritorio
        )

        self.marcar_activo(nombre)

        # Si ya existe, reutilizar la ventana.
        for ventana in self.escritorio.subWindowList():

            if ventana.windowTitle() == nombre:

                ventana.showNormal()

                self.mantener_ventana_visible(
                    ventana
                )

                panel = ventana.widget()
                self.refrescar_modulo(panel)

                self.escritorio.setActiveSubWindow(
                    ventana
                )

                ventana.raise_()
                self.actualizar_indicadores()
                return

        # Crear el módulo solicitado.
        if nombre == "Procesos":

            panel = ProcesosUI(
                self.gestor_procesos,
                self.gestor_memoria
            )

            # NUEVO: escuchar cambios en los procesos.
            panel.procesos_cambiados.connect(
                self.procesos_actualizados
            )

        elif nombre == "Planificador CPU":

            panel = PlanificadorUI(
                self.gestor_procesos
            )

        elif nombre == "Concurrencia":

            panel = ConcurrenciaUI()

        elif nombre == "Comunicación":

            panel = ComunicacionUI(
                self.cola_mensajes,
                self.gestor_procesos
            )

        elif nombre == "Memoria":

            panel = MemoriaUI(
                self.gestor_memoria,
                self.gestor_procesos
            )

        elif nombre == "Archivos":

            panel = ArchivosUI(
                self.gestor_archivos
            )

        else:
            return

        ventana = self.escritorio.addSubWindow(
            panel
        )

        ventana.setWindowTitle(nombre)

        ventana.setWindowFlags(
            Qt.WindowType.SubWindow
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        ventana.show()
        self.centrar_ventana(ventana)

        self.escritorio.setActiveSubWindow(
            ventana
        )

        ventana.raise_()
        self.actualizar_indicadores()

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0B1220;
            }

            QFrame#encabezado {
                background-color: #111827;
                border-bottom: 1px solid #26354D;
            }

            QLabel#logo {
                background-color: #2563EB;
                color: white;
                border-radius: 11px;
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#tituloPrincipal {
                color: #F8FAFC;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#subtituloPrincipal {
                color: #94A3B8;
                font-size: 10px;
                letter-spacing: 1px;
            }

            QLabel#indicadorActivo {
                color: #4ADE80;
                background-color: #15332D;
                border: 1px solid #23594A;
                border-radius: 9px;
                padding: 9px 13px;
                font-size: 11px;
                font-weight: bold;
            }

            QFrame#lateral {
                background-color: #111C30;
                border-right: 1px solid #26354D;
            }

            QLabel#seccion {
                color: #7892B5;
                font-size: 10px;
                font-weight: bold;
                padding: 7px 8px;
            }

            QPushButton#botonNavegacion {
                background-color: transparent;
                color: #B7C7DC;
                border: none;
                border-radius: 9px;
                padding: 12px;
                text-align: left;
                font-size: 13px;
            }

            QPushButton#botonNavegacion:hover {
                background-color: #203652;
                color: white;
            }

            QPushButton#botonNavegacion:checked {
                background-color: #25477E;
                color: #FFFFFF;
                font-weight: bold;
                border-left: 3px solid #60A5FA;
            }

            QLabel#notaLateral {
                color: #7186A4;
                font-size: 11px;
                padding: 10px;
            }

            QStackedWidget#vistas {
                background-color: #0B1220;
            }

            QScrollArea#dashboardArea {
                background-color: #0B1220;
                border: none;
            }

            QWidget#dashboard {
                background-color: #0B1220;
            }

            QLabel#etiquetaSuperior {
                color: #60A5FA;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#tituloDashboard {
                color: #F8FAFC;
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#descripcionDashboard {
                color: #94A3B8;
                font-size: 13px;
            }

            QFrame#tarjetaResumen {
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 12px;
            }

            QLabel#nombreTarjeta {
                color: #AFC2DA;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#iconoTarjeta {
                color: #60A5FA;
                font-size: 20px;
            }

            QLabel#valorTarjeta {
                color: #FFFFFF;
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#detalleTarjeta {
                color: #94A3B8;
                font-size: 11px;
            }

            QFrame#panelResumen {
                background-color: #182A44;
                border: 1px solid #2A405E;
                border-radius: 12px;
            }

            QLabel#tituloPanel {
                color: #F8FAFC;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#textoSecundario {
                color: #AFC2DA;
                font-size: 12px;
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

            QPushButton#accesoRapido {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 13px;
                font-weight: bold;
            }

            QPushButton#accesoRapido:hover {
                background-color: #1D4ED8;
            }

            QLabel#textoAyuda {
                color: #8299B8;
                font-size: 12px;
                padding: 8px;
            }

            QMdiArea#escritorio {
                background-color: #0F1B2E;
                border: none;
            }

            QMdiSubWindow {
                background-color: #111C30;
                border: 1px solid #345071;
            }

            QFrame#barraInferior {
                background-color: #111827;
                border-top: 1px solid #26354D;
            }

            QPushButton#botonInicio {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 9px 15px;
                font-weight: bold;
            }

            QPushButton#botonInicio:hover {
                background-color: #1D4ED8;
            }

            QPushButton#botonAplicaciones {
                background-color: #24364F;
                color: #E5E7EB;
                border: none;
                border-radius: 7px;
                padding: 9px 15px;
            }

            QPushButton#botonAplicaciones:hover {
                background-color: #345174;
            }

            QMenu {
                background-color: #17263E;
                color: #F8FAFC;
                border: 1px solid #345174;
                padding: 6px;
            }

            QMenu::item {
                padding: 9px 25px;
            }

            QMenu::item:selected {
                background-color: #2563EB;
            }

            QLabel#estadoSistema {
                color: #94A3B8;
                font-size: 11px;
                padding-left: 8px;
            }

            QLabel#reloj {
                color: #E5E7EB;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 10px;
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

            QScrollBar:horizontal {
                background-color: #111C30;
                height: 10px;
            }

            QScrollBar::handle:horizontal {
                background-color: #3A5374;
                border-radius: 5px;
                min-width: 20px;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    ventana = PyOS()
    ventana.show()

    sys.exit(app.exec())
