from pandas import DataFrame
import pandas as pd
import math


def convert_timestamp_to_datetime(df: DataFrame) -> DataFrame:
    """
    Create a datetime object from the given string. This function should
    be customised according to your datetime format.

    Args:
        df

    Returns: the corresponding timestamp.

    """
    df['Unixtime'] = df['Timestamp'].apply(lambda x: int(pd.Timestamp(x, tz='Europe/Berlin').timestamp()) - 3600)
    df['Date'] = df['Timestamp'].apply(lambda x: pd.Timestamp(x, tz='Europe/Berlin').date())
    df['Time'] = df['Timestamp'].apply(lambda x: pd.Timestamp(x, tz='Europe/Berlin').time())

    return df


def add_course_week(df: DataFrame, semester: int, week_field: str = 'Week'):
    """
    Add the week number for every course from its start: 1st week, 2nd week, etc. according to the week of the year

    Returns:
        Object of class Records with the week field

    Parameters
    ----------
    week_field: name of the week column which indicates the week from the start date of the course/area
    df
    semester
    """

    weekly_seconds = 604800

    if semester == 1:
        startdate = 1693782000  # 03.09.2023
        enddate = 1705186799  # 13.01.2024
    else:
        startdate = 1705276800  # 15.01.2024
        enddate = 1716854399  # 27.05.2024

    # get the weeks number
    df[week_field] = pd.Series()
    week_number = math.ceil((enddate - startdate) / weekly_seconds)
    for wn in range(1, week_number + 1):
        week_number = wn
        df.loc[(df.Unixtime < startdate + wn * weekly_seconds) & (df[week_field].isnull()), week_field] = week_number

    df.loc[(df[week_field].isnull()) & (semester == 1), week_field] = 0
    return df


def semester_retrieval(course_id: int) -> int:
    """

    Parameters
    ----------
    course_id

    Returns
    -------

    """
    semester = 1
    second_semester = [1, 4, 7, 9, 10, 11, 12]

    if course_id in second_semester:
        semester = 2

    return semester
