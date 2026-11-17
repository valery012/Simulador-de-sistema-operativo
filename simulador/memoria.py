
"""Gestión de memoria simulada de PyOS."""


class GestorMemoria:

    def __init__(self, capacidad=1024):
        if capacidad <= 0:
            raise ValueError(
                "La capacidad debe ser mayor que cero."
            )

        self.capacidad = capacidad
        self._asignaciones = {}

    @property
    def ocupada(self):
        return sum(self._asignaciones.values())

    @property
    def disponible(self):
        return self.capacidad - self.ocupada

    def asignar(self, pid, cantidad):

        if pid <= 0 or cantidad <= 0:
            raise ValueError(
                "El PID y la memoria deben ser positivos."
            )

        if pid in self._asignaciones:
            raise ValueError(
                "El proceso ya tiene memoria asignada."
            )

        if cantidad > self.disponible:
            raise ValueError(
                f"Memoria insuficiente. "
                f"Disponibles: {self.disponible} MB."
            )

        self._asignaciones[pid] = cantidad
        return cantidad

    def liberar(self, pid):

        if pid not in self._asignaciones:
            raise ValueError(
                "El proceso no tiene memoria asignada."
            )

        return self._asignaciones.pop(pid)

    def consultar(self):
        return self._asignaciones.copy()
