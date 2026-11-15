
"""Demostración de hilos y sincronización en PyOS."""

import threading
import time
from dataclasses import dataclass


@dataclass
class ResultadoConcurrencia:
    con_lock: bool
    esperado: int
    obtenido: int
    incrementos_perdidos: int
    mensajes: list[str]


def ejecutar_concurrencia(
    con_lock: bool,
    repeticiones: int = 100
) -> ResultadoConcurrencia:
    """Ejecuta dos hilos sobre un contador compartido."""

    if not isinstance(repeticiones, int) or repeticiones <= 0:
        raise ValueError(
            "Las repeticiones deben ser un entero positivo."
        )

    contador = [0]
    lock = threading.Lock()
    barrera = threading.Barrier(2)

    mensajes = []

    def tarea(numero_hilo):
        for paso in range(repeticiones):

            if con_lock:
                # Sección crítica protegida
                with lock:
                    valor = contador[0]
                    contador[0] = valor + 1

            else:
                # Lectura sin protección
                valor = contador[0]

                # Forzamos que ambos hilos lean el
                # mismo valor en la primera iteración.
                if paso == 0:
                    barrera.wait(timeout=10)

                # Pausa didáctica para mostrar la carrera
                time.sleep(0.0001)

                contador[0] = valor + 1

        with lock:
            mensajes.append(
                f"Hilo {numero_hilo}: "
                f"{repeticiones} incrementos intentados."
            )

    hilos = [
        threading.Thread(target=tarea, args=(1,)),
        threading.Thread(target=tarea, args=(2,))
    ]

    for hilo in hilos:
        hilo.start()

    for hilo in hilos:
        hilo.join()

    esperado = repeticiones * 2
    obtenido = contador[0]

    return ResultadoConcurrencia(
        con_lock=con_lock,
        esperado=esperado,
        obtenido=obtenido,
        incrementos_perdidos=esperado - obtenido,
        mensajes=mensajes
    )
