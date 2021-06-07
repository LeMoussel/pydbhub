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
        console.print(
            "[ERROR] Make sure you have Python 3.7+ installed, quitting.\n\n", style="error")
        sys.exit(1)

    # Create a new DBHub.io API object
    db = dbhub.Dbhub(config_file=f"{os.path.join(os.path.dirname(__file__), '..', 'config.ini')}")

    # Retrieve the column info for a table or view in the remote database
    table = "table1"
    columns, err = db.Columns(db_owner='justinclift', db_name="Join Testing.sqlite", table=table)
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the retrieved column details
    console.print(f"Columns on table or view '{table}':", style="info")
    for column in columns:
        console.print(f"   - Name: {column.name}", style="info")
        console.print(f"        Column ID    : {column.column_id}", style="info")
        console.print(f"        Data type    : {column.data_type}", style="info")
        console.print(f"        Defualt value: {column.default_value}", style="info")
        console.print(f"        Not null     : {column.not_null}", style="info")
        console.print(f"        Primary key  : {column.primary_key}", style="info")
