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
    meta, err = db.Metadata("justinclift", "Join Testing.sqlite")
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # * Display the retrieved metadata *

    # Display the database branches
    console.print('Branches:', style="info")
    for branche_name in meta.branches:
        console.print(f"   - {branche_name} #commit: {meta.branches[branche_name].commit_count}", style="info")
    console.print(f"Default branch: {meta.default_branch}", style="info")

    # Display the database releases
    if len(meta.releases) > 0:
        console.print('Releases:', style="info")
        for release in meta.releases:
            console.print(f"   - {release}", style="info")

    # Display the database tags
    if len(meta.tags) > 0:
        console.print('Tags:', style="info")
        for tag in meta.tags:
            console.print(f"   - {tag}", style="info")

    # Display the database commits
    if len(meta.commits) > 0:
        console.print('Commits:', style="info")
        for commit in meta.commits:
            console.print(f"   - {commit.id}, {commit.timestamp}", style="info")

    # Display the web page for the database
    console.print(f"Web page: {meta.web_page}", style="info")
