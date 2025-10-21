import src.MoodleLogsAlgorithms.function_utils as fu
from pandas import DataFrame
import numpy as np
import pandas as pd


def read_json_file(course: int, path_json, path_pickle):
    """
    Normalise and convert json files and save them as pickle files.

    Parameters
    ----------
    course
        ID of the course to be preprocessed.
    path_json
        Path of the json files
    path_pickle
        Path of the pickle files

    Returns
    -------
    Pickle file
        A pickle file for every course

    """

    file_path = path_json / f"cours_{course}.json"
    # load the JSON file
    json_file = fu.load_json(file_path)
    # normalise the JSON file
    df = fu.normalise_json(json_file)
    # save the normalised file as pickle
    converted_file_path = path_pickle / f"cours_{course}.pkl"
    df.to_pickle(converted_file_path)


def filter_and_rename_columns(df: DataFrame) -> DataFrame:
    """
    Rename the fields of the dataframe. Some fields can be renamed according to specific needs.

    Parameters
    ----------
    df: dataframe to be renamed

    Raises
    ----------
    KeyError
        If any of the labels is not found in the selected axis.

    Returns
    ---------
    The dataframe after column renaming.

    """

    cols = {
        'actor.name': 'User',
        'timestamp': 'Timestamp',
        'verb.display.en': 'Action_verb',
        'verb.display.fr': 'Action_verb_fr',  # can be removed
        'object.id': "Object_id",
        'object.definition.type': "Object_type",
        'object.definition.name.en': "Context",
        'object.definition.name.fr': "Context_fr",  # can be removed
        'object.definition.description.en': 'Description',
        'object.definition.description.fr': 'Description_fr',  # can be removed
        'context.contextActivities.grouping': 'RelatedActivities',
        'context.extensions.http://lrs&46;learninglocker&46;net/define/extensions/info.event_name': 'Path',
    }

    # filter the dataframe based on the selected columns
    df = df[cols.keys()]
    # rename columns
    df = df.rename(columns=cols)

    return df


def merge_duplicates_missing_values(df: DataFrame) -> DataFrame:
    # TODO remove on Github
    """

    Parameters
    ----------
    df

    Returns
    -------

    """
    # merge the values of the FR columns with the EN ones
    df.loc[df.Action_verb.isnull(), 'Action_verb'] = df.loc[df.Action_verb_fr.notnull()]['Action_verb_fr']
    df.loc[df.Context.isnull(), 'Context'] = df.loc[df.Context_fr.notnull()]['Context_fr']
    df.loc[df.Description.isnull(), 'Description'] = df.loc[df.Description_fr.notnull()]['Description_fr']

    # remove unused columns
    df = df.drop(columns=['Action_verb_fr', 'Context_fr', 'Description_fr'])

    return df


def add_component_event_name(df: DataFrame) -> DataFrame:
    """
    Add the component and the event_name fields to the dataframe extracting this information from the Path

    Parameters
    ----------
    df: dataframe

    Returns
    -------
    The dataframe with the Component and Event_name fields
    """

    df.loc[:, 'Component'] = df.loc[:, 'Path'].map(lambda x: x.split('\\')[1], na_action='ignore')
    df.loc[:, 'Event_name'] = df.loc[:, 'Path'].map(lambda x: x.split('event\\')[1], na_action='ignore')

    completion = df.Path.str.contains('course_module_completion_updated')
    df.loc[completion, 'Component'] = df.loc[completion, 'Object_id'].map(
        lambda x: x.split('.fr/')[1].split('/view.php')[0].replace('/', '_'))

    return df


