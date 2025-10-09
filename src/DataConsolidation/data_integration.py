from pandas import DataFrame
import pandas as pd
import numpy as np




def get_group_table(df: DataFrame, course: int) -> DataFrame:
    """
    Create a table with the assigned and unassigned groups based on the difference (assigned-unassigned)

    Parameters
    ----------
    df: dataframe
    course: course id

    Returns
    -------
    A table with assigned and unassigned groups

    """
    groups_A = {
        'XXX': 'Group 1',
        'XXX': 'Group 2',
        'XXX': 'Group 3',
        'XXX': 'Group 4',
    }

    groups_B = {
        'XXX': 'Group 1',
        'XXX': 'Group 2',
        'XXX': 'Group 3',
  
    }

   

    # correspondence course - groups list
    course_groups = {
        A: groups_A,
        B: groups_B,
    }

    if course in course_groups.keys():

        group_list = course_groups[course]

        # users that have been added in a group
        added = df.loc[(df.CourseID == course)
                       & (df.Component == 'Groups')
                       & (df.Event_name == 'Group member added')][['User', 'Context']]
        added['Group'] = added['Context'].map(group_list)

        # users that have been removed from a group
        removed = df.loc[(df.CourseID == course)
                         & (df.Component == 'Groups')
                         & (df.Event_name == 'Group member removed')][['User', 'Context']]
        removed['Group'] = removed['Context'].map(group_list)

        # create a table to host the users with their corresponding group
        cols = ['User'] + list(set(group_list.values()))

        group_table = pd.DataFrame(columns=cols)
        group_table['User'] = added['User'].unique()
        group_table = group_table.mask(group_table.isna(), 0)  # fill the dataframe with 0 for the sum

        # fill the table with the assigned group
        for user in added['User'].unique():
            groups = added.loc[added['User'] == user]['Group'].values
            groups = [x for x in groups if str(x) != 'nan']
            for group in groups:
                group_table.loc[(group_table['User'] == user), group] = group_table.loc[
                                                                            (group_table['User'] == user), group] + 1

        # remove the unassigned group from the table
        for user in removed['User'].unique():
            groups = removed.loc[removed['User'] == user]['Group'].values
            groups = [x for x in groups if str(x) != 'nan']
            for group in groups:
                group_table.loc[(group_table['User'] == user), group] = group_table.loc[
                                                                            (group_table['User'] == user), group] - 1

        # fix double group assignment
        group_table[group_table == 2] = 1

    else:
        group_table = pd.DataFrame()

    return group_table


def assign_groups(group_table: DataFrame, df: DataFrame, course: int) -> DataFrame:
    """
    Assign the retrieved groups to the users in the dataframe

    Parameters
    ----------
    group_table: table with the groups for each user
    df: dataframe containing the users
    course: course ID

    Returns
    -------
    The dataframe with the field Group

    """

    df['Group'] = np.empty((len(df), 0)).tolist()

    if group_table.empty:
        df['Group'] = np.nan
    else:
        # remove all users that aren't added to a group
        group_table = group_table.loc[group_table[group_table.columns.difference(['User'])].sum(axis=1) != 0]

        for user in group_table.User:
            selected_user = group_table.loc[group_table.User == user]
            # a user can be added in more than one group
            group = selected_user.columns[(selected_user == 1).any()]
            # assign the groups to the user in the course
            df.loc[(df.User == user) & (df.CourseID == course), 'Group'] = \
                df.loc[(df.User == user) & (df.CourseID == course)]['Group'].apply(lambda x: list(group))


    return df
