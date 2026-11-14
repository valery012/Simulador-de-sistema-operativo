
"""Algoritmos de planificación de CPU para PyOS."""

from collections import deque
from dataclasses import dataclass

from simulador.procesos import EstadoProceso


@dataclass
class Tramo:
    pid: int | None
    inicio: int
    fin: int


@dataclass
class Metrica:
    pid: int
    nombre: str
    llegada: int
    cpu: int
    finalizacion: int
    retorno: int
    espera: int


@dataclass
class Resultado:
    algoritmo: str
    tramos: list[Tramo]
    metricas: list[Metrica]
    promedio_espera: float
    promedio_retorno: float


def planificar(procesos, algoritmo, quantum=2):
    """Calcula una planificación sin modificar los procesos."""

    activos = [
        p for p in procesos
        if p.estado != EstadoProceso.FINALIZADO
    ]

    if not activos:
        raise ValueError("No hay procesos disponibles.")

    if algoritmo not in ("FCFS", "SJF", "Round Robin"):
        raise ValueError("Algoritmo no reconocido.")

    if algoritmo == "Round Robin" and quantum <= 0:
        raise ValueError("El quantum debe ser mayor que cero.")

    ordenados = sorted(
        activos, key=lambda p: (p.llegada, p.pid)
    )

    tramos = []
    finalizaciones = {}
    tiempo = 0

    if algoritmo in ("FCFS", "SJF"):
        pendientes = ordenados.copy()

        while pendientes:
            disponibles = [
                p for p in pendientes
                if p.llegada <= tiempo
            ]

            if not disponibles:
                siguiente = min(
                    p.llegada for p in pendientes
                )

                tramos.append(
                    Tramo(None, tiempo, siguiente)
                )
                tiempo = siguiente

                disponibles = [
                    p for p in pendientes
                    if p.llegada <= tiempo
                ]

            if algoritmo == "FCFS":
                proceso = min(
                    disponibles,
                    key=lambda p: (p.llegada, p.pid)
                )
            else:
                proceso = min(
                    disponibles,
                    key=lambda p: (
                        p.cpu_requerida,
                        p.llegada,
                        p.pid
                    )
                )

            inicio = tiempo
            tiempo += proceso.cpu_requerida

            tramos.append(
                Tramo(proceso.pid, inicio, tiempo)
            )

            finalizaciones[proceso.pid] = tiempo
            pendientes.remove(proceso)

    else:
        restantes = {
            p.pid: p.cpu_requerida
            for p in ordenados
        }

        cola = deque()
        indice = 0

        while indice < len(ordenados) or cola:

            if not cola and indice < len(ordenados):
                siguiente = ordenados[indice].llegada

                if tiempo < siguiente:
                    tramos.append(
                        Tramo(None, tiempo, siguiente)
                    )
                    tiempo = siguiente

            while (
                indice < len(ordenados)
                and ordenados[indice].llegada <= tiempo
            ):
                cola.append(ordenados[indice])
                indice += 1

            proceso = cola.popleft()

            inicio = tiempo
            duracion = min(
                quantum, restantes[proceso.pid]
            )

            tiempo += duracion
            restantes[proceso.pid] -= duracion

            tramos.append(
                Tramo(proceso.pid, inicio, tiempo)
            )

            # Primero ingresan los procesos que llegaron.
            while (
                indice < len(ordenados)
                and ordenados[indice].llegada <= tiempo
            ):
                cola.append(ordenados[indice])
                indice += 1

            if restantes[proceso.pid] > 0:
                cola.append(proceso)
            else:
                finalizaciones[proceso.pid] = tiempo

    # Estadísticas de cada proceso
    metricas = []

    for proceso in ordenados:
        fin = finalizaciones[proceso.pid]
        retorno = fin - proceso.llegada
        espera = retorno - proceso.cpu_requerida

        metricas.append(
            Metrica(
                pid=proceso.pid,
                nombre=proceso.nombre,
                llegada=proceso.llegada,
                cpu=proceso.cpu_requerida,
                finalizacion=fin,
                retorno=retorno,
                espera=espera
            )
        )

    promedio_espera = (
        sum(m.espera for m in metricas)
        / len(metricas)
    )

    promedio_retorno = (
        sum(m.retorno for m in metricas)
        / len(metricas)
    )

    return Resultado(
        algoritmo=algoritmo,
        tramos=tramos,
        metricas=metricas,
        promedio_espera=promedio_espera,
        promedio_retorno=promedio_retorno
    )
