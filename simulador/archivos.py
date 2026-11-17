
"""Sistema de archivos seguro para PyOS Simulator."""

from pathlib import Path
import re


class GestorArchivos:

    def __init__(self, carpeta=None):
        if carpeta is None:
            carpeta = (
                Path(__file__).resolve().parent.parent
                / "archivos_prueba"
            )

        self.carpeta = Path(carpeta).resolve()
        self.carpeta.mkdir(
            parents=True,
            exist_ok=True
        )

    def _ruta_segura(self, nombre):
        """Permite solo nombres sencillos de archivos .txt."""

        if not isinstance(nombre, str):
            raise ValueError("El nombre debe ser texto.")

        nombre = nombre.strip()

        patron = r"[\w -]{1,60}\.txt"

        if not re.fullmatch(
            patron, nombre, flags=re.IGNORECASE
        ):
            raise ValueError(
                "Usa un nombre como notas.txt. "
                "No se permiten rutas ni subcarpetas."
            )

        # Nombres reservados en Windows
        base = nombre[:-4].strip().upper()

        reservados = {
            "CON", "PRN", "AUX", "NUL",
            *[f"COM{i}" for i in range(1, 10)],
            *[f"LPT{i}" for i in range(1, 10)]
        }

        if base in reservados:
            raise ValueError(
                "Ese nombre está reservado en Windows."
            )

        ruta = self.carpeta / nombre

        if ruta.is_symlink():
            raise ValueError(
                "No se permiten enlaces simbólicos."
            )

        return ruta

    def crear(self, nombre, contenido=""):
        ruta = self._ruta_segura(nombre)

        # Modo x: no sobrescribe archivos existentes
        with ruta.open("x", encoding="utf-8") as archivo:
            archivo.write(contenido)

        return ruta.name

    def listar(self):
        nombres = []

        for ruta in self.carpeta.iterdir():
            if not ruta.is_file() or ruta.is_symlink():
                continue

            try:
                self._ruta_segura(ruta.name)
                nombres.append(ruta.name)
            except ValueError:
                continue

        return sorted(nombres, key=str.casefold)

    def leer(self, nombre):
        ruta = self._ruta_segura(nombre)

        if not ruta.is_file():
            raise FileNotFoundError(
                "El archivo no existe."
            )

        return ruta.read_text(encoding="utf-8")

    def modificar(self, nombre, contenido):
        ruta = self._ruta_segura(nombre)

        if not ruta.is_file():
            raise FileNotFoundError(
                "El archivo no existe."
            )

        ruta.write_text(
            contenido,
            encoding="utf-8"
        )

        return ruta.name

    def eliminar(self, nombre):
        ruta = self._ruta_segura(nombre)

        if not ruta.is_file():
            raise FileNotFoundError(
                "El archivo no existe."
            )

        ruta.unlink()
        return ruta.name
