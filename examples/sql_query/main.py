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

    # Retrieve the metadata for the remote database
    r, err = db.Query(
        "justinclift",
        "Join Testing.sqlite",
        '''
        SELECT table1.id, table1.name, table2.value
        FROM table1 JOIN table2
        USING (id)
        ORDER BY table1.id
        '''
    )
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the query result (without unmarshalling)
    console.print("Query results:", style="info")
    for row in r:
        console.print(f"\t {row}", style="info")
    console.print()