def extract_ids(df: DataFrame) -> DataFrame:
    """
    Extract all IDs from the RelatedActivities field and create 4 new columns:
     'CourseID', 'ObjectID', 'ItemID', 'QuestionID'. For each, the id is assigned.

    Parameters
    ----------
    df: dataframe

    Returns
    -------
    The dataframe with all IDs extracted.

    """
    # explode the Related Activities field
    id_cols = ['Platform', 'CourseID', 'ObjectID', 'ItemID', 'QuestionID']
    df[id_cols] = df['RelatedActivities'].apply(fu.explode_list).tolist()
    # remove redundant information
    df = df.drop(columns=['Platform'])

    ###############
    ## Course ID ##
    # extract CourseID from RelatedActivities
    df.loc[:, 'CourseID'] = df.loc[:, 'CourseID'].map(lambda x: x.split('/course/view.php?id=')[1], na_action='ignore')
    # extract CourseID from Object_id
    course_view = (df['CourseID'].isnull()) & (df['Object_id'].str.contains("/course/view.php"))
    df.loc[course_view, 'CourseID'] = df.loc[course_view, 'Object_id'].map(lambda x: x.split('/course/view.php?id=')[1])
    # set missing values in CourseID to 1 since 1 is the id of the platform
    df.loc[df.CourseID.isnull(), 'CourseID'] = '1'
    # set data type
    df.loc[:, 'CourseID'] = df['CourseID'].astype('int')

    ###############
    ## Object ID ##
    # fix plugin bugs
    course_searched = (df.Path == '\\mod_forum\\event\\course_searched')
    df.loc[course_searched, 'ObjectID'] = np.nan
    # fix deleted activities
    deleted_activities = ((df.Object_id == 'https://moodle-sciences-23.sorbonne-universite.fr/mod/')
                          | (df.ObjectID == 'https://moodle-sciences-23.sorbonne-universite.fr/mod/'))
    # | (df.Description == 'deleted'))  # TODO change?
    df.loc[deleted_activities, 'ObjectID'] = np.nan

    # extract ObjectID from ObjectID
    df.loc[:, 'ObjectID'] = df.loc[:, 'ObjectID'].map(lambda x: x.split('/view.php?id=')[1], na_action='ignore')

    # extract ObjectID from Object_id
    multiple_check = ((df.ObjectID.isnull()) & (df.Object_id.str.contains('/mod/')) & (
        ~df.Object_id.str.contains('user.php')) & (~deleted_activities))
    df.loc[multiple_check, 'ObjectID'] = df.loc[multiple_check, 'Object_id'].map(lambda x: x.split('id=')[1])

    groupid = (df.Object_id.str.contains('group=')) & (~df.Path.str.contains('mod_questionnaire'))
    df.loc[groupid, 'ObjectID'] = df.loc[groupid, 'Object_id'].map(lambda x: x.split('group=')[1])

    categoryid = df.Object_id.str.contains('categoryid=')
    df.loc[categoryid, 'ObjectID'] = df.loc[categoryid, 'Object_id'].map(lambda x: x.split('categoryid=')[1])

    roleid = df.Object_id.str.contains('roleid=')
    df.loc[roleid, 'ObjectID'] = df.loc[roleid, 'Object_id'].map(lambda x: x.split('roleid=')[1])

    # fix instance_list objectID
    instance_list = (df.Path.str.contains('course_module_instance_list_viewed'))
    df.loc[instance_list, 'ObjectID'] = np.nan

    # set missing values to 0
    df.loc[df.ObjectID.isnull(), 'ObjectID'] = '0'
    # set data type
    df.loc[:, 'ObjectID'] = df['ObjectID'].astype('int')

    #############
    ## Item ID ##
    # fix plugin bugs
    assign_id = (df.ItemID.str.contains('assign', na=False))
    df.loc[assign_id, 'ItemID'] = np.nan

    # extract ItemID from ItemID
    attemptid_qid = (df.ItemID.str.contains('attempt', na=False))
    df.loc[attemptid_qid, 'ItemID'] = df.loc[attemptid_qid, 'ItemID'].map(
        lambda x: x.split("attempt=")[1].split('&cmid=')[0])

    discussid = (df.ItemID.str.contains('discuss', na=False))
    df.loc[discussid, 'ItemID'] = df.loc[discussid, 'ItemID'].map(lambda x: x.split("d=")[1])

    # extract ItemID from Object_id
    instance_id = (df.Component == 'mod_questionnaire') & (df.Event_name == 'response_viewed')
    df.loc[instance_id, 'ItemID'] = df.loc[instance_id]['Object_id'].map(
        lambda x: x.split('instance=')[1].split('&user')[0])

    instance_id_all = (df.Component == 'mod_questionnaire') & (df.Event_name == 'all_responses_viewed')
    df.loc[instance_id_all, 'ItemID'] = df.loc[instance_id_all]['Object_id'].map(
        lambda x: x.split('instance=')[1].split('&group')[0])

    record_id = (df.Component == 'mod_data') & (df.Path.str.contains('record_'))
    df.loc[record_id, 'ItemID'] = df.loc[record_id, 'Object_id'].map(lambda x: x.split('&rid=')[1])

    attemptid = (df.ItemID.isnull()) & (df.Path.str.contains('attempt')) & (df.Component == 'mod_quiz')
    df.loc[attemptid, 'ItemID'] = df.loc[attemptid, 'Object_id'].map(lambda x: x.split('attempt=')[1].split('&cmid')[0])

    feedback_attemptid = (df.Path.str.contains('response')) & (
            (df.Action_verb == 'submitted') | (df.Action_verb == 'deleted'))
    df.loc[feedback_attemptid, 'ItemID'] = df.loc[feedback_attemptid, 'Object_id'].map(
        lambda x: x.split('showcompleted=')[1])

    entry_id = (df.ItemID.isnull()) & (df.Component == 'mod_glossary') & (df.Path.str.contains('entry_'))
    df.loc[entry_id, 'ItemID'] = df.loc[entry_id, 'Object_id'].map(lambda x: x.split('hook=')[1])

    discussion_subscription = (df.Path.str.contains('discussion_subscription'))
    df.loc[discussion_subscription, 'ItemID'] = df.loc[discussion_subscription, 'Object_id'].map(
        lambda x: x.split('d=')[1].split('&')[0])

    discussion_id = ((df.ItemID.isnull()) & (df.Component == 'mod_forum') &
                     ((df.Path.str.contains('discussion_')) | (df.Path.str.contains('post_')) | (
                         df.Path.str.contains('subscription_'))))
    df.loc[discussion_id, 'ItemID'] = df.loc[discussion_id, 'Object_id'].map(lambda x: x.split('d=')[1])

    chapter_id = (df.Path.str.contains('chapter')) & (df.Component.str.contains('book'))
    df.loc[chapter_id, 'ItemID'] = df.loc[chapter_id, 'Object_id'].map(lambda x: x.split('chapterid=')[1])

    wiki_page = (df.Component == 'mod_wiki') & (
            (df.Path.str.contains('page_')) | (df.Path.str.contains('comments_viewed')))
    df.loc[wiki_page, 'ItemID'] = df.loc[wiki_page, 'Object_id'].map(lambda x: x.split('pageid=')[1])

    lesson_page = (df.Component == 'mod_lesson') & (
            (df.Path.str.contains('page_')) | (df.Path.str.contains('question_')))
    df.loc[lesson_page, 'ItemID'] = df.loc[lesson_page, 'Object_id'].map(lambda x: x.split('pageid=')[1])

    workshop = (df.Component == 'mod_workshop') & (df.Path.str.contains('assessed'))
    df.loc[workshop, 'ItemID'] = df.loc[workshop, 'ItemID'].map(lambda x: x.split('&id=')[1])

    # set missing values to 0
    df.loc[df.ItemID.isnull(), 'ItemID'] = '0'
    # set data type
    df.loc[:, 'ItemID'] = df['ItemID'].astype('int')

    #############
    ## Question ID ##
    # extract QuestionID from Object_id
    quiz_question_id = ((df.Path.str.contains('attempt_submitted')) & (df.Component == 'mod_quiz') &
                        (df.Action_verb == 'answered'))
    df.loc[quiz_question_id, 'QuestionID'] = df.loc[quiz_question_id, 'Object_id'].map(lambda x: x.split('&id=')[1])

    feedback_question_id = (df.Path.str.contains('response_submitted') & (df.Component == 'mod_feedback') & (
            df.Action_verb == 'answered'))
    df.loc[feedback_question_id, 'QuestionID'] = df.loc[feedback_question_id, 'Object_id'].map(
        lambda x: x.split('id=')[1])

    # set missing values to 0
    df.loc[df.QuestionID.isnull(), 'QuestionID'] = '0'
    # set data type
    df.loc[:, 'QuestionID'] = df['QuestionID'].astype('int')

    return df


