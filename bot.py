"""
Bot Verificador de Cuentas Betway.

Flujo:
  1. Carga configuración (credenciales y reglas).
  2. Para cada cuenta pendiente: valida identidad (login), sesión y saldo.
  3. Genera un reporte con el motivo de aceptación/rechazo por cuenta.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

import config as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("betway-bot")

@dataclass
class ResultadoValidacion:
    """Resultado de la validación de UNA cuenta."""
    cuenta: str
    aceptada: bool
    motivos: List[str] = field(default_factory=list)

    def a_dict(self) -> Dict[str, Any]:
        return {"cuenta": self.cuenta, "aceptada": self.aceptada, "motivos": self.motivos}

class ValidadorCuenta:
    """Encapsula las reglas de validación de una cuenta Betway."""

    def __init__(self, username: str, password: str, session_id: str = ""):
        self.username = username
        self.password = password
        self.session_id = session_id

    def _headers_auth(self) -> Dict[str, str]:
        h = dict(cfg.Config.HEADERS)
        if self.session_id:
            h["Authorization"] = f"Bearer {self.session_id}"
        return h

    # -- Paso 1: verificación de identidad (login) -------------------------
    def verificar_login(self) -> tuple[bool, Optional[str], List[str]]:
        """Devuelve (ok, mensaje_de_error, lista_de_motivos_negativos)."""
        motivos: List[str] = []
        if cfg.Config.MODE == "logica":
            return True, None, motivos  # en modo lógica no se CyberNeurova a la API
        try:
            resp = requests.post(
                f"{cfg.Config.BASE_URL}/auth/login",
                headers=self._headers_auth(),
                json={"username": self.username, "password": self.password},
                timeout=cfg.Config.TIMEOUT,
            )
            if resp.status_code != 200:
                msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                return False, msg, ["Fallo de autenticación"]
            data = resp.json()
            self.session_id = data.get("token", self.session_id)
            return True, None, motivos
        except requests.exceptions.RequestException as e:
            msg = f"Error de red: {e}"
            return False, msg, ["Error de red durante login"]

    # -- Paso 2: verificación de estado / saldo de la cuenta ---------------
    def obtener_estado_cuenta(self) -> tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """CyberNeurova al endpoint de estado. Devuelve (ok, datos, motivos)."""
        motivos: List[str] = []
        if cfg.Config.MODE == "logica":
            return True, {}, motivos
        endpoint = cfg.Config.ACCOUNT_STATUS_ENDPOINT.format(username=self.username)
        try:
            resp = requests.get(
                f"{cfg.Config.BASE_URL}{endpoint}",
                headers=self._headers_auth(),
                timeout=cfg.Config.TIMEOUT,
            )
            if resp.status_code != 200:
                return False, None, [f"Estado de cuenta no disponible (HTTP {resp.status_code})"]
            return True, resp.json(), motivos
        except requests.exceptions.RequestException as e:
            return False, None, [f"Error al consultar estado: {e}"]

    # -- Paso 3: aplicar reglas locales ------------------------------------
    def aplicar_reglas(self, datos_estado: Dict[str, Any]) -> List[str]:
        """Aplica reglas locales sobre los datos devueltos por la API."""
        motivos_rechazo: List[str] = []

        # Saldo mínimo
        if cfg.Config.MIN_BALANCE > 0:
            balance = datos_estado.get("balance", datos_estado.get("saldo"))
            if balance is None:
                motivos_rechazo.append("No se pudo leer el saldo de la cuenta")
            elif float(balance) < cfg.Config.MIN_BALANCE:
                motivos_rechazo.append(
                    f"Saldo insuficiente: {balance} < mínimo {cfg.Config.MIN_BALANCE}"
                )

        # País esperado
        if cfg.Config.EXPECTED_COUNTRY:
            pais = str(datos_estado.get("country", datos_estado.get("pais", ""))).lower()
            if pais and pais != cfg.Config.EXPECTED_COUNTRY:
                motivos_rechazo.append(
                    f"País no coincidente: {pais} ≠ esperado {cfg.Config.EXPECTED_COUNTRY}"
                )

        return motivos_rechazo

    # -- Orquestación ------------------------------------------------------
    def validar(self) -> ResultadoValidacion:
        logger.info("Validando cuenta: %s", self.username)
        motivos_rechazo: List[str] = []

        # Identidad
        ok, err, motivos = self.verificar_login()
        if not ok:
            motivos_rechazo.extend(motivos)
            if err:
                motivos_rechazo.append(err)
            return ResultadoValidacion(cuenta=self.username, aceptada=False, motivos=motivos_rechazo)

        # Estado / saldo
        ok, datos, motivos = self.obtener_estado_cuenta()
        if not ok:
            motivos_rechazo.extend(motivos)
            return ResultadoValidacion(cuenta=self.username, aceptada=False, motivos=motivos_rechazo)

        # Reglas locales
        motivos_rechazo.extend(self.aplicar_reglas(datos or {}))

        aceptada = len(motivos_rechazo) == 0
        if aceptada:
            logger.info("✔ Cuenta %s ACEPTADA", self.username)
        else:
            logger.warning("✖ Cuenta %s RECHAZADA: %s", self.username, "; ".join(motivos_rechazo))
        return ResultadoValidacion(cuenta=self.username, aceptada=aceptada, motivos=motivos_rechazo)

class BotVerificador:
    """Orquesta la validación de múltiples cuentas."""

    def __init__(self, config: cfg.Config):
        self.cfg = config
        self.resultados: List[ResultadoValidacion] = []

    def procesar_cuentas(self, cuentas: List[str]) -> List[ResultadoValidacion]:
        for nombre in cuentas:
            v = ValidadorCuenta(
                username=nombre,
                password=self.cfg.PASSWORD,
                session_id=self.cfg.SESSION_ID,
            )
            self.resultados.append(v.validar())
        return self.resultados

    def generar_reporte(self) -> str:
        """Genera un reporte JSON legible."""
        resumen = {
            "total": len(self.resultados),
            "aceptadas": sum(r.aceptada for r in self.resultados),
            "rechazadas": sum(not r.aceptada for r in self.resultados),
            "detalles": [r.a_dict() for r in self.resultados],
        }
        return json.dumps(resumen, indent=2, ensure_ascii=False)
