
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QPushButton,
    QListWidget, QPlainTextEdit, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout
)


class ArchivosUI(QWidget):

    def __init__(self, gestor_archivos):
        super().__init__()

        self.gestor = gestor_archivos

        self.setWindowTitle("Archivos")
        self.setObjectName("vistaArchivos")
        self.setMinimumSize(720, 490)

        self.crear_interfaz()
        self.aplicar_estilos()
        self.actualizar_lista()

    def crear_interfaz(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 17, 18, 15)
        principal.setSpacing(13)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        icono = QLabel("▤")
        icono.setObjectName("iconoModulo")
        icono.setFixedSize(48, 48)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textos = QVBoxLayout()

        titulo = QLabel("Administrador de archivos")
        titulo.setObjectName("tituloModulo")

        descripcion = QLabel(
            "Crea, lee, modifica y elimina archivos .txt "
            "en la carpeta archivos_prueba."
        )
        descripcion.setObjectName("descripcionModulo")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addWidget(icono)
        encabezado.addLayout(textos, 1)

        principal.addLayout(encabezado)

        # NOMBRE DEL ARCHIVO
        panel_nombre = QFrame()
        panel_nombre.setObjectName("panelFormulario")

        nombre_layout = QVBoxLayout(panel_nombre)
        nombre_layout.setContentsMargins(
            15, 12, 15, 12
        )

        etiqueta = QLabel("Nombre del archivo")
        etiqueta.setObjectName("etiquetaCampo")

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText(
            "Ej. notas.txt"
        )

        nombre_layout.addWidget(etiqueta)
        nombre_layout.addWidget(self.nombre)

        principal.addWidget(panel_nombre)

        # EXPLORADOR Y EDITOR
        columnas = QGridLayout()
        columnas.setSpacing(12)
        columnas.setColumnStretch(0, 1)
        columnas.setColumnStretch(1, 2)

        # IZQUIERDA: LISTA
        panel_lista = QFrame()
        panel_lista.setObjectName("panelContenido")

        lista_layout = QVBoxLayout(panel_lista)
        lista_layout.setContentsMargins(
            12, 12, 12, 12
        )
        lista_layout.setSpacing(10)

        cabecera_lista = QHBoxLayout()

        titulo_lista = QLabel("Archivos existentes")
        titulo_lista.setObjectName("tituloSeccion")

        self.contador = QLabel("0 archivos")
        self.contador.setObjectName("contador")

        cabecera_lista.addWidget(titulo_lista)
        cabecera_lista.addStretch()
        cabecera_lista.addWidget(self.contador)

        lista_layout.addLayout(cabecera_lista)

        self.lista = QListWidget()
        self.lista.setObjectName("listaArchivos")
        self.lista.itemSelectionChanged.connect(
            self.seleccionar_archivo
        )

        lista_layout.addWidget(self.lista, 1)

        columnas.addWidget(panel_lista, 0, 0)

        # DERECHA: EDITOR
        panel_editor = QFrame()
        panel_editor.setObjectName("panelContenido")

        editor_layout = QVBoxLayout(panel_editor)
        editor_layout.setContentsMargins(
            12, 12, 12, 12
        )
        editor_layout.setSpacing(10)

        titulo_editor = QLabel("Contenido del archivo")
        titulo_editor.setObjectName("tituloSeccion")

        editor_layout.addWidget(titulo_editor)

        self.contenido = QPlainTextEdit()
        self.contenido.setObjectName("editorArchivo")
        self.contenido.setPlaceholderText(
            "Escribe aquí el contenido del archivo..."
        )

        editor_layout.addWidget(self.contenido, 1)

        columnas.addWidget(panel_editor, 0, 1)

        principal.addLayout(columnas, 1)

        # BOTONES
        acciones = QHBoxLayout()
        acciones.setSpacing(9)

        self.boton_crear = QPushButton(
            "＋  Crear"
        )
        self.boton_crear.setObjectName("botonPrincipal")
        self.boton_crear.clicked.connect(
            self.crear_archivo
        )

        self.boton_leer = QPushButton("Leer")
        self.boton_leer.setObjectName("botonSecundario")
        self.boton_leer.clicked.connect(
            self.leer_archivo
        )

        self.boton_guardar = QPushButton(
            "Guardar cambios"
        )
        self.boton_guardar.setObjectName("botonPrincipal")
        self.boton_guardar.clicked.connect(
            self.modificar_archivo
        )

        self.boton_eliminar = QPushButton(
            "Eliminar"
        )
        self.boton_eliminar.setObjectName("botonEliminar")
        self.boton_eliminar.clicked.connect(
            self.eliminar_archivo
        )

        self.boton_actualizar = QPushButton(
            "↻  Actualizar"
        )
        self.boton_actualizar.setObjectName("botonSecundario")
        self.boton_actualizar.clicked.connect(
            self.actualizar_lista
        )

        acciones.addWidget(self.boton_crear)
        acciones.addWidget(self.boton_leer)
        acciones.addWidget(self.boton_guardar)
        acciones.addWidget(self.boton_eliminar)
        acciones.addWidget(self.boton_actualizar)

        principal.addLayout(acciones)

        # ESTADO
        self.estado = QLabel(
            "Selecciona un archivo o crea uno nuevo."
        )
        self.estado.setObjectName("mensajeEstado")
        self.estado.setWordWrap(True)

        principal.addWidget(self.estado)

    # =====================================
    # OPERACIONES
    # =====================================

    def obtener_nombre(self):
        return self.nombre.text().strip()

    def seleccionar_archivo(self):
        elemento = self.lista.currentItem()

        if elemento is None:
            return

        self.nombre.setText(
            elemento.text()
        )

        self.contenido.clear()

        self.informar(
            "Archivo seleccionado. Pulsa Leer "
            "para abrir su contenido."
        )

    def actualizar_lista(self, seleccionar=None):
        try:
            archivos = self.gestor.listar()

            self.lista.blockSignals(True)
            self.lista.clear()
            self.lista.addItems(archivos)

            if seleccionar is not None:
                coincidencias = self.lista.findItems(
                    seleccionar,
                    Qt.MatchFlag.MatchExactly
                )
                if coincidencias:
                    self.lista.setCurrentItem(
                        coincidencias[0]
                    )

            self.lista.blockSignals(False)

            cantidad = len(archivos)
            self.contador.setText(
                f"{cantidad} "
                f"{'archivo' if cantidad == 1 else 'archivos'}"
            )

        except OSError as error:
            self.lista.blockSignals(False)
            self.informar(
                f"No se pudo actualizar: {error}",
                "error"
            )

    def crear_archivo(self):
        nombre = self.obtener_nombre()

        if not nombre:
            self.informar(
                "Escribe el nombre del archivo.",
                "advertencia"
            )
            return

        try:
            self.gestor.crear(
                nombre,
                self.contenido.toPlainText()
            )

            self.actualizar_lista(
                seleccionar=nombre
            )

            self.informar(
                f"Archivo {nombre} creado correctamente.",
                "exito"
            )

        except (ValueError, OSError) as error:
            self.informar(
                f"No se pudo crear: {error}",
                "error"
            )

    def leer_archivo(self):
        nombre = self.obtener_nombre()

        if not nombre:
            self.informar(
                "Selecciona un archivo para leer.",
                "advertencia"
            )
            return

        try:
            contenido = self.gestor.leer(nombre)

            self.contenido.setPlainText(
                contenido
            )

            self.informar(
                f"Archivo {nombre} abierto correctamente.",
                "exito"
            )

        except (ValueError, OSError) as error:
            self.informar(
                f"No se pudo leer: {error}",
                "error"
            )

    def modificar_archivo(self):
        nombre = self.obtener_nombre()

        if not nombre:
            self.informar(
                "Selecciona un archivo para guardar cambios.",
                "advertencia"
            )
            return

        try:
            self.gestor.modificar(
                nombre,
                self.contenido.toPlainText()
            )

            self.informar(
                f"Cambios guardados en {nombre}.",
                "exito"
            )

        except (ValueError, OSError) as error:
            self.informar(
                f"No se pudo guardar: {error}",
                "error"
            )

    def eliminar_archivo(self):
        nombre = self.obtener_nombre()

        if not nombre:
            self.informar(
                "Selecciona un archivo para eliminar.",
                "advertencia"
            )
            return

        confirmacion = QMessageBox(self)
        confirmacion.setWindowTitle(
            "Confirmar eliminación"
        )
        confirmacion.setIcon(
            QMessageBox.Icon.Warning
        )
        confirmacion.setText(
            f"¿Eliminar el archivo {nombre}?"
        )
        confirmacion.setInformativeText(
            "Esta acción no se puede deshacer."
        )

        boton_eliminar = confirmacion.addButton(
            "Eliminar",
            QMessageBox.ButtonRole.DestructiveRole
        )

        confirmacion.addButton(
            "Cancelar",
            QMessageBox.ButtonRole.RejectRole
        )

        confirmacion.exec()

        if confirmacion.clickedButton() is not boton_eliminar:
            return

        try:
            self.gestor.eliminar(nombre)

            self.nombre.clear()
            self.contenido.clear()
            self.actualizar_lista()

            self.informar(
                f"Archivo {nombre} eliminado correctamente.",
                "exito"
            )

        except (ValueError, OSError) as error:
            self.informar(
                f"No se pudo eliminar: {error}",
                "error"
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

    # =====================================
    # ESTILO MIDNIGHT TECH
    # =====================================

    def aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget#vistaArchivos {
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
            QFrame#panelFormulario,
            QFrame#panelContenido {
                background: #182A44;
                border: 1px solid #2A405E;
                border-radius: 11px;
            }
            QLabel#etiquetaCampo {
                color: #B7C7DC;
                background: transparent;
                font-size: 12px;
            }
            QLabel#tituloSeccion {
                color: #F8FAFC;
                background: transparent;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#contador {
                color: #93C5FD;
                background: #1E3A5F;
                border-radius: 8px;
                padding: 6px 9px;
                font-size: 11px;
            }
            QLineEdit,
            QListWidget,
            QPlainTextEdit {
                background: #0F1B2E;
                color: #F8FAFC;
                border: 1px solid #345071;
                border-radius: 7px;
                padding: 9px;
                selection-background-color: #25477E;
            }
            QLineEdit:focus,
            QPlainTextEdit:focus {
                border: 1px solid #60A5FA;
            }
            QListWidget::item {
                padding: 9px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background: #25477E;
                color: #FFFFFF;
            }
            QPlainTextEdit#editorArchivo {
                font-family: "Consolas";
                font-size: 12px;
            }
            QPushButton#botonPrincipal {
                background: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 11px 10px;
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
                padding: 10px;
            }
            QPushButton#botonSecundario:hover {
                background: #345174;
            }
            QPushButton#botonEliminar {
                background: #462736;
                color: #FCA5A5;
                border: 1px solid #7F3849;
                border-radius: 7px;
                padding: 10px;
            }
            QPushButton#botonEliminar:hover {
                background: #713344;
                color: white;
            }
            QLabel#mensajeEstado {
                background: #182A44;
                color: #AFC2DA;
                border: 1px solid #2A405E;
                border-radius: 7px;
                padding: 11px;
            }
        """)
