
import os
import io
import configparser
import base64
import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass
from typing_extensions import Literal

# https://dateutil.readthedocs.io/
import dateutil.parser as p


import pydbhub.httphub as httphub


# Dictionnary to object
class _DbhubDictToObject(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return _DbhubDictToObject(value) if isinstance(value, dict) else value


# Connection is a simple container holding the API key and address of the DBHub.io server
@dataclass()
class Connection:
    api_key: str = ''
    server: str = "https://api.dbhub.io"


# Identifier holds information used to identify a specific commit, tag, release, or the head of a specific branch
@dataclass()
class Identifier:
    branch: str = ''
    commit_id: str = ''
    release: str = ''
    tag: str = ''


# UploadInformation holds information used when uploading
@dataclass()
class UploadInformation:
    identifier: Identifier = Identifier()
    commitmsg: str = ''
    sourceurl: str = ''
    lastmodified: datetime.datetime = None
    licence: str = ''
    public: bool = True
    force: bool = True
    committimestamp: datetime.datetime = None
    authorname: str = ''
    authoremail: str = ''
    committername: str = ''
    committeremail: str = ''
    otherparents: str = ''
    dbshasum: str = ''


class Dbhub:
    PRESERVE_PK_MERGE = 1
    NEX_PK_MERGE = 2

    def __init__(self, config_data: str = None, config_file: str = None):
        """
        Creates a new DBHub.io connection object.  It doesn't connect to DBHub.io.
        Connection only occurs when subsequent functions (eg Query()) are called.

        Parameters
        ----------
        key : str
            API key
        config_data : str
            INI configuration data from a string
        config_file : str
            INI configuration file
        """

        config = configparser.ConfigParser()
        if config_data:
            config.read_string(config_data)
        elif config_file:
            if os.path.exists(config_file) > 0:
                try:
                    with open(config_file) as f:
                        config.read_file(f)
                except IOError as e:
                    raise ValueError(f"Failed to read config file: {config_file} Erreor: {e}")
            else:
                raise ValueError(f"INI configuration file: {config_file} doesn't exist")
        else:
            raise ValueError("No INI configuration specified")

        if config.has_section('dbhub') is False:
            raise configparser.NoSectionError('dbhub')
        if config.has_option('dbhub', 'api_key') is False:
            raise configparser.NoOptionError('api_key', 'dbhub')
        if config.has_option('dbhub', 'db_owner') is False:
            raise configparser.NoOptionError('db_owner', 'dbhub')
        if config.has_option('dbhub', 'db_name') is False:
            raise configparser.NoOptionError('db_name', 'dbhub')

        self._connection = Connection(api_key=config['dbhub'].get('api_key'))

    def __prepareVals(self, dbOwner: str = None, dbName: str = None, ident: Identifier = None):
        data = {}
        if len(self._connection.api_key) > 0:
            data['apikey'] = (None, self._connection.api_key)
        if dbOwner is not None:
            data['dbowner'] = (None, dbOwner)
        if dbName is not None:
            data['dbname'] = (None, dbName)
        if ident is not None:
            if ident.branch is not None:
                data['branch'] = (None, ident.branch)
            if ident.commit_id is not None:
                data['commit'] = (None, ident.commit_id)
            if ident.release is not None:
                data['release'] = (None, ident.release)
            if ident.tag is not None:
                data['tag'] = (None, ident.tag)
        return data

    def Databases(self) -> Tuple[List[str], str]:
        """
        Returns the list of databases in the requesting users account.
        Ref: https://api.dbhub.io/#databases

        Returns
        -------
        Tuple[List[Dict], str]
            The returned data is
                - a list of string. Each string is the name of a database in your account.
                - a string describe error if occurs
        """
        data = {
            'apikey': (None, self._connection.api_key),
        }
        return httphub.send_request_json(self._connection.server + "/v1/databases", data)

    def Columns(self, db_owner: str, db_name: str, table: str, ident: Identifier = None) -> Tuple[List[Dict], str]:
        """
        Returns the details of all columns in a table or view, as per the SQLite "table_info" PRAGMA.
        Ref: https://api.dbhub.io/#columns

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database
        table : str
            The name of the table or view to return column information for
        ident : Identifier
            Information used to identify a specific commit, tag, release, or the head of a specific branch

        Returns
        -------
        Tuple[List[Dict], str]
            The returned data is
                - a list containing the details of each column in dictionnary objects.
                - a string describe error if occurs
        """
        data = self.__prepareVals(db_owner, db_name, ident)
        data['table'] = table

        res, err = httphub.send_request_json(self._connection.server + "/v1/columns", data)
        if err:
            return None, res

        for i, val in enumerate(res):
            res[i] = _DbhubDictToObject(val)

        return res, None

    def Delete(self, db_name: str) -> str:
        """
        Delete a database from the requesting users account.
        Ref: https://api.dbhub.io/#delete

        Parameters
        ----------
        db_name : str
            The name of the database

        Returns
        -------
        str
            a string describe error if occurs
        """
        data = self.__prepareVals(dbName=db_name)
        res, err = httphub.send_request_json(self._connection.server + "/v1/delete", data)
        if err:
            return res

        return ''

    def Branches(self, db_owner: str, db_name: str) -> Tuple[Dict, str, str]:
        """
        List of branches for a database
        Ref: https://api.dbhub.io/#branches

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str, str]
            The returned data is
                - a dicrionnary containing the details for each of the branches
                - a string containing the default branch name
                - a string describe error if occurs
        """
        data = self.__prepareVals(dbOwner=db_owner, dbName=db_name)
        res, err = httphub.send_request_json(self._connection.server + "/v1/branches", data)
        if err:
            return None, None, res

        branches = {}
        for branche_name in res["branches"]:
            branches.update({branche_name: _DbhubDictToObject(res['branches'][branche_name])})

        return branches, res["default_branch"], None

    def Commits(self, db_owner: str, db_name: str) -> Tuple[List[Dict], str]:
        """
        Returns the details of all commits for a database
        Ref: https://api.dbhub.io/#commits

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dictionnary containing the details of all commits in the database
                - a string describe error if occurs
        """
        data = self.__prepareVals(dbOwner=db_owner, dbName=db_name)
        res, err = httphub.send_request_json(self._connection.server + "/v1/commits", data)
        if err:
            return None, res

        commits = [_DbhubDictToObject(res[i]) for i in res]
        for commit in commits:
            commit.timestamp = p.parse(commit.timestamp)
            for entry in commit.tree.entries:
                entry.last_modified = p.parse(entry.last_modified)

        return commits, None

    def Diff(self, db_owner_a: str, db_name_a: str, ident_a: Identifier, db_owner_b: str, db_name_b: str, ident_b: Identifier, merge: Literal) -> Tuple[Dict, str]:
        """
        Generates a diff between two databases or two versions of a database

        Parameters
        ----------
        db_owner_a : str
            The owner of the first database
        db_name_a : str
            The name of the first database
        ident_a : Identifier
            Information used to identify a specific commit, tag, release, or the head of a specific branch
        db_owner_b : str
            The owner of the second database
        db_name_b : str
            The name of the second database
        ident_b : Identifier
            Information used to identify a specific commit, tag, release, or the head of a specific branch
        merge : Literal
            Specifies the type of SQL statements included in the diff results

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dicrionnary containing the differences between two commits of two databases
                - a string describe error if occurs
        """
        data = {
            'apikey': (None, self._connection.api_key),
            'dbowner_a': db_owner_a,
            'dbname_a': db_name_a,
            'dbowner_b': db_owner_b,
            'dbname_b': db_name_b,
        }

        if ident_a:
            if ident_a.branch:
                data['branch_a'] = ident_a.branch
            if ident_a.commit_id:
                data['commit_a'] = ident_a.commit_id
            if ident_a.release:
                data['release_a'] = ident_a.release
            if ident_a.tag:
                data['tag_a'] = ident_a.tag

        if ident_b:
            if ident_b.branch:
                data['branch_b'] = ident_b.branch
            if ident_b.commit_id:
                data['commit_b'] = ident_b.commit_id
            if ident_b.release:
                data['release_b'] = ident_b.release
            if ident_b.tag:
                data['tag_b'] = ident_b.tag

        if merge == self.PRESERVE_PK_MERGE:
            data['merge'] = 'preserve_pk'
        elif merge == self.NEX_PK_MERGE:
            data['merge'] = 'new_pk'
        else:
            data['merge'] = 'none'

        # Fetch the diffs
        res, err = httphub.send_request_json(self._connection.server + "/v1/diff", data)
        if err:
            return None, res

        return _DbhubDictToObject(res), None

    def Download(self, db_owner: str, db_name: str) -> Tuple[List[bytes], str]:
        """
        Get the requested SQLite database file as a stream of bytes
        Ref: https://api.dbhub.io/#download

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[List[bytes], str]
            The returned data is
                - database file as a list of bytes
                - a string describe error if occurs
        """
        data = self.__prepareVals(db_owner, db_name)
        return httphub.send_request(self._connection.server + "/v1/download", data)

    def Indexes(self, db_owner: str, db_name: str) -> Tuple[List[Dict], str]:
        """
        Returns the details of all indexes in a SQLite database
        Ref: https://api.dbhub.io/#indexes

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dicrionnary containing the details of all indexes in the database
                - a string describe error if occurs
        """
        data = self.__prepareVals(db_owner, db_name)
        res, err = httphub.send_request_json(self._connection.server + "/v1/indexes", data)
        if err:
            return None, res

        indexes = [_DbhubDictToObject(index) for index in res]

        return indexes, None

    def Metadata(self, db_owner: str, db_name: str) -> Tuple[List[Dict], str]:
        """
        Returns the commit, branch, release, tag and web page information for a database
        Ref: https://api.dbhub.io/#metadata

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dictionnary containing the details of all indexes in the database
                - a string describe error if occurs
        """
        data = self.__prepareVals(db_owner, db_name)
        res, err = httphub.send_request_json(self._connection.server + "/v1/metadata", data)
        if err:
            return None, res

        metadata = _DbhubDictToObject(res)

        metadata.branches = {}
        for branche in res["branches"]:
            metadata.branches.update({branche: _DbhubDictToObject(res['branches'][branche])})

        metadata.releases = {}
        for release in res["releases"]:
            metadata.releases.update({release: _DbhubDictToObject(res['releases'][release])})

        metadata.tags = {}
        for tag in res["tags"]:
            metadata.tags.update({tag: _DbhubDictToObject(res['tags'][tag])})

        commits = [_DbhubDictToObject(res['commits'][i]) for i in res['commits']]
        for commit in commits:
            commit.timestamp = p.parse(commit.timestamp)
        metadata.commits = commits

        return metadata, None

    def Query(self, db_owner: str, db_name: str, sql: str) -> Tuple[List, str]:
        """
        Run a SQLite query (SELECT only) on the chosen database, returning the results.
        Ref: https://api.dbhub.io/#query

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database
        sql : str
            The SQLite query (SELECT only)

        Returns
        -------
        Tuple[str, str]
            The returned data is
                - an array of dictionnary returned from the SQL query having three components:
                    - The name of the return field
                    - The type of data in the field (numeric)
                    - The value of the field
                - a string describe error if occurs
        """
        data = self.__prepareVals(db_owner, db_name)
        data['sql'] = base64.b64encode(sql.encode('ascii'))
        res, err = httphub.send_request_json(self._connection.server + "/v1/query", data)
        if err:
            return None, res

        rows = []
        for result_row in res:
            one_row = {}
            for data in result_row:
                result = {
                    0: lambda v: base64.b64decode(v.encode('ascii')) if isinstance(v, str) else None,   # Binary
                    1: lambda: "",                                                                      # Image - just output as an empty string (for now)
                    2: lambda: None,                                                                    # Null
                    3: lambda v: str(v) if isinstance(v, str) else "",                                  # Text
                    4: lambda v: int(v),                                                                # Integer
                    5: lambda v: float(v)                                                               # Float
                }[data['Type']](data['Value'])
                one_row.update({data['Name']: result})
            rows.append(one_row)

        return rows, None

    def Releases(self, db_owner: str, db_name: str) -> Tuple[List[Dict], str]:
        """
        Returns the details of all releases for a database
        Ref: https://api.dbhub.io/#releases

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dictionnary containing the details of all the releases of the database
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(db_owner, db_name)
        # Fetch the releases
        res, err = httphub.send_request_json(self._connection.server + "/v1/releases", data)
        if err:
            return None, res

        releases = {index: _DbhubDictToObject(res[index]) for index in res}
        for release in releases:
            releases[release].date = p.parse(releases[release].date)

        return releases, None

    def Tables(self, db_owner: str, db_name: str) -> Tuple[List[str], str]:
        """
        Returns the list of tables in a SQLite database
        Ref: https://api.dbhub.io/#tables

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[List[str], str]
            The returned data is
                - an string array.  Each string is the name of a table in the database.
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(db_owner, db_name)
        # Fetch the list of tables
        res, err = httphub.send_request_json(self._connection.server + "/v1/tables", data)
        if err:
            return None, res

        return res, None

    def Tags(self, db_owner: str, db_name: str) -> Tuple[List[Dict], str]:
        """
        Returns the details of all tags for a database
        Ref: https://api.dbhub.io/#tags

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dictionnary containing the details of all the tags in the database
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(db_owner, db_name)
        # Fetch the releases
        res, err = httphub.send_request_json(self._connection.server + "/v1/tags", data)
        if err:
            return None, res

        tags = {index: _DbhubDictToObject(res[index]) for index in res}
        for tag in tags:
            tags[tag].date = p.parse(tags[tag].date)

        return tags, None

    def Upload(self, db_name: str, info: UploadInformation, db_bytes: io.BufferedReader) -> Tuple[Dict, str]:
        """
        Creates a new database in your account, or adds a new commit to an existing database
        Ref: https://api.dbhub.io/#upload

        Parameters
        ----------
        db_name : str
            The name of the database
        info : UploadInformation
            Upload parameters
        db_bytes : io.BufferedReader
            A buffered binary stream of the database file.

        Returns
        -------
        Tuple[Dict, str]
            The returned data is
                - a dictionnary containing the new commit ID and web page URL
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(dbName=db_name, ident=info.identifier)

        if info:
            if info.commitmsg:
                data['commitmsg'] = info.commitmsg
            if info.sourceurl:
                data['sourceurl'] = info.sourceurl
            if info.lastmodified:
                data['lastmodified'] = info.committimestamp.astimezone(datetime.timezone.utc).isoformat()
            if info.licence:
                data['licence'] = info.licence
            data['public'] = str(info.public)
            data['force'] = str(info.force)
            if info.committimestamp:
                data['committimestamp'] = info.committimestamp.astimezone(datetime.timezone.utc).isoformat()
            if info.authorname:
                data['authorname'] = info.authorname
            if info.authoremail:
                data['authoremail'] = info.authoremail
            if info.committername:
                data['committername'] = info.committername
            if info.committeremail:
                data['committeremail'] = info.committeremail
            if info.otherparents:
                data['otherparents'] = info.otherparents
            if info.dbshasum:
                data['dbshasum'] = info.dbshasum

        res, err = httphub.send_upload(self._connection.server + "/v1/upload", data, db_bytes)
        if err:
            return None, res

        return res, None

    def Views(self, db_owner: str, db_name: str, ident: Identifier = None) -> Tuple[List[Dict], str]:
        """
        Returns the list of views in a SQLite database
        Ref: https://api.dbhub.io/#views

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database
        ident : Identifier
            Information used to identify a specific commit, tag, release, or the head of a specific branch

        Returns
        -------
        Tuple[List[Dict], str]
            The returned data is
                - a list of string. Each string is the name of a view in the database.
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(db_owner, db_name, ident)
        # Fetch the list of views
        res, err = httphub.send_request_json(self._connection.server + "/v1/views", data)
        if err:
            return None, res

        return res, None

    def Webpage(self, db_owner: str, db_name: str) -> Tuple[str, str]:
        """
        Returns the address of the database in the webUI. eg. for web browsers.
        Ref: https://api.dbhub.io/#webpage

        Parameters
        ----------
        db_owner : str
            The owner of the database
        db_name : str
            The name of the database

        Returns
        -------
        Tuple[str, str]
            The returned data is
                - a string with the URL of a database
                - a string describe error if occurs
        """
        # Prepare the API parameters
        data = self.__prepareVals(db_owner, db_name)
        # Fetch the address of the database in the webUI
        res, err = httphub.send_request_json(self._connection.server + "/v1/webpage", data)
        if err:
            return None, res

        return res['web_page'], None
