from pandas import DataFrame


def course_name_retrieval(df: DataFrame, course: int) -> DataFrame:
    if course == 313:  # TODO remove on GitHub
        course_name = 'Minéralogie - S1-23'
    elif course == 1539:
        course_name = 'LU2IN011 - Représentation et méthodes numériques - S1-23'
    elif course == 2961:
        course_name = 'Diversité des Interactions Marines - S1-23'
    elif course == 3135:
        course_name = 'Label vert 2 - S1-23'
    elif course == 3791:
        course_name = 'IMTT-GES-S2-23'
    elif course == 1527:
        course_name = 'Organisation moléculaire du vivant - S2'
    elif course == 1587:
        course_name = 'Organisation cellulaire du vivant - S1-23'
    elif course == 2781:
        course_name = 'Organisation et fonctions des organismes photosynthétiques - S2-23'
    elif course == 3499:
        course_name = 'Mécanique - Physique 2 - S2-23'
    else:
        course_id = f'id={course}'
        course_name = df.loc[(df['Object_id'].str.contains('course/view.php')) &
                             (df['Object_id'].str.contains(course_id))].head(1).Context.values[0]

    return course_name


def filter_semester_data(df: DataFrame, course: int) -> DataFrame:
    """
    Remove values that are inconsistent with the start and end dates.

    Returns:
        The dataframe purged of records previously or lately recorded in relation to course dates.
    """

    course_name = course_name_retrieval(df, course)

    if 'S1' in course_name:
        start_date = '2023-09-01T00:00:01+01:00'
        end_date = '2024-01-13T23:59:59+01:00'
    else:
        start_date = '2024-01-15T00:00:00+01:00'
        end_date = '2024-05-27T23:59:59+02:00'

    df = df.loc[((df['Timestamp'] > start_date) & (df['Timestamp'] < end_date))]
    # reverse the order based on the index
    # df = df.iloc[::-1]
    df = df.reset_index(drop=True)

    return df
