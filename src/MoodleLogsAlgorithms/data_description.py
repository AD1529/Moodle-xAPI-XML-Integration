from pandas import DataFrame
import src.MoodleLogsAlgorithms.data_preprocessing as pp
import src.MoodleLogsAlgorithms.function_utils as fu
import pandas as pd
import numpy as np


def preprocessing_description(role_table: DataFrame, df: DataFrame, course: int):
    """
    Change the roles according to specific needs

    Parameters
    ----------
    role_table
    df
    course

    Returns
    -------

    """
    # Print the number of students, teachers, non-editing teachers, administratives, extended_students
    print('Course ID:', course)
    print(f'Enrolled users: '
          f'{len(role_table.loc[role_table['Manager'] > 0])} Manager, '
          f'{len(role_table.loc[role_table['Administrative'] > 0])} Administratives, '
          f'{len(role_table.loc[role_table['Editing Teacher'] > 0])} Editing Teachers, '
          f'{len(role_table.loc[role_table['Teacher'] > 0])} Non-Editing Teachers, '
          f'{len(role_table.loc[role_table['Student'] > 0])} Students, '
          f'{len(role_table.loc[role_table['Extended student'] > 0])} Extended students')

    # Students that were unenrolled from course
    users = len(df.loc[(df.ObjectID == 9) & (df.CourseID == course)]['User'].unique())
    unenrolled = users - len(role_table.loc[role_table['Student'] == 1])
    print(f'{unenrolled} Students were unenrolled')

    # Students that have other than student role in other courses
    students_with_other_than_student_roles = set(pp.detect_potential_fake_students(df, course))
    if len(students_with_other_than_student_roles) > 0:
        print(
            f'\n{len(students_with_other_than_student_roles)} enrolled students have roles other than '
            f'Student/Extended student in other courses:')
        role_es = pp.get_users_roles(df, students_with_other_than_student_roles)
        print('Roles assigned to enrolled students in other courses:')
        for key, values in role_es.items():
            values = [x for x in list(values) if x not in (9, 20)]
            print(key, values)
        print('These enrolled students have been unassigned the role student.')

    # Users that performed some actions in the course without being enrolled
    not_enrolled_users = pp.get_not_enrolled_users(df, course)
    if len(not_enrolled_users) > 0:
        print(f'\n{len(not_enrolled_users)} users performed some actions in the course without being enrolled')

        # Role assigned to the not enrolled users in other courses
        role_neu = pp.get_users_roles(df, not_enrolled_users)
        print('Roles assigned to not enrolled users in other courses:')
        for key, value in role_neu.items():
            print(key, value)


def activities_description(df: DataFrame, course: int):
    # Activities that were deleted
    deleted_activities = (df.loc[(df.CourseID == course) & (df.Status == 'DELETED') & (
        ~df.Path.str.contains('comment'))].RelatedActivities.apply(fu.explode_list).tolist())

    unique_data = [list(x) for x in set(tuple(x) for x in deleted_activities)]

    print(f'\nDeleted activities: {len(unique_data)}')

    exclude = ['Enrolment', 'Role', 'Groups', 'User profile']
    course_student_logs = df.loc[(df.Role == 'Student')
                                 & (df.CourseID == course)
                                 & (~df.Component.isin(exclude))
                                 & (~df.Event_name.str.contains('list'))]

    # number of activities for each component
    table = pd.DataFrame(course_student_logs.groupby(['Component']).ObjectID.nunique())
    table.columns = ['# Activities']
    # number of actions for each component
    table['# Actions'] = course_student_logs.groupby('Component').size()
    # number of students that performed some actions on the component
    table['# Students'] = course_student_logs.groupby(['Component']).User.nunique().astype(int)
    # average number of actions for each component
    table['Average'] = round(table['# Actions'] / table['# Students'], 0).astype(int)

    table.loc['Sum'] = table.sum()
    table.loc[table.index[-1], '# Students'] = np.nan
    table.loc[table.index[-1], 'Average'] = np.nan
    print(table)
