# pydbhub

A Python library for accessing and using SQLite databases on DBHub.io. *This is an early stage work in progress*

## What works now

* Run read-only queries (eg SELECT statements) on databases, returning the results as JSON
* Upload and download your databases
* List the databases in your account
* List the tables, views, and indexes present in a database
* List the columns in a table, view or index, along with their details
* List the branches, releases, tags, and commits for a database
* Generate diffs between two databases, or database revisions
* Download the database metadata (size, branches, commit list, etc.)
* Retrieve the web page URL of a database

### Still to do

* Anything else people suggest and seems like a good idea.
Please try it out, submits PRs to extend or fix things, and report any weirdness or bugs you encounter. :smile:

## Pre-requisites

* [Python](https://www.python.org/) version 3.7
  * Older Python releases should NOT be OK. Newer Python releases should be OK, but only Python 3.7 has been tested (so far).
* A DBHub.io API key
  * These can be generated in your [Settings](https://dbhub.io/pref) page, when logged in.

### Linux

```bash
sudo apt-get install python3.7
python3.7 pip install -r requirements.txt
python3.7 pip install --upgrade --user git+https://github.com/LeMoussel/pydbhub.git
```

### Windows

Install Python 3.7

cmd (admin)

```bash
python pip install -r requirements.txt
python pip install --upgrade --user git+https://github.com/LeMoussel/pydbhub.git
```

## Further examples

* [SQL Query](https://github.com/LeMoussel/pydbhub/blob/master/examples/sql_query/main.py) - Run a SQL query, return the results as JSON
* [List databases](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_databases/main.py) - List the databases present in your account
* [List tables](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_tables/main.py) - List the tables present in a database
* [List views](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_views/main.py) - List the views present in a database
* [List indexes](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_indexes/main.py) - List the indexes present in a database
* [Retrieve column details](https://github.com/LeMoussel/pydbhub/blob/master/examples/column_details/main.py) - Retrieve the details of columns in a table
* [List branches](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_branches/main.py) - List all branches of a database
* [List releases](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_releases/main.py) - Display the releases for a database
* [List tags](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_tags/main.py) - Display the tags for a database
* [List commits](https://github.com/LeMoussel/pydbhub/blob/master/examples/list_commits/main.py) - Display the commits for a database
* [Generate diff between two revisions](https://github.com/LeMoussel/pydbhub/blob/master/examples/diff_commits/main.py) - Figure out the differences between two databases or two versions of one database
* [Upload database](https://github.com/LeMoussel/pydbhub/blob/master/examples/upload/main.py) - Upload a new database file
* [Download database](https://github.com/LeMoussel/pydbhub/blob/master/examples/download_database/main.py) - Download the complete database file
* [Delete database](https://github.com/LeMoussel/pydbhub/blob/master/examples/delete_database/main.py) - Delete a database
* [Retrieve metadata](https://github.com/LeMoussel/pydbhub/blob/master/examples/metadata/main.py) - Download the database metadata (size, branches, commit list, etc)
* [Web page](https://github.com/LeMoussel/pydbhub/blob/master/examples/webpage/main.py) - Get the URL of the database file in the webUI.  eg. for web browsers
