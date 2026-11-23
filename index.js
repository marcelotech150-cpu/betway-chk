## Configuración
| Variable | Descripción | Por defecto |
|---|---|---|
| `BETWAY_USERNAME` | Usuario a verificar | (vacío) |
| `BETWAY_PASSWORD` | Contraseña | (vacío) |
| `BETWAY_MODE` | `http` (API real) o `logica` (solo reglas locales) | `logica` |
| `BETWAY_MIN_BALANCE` | Saldo mínimo exigido | `0` |
| `BETWAY_EXPECTED_COUNTRY` | País requerido | (vacío) |
| `BETWAY_BASE_URL` | Base de la API | `https://api.betway.com/v1` |

## Estructura
- **config.py** – Parámetros y credenciales (con soporte `.env`).
- **bot.py** – Clases `ValidadorCuenta` y `BotVerificador` (lógica de validación).
- **main.py** – Punto de entrada CLI.
- **run.sh** – Script de arranque.
