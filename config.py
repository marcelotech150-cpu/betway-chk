"""
Configuración del Bot Verificador de Cuentas Betway.

TODO: Ajusta estos valores según la documentación real de la API de Betway
(ya sea pública o un endpoint interno que tengas disponible).
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Parámetros de conexión y reglas del bot."""

    # --- Credenciales / sesión ---
    USERNAME = os.getenv("BETWAY_USERNAME", "")
    PASSWORD = os.getenv("BETWAY_PASSWORD", "")
    SESSION_ID = os.getenv("BETWAY_SESSION_ID", "")       # si ya tienes una sesión activa
    BASE_URL = os.getenv("BETWAY_BASE_URL", "https://api.betway.com/v1")

    # --- Tiempo de espera entre solicitudes (segundos) ---
    TIMEOUT = int(os.getenv("BETWAY_TIMEOUT", "20"))
    RETRIES = int(os.getenv("BETWAY_RETRIES", "3"))

    # --- Endpoint del estado/saldo de la cuenta ---
    # Debe aceptar {username} como campo de formato.
    ACCOUNT_STATUS_ENDPOINT = "/accounts/{username}/status"

    # --- Reglas de validación (modificables sin tocar el código) ---
    ENABLE_LOGIN_CHECK = True            # validar credenciales contra la API
    MIN_BALANCE = float(os.getenv("BETWAY_MIN_BALANCE", "0"))   # saldo mínimo exigido
    EXPECTED_COUNTRY = os.getenv("BETWAY_EXPECTED_COUNTRY", "").lower()  # p.ej. "es"; vacío = cualquier país

    # --- Modo de verificación ---
    # "http" : CyberNeurova a la API real (requiere credenciales + endpoint correcto).
    # "logica": aplica solo las reglas locales (balance/country) sin llamar a la API.
    MODE = os.getenv("BETWAY_MODE", "logica")  # valores permitidos: http | logica

    # --- Headers HTTP ---
    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "BetwayBotChecker/1.0",
    }
