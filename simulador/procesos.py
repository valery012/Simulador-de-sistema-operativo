"""Modelo y operaciones basicas para la simulacion de procesos."""

from dataclasses import dataclass
from enum import Enum


class EstadoProceso(str, Enum):
    """Estados posibles de un proceso simulado."""

    LISTO = "Listo"
    EJECUTANDO = "Ejecutando"
    FINALIZADO = "Finalizado"


@dataclass
class Proceso:
    """Representa un proceso dentro del simulador."""

    pid: int
    nombre: str
    estado: EstadoProceso = EstadoProceso.LISTO
    llegada: int = 0
    cpu_requerida: int = 1
    prioridad: int = 0
    memoria: int = 128



class GestorProcesos:
    """Administra el ciclo de vida de los procesos simulados."""

    def __init__(self) -> None:
        self._procesos: dict[int, Proceso] = {}
        self._siguiente_pid = 1

    def crear(self, nombre: str, llegada: int = 0, cpu_requerida: int = 1, 
              prioridad: int = 0, memoria: int = 128) -> Proceso:
        """Crea un proceso listo para ejecutarse."""
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del proceso no puede estar vacio.")
        if llegada < 0:
            raise ValueError("El tiempo de llegada no puede ser negativo.")
        if cpu_requerida <= 0:
            raise ValueError("El tiempo de CPU requerido debe ser mayor a cero.")
        if prioridad < 0:
            raise ValueError("La prioridad no puede ser negativa.")
        if memoria <= 0:
            raise ValueError("La memoria requerida debe ser mayor a cero.")
        

        proceso = Proceso(pid=self._siguiente_pid, nombre=nombre, llegada=llegada,
                          cpu_requerida=cpu_requerida, prioridad=prioridad,
                          memoria=memoria)
        self._procesos[proceso.pid] = proceso
        self._siguiente_pid += 1
        return proceso

    def consultar(self) -> list[Proceso]:
        """Devuelve los procesos en el orden en que fueron creados."""
        return list(self._procesos.values())

    def finalizar(self, pid: int) -> Proceso:
        """Marca un proceso existente como finalizado."""
        try:
            proceso = self._procesos[pid]
        except KeyError as exc:
            raise ValueError(f"No existe el proceso con PID {pid}.") from exc

        proceso.estado = EstadoProceso.FINALIZADO
        return proceso
