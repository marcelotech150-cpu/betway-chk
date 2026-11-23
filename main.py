#!/usr/bin/env python3
"""
Punto de entrada del Bot Verificador de Cuentas Betway.

Uso:
    python main.py
    python main.py --cuenta usuario1 --cuenta usuario2
"""

import argparse
import sys

import config as cfg
from bot import BotVerificador

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bot Verificador de Cuentas Betway")
    p.add_argument("--cuenta", "-c", action="append", default=[], help="Nombre de usuario a verificar (repetible)")
    return p.parse_args()

def main() -> int:
    args = parse_args()

    # Si no se pasaron cuentas por CLI, usa la primera credencial configurada
    cuentas = args.cuenta
    if not cuentas:
        if cfg.Config.USERNAME:
            cuentas = [cfg.Config.USERNAME]
        else:
            print("Advierte: no hay cuentas definidas ni credenciales en config/.env")
            return 0

    bot = BotVerificador(config=cfg.Config)
    bot.procesar_cuentas(cuentas)
    print("\n=== REPORTE FINAL ===")
    print(bot.generar_reporte())
    return 0

if __name__ == "__main__":
    sys.exit(main())
