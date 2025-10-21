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


def patch(df, prior_statements_path):
    # TODO remove on Github
    prior_statements = pd.read_pickle(prior_statements_path)
    list_actors_prior_statements = prior_statements['actor.name'].unique()
    list_actors_df = df['actor.name'].unique()
    df_begin_time = df.iloc[0].timestamp
    for actor in list_actors_df:
        if actor in list_actors_prior_statements:
            logs_to_add = prior_statements.loc[
                (prior_statements['actor.name'] == actor) & (prior_statements['timestamp'] <= df_begin_time)]
            df = pd.concat([logs_to_add, df], axis=0)

    df_patched = df.copy()  # to have a defragmented df for small courses
    df_patched['index'] = df_patched.index
    df_patched = df_patched.sort_values(by=['timestamp', 'index'])
    df_patched = df_patched.reset_index(drop=True)

    return df_patched


def patch_modified_names(df: DataFrame) -> DataFrame:
    # TODO remove on Github
    df.loc[df.User == '0e143436d3cb0c5e16d74253b9ef019f23c73e6e9bbba4aabbb593e594dde922', 'User'] = \
        '98a0d3aee96ce2202a1abde88b632040098c27c0ad17711841f2c4baefe125c0'

    return df
