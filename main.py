
import sys

from PySide6.QtCore import QDateTime, QTimer
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMdiArea,
    QMenu,
)

from simulador.procesos import GestorProcesos
from interfaz.procesos_ui import ProcesosUI
from interfaz.planificador_ui import PlanificadorUI


class PyOS(QMainWindow):

    MODULOS = {
        "Procesos": "Crear, consultar y finalizar procesos.",
        "Planificador CPU": "FCFS, SJF, Round Robin y estadísticas.",
        "Concurrencia": "Hilos y sincronización con Lock.",
        "Comunicación": "Cola de mensajes entre procesos.",
        "Memoria": "Asignar y liberar memoria simulada.",
        "Archivos": "Crear, leer, modificar y eliminar archivos.",
    }

    def __init__(self):
        super().__init__()

        # Gestor compartido entre Procesos y Planificador CPU
        self.gestor_procesos = GestorProcesos()

        # Configuración de la ventana principal
        self.setWindowTitle("PyOS Simulator")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        self.crear_escritorio()
        self.aplicar_estilos()

    def crear_escritorio(self):

        # Contenedor principal
        principal = QWidget()
        self.setCentralWidget(principal)

        layout = QVBoxLayout(principal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        encabezado = QFrame()
        encabezado.setObjectName("encabezado")

        barra_superior = QHBoxLayout(encabezado)

        titulo = QLabel("PyOS Simulator")
        titulo.setObjectName("titulo")

        barra_superior.addWidget(titulo)
        barra_superior.addStretch()

        layout.addWidget(encabezado)

        contenido = QHBoxLayout()
        contenido.setContentsMargins(0, 0, 0, 0)
        contenido.setSpacing(0)

        lateral = QFrame()
        lateral.setObjectName("lateral")
        lateral.setFixedWidth(190)

        menu_lateral = QVBoxLayout(lateral)

        etiqueta = QLabel("APLICACIONES")
        etiqueta.setObjectName("seccion")
        menu_lateral.addWidget(etiqueta)

        for nombre in self.MODULOS:

            boton = QPushButton(nombre)
            boton.setObjectName("botonModulo")

            boton.clicked.connect(
                lambda checked=False, n=nombre:
                self.abrir_modulo(n)
            )

            menu_lateral.addWidget(boton)

        menu_lateral.addStretch()
        contenido.addWidget(lateral)


        self.escritorio = QMdiArea()

        self.escritorio.setBackground(
            QBrush(QColor("#152842"))
        )

        contenido.addWidget(self.escritorio)
        layout.addLayout(contenido)


        barra_tareas = QFrame()
        barra_tareas.setObjectName("barraTareas")

        tareas = QHBoxLayout(barra_tareas)

        boton_inicio = QPushButton("Inicio")
        boton_inicio.setObjectName("inicio")

        menu_inicio = QMenu(self)

        for nombre in self.MODULOS:

            accion = menu_inicio.addAction(nombre)

            accion.triggered.connect(
                lambda checked=False, n=nombre:
                self.abrir_modulo(n)
            )

        boton_inicio.setMenu(menu_inicio)
        tareas.addWidget(boton_inicio)

        tareas.addStretch()

        # Reloj del sistema
        self.reloj = QLabel()
        self.reloj.setObjectName("reloj")

        tareas.addWidget(self.reloj)

        layout.addWidget(barra_tareas)

        # Actualización automática del reloj
        self.actualizar_reloj()

        self.temporizador = QTimer(self)

        self.temporizador.timeout.connect(
            self.actualizar_reloj
        )

        self.temporizador.start(1000)

    def actualizar_reloj(self):

        hora = QDateTime.currentDateTime()

        self.reloj.setText(
            hora.toString("hh:mm:ss")
        )

    def abrir_modulo(self, nombre):

        # Evitar abrir dos veces la misma ventana
        for ventana in self.escritorio.subWindowList():

            if ventana.windowTitle() == nombre:

                ventana.showNormal()

                self.escritorio.setActiveSubWindow(
                    ventana
                )

                return
        if nombre == "Procesos":

            panel = ProcesosUI(
                self.gestor_procesos
            )

        elif nombre == "Planificador CPU":

            panel = PlanificadorUI(
                self.gestor_procesos
            )

        else:

            panel = QWidget()
            panel.setObjectName("panel")

            panel_layout = QVBoxLayout(panel)

            panel_layout.setContentsMargins(
                25, 25, 25, 25
            )

            titulo = QLabel(nombre)
            titulo.setObjectName("tituloModulo")

            descripcion = QLabel(
                self.MODULOS[nombre]
            )

            descripcion.setWordWrap(True)

            estado = QLabel(
                "Módulo pendiente de implementación"
            )

            estado.setObjectName("estado")

            panel_layout.addWidget(titulo)
            panel_layout.addWidget(descripcion)
            panel_layout.addSpacing(20)
            panel_layout.addWidget(estado)
            panel_layout.addStretch()

        ventana = self.escritorio.addSubWindow(
            panel
        )

        ventana.setWindowTitle(nombre)

        # Tamaños según el módulo
        if nombre in (
            "Procesos",
            "Planificador CPU"
        ):

            ventana.resize(850, 560)

        else:

            ventana.resize(520, 320)

        ventana.show()

        self.escritorio.setActiveSubWindow(
            ventana
        )

    # ------------------------------------
    # ESTILOS DE PYOS
    # ------------------------------------

    def aplicar_estilos(self):

        self.setStyleSheet("""
            QMainWindow {
                background-color: #101B30;
            }

            QFrame#encabezado {
                background-color: #102039;
            }

            QLabel#titulo {
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 8px;
            }

            QFrame#lateral {
                background-color: #192D49;
            }

            QLabel#seccion {
                color: #93C5FD;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton#botonModulo {
                background-color: #284467;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                text-align: left;
            }

            QPushButton#botonModulo:hover {
                background-color: #2563EB;
            }

            QFrame#barraTareas {
                background-color: #101E33;
            }

            QPushButton#inicio {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                padding: 9px 18px;
            }

            QLabel#reloj {
                color: white;
                padding: 8px;
            }

            QWidget#panel {
                background-color: #F8FAFC;
            }

            QLabel#tituloModulo {
                color: #102039;
                font-size: 22px;
                font-weight: bold;
            }

            QWidget#panel QLabel {
                color: #334155;
                font-size: 14px;
            }

            QLabel#estado {
                color: #2563EB;
                font-weight: bold;
            }
        """)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    ventana = PyOS()
    ventana.show()

    sys.exit(app.exec())
