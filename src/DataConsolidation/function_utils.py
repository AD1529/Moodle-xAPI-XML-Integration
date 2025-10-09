import json
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np


def load_json(file_path: Path) -> list:
    """
    Takes a file object and returns the JSON object.

    Parameters
    -----------
    file_path
        Path object from where the JSON data are loaded.

    Returns
    --------
    List
        Loaded JSON data in the form of key/value pair.
        The keys are strings and the values are the JSON types. Keys and values are separated by a colon.
        Each entry (key/value pair) is separated by a comma.

    Raises
    -------
    FileNotFoundError
        When the file is requested but doesn't exist.
    JSONDecodeError
        When the data being deserialized is not a valid JSON document.

    """

    with open(file_path, mode='r') as file:
        json_file = json.load(file)

    return json_file


def normalise_json(json_file: list) -> DataFrame:
    """
    Takes a JSON object and returns normalised JSON data.

    Parameters
    -----------
    json_file
        JSON object to be normalised.

    Returns
    --------
    DataFrame
        Flat table of semi-structured JSON data.

    Raises
    -------
        KeyError
            When keys listed in metadata (list of paths) are not always present.

    """

    statements = [dict_.get("statement") for dict_ in json_file]

    df = pd.json_normalize(statements)

    return df


def explode_list(items: list) -> list:
    """
    A function that explodes a list of items.

    """
    # create an empty list object if None
    if not isinstance(items, list) or isinstance(items, float):
        items = []
    # create a list with all 'id' keys in the list of items (dictionaries)
    ids = [item.get('id') for item in items]
    # fill the list with np.nan to keep the same length for all items
    ids.extend([np.nan] * (5 - len(ids)))

    return ids
