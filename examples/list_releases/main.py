import sys
import os
from platform import python_version

# https://github.com/willmcgugan/rich
from rich.console import Console
from rich.theme import Theme

import dbhub


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

    # Retrieve the list of branches for a database
    rels, err = db.Releases("justinclift", "Join Testing.sqlite")
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the release info
    console.print('Releases:', style="info")
    for release_name in rels:
        console.print(f"   - {release_name}", style="info")
        console.print(f"       Commit: {rels[release_name].commit}", style="info")
        console.print(f"       Date: {rels[release_name].date}", style="info")
        console.print(f"       Size: {rels[release_name].size}", style="info")
        console.print(f"       Releaser Name: {rels[release_name].name}", style="info")
        console.print(f"       Releaser Email: {rels[release_name].email}", style="info")
        console.print(f"       Description: {rels[release_name].description}", style="info")
