import time
import subprocess
import os
from datetime import datetime


def log(msg):
    with open("/srv/app/reset_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def run(command):
    log(f"Spouštím: {' '.join(command)}")
    subprocess.run(
        command,
        env={
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "aukce.settings",
        }
    )


def main():
    while True:
        # 1. Smazat databázi
        try:
            os.remove("/srv/app/db.sqlite3")
            log("Databáze odstraněna.")
        except FileNotFoundError:
            log("Databázový soubor neexistuje, není co mazat.")

        # 1b. Smazat všechny .jpg/.jpeg soubory ve složce s fotkami
        MEDIA_DIR = "/srv/app/media/auction_images/photos_add_auction"

        if os.path.isdir(MEDIA_DIR):
            for name in os.listdir(MEDIA_DIR):
                # smaže jen .jpg/.jpeg soubory
                if name.lower().endswith((".jpg", ".jpeg")):
                    full_path = os.path.join(MEDIA_DIR, name)
                    if os.path.isfile(full_path):
                        os.remove(full_path)
            log("Smazány všechny .jpg/.jpeg soubory ve složce s fotkami.")
        else:
            log(f"Složka s fotkami neexistuje: {MEDIA_DIR}")

        # 2. Proveď migrace
        run([
            "/srv/venv/bin/python",
            "/srv/app/manage.py",
            "migrate",
            "--noinput",
        ])

        # 3. Spusť populate_date přes runscript
        run([
            "/srv/venv/bin/python",
            "/srv/app/manage.py",
            "runscript",
            "populate_date",
        ])

        log("Reset dokončen. Spím 1 den (86400 s)...")
        time.sleep(86400)


if __name__ == "__main__":
    main()