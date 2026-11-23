"""Tests unitarios para bot.py usando mocks."""

import unittest
from unittest.mock import patch, MagicMock

import config as cfg
from bot import ValidadorCuenta, BotVerificador

class TestReglasLocales(unittest.TestCase):
    """Prueba las reglas sin llamar a la API (modo lógica)."""

    def setUp(self):
        # Forzar modo lógica para no hacer peticiones HTTP
        self._old_mode = cfg.Config.MODE
        cfg.Config.MODE = "logica"

    def tearDown(self):
        cfg.Config.MODE = self._old_mode

    def test_cuenta_sana_se_acepta(self):
        cfg.Config.MIN_BALANCE = 0
        cfg.Config.EXPECTED_COUNTRY = ""
        v = ValidadorCuenta("usuario_ok", "pass")
        r = v.validar()
        self.assertTrue(r.aceptada)

    def test_saldo_insuficiente_rechaza(self):
        cfg.Config.MIN_BALANCE = 100
        cfg.Config.EXPECTED_COUNTRY = ""
        v = ValidadorCuenta("usuario_pobre", "pass")
        # Simular que la API devuelve un saldo bajo
        with patch.object(ValidadorCuenta, "obtener_estado_cuenta",
                          return_value=(True, {"balance": 10}, [])):
            r = v.validar()
        self.assertFalse(r.aceptada)
        self.assertTrue(any("insuficiente" in m.lower() for m in r.motivos))

    def test_pais_no_coincide_rechaza(self):
        cfg.Config.MIN_BALANCE = 0
        cfg.Config.EXPECTED_COUNTRY = "es"
        v = ValidadorCuenta("usuario_extranjero", "pass")
        with patch.object(ValidadorCuenta, "obtener_estado_cuenta",
                          return_value=(True, {"country": "US"}, [])):
            r = v.validar()
        self.assertFalse(r.aceptada)

class TestReporte(unittest.TestCase):
    def test_resumen_de_reporte(self):
        cfg.Config.MODE = "logica"
        cfg.Config.MIN_BALANCE = 0
        cfg.Config.EXPECTED_COUNTRY = ""
        b = BotVerificador(cfg.Config)
        b.procesar_cuentas(["a", "b"])
        assert "total": 2 in b.generar_reporte()

if __name__ == "__main__":
    unittest.main()
