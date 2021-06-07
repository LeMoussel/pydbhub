import pydbhub
from typing import Any, Dict, List, Tuple
from json.decoder import JSONDecodeError
import requests
import io


def send_request_json(query_url: str, data: Dict[str, Any]) -> Tuple[List[Any], str]:
    """
    send_request_json sends a request to DBHub.io, formatting the returned result as JSON

    Parameters
    ----------
    query_url : str
        url of the API endpoint
    data : Dict[str, Any]
        data to be processed to the server.

    Returns
    -------
    Tuple[List[Any], str]
    The returned data is
        - a list of JSON object.
        - a string describe error if occurs
    """

    try:
        headers = {'User-Agent': f'pydbhub v{pydbhub.__version__}'}
        response = requests.post(query_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except JSONDecodeError as e:
        return None, e.args[0]
    except TypeError as e:
        return None, e.args[0]
    except requests.exceptions.HTTPError as e:
        try:
            return response.json(), e.args[0]
        except JSONDecodeError:
            return None, e.args[0]
    except requests.exceptions.RequestException as e:
        cause = e.args(0)
        return None, str(cause.args[0])


def send_request(query_url: str, data: Dict[str, Any]) -> Tuple[List[bytes], str]:
    """
    send_request sends a request to DBHub.io.

    Parameters
    ----    query_url : str
        url of the API endpoint
    data : Dict[str, Any]
        data to be processed to the server.------


    Returns
    -------
    List[bytes]
        database file is returned as a list of bytes
    """
    try:
        headers = {'User-Agent': f'pydbhub v{pydbhub.__version__}'}
        response = requests.post(query_url, data=data, headers=headers)
        response.raise_for_status()
        return response.content, None
    except requests.exceptions.HTTPError as e:
        return None, e.args[0]
    except requests.exceptions.RequestException as e:
        cause = e.args(0)
        return None, str(cause.args[0])


def send_upload(query_url: str, data: Dict[str, Any], db_bytes: io.BufferedReader) -> Tuple[List[Any], str]:
    """
    send_upload uploads a database to DBHub.io.

    Parameters
    ----------
    query_url : str
        url of the API endpoint.
    data : Dict[str, Any]
        data to be processed to the server.
    db_bytes : io.BufferedReader
        A buffered binary stream of the database file.

    Returns
    -------
    Tuple[List[Any], str]
    The returned data is
        - a list of JSON object.
        - a string describe error if occurs
    """
    try:
        headers = {'User-Agent': f'pydbhub v{pydbhub.__version__}'}
        files = {"file": db_bytes}
        response = requests.post(query_url, data=data, headers=headers, files=files)
        response.raise_for_status()
        if response.status_code != 201:
            # The returned status code indicates something went wrong
            try:
                return response.json(), str(response.status_code)
            except JSONDecodeError:
                return None, str(response.status_code)
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            return response.json(), e.args[0]
        except JSONDecodeError:
            return None, e.args[0]
    except requests.exceptions.RequestException as e:
        cause = e.args(0)
        return None, str(cause.args[0])
