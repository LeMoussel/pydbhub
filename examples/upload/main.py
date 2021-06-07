import sys
import os
import datetime
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

    # Prepare any information you want to include with the upload (eg a commit message, etc)
    info = dbhub.UploadInformation(
        commitmsg="An example upload",
        committimestamp=datetime.datetime.fromisoformat("2021-06-01 10:00:00"),
    )

    try:
        # Read the database file
        myDB = os.path.join(os.getcwd(), "examples", "upload", 'example.db')
        f = open(myDB, 'rb')
    except FileNotFoundError:
        print(f"File {myDB} not found.  Aborting")
        sys.exit(1)
    except OSError:
        print(f"OS error occurred trying to open {myDB}")
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected error opening {myDB} is", repr(err))
        sys.exit(1)
    else:
        with f:
            # Upload the database
            res, err = db.Upload(db_name='somedb.sqlite', info=info, db_bytes=f)
            if err is not None:
                console.print(f"[ERROR] {err}", style="error")
                sys.exit(1)

            console.print(f"Database uploaded, commit: {res['commit']}", style="info")
