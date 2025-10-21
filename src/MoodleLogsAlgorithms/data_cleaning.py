from pandas import DataFrame


def clean_events(df: DataFrame) -> DataFrame:
    """
    Remove unnecessary data specific to your dataset.
    Please be aware that if you are performing any temporal analysis these activities must be removed after
    duration calculation. The function is customisable according to your needs.

    """

    # automatically generated events that do not involve student actions
    df = df.loc[df['Event_name'] != 'Notification sent']
    # events that depends on activity settings
    df = df.loc[df['Event_name'] != 'Course activity completion updated']

    df = df.reset_index(drop=True)

    return df
