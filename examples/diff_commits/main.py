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

    # Retrieve the differences between two commmits of the same database
    commit1 = dbhub.Identifier(commit_id="34cbeebfc347a09406707f4220cd40f60778692523d2e7d227ccd92f4125c9ea")
    commit2 = dbhub.Identifier(commit_id="bc6a07955811d86db79e9b4f7fdc3cb2360d40da793066510d792588a8bf8de2")

    diffs, err = db.Diff("justinclift", "DB4S download stats.sqlite", commit1, '', '', commit2, db.PRESERVE_PK_MERGE)
    if err is not None:
        console.print(f"[ERROR] {err}", style="error")
        sys.exit(1)

    # Display the SQL statements needed to turn the first version of the database into the second.
    # This should produce a similar output to the sqldiff utility.
    for diff in diffs.diff:
        # Print schema changes to this object if there are any
        if hasattr(diff, 'schema'):
            console.print(diff.schema.sql, style="info")

        # Loop over all data changes in this object if there are any
        for data in diff.data:
            console.print(data.sql, style="info")

    '''
    for diff in diffs['diff']:
        # Print schema changes to this object if there are any
        if 'schema' in diff and diff['schema']:
            console.print(diff['schema']['sql'], style="info")

        # Loop over all data changes in this object if there are any
        for data in diff['data']:
            console.print(data['sql'], style="info")
    '''
