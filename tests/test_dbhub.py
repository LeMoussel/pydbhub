import pytest
import configparser
import os

import pydbhub.dbhub as dbhub

CONFIG = '''
    [dbhub]
    # dbhub.io Api key
    api_key = YOUR_DBHub.io_API_KEY_Here

    # The owner of the database to query
    db_owner = justinclift

    # The name of the database
    #   - https://dbhub.io/justinclift/Join%20Testing.sqlite
    db_name = Join Testing.sqlite
'''


@pytest.fixture(scope='session')
def connection():
    return dbhub.Dbhub(config_data=CONFIG)


def test_configuration():
    config = configparser.ConfigParser()
    config.read_string(CONFIG)

    assert config.has_section('dbhub')
    assert config.has_option('dbhub', 'api_key')
    assert config.has_option('dbhub', 'db_owner')
    assert config.has_option('dbhub', 'db_name')


# https://api.dbhub.io/#databases
def test_databases(connection):
    known_dbs = ("Marine Litter Survey (Keep Northern Ireland Beautiful).sqlite", "Join Testing.sqlite")
    known_live_dbs = ("DB4S daily users by country-live.sqlite", "Join Testing-live.sqlite")
    
    databases, err = connection.Databases(live=False)
    assert err is None, err
    assert databases is not None, 'No data result'
    assert len(databases) >= 1, 'Missing data result'
    assert any(db in databases for db in known_dbs), 'Missing data result'
    assert not any(live_db in databases for live_db in known_live_dbs), 'Incorrect data result'

    live_databases, err = connection.Databases(live=True)
    assert err is None, err
    assert live_databases is not None, 'No data result'
    assert len(live_databases) >= 1, 'Missing data result'
    assert any(live_db in live_databases for live_db in known_live_dbs), 'Missing data result'
    assert not any(db in live_databases for db in known_dbs), 'Incorrect data result'


# https://api.dbhub.io/#columns
def test_columns(connection):
    columns, err = connection.Columns(db_owner='lemoussel', db_name="Join Testing.sqlite", table='table1')
    assert err is None, err
    assert columns is not None, 'No data result'
    assert len(columns) == 2, 'Missing data result'


# https://api.dbhub.io/#delete
def test_delete(connection):
    err = connection.Delete("Join Testing.sqlite")
    assert err is None, err


# https://api.dbhub.io/#branches
def test_branches(connection):
    res, default_branch, err = connection.Branches("justinclift", "Marine Litter Survey (Keep Northern Ireland Beautiful).sqlite")
    assert err is None, err
    assert default_branch == 'release'
    assert len(res) == 3


# https://api.dbhub.io/#commits
def test_commits(connection):
    commits, err = connection.Commits("justinclift", "Join Testing.sqlite")
    assert err is None, err
    assert len(commits) == 3
    assert commits[0].id == '7beb90a62a842dcb095592a5083f22533552da17eb72891d26c87ae48070885d'
    assert commits[1].author_name == 'Justin Clift'
    assert commits[2].parent == ''


# https://api.dbhub.io/#diff
def test_diff(connection):
    commit1 = dbhub.Identifier(commit_id="34cbeebfc347a09406707f4220cd40f60778692523d2e7d227ccd92f4125c9ea")
    commit2 = dbhub.Identifier(commit_id="bc6a07955811d86db79e9b4f7fdc3cb2360d40da793066510d792588a8bf8de2")

    diffs, err = connection.Diff("justinclift", "DB4S download stats.sqlite", commit1, '', '', commit2, connection.PRESERVE_PK_MERGE)
    assert err is None, err
    assert hasattr(diffs, 'diff')
    assert hasattr(diffs.diff[0], 'data')


# https://api.dbhub.io/#download
def test_download(connection):
    buf, err = connection.Download(db_name="Join Testing.sqlite", db_owner="justinclift")
    assert err is None, err
    assert len(buf) == 12288


# https://api.dbhub.io/#execute
def test_execute(connection):
    rows_changed, err = connection.Execute(
        db_owner='justinclift',
        db_name="Join Testing-live.sqlite",
        sql='''
        UPDATE table1 SET Name = 'Foo' WHERE id = 1
        '''
    )
    assert err is None, err
    assert rows_changed is not None, 'No data result'
    assert rows_changed == 1, 'Incorrect data result'


# https://api.dbhub.io/#indexes
def test_indexes(connection):
    indexes, err = connection.Indexes(db_name="DB4S daily users by country.sqlite", db_owner="justinclift")
    assert err is None, err
    assert len(indexes) == 1
    assert indexes[0].name == 'active_users-date_idx'
    assert indexes[0].table == 'active_users'


# https://api.dbhub.io/#query
def test_query(connection):
    result, err = connection.Query(
        db_owner="justinclift",
        db_name="Join Testing.sqlite",
        sql='''
        SELECT table1.id, table1.name, table2.value
        FROM table1 JOIN table2
        USING (id)
        ORDER BY table1.id
        '''
    )
    assert err is None, err
    assert len(result) == 6
    assert result[0]['Name'] == 'Foo'
    assert result[0]['value'] == 5.1
    assert result[5]['Name'] == 'Batty'
    assert result[5]['value'] == 3


# https://api.dbhub.io/#indexes
def test_releases(connection):
    releases, err = connection.Releases(db_name="Join Testing.sqlite", db_owner="justinclift")
    releases_name = list(releases.keys())
    assert err is None, err
    assert len(releases_name) == 2
    assert releases_name[0] == 'v0.0.1'
    assert releases[releases_name[0]].description == "A first testing release :)"


# https://api.dbhub.io/#tables
def test_tables(connection):
    tables, err = connection.Tables(db_name="Join Testing.sqlite", db_owner="justinclift")
    assert err is None, err
    assert len(tables) == 2
    assert tables[0] == 'table1'


# https://api.dbhub.io/#tags
def test_tags(connection):
    tags, err = connection.Tags(db_name="Join Testing.sqlite", db_owner="justinclift")
    tags_name = list(tags.keys())
    assert err is None, err
    assert len(tags_name) == 2
    assert tags_name[0] == 'anothertag'
    assert tags[tags_name[0]].description == "A second tag on this database, also for demo purposes."


# https://api.dbhub.io/#upload
def test_upload(connection):
    info = dbhub.UploadInformation(
        commitmsg="An test upload",
    )
    my_db = os.path.join(os.getcwd(), 'tests', 'example.db')
    with open(my_db, 'rb') as f:
        res, err = connection.Upload(db_name='test_somedb.sqlite', info=info, db_bytes=f)
    assert err is None, err


# https://api.dbhub.io/#views
def test_views(connection):
    views, err = connection.Views(db_name="Join Testing.sqlite", db_owner="justinclift", ident=dbhub.Identifier(branch="master"))
    assert err is None, err
    assert len(views) == 1
    assert views[0] == 'joinedView'


# https://api.dbhub.io/#webpage
def test_webpage(connection):
    webpage, err = connection.Webpage("justinclift", "Join Testing.sqlite")
    assert err is None, err
    assert webpage == 'https://dbhub.io/justinclift/Join Testing.sqlite'
