import sys
import os
from platform import python_version

# https://github.com/willmcgugan/rich
from rich.console import Console
from rich.theme import Theme

import pydbhub.dbhub as dbhub


if __name__ == '__main__':
    custom_theme = Theme({
        "info": "green",
        "warning": "yellow",
        "error": "bold red"
    })
    console = Console(theme=custom_theme)

    if python_version()[0:3] < '3.7':
        console.print("[ERROR] Make sure you have Python 3.7+ installed, quitting.\n\n", style="error")
        sys.exit(1)

    # Create a new DBHub.io API object
    db = dbhub.Dbhub(config_file=f"{os.path.join(os.path.dirname(__file__), '..', 'config.ini')}")

    # Retrieve the metadata for the remote database
    wp, err = db.Webpage("justinclift", "Join Testing.sqlite")
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the web page for the database
    console.print(f'Web page: {wp}', style="info")
