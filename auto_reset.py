import time
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Kořen projektu (tam, kde leží auto_reset.py, manage.py, db.sqlite3)
BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "db.sqlite3"
LOG_PATH = BASE_DIR / "reset_log.txt"
MEDIA_DIR = BASE_DIR / "media" / "auction_images" / "photos_add_auction"
MANAGE_PY = BASE_DIR / "manage.py"


def log(msg: str) -> None:
    """Zapisuje zprávy do reset_log.txt v rootu projektu."""
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def run(command: list[str]) -> None:
    """Spustí příkaz s nastaveným DJANGO_SETTINGS_MODULE a zaloguje ho."""
    log(f"Spouštím: {' '.join(command)}")
    subprocess.run(
        command,
        env={
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "aukce.settings",
        },
        check=True,
    )


def reset_once() -> None:
    """Provede jeden reset: smaže DB, fotky, migrace, populate."""
    # 1. Smazat databázi
    try:
        DB_PATH.unlink()
        log(f"Databáze odstraněna: {DB_PATH}")
    except FileNotFoundError:
        log(f"Databázový soubor neexistuje, není co mazat: {DB_PATH}")

    # 1b. Smazat všechny .jpg/.jpeg soubory ve složce s fotkami
    if MEDIA_DIR.is_dir():
        deleted = 0
        for name in os.listdir(MEDIA_DIR):
            if name.lower().endswith((".jpg", ".jpeg")):
                full_path = MEDIA_DIR / name
                if full_path.is_file():
                    full_path.unlink()
                    deleted += 1
        log(f"Smazány všechny .jpg/.jpeg soubory ve složce s fotkami ({deleted} souborů).")
    else:
        log(f"Složka s fotkami neexistuje: {MEDIA_DIR}")

    # 2. Proveď migrace
    py = sys.executable  # použije stejný Python, jako běží skript
    run([py, str(MANAGE_PY), "migrate", "--noinput"])

    # 3. Spusť populate_date přes runscript
    run([py, str(MANAGE_PY), "runscript", "populate_date"])

    log("Reset dokončen.")


def main() -> None:
    # pokud chceš reset JEDNOU při startu containeru, nech jen:
    # reset_once()

    # pokud chceš opakovat každý den, odkomentuj tento blok
    while True:
        log("Reset dokončen. Spím 1 den (86400 s)...")
        time.sleep(86400)
        reset_once()


if __name__ == "__main__":
    main()