def add_course_area(df: DataFrame) -> DataFrame:
    """
    Add the Course_Area field to those records that identify actions performed in the site outside a course and that
    miss a value.

    Parameters
    ----------
    df: dataframe

    Returns
    -------
    The dataframe with added the Course_Area column.

    """

    # course
    df.loc[df.CourseID != 1, 'Course_Area'] = 'Course'

    # moodle site
    df.loc[df.CourseID == 1, 'Course_Area'] = 'Moodle Site'

    ## OVERRIDE ##
    # authentication
    df.loc[df['Event_name'] == 'user_loggedin', 'Course_Area'] = 'Authentication'
    df.loc[df['Event_name'] == 'user_loggedout', 'Course_Area'] = 'Authentication'

    # profile
    df.loc[df['Event_name'].str.contains('dashboard'), 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'user_profile_viewed') & (df['CourseID'] == 1), 'Course_Area'] = 'Profile'
    df.loc[(df['Event_name'] == 'grade_report_viewed') & (df['CourseID'] == 1), 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_password_updated', 'Course_Area'] = 'Profile'
    df.loc[df['Event_name'] == 'user_updated', 'Course_Area'] = 'Profile'

    # social interaction
    df.loc[(df['Event_name'].str.contains('(?i)message')) & (
            df['Component'] != 'mod_chat'), 'Course_Area'] = 'Social interaction'

    return df


def redefine_component(df: DataFrame) -> DataFrame:
    """
    The component field can be labelled with the 'System' value even though the log is clearly generated when the user
    is performing an action on a specific module. Sometimes some records are recorded on different components even
    though they are related to the same component. This function redefines the component field.

    Parameters
    ----------
    df: dataframe

    Returns
    -------
    The dataframe with redefined components

    """

    # assignment
    assign = ((df['Component'] == 'assignsubmission_file') |
              (df['Component'] == 'assignsubmission_onlinetext') |
              (df['Component'] == 'assignsubmission_comments') |
              (df['Component'] == 'mod_assign'))
    df.loc[assign, 'Component'] = 'Assignment'

    # attendance
    df.loc[(df['Component'] == 'mod_attendance'), 'Component'] = 'Attendance'

    # authentication
    df.loc[df['Event_name'] == 'user_loggedin', 'Component'] = 'Login'
    df.loc[df['Event_name'] == 'user_loggedout', 'Component'] = 'Logout'

    # bigbluebutton
    df.loc[df['Component'] == 'mod_bigbluebuttonbn', 'Component'] = 'BigBlueButton'

    # block
    df.loc[df['Component'].str.contains('block'), 'Component'] = 'Block'

    # book
    book = ((df['Component'] == 'mod_book') |
            (df['Component'] == 'booktool_print'))
    df.loc[book, 'Component'] = 'Book'

    # chat
    df.loc[df['Component'] == 'mod_chat', 'Component'] = 'Chat'

    # checklist
    df.loc[df['Component'] == 'mod_checklist', 'Component'] = 'Checklist'

    # choice
    df.loc[df['Component'] == 'mod_choice', 'Component'] = 'Choice'

    # course
    df.loc[(df['CourseID'] != 1) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Course'
    course = ((df['Event_name'] == 'course_resources_list_viewed') |
              (df['Event_name'] == 'course_information_viewed'))
    df.loc[course, 'Component'] = 'Course'

    # dashboard
    df.loc[df['Event_name'].str.contains('dashboard'), 'Component'] = 'Dashboard'

    # database
    df.loc[df['Component'] == 'mod_data', 'Component'] = 'Database'

    # enrollment
    df.loc[df['Event_name'].str.contains('user_enrolment'), 'Component'] = 'Enrolment'

    # feedback
    df.loc[df['Component'] == 'mod_feedback', 'Component'] = 'Feedback'

    # file
    df.loc[df['Component'] == 'mod_resource', 'Component'] = 'File'

    # folder
    df.loc[df['Component'] == 'mod_folder', 'Component'] = 'Folder'

    # forum
    df.loc[df['Component'] == 'mod_forum', 'Component'] = 'Forum'

    # glossary
    df.loc[df['Component'] == 'mod_glossary', 'Component'] = 'Glossary'

    # grades
    grades = ((df['Event_name'] == 'grade_report_viewed') |
              (df['Event_name'] == 'course_user_report_viewed') |
              (df['Event_name'] == 'grade_item_updated') |
              (df['Event_name'] == 'grade_item_created'))
    df.loc[grades, 'Component'] = 'Grades'

    # group choice
    df.loc[df['Component'] == 'mod_choicegroup', 'Component'] = 'Group choice'

    # groups
    group_member = ((df['Event_name'] == 'group_member_added') |
                    (df['Event_name'] == 'group_member_removed') |
                    (df['Event_name'].str.contains('group|Grouping')) & (df['Event_name'] != 'group_message_sent'))
    df.loc[group_member, 'Component'] = 'Groups'

    # h5p
    df.loc[df['Component'] == 'mod_h5pactivity', 'Component'] = 'H5P'

    # imscp
    df.loc[df['Component'] == 'mod_imscp', 'Component'] = 'IMS content package'

    # label
    df.loc[(df['Component'] == 'mod_label'), 'Component'] = 'Label'

    # lesson
    df.loc[(df['Component'] == 'mod_lesson'), 'Component'] = 'Lesson'

    # lti
    df.loc[(df['Component'] == 'mod_lti'), 'Component'] = 'External tool'

    # messaging
    df.loc[(df['Event_name'].str.contains('(?i)message')) & (df['Component'] != 'mod_chat'), 'Component'] = 'Messaging'

    # notification
    df.loc[df['Event_name'].str.contains('notification'), 'Component'] = 'Notification'

    # page
    df.loc[(df['Component'] == 'mod_page'), 'Component'] = 'Page'

    # questionnaire
    df.loc[(df['Component'] == 'mod_questionnaire'), 'Component'] = 'Questionnaire'

    # quiz
    quiz = (((df['Event_name'].str.contains('Question')) & (df['Component'] == 'core')) |
            (df['Component'] == 'mod_quiz'))
    df.loc[quiz, 'Component'] = 'Quiz'

    # recent activity
    df.loc[df['Event_name'] == 'recent_activity_viewed', 'Component'] = 'Recent activity'

    # role
    df.loc[df['Event_name'].str.contains('role'), 'Component'] = 'Role'

    # scheduler
    df.loc[df['Component'] == 'mod_scheduler', 'Component'] = 'Scheduler'

    # scorm
    df.loc[df['Component'] == 'mod_scorm', 'Component'] = 'SCORM package'

    # site home
    df.loc[(df['CourseID'] == 1) & (df['Event_name'] == 'course_viewed'), 'Component'] = 'Site home'

    # survey
    df.loc[df['Component'] == 'mod_survey', 'Component'] = 'Survey'

    # system
    clist = ((df['Event_name'] == 'course_category_viewed') |
             (df['Event_name'] == 'courses_searched') |
             (df['Event_name'] == 'user_created'))
    df.loc[clist, 'Component'] = 'System'

    # tour
    df.loc[df['Component'] == 'tool_usertours', 'Component'] = 'Tour'

    # url
    df.loc[df['Component'] == 'mod_url', 'Component'] = 'URL'

    # user profile
    user_profile = ((df['Event_name'] == 'user_list_viewed') |
                    (df['Event_name'] == 'user_updated') |
                    (df['Event_name'] == 'user_profile_viewed'))
    df.loc[user_profile, 'Component'] = 'User profile'

    # wiki
    df.loc[(df['Component'] == 'mod_wiki'), 'Component'] = 'Wiki'

    # wooclap
    df.loc[(df['Component'] == 'mod_wooclap'), 'Component'] = 'Wooclap'

    # workshop
    df.loc[(df['Component'] == 'mod_workshop'), 'Component'] = 'Workshop'

    # deleted activities
    # df.loc[df.Component.str.contains('mod_'), 'Component'] = 'DELETED'

    return df


def redefine_event_name(df: DataFrame) -> DataFrame:
    """
    Transform the path extracted from the statement.extension in the extended readable format. This function can be
    modified according to your needs. The complete list of events is available on
    https://yoursite/report/eventlist/index.php

    Parameters
    ----------
    df: dataframe

    Returns
    -------
    The dataframe with redefined event_name

    """
    ############
    ## Module ##
    # assignment
    assignment = (df['Component'] == 'Assignment')
    df.loc[assignment & (df['Event_name'] == 'assessable_submitted'), 'Event_name'] = 'A submission has been submitted'
    df.loc[assignment & (df['Event_name'] == 'assessable_uploaded'), 'Event_name'] = 'A file has been uploaded'
    df.loc[assignment & (df['Event_name'] == 'comment_created'), 'Event_name'] = 'Comment created'
    df.loc[assignment & (df['Event_name'] == 'comment_deleted'), 'Event_name'] = 'Comment deleted'
    df.loc[assignment & (df['Event_name'] == 'feedback_viewed'), 'Event_name'] = 'Feedback viewed'
    df.loc[assignment & (df['Event_name'] == 'remove_submission_form_viewed'), 'Event_name'] = ('Remove submission '
                                                                                                'confirmation viewed')
    df.loc[assignment & (df['Event_name'] == 'submission_confirmation_form_viewed'), 'Event_name'] = ('Submission '
                                                                                                      'confirmation '
                                                                                                      'form viewed')
    df.loc[assignment & (df['Event_name'] == 'submission_created'), 'Event_name'] = 'Submission created'
    df.loc[assignment & (
            df['Event_name'] == 'submission_duplicated'), 'Event_name'] = 'The user duplicated their submission'
    df.loc[assignment & (df['Event_name'] == 'submission_form_viewed'), 'Event_name'] = 'Submission form viewed'
    df.loc[assignment & (df['Event_name'] == 'submission_graded'), 'Event_name'] = 'The submission has been graded'
    df.loc[assignment & (df['Event_name'] == 'submission_status_viewed'), 'Event_name'] = ('The status of the '
                                                                                           'submission has been viewed')
    df.loc[assignment & (df['Event_name'] == 'submission_updated'), 'Event_name'] = 'Submission updated'
    df.loc[assignment & (df['Event_name'] == 'submission_viewed'), 'Event_name'] = 'Submission viewed'

    # attendance
    attendance = (df['Component'] == 'Attendance')
    df.loc[
        attendance & (df['Event_name'] == 'attendance_taken_by_student'), 'Event_name'] = 'Attendance taken by student'
    df.loc[attendance & (df['Event_name'] == 'session_report_viewed'), 'Event_name'] = 'Session report viewed'

    # big blue button
    bigbluebutton = (df['Component'] == 'BigBlueButton')
    df.loc[bigbluebutton & (df['Event_name'] == 'activity_viewed'), 'Event_name'] = 'Activity viewed'
    df.loc[bigbluebutton &
           (df['Event_name'] == 'bigbluebuttonbn_activity_management_viewed'), 'Event_name'] = ('BigBlueButtonBN '
                                                                                                'activity management '
                                                                                                'viewed')
    df.loc[bigbluebutton & (df['Event_name'] == 'live_session_event'), 'Event_name'] = 'Live session event'
    df.loc[bigbluebutton & (df['Event_name'] == 'meeting_created'), 'Event_name'] = 'Meeting created'
    df.loc[bigbluebutton & (df['Event_name'] == 'meeting_ended'), 'Event_name'] = 'Meeting ended'
    df.loc[bigbluebutton & (df['Event_name'] == 'meeting_joined'), 'Event_name'] = 'Meeting joined'
    df.loc[bigbluebutton & (df['Event_name'] == 'meeting_left'), 'Event_name'] = 'Meeting left'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_deleted'), 'Event_name'] = 'Recording deleted'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_edited'), 'Event_name'] = 'Recording edited'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_imported'), 'Event_name'] = 'Recording imported'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_protected'), 'Event_name'] = 'Recording protected'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_published'), 'Event_name'] = 'Recording published'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_unprotected'), 'Event_name'] = 'Recording unprotected'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_unpublished'), 'Event_name'] = 'Recording unpublished'
    df.loc[bigbluebutton & (df['Event_name'] == 'recording_viewed'), 'Event_name'] = 'Recording viewed'

    # book
    book = (df['Component'] == 'Book')
    df.loc[book & (df['Event_name'] == 'book_printed'), 'Event_name'] = 'Book printed'
    df.loc[book & (df['Event_name'] == 'chapter_viewed'), 'Event_name'] = 'Chapter viewed'
    df.loc[book & (df['Event_name'] == 'chapter_printed'), 'Event_name'] = 'Chapter printed'

    # chat
    chat = (df['Component'] == 'Chat')
    df.loc[chat & (df['Event_name'] == 'sessions_viewed'), 'Event_name'] = 'Sessions viewed'
    df.loc[chat & (df['Event_name'] == 'message_sent'), 'Event_name'] = 'Message sent'

    # checklist
    checklist = (df['Component'] == 'Checklist')
    df.loc[checklist & (df['Event_name'] == 'checklist_completed'), 'Event_name'] = 'Checklist completed'
    df.loc[checklist & (df['Event_name'] == 'student_comment_created'), 'Event_name'] = 'Student comment created'
    df.loc[checklist & (df['Event_name'] == 'student_comment_updated'), 'Event_name'] = 'Student comment updated'
    df.loc[checklist & (df['Event_name'] == 'student_checks_updated'), 'Event_name'] = 'Student checks updated'

    # choice
    choice = (df['Component'] == 'Choice')
    df.loc[choice & (df['Event_name'] == 'answer_created'), 'Event_name'] = 'Choice answer added'
    df.loc[choice & (df['Event_name'] == 'answer_deleted'), 'Event_name'] = 'Choice answer deleted'

    # database
    database = (df['Component'] == 'Database')
    df.loc[database & (df['Event_name'] == 'record_created'), 'Event_name'] = 'Record created'
    df.loc[database & (df['Event_name'] == 'record_deleted'), 'Event_name'] = 'Record deleted'
    df.loc[database & (df['Event_name'] == 'record_updated'), 'Event_name'] = 'Record updated'

    # feedback
    feedback = (df['Component'] == 'Feedback')
    df.loc[feedback & (df['Event_name'] == 'response_deleted'), 'Event_name'] = 'Response deleted'
    df.loc[feedback & (df['Event_name'] == 'response_submitted')] = 'Response submitted'

    # folder
    df.loc[(df['Event_name'] == 'all_files_downloaded'), 'Event_name'] = 'Zip archive of folder downloaded'

    # forum
    forum = (df['Component'] == 'Forum')
    df.loc[forum & (df['Event_name'] == 'assessable_uploaded'), 'Event_name'] = 'Some content has been posted'
    df.loc[forum & (df['Event_name'] == 'course_searched'), 'Event_name'] = 'Course searched'
    df.loc[forum & (df['Event_name'] == 'discussion_created'), 'Event_name'] = 'Discussion created'
    df.loc[forum & (df['Event_name'] == 'discussion_deleted'), 'Event_name'] = 'Discussion deleted'
    df.loc[forum & (df['Event_name'] == 'discussion_viewed'), 'Event_name'] = 'Discussion viewed'
    df.loc[forum & (df['Event_name'] == 'discussion_subscription_created'), 'Event_name'] = ('Discussion subscription '
                                                                                             'created')
    df.loc[forum & (df['Event_name'] == 'discussion_subscription_deleted'), 'Event_name'] = ('Discussion subscription '
                                                                                             'deleted')
    df.loc[forum & (df['Event_name'] == 'post_created'), 'Event_name'] = 'Post created'
    df.loc[forum & (df['Event_name'] == 'post_deleted'), 'Event_name'] = 'Post deleted'
    df.loc[forum & (df['Event_name'] == 'post_updated'), 'Event_name'] = 'Post updated'
    df.loc[forum & (df['Event_name'] == 'readtracking_disabled'), 'Event_name'] = 'Read tracking disabled'
    df.loc[forum & (df['Event_name'] == 'readtracking_enabled'), 'Event_name'] = 'Read tracking enabled'
    df.loc[forum & (df['Event_name'] == 'subscription_created'), 'Event_name'] = 'Subscription created'
    df.loc[forum & (df['Event_name'] == 'subscription_deleted'), 'Event_name'] = 'Subscription deleted'
    df.loc[forum & (df['Event_name'] == 'user_report_viewed'), 'Event_name'] = 'User report viewed'

    # glossary
    glossary = (df['Component'] == 'Glossary')
    df.loc[glossary & (df['Event_name'] == 'entry_created'), 'Event_name'] = 'Entry has been created'
    df.loc[glossary & (df['Event_name'] == 'entry_deleted'), 'Event_name'] = 'Entry has been deleted'
    df.loc[glossary & (df['Event_name'] == 'entry_updated'), 'Event_name'] = 'Entry has been updated'
    df.loc[glossary & (df['Event_name'] == 'entry_viewed'), 'Event_name'] = 'Entry has been viewed'

    # group choice
    groupchoice = (df['Component'] == 'Group choice')
    df.loc[groupchoice & (df['Event_name'] == 'choice_removed'), 'Event_name'] = 'Choice removed'
    df.loc[groupchoice & (df['Event_name'] == 'choice_updated'), 'Event_name'] = 'Choice made'

    # h5p
    h5p = (df.Component == 'H5P')
    df.loc[h5p & (df['Event_name'] == 'report_viewed'), 'Event_name'] = 'Report viewed'
    df.loc[h5p & (df['Event_name'] == 'statement_received'), 'Event_name'] = 'xAPI statement received'

    # lesson
    lesson = (df['Component'] == 'Lesson')
    df.loc[lesson & (df['Event_name'] == 'content_page_viewed'), 'Event_name'] = 'Content page viewed'
    df.loc[lesson & (df['Event_name'] == 'lesson_ended'), 'Event_name'] = 'Lesson ended'
    df.loc[lesson & (df['Event_name'] == 'lesson_restarted'), 'Event_name'] = 'Lesson restarted'
    df.loc[lesson & (df['Event_name'] == 'lesson_resumed'), 'Event_name'] = 'Lesson resumed'
    df.loc[lesson & (df['Event_name'] == 'lesson_started'), 'Event_name'] = 'Lesson started'
    df.loc[lesson & (df['Event_name'] == 'question_answered'), 'Event_name'] = 'Question answered'
    df.loc[lesson & (df['Event_name'] == 'question_viewed'), 'Event_name'] = 'Question viewed'

    # questionnaire
    questionnaire = (df['Component'] == 'Questionnaire')
    df.loc[questionnaire & (df['Event_name'] == 'all_responses_viewed'), 'Event_name'] = 'All Responses report viewed'
    df.loc[questionnaire & (df['Event_name'] == 'attempt_resumed'), 'Event_name'] = 'Attempt resumed'
    df.loc[questionnaire & (df['Event_name'] == 'attempt_saved'), 'Event_name'] = 'Responses saved'
    df.loc[questionnaire & (df['Event_name'] == 'attempt_submitted'), 'Event_name'] = 'Responses submitted'
    df.loc[questionnaire & (df['Event_name'] == 'response_viewed'), 'Event_name'] = 'Individual Responses report viewed'

    # quiz
    quiz = (df['Component'] == 'Quiz')
    df.loc[quiz & (df['Event_name'] == 'attempt_abandoned'), 'Event_name'] = 'Quiz attempt abandoned'
    df.loc[quiz & (df['Event_name'] == 'attempt_reviewed'), 'Event_name'] = 'Quiz attempt reviewed'
    df.loc[quiz & (df['Event_name'] == 'attempt_started'), 'Event_name'] = 'Quiz attempt started'
    df.loc[quiz & (df['Event_name'] == 'attempt_submitted'), 'Event_name'] = 'Quiz attempt submitted'
    df.loc[quiz & (df['Event_name'] == 'attempt_summary_viewed'), 'Event_name'] = 'Quiz attempt summary viewed'
    df.loc[quiz & (df['Event_name'] == 'attempt_viewed'), 'Event_name'] = 'Quiz attempt viewed'

    # scheduler
    scheduler = (df['Component'] == 'Scheduler')
    df.loc[scheduler & (df['Event_name'] == 'booking_added'), 'Event_name'] = 'Scheduler booking added'
    df.loc[scheduler & (df['Event_name'] == 'booking_form_viewed'), 'Event_name'] = 'Scheduler booking form viewed'
    df.loc[scheduler & (df['Event_name'] == 'booking_removed'), 'Event_name'] = 'Scheduler booking removed'

    # scorm
    scorm = (df['Component'] == 'SCORM package')
    df.loc[scorm & (df['Event_name'] == 'sco_launched'), 'Event_name'] = 'Sco launched'
    df.loc[scorm & (df['Event_name'] == 'scoreraw_submitted'), 'Event_name'] = 'Submitted SCORM raw score'
    df.loc[scorm & (df['Event_name'] == 'status_submitted'), 'Event_name'] = 'Submitted SCORM status'

    # survey
    df.loc[(df['Event_name'] == 'response_submitted') &
           (df['Component'] == 'Survey'), 'Event_name'] = 'Survey response submitted'

    # wiki
    wiki = (df['Component'] == 'Wiki')
    df.loc[
        wiki & (df['Event_name'] == 'comments_viewed') & (df['Component'] == 'Wiki'), 'Event_name'] = 'Comments viewed'
    df.loc[
        wiki & (df['Event_name'] == 'comments_deleted') & (df['Component'] == 'Wiki'), 'Event_name'] = 'Comment deleted'
    df.loc[
        wiki & (df['Event_name'] == 'comments_created') & (df['Component'] == 'Wiki'), 'Event_name'] = 'Comment created'
    df.loc[wiki & (df['Event_name'] == 'page_created'), 'Event_name'] = 'Wiki page created'
    df.loc[wiki & (df['Event_name'] == 'page_deleted'), 'Event_name'] = 'Wiki page deleted'
    df.loc[wiki & (df['Event_name'] == 'page_diff_viewed'), 'Event_name'] = 'Wiki diff viewed'
    df.loc[wiki & (df['Event_name'] == 'page_history_viewed'), 'Event_name'] = 'Wiki history viewed'
    df.loc[wiki & (df['Event_name'] == 'page_map_viewed'), 'Event_name'] = 'Wiki page map viewed'
    df.loc[wiki & (df['Event_name'] == 'page_updated'), 'Event_name'] = 'Wiki page updated'
    df.loc[wiki & (df['Event_name'] == 'page_version_deleted'), 'Event_name'] = 'Wiki page version deleted'
    df.loc[wiki & (df['Event_name'] == 'page_version_restored'), 'Event_name'] = 'Wiki page version restored'
    df.loc[wiki & (df['Event_name'] == 'page_version_viewed'), 'Event_name'] = 'Wiki page version viewed'
    df.loc[wiki & (df['Event_name'] == 'page_viewed'), 'Event_name'] = 'Wiki page viewed'

    # workshop
    workshop = (df['Component'] == 'Workshop')
    df.loc[workshop & (df['Event_name'] == 'assessable_uploaded'), 'Event_name'] = 'A submission has been uploaded'
    df.loc[workshop & (df['Event_name'] == 'submission_assessed'), 'Event_name'] = 'Submission assessed'
    df.loc[workshop & (df['Event_name'] == 'submission_created'), 'Event_name'] = 'Submission created'
    df.loc[workshop & (df['Event_name'] == 'submission_deleted'), 'Event_name'] = 'Submission deleted'
    df.loc[workshop & (df['Event_name'] == 'submission_reassessed'), 'Event_name'] = 'Submission re-assessed'
    df.loc[workshop & (df['Event_name'] == 'submission_updated'), 'Event_name'] = 'Submission updated'
    df.loc[workshop & (df['Event_name'] == 'submission_viewed'), 'Event_name'] = 'Submission viewed'

    ############
    ## Course ##
    df.loc[(df['Event_name'] == 'course_viewed'), 'Event_name'] = 'Course viewed'
    df.loc[(df['Event_name'] == 'course_completed'), 'Event_name'] = 'Course completed'
    df.loc[(df['Event_name'] == 'course_information_viewed'), 'Event_name'] = 'Course summary viewed'
    df.loc[
        (df['Event_name'] == 'course_module_completion_updated'), 'Event_name'] = 'Course activity completion updated'
    df.loc[(df['Event_name'] == 'course_resources_list_viewed'), 'Event_name'] = 'Course module instance list viewed'
    df.loc[(df['Event_name'] == 'courses_searched'), 'Event_name'] = 'Courses searched'
    df.loc[(df['Event_name'] == 'course_user_report_viewed'), 'Event_name'] = 'Course user report viewed'
    df.loc[
        (df['Event_name'] == 'course_module_instance_list_viewed'), 'Event_name'] = 'Course module instance list viewed'
    df.loc[(df['Event_name'] == 'course_module_viewed'), 'Event_name'] = 'Course module viewed'

    ############
    ## System ##
    # category
    df.loc[(df['Event_name'] == 'course_category_viewed'), 'Event_name'] = 'Category viewed'
    df.loc[(df['Event_name'] == 'search_results_viewed'), 'Event_name'] = 'Search results viewed'
    # comment
    df.loc[(df['Event_name'] == 'comment_created'), 'Event_name'] = 'Comment created'
    df.loc[(df['Event_name'] == 'comment_deleted'), 'Event_name'] = 'Comment deleted'
    # dashboard
    df.loc[(df['Event_name'] == 'dashboard_reset'), 'Event_name'] = 'Dashboard reset'
    df.loc[(df['Event_name'] == 'dashboard_viewed'), 'Event_name'] = 'Dashboard viewed'
    # enrollment
    df.loc[(df['Event_name'] == 'user_enrolment_created'), 'Event_name'] = 'User enrolled in course'
    df.loc[(df['Event_name'] == 'user_enrolment_deleted'), 'Event_name'] = 'User unenrolled from course'
    df.loc[(df['Event_name'] == 'user_enrolment_updated'), 'Event_name'] = 'User enrolment updated'
    # grade
    df.loc[(df['Event_name'] == 'grade_item_created'), 'Event_name'] = 'Grade item created'
    df.loc[(df['Event_name'] == 'grade_item_updated'), 'Event_name'] = 'Grade item updated'
    df.loc[
        (df['Event_name'] == 'grade_report_viewed') & (df.CourseID == 1), 'Event_name'] = 'Grade overview report viewed'
    df.loc[(df['Event_name'] == 'grade_report_viewed') & (df.CourseID != 1), 'Event_name'] = 'Grade user report viewed'
    # group
    df.loc[(df['Event_name'] == 'group_member_added'), 'Event_name'] = 'Group member added'
    df.loc[(df['Event_name'] == 'group_member_removed'), 'Event_name'] = 'Group member removed'
    # login/logout
    df.loc[(df['Event_name'] == 'user_loggedin'), 'Event_name'] = 'User has logged in'
    df.loc[(df['Event_name'] == 'user_loggedout'), 'Event_name'] = 'User logged out'
    # message
    df.loc[(df['Event_name'] == 'group_message_sent'), 'Event_name'] = 'Group message sent'
    df.loc[(df['Event_name'] == 'message_sent'), 'Event_name'] = 'Message sent'
    df.loc[(df['Event_name'] == 'message_deleted'), 'Event_name'] = 'Message deleted'
    df.loc[(df['Event_name'] == 'message_viewed'), 'Event_name'] = 'Message viewed'
    # notification
    df.loc[(df['Event_name'] == 'notification_sent'), 'Event_name'] = 'Notification sent'
    df.loc[(df['Event_name'] == 'notification_viewed'), 'Event_name'] = 'Notification viewed'
    # recent activity
    df.loc[(df['Event_name'] == 'recent_activity_viewed'), 'Event_name'] = 'Recent activity viewed'
    # role
    df.loc[(df['Event_name'] == 'role_assigned'), 'Event_name'] = 'Role assigned'
    df.loc[(df['Event_name'] == 'role_unassigned'), 'Event_name'] = 'Role unassigned'
    df.loc[(df['Event_name'] == 'role_updated'), 'Event_name'] = 'Role updated'
    # tour
    df.loc[(df['Event_name'] == 'tour_ended'), 'Event_name'] = 'Tour ended'
    df.loc[(df['Event_name'] == 'tour_started'), 'Event_name'] = 'Tour started'
    # user
    df.loc[(df['Event_name'] == 'user_profile_viewed'), 'Event_name'] = 'User profile viewed'
    df.loc[(df['Event_name'] == 'user_updated'), 'Event_name'] = 'User updated'
    df.loc[(df['Event_name'] == 'user_created'), 'Event_name'] = 'User created'
    df.loc[(df['Event_name'] == 'user_deleted'), 'Event_name'] = 'User deleted'
    df.loc[(df['Event_name'] == 'user_list_viewed'), 'Event_name'] = 'User list viewed'

    return df


