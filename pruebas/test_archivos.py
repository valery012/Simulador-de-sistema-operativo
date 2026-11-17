
import pytest

from simulador.archivos import GestorArchivos


def test_crear_listar_y_leer(tmp_path):
    gestor = GestorArchivos(tmp_path)

    gestor.crear("notas.txt", "Hola PyOS")

    assert gestor.listar() == ["notas.txt"]
    assert gestor.leer("notas.txt") == "Hola PyOS"


def test_modificar(tmp_path):
    gestor = GestorArchivos(tmp_path)

    gestor.crear("tarea.txt", "Versión uno")
    gestor.modificar("tarea.txt", "Versión dos")

    assert gestor.leer("tarea.txt") == "Versión dos"


def test_eliminar(tmp_path):
    gestor = GestorArchivos(tmp_path)

    gestor.crear("temporal.txt", "Prueba")
    gestor.eliminar("temporal.txt")

    assert gestor.listar() == []

    with pytest.raises(FileNotFoundError):
        gestor.leer("temporal.txt")


def test_no_sobrescribir(tmp_path):
    gestor = GestorArchivos(tmp_path)

    gestor.crear("datos.txt", "Original")

    with pytest.raises(FileExistsError):
        gestor.crear("datos.txt", "Nuevo")

    assert gestor.leer("datos.txt") == "Original"


def test_rechazar_rutas_peligrosas(tmp_path):
    gestor = GestorArchivos(tmp_path)

    nombres = [
        "../secreto.txt",
        "carpeta/archivo.txt",
        r"C:\Users\archivo.txt",
        "CON.txt",
        "programa.py",
        ""
    ]

    for nombre in nombres:
        with pytest.raises(ValueError):
            gestor.crear(nombre, "Prueba")


def test_persistencia(tmp_path):
    gestor1 = GestorArchivos(tmp_path)
    gestor1.crear("persistente.txt", "Guardado")

    # Un segundo gestor recupera el mismo archivo
    gestor2 = GestorArchivos(tmp_path)

    assert gestor2.leer("persistente.txt") == "Guardado"
