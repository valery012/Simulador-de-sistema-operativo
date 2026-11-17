
"""Administrador gráfico de archivos de PyOS."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QListWidget,
    QPushButton,
    QMessageBox
)


class ArchivosUI(QWidget):

    def __init__(self, gestor):
        super().__init__()

        self.gestor = gestor
        self.construir_interfaz()
        self.actualizar_lista()

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        titulo = QLabel("Administrador de archivos")
        titulo.setObjectName("tituloArchivos")
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Crea, abre, modifica y elimina archivos .txt "
            "dentro de la carpeta archivos_prueba."
        )
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        layout.addWidget(QLabel("Nombre del archivo:"))

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ej.: notas.txt")
        layout.addWidget(self.nombre)

        contenido = QHBoxLayout()

        # Lista de archivos
        panel_lista = QVBoxLayout()
        panel_lista.addWidget(
            QLabel("Archivos existentes:")
        )

        self.lista = QListWidget()
        self.lista.currentTextChanged.connect(
            self.seleccionar_archivo
        )

        panel_lista.addWidget(self.lista)
        contenido.addLayout(panel_lista, 1)

        # Editor de texto
        panel_editor = QVBoxLayout()
        panel_editor.addWidget(
            QLabel("Contenido del archivo:")
        )

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(
            "Escribe aquí el contenido..."
        )

        panel_editor.addWidget(self.editor)
        contenido.addLayout(panel_editor, 2)

        layout.addLayout(contenido)

        # Botones
        botones = QHBoxLayout()

        crear = QPushButton("Crear")
        crear.clicked.connect(self.crear)

        leer = QPushButton("Leer")
        leer.clicked.connect(self.leer)

        modificar = QPushButton("Guardar cambios")
        modificar.clicked.connect(self.modificar)

        eliminar = QPushButton("Eliminar")
        eliminar.clicked.connect(self.eliminar)

        actualizar = QPushButton("Actualizar lista")
        actualizar.clicked.connect(
            self.actualizar_lista
        )

        for boton in (
            crear, leer, modificar,
            eliminar, actualizar
        ):
            botones.addWidget(boton)

        layout.addLayout(botones)

        self.estado = QLabel(
            "Selecciona un archivo o crea uno nuevo."
        )
        self.estado.setWordWrap(True)
        layout.addWidget(self.estado)

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
                font-size: 14px;
            }

            QLabel#tituloArchivos {
                font-size: 22px;
                font-weight: bold;
            }

            QLineEdit, QPlainTextEdit, QListWidget {
                background-color: #111827;
                color: white;
                border: 1px solid #475569;
                border-radius: 5px;
                padding: 8px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

    def seleccionar_archivo(self, nombre):
        if nombre:
            self.nombre.setText(nombre)

    def actualizar_lista(self):
        nombre_actual = self.nombre.text()

        self.lista.clear()
        self.lista.addItems(self.gestor.listar())

        self.nombre.setText(nombre_actual)

        self.estado.setText(
            f"Archivos disponibles: "
            f"{self.lista.count()}"
        )

    def mostrar_error(self, error):
        QMessageBox.warning(
            self, "Sistema de archivos", str(error)
        )

    def crear(self):
        try:
            nombre = self.gestor.crear(
                self.nombre.text(),
                self.editor.toPlainText()
            )

            self.actualizar_lista()
            self.estado.setText(
                f"Archivo creado: {nombre}"
            )

        except (ValueError, OSError) as error:
            self.mostrar_error(error)

    def leer(self):
        try:
            contenido = self.gestor.leer(
                self.nombre.text()
            )

            self.editor.setPlainText(contenido)
            self.estado.setText(
                "Archivo abierto correctamente."
            )

        except (ValueError, OSError) as error:
            self.mostrar_error(error)

    def modificar(self):
        try:
            nombre = self.gestor.modificar(
                self.nombre.text(),
                self.editor.toPlainText()
            )

            self.estado.setText(
                f"Cambios guardados en {nombre}"
            )

        except (ValueError, OSError) as error:
            self.mostrar_error(error)

    def eliminar(self):
        nombre = self.nombre.text().strip()

        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar el archivo {nombre}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if confirmacion != QMessageBox.StandardButton.Yes:
            return

        try:
            self.gestor.eliminar(nombre)

            self.nombre.clear()
            self.editor.clear()
            self.actualizar_lista()

            self.estado.setText(
                f"Archivo eliminado: {nombre}"
            )

        except (ValueError, OSError) as error:
            self.mostrar_error(error)