def get_role_table(df: DataFrame, course: int) -> DataFrame:
    """
    Create a table with the assigned and unassigned role assignments based on the difference (assigned-unassigned)

    Parameters
    ----------
    df: dataframe
    course: course id

    Returns
    -------
        The table with the assigned roles to each user of the course
    """

    roles = {
        1: 'Manager',
        16: 'Administrative',  # not standard Moodle role
        5: 'Editing Teacher',
        7: 'Teacher',
        9: 'Student',
        20: 'Extended student',  # not standard Moodle role
        11: 'Guest',
        13: 'Authenticated user',
        15: 'Authenticated user on site home'
    }

    # users that have been assigned a role
    assigned = df.loc[(df['Event_name'] == 'Role assigned') & (df.CourseID == course)][['User', 'ObjectID']]
    assigned['Role'] = assigned['ObjectID'].map(roles)

    # users that have been unassigned a role
    unassigned = df.loc[(df['Event_name'] == 'Role unassigned') & (df.CourseID == course)][['User', 'ObjectID']]
    unassigned['Role'] = unassigned['ObjectID'].map(roles)

    # create a table to host the users with their corresponding role
    cols = ['User'] + list(roles.values())[
        :6]  # Guest, Authenticated user, and Authenticated user on site home are assigned outside a
    # course
    role_table = pd.DataFrame(columns=cols)
    role_table['User'] = assigned['User'].unique()
    role_table = role_table.mask(role_table.isna(), 0)  # fill the dataframe with 0 for the sum

    # fill the table with the assigned role
    for user in assigned['User'].unique():
        roles = assigned.loc[assigned['User'] == user]['Role'].values
        for role in roles:
            role_table.loc[(role_table['User'] == user), role] = role_table.loc[(role_table['User'] == user), role] + 1

    # remove the unassigned role from the table
    for user in unassigned['User'].unique():
        roles = unassigned.loc[unassigned['User'] == user]['Role'].values
        for role in roles:
            role_table.loc[(role_table['User'] == user), role] = role_table.loc[(role_table['User'] == user), role] - 1

    # fix teachers with two accounts
    role_table[role_table == 2] = 1

    return role_table


