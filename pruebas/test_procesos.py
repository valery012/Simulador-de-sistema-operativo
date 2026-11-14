import unittest

from simulador.procesos import EstadoProceso, GestorProcesos


class TestGestorProcesos(unittest.TestCase):
    def test_crear_proceso_asigna_pid_y_estado_listo(self) -> None:
        gestor = GestorProcesos()

        proceso = gestor.crear("Terminal")

        self.assertEqual(proceso.pid, 1)
        self.assertEqual(proceso.nombre, "Terminal")
        self.assertIs(proceso.estado, EstadoProceso.LISTO)

    def test_finalizar_proceso_actualiza_su_estado(self) -> None:
        gestor = GestorProcesos()
        proceso = gestor.crear("Editor")

        gestor.finalizar(proceso.pid)

        self.assertIs(
            gestor.consultar()[0].estado,
            EstadoProceso.FINALIZADO,
        )

    def test_no_permite_nombre_vacio(self) -> None:
        gestor = GestorProcesos()

        with self.assertRaises(ValueError):
            gestor.crear("   ")


if __name__ == "__main__":
    unittest.main()
