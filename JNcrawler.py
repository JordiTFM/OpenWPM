import argparse
from pathlib import Path
from typing import Literal

import tranco

from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

# Sitios a analizar
SITES = [
    "https://www.amazon.es",
    "https://www.elcorteingles.es",
    "https://www.mediamarkt.es",
    "https://www.uoc.edu",
    "https://www.microsoft.com",
]

def main():
    # Configuramos manager_params y la carpeta de datos
    NUM_BROWSERS = 2
    manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
    manager_params.data_directory = Path("./datadir/")
    manager_params.log_path = Path("./datadir/openwpm.log")

    # Configuramos browsers
    browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]
    for bp in browser_params:
        bp.http_instrument = True
        bp.cookie_instrument = True
        bp.navigation_instrument = True
        bp.js_instrument = True
        bp.dns_instrument = True
        # Ajusta si quieres ver callstack, etc.

    # Crea la BD SQLite
    storage_provider = SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite"))

    # Lanza TaskManager
    with TaskManager(manager_params, browser_params, storage_provider, None) as manager:
        for i, site in enumerate(SITES):

            def callback(success: bool, val: str = site) -> None:
                print(
                    f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
                )

            cs = CommandSequence(site, site_rank=i, callback=callback)
            # Visita la página
            cs.append_command(GetCommand(url=site, sleep=3), timeout=60)
            # Podrías añadir más comandos para extraer info o personalizar

            manager.execute_command_sequence(cs)

if __name__ == "__main__":
    main()