def detect_potential_fake_students(df: DataFrame, course: int) -> list:
    """
    Usually when a user is enrolled in a course, the first proposed option for enrolment is student. In case of hurry
    or distraction, some users can be enrolled in a course without being a student, for instance a manager to help,
    teachers to have a look. Please consider that a user can be assigned a role by distraction and immediately after
    unassigned. This function helps to detect fake students by checking if a student enrolled as not student in
    another course is really a student or not. This check is done by calculating the number of times in a course a
    user was given a role and then unassigned it (if any). If the difference is positive, the user has been assigned
    that role.

    Parameters
    ----------
    df: dataframe
    course: course id

    Returns
    -------
        list of potential fake students

    """

    # students of the course
    role_table = get_role_table(df, course)
    students = role_table.loc[role_table['Student'] == 1].User
    other_role_students = []

    for student in students:
        # for each student, check if they have been assigned another role in any other course
        other_roles = df.loc[(df.Event_name == 'Role assigned') & (df.User == student) & (df.ObjectID != 9) &
                             (df.ObjectID != 20)][['CourseID', 'ObjectID']]
        # if they have been assigned another role
        if not other_roles.empty:
            # find in what courses
            course_ids = other_roles.CourseID.unique()
            for course_id in course_ids:
                # for each course find the assigned role
                object_ids = other_roles.loc[other_roles.CourseID == course_id]['ObjectID'].unique()
                for objectID in object_ids:
                    # count the number of times they have been assigned
                    assigned = len(df.loc[(df.CourseID == course_id) & (df.User == student) &
                                          (df.ObjectID == objectID) & (df.Event_name == 'Role assigned')])
                    # count the number of times they have been unassigned
                    unassigned = len(df.loc[(df.CourseID == course_id) & (df.User == student) &
                                            (df.ObjectID == objectID) & (df.Event_name == 'Role unassigned')])
                    check_role = assigned - unassigned
                    if check_role > 0:
                        # add the user to the list of potential fake students
                        other_role_students.append(student)

    # return the set of unique students
    return list(set(other_role_students))


