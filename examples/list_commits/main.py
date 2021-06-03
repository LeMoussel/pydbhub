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
    commits, err = db.Commits("justinclift", "Join Testing.sqlite")
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the commits
    console.print('Commits:', style="info")
    for commit in commits:
        console.print(f"   - {commit.id}", style="info")
        if commit.committer_name != '':
            console.print(f"      Committer Name : {commit.committer_name}", style="info")
        if commit.committer_email != '':
            console.print(f"      Committer Email: {commit.committer_email}", style="info")
        console.print(f"      Timestamp      : {commit.timestamp}", style="info")
        console.print(f"      Author Name    : {commit.author_name}", style="info")
        console.print(f"      Author Email   : {commit.author_email}", style="info")
        if commit.message != '':
            console.print(f"      Message        : {commit.message}", style="info")
        if commit.parent == '':
            console.print("      Parent         : NONE", style="info")
        else:
            console.print(f"      Parent         : {commit.parent}", style="info")