def get_not_enrolled_users(df: DataFrame, course: int) -> set:
    """
    Retrieve the users that are not enrolled in a course despite having performed some actions because they
    have been unenrolled or they have superior capabilities

    Parameters
    ----------
    df: dataframe
    course: course id

    Returns
    -------
        the set of users that are not enrolled in a course

    """
    # list of all users that performed some actions in the course without a role
    all_users = df.loc[df.CourseID == course].User.unique()
    enrolled_users = df.loc[(df.CourseID == course) & (df['Event_name'] == 'Role assigned')]['User'].unique()
    not_enrolled_users = set(all_users) ^ set(enrolled_users)

    return not_enrolled_users


def get_users_roles(df: DataFrame, users: set) -> dict:
    """
    For each user of the dataframe, return the roles assigned to each user

    Parameters
    ----------
    df: the dataframe
    users: unique users in the dataframe

    Returns
    -------
    A dictionary with users as keys and roles as values

    """
    roles_neu = {}
    for user in users:
        other_roles = df.loc[(df.Event_name == 'Role assigned') & (df.User == user)]['ObjectID'].values
        if len(other_roles) > 0:
            roles_neu[user] = set(other_roles)
        else:
            roles_neu[user] = 1

    return roles_neu


def assign_roles(role_table: DataFrame, df: DataFrame, course: int) -> DataFrame:
    """
    According to the role table, assign the correct role to each user per course

    Parameters
    ----------
    role_table: table of roles
    df: dataframe
    course: the course id of the specific course used for role assignment

    Returns
    -------
     The dataframe with roles assigned to each user

    """
    # remove all users that aren't assigned a role
    role_table = role_table.loc[role_table[role_table.columns.difference(['User'])].sum(axis=1) != 0]

    for user in role_table.User:
        # roles are ordered according to their capabilities, take the most important one
        selected_user = role_table.loc[role_table.User == user]
        role = selected_user.columns[(selected_user == 1).any()][0]
        # assign the role to the user in the course
        df.loc[(df.User == user) & (df.CourseID == course), 'Role'] = role
        # assign the role to the user in other courses
        df.loc[(df.User == user) & (df.CourseID != course) & (df.Course_Area == 'Course'), 'Role'] = 'Other courses'
        # assign the "Authenticated user" role to the user in the platform
        df.loc[df.Role.isnull(), 'Role'] = 'Authenticated user'

    return df


def remove_fake_students(role_table: DataFrame, students_to_remove: list) -> DataFrame:
    """
    Remove users with the role Student identified as fake

    Parameters
    ----------
    role_table: table of roles
    students_to_remove: list of students to remove

    Returns
    -------
    role_table without fake students

    """
    for student in students_to_remove:
        role_table.loc[role_table.User == student, 'Student'] = 0

    return role_table
