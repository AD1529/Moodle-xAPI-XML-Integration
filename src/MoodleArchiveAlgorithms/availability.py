from datetime import datetime
import json


class Availability:
    """
    Most Moodle objects have an "access restriction" (availability) setting. The restriction is a combination of
    restrictions, each of which can have several types (group membership, date, completion of activity, roles, etc.).
    According to restrictions, students can (or not) access the object.
    All the standard Moodle configurations have been taken into account in this class.
    Additionally, the "Availability role plugin" (‘https://moodle.org/plugins/availability_role’) was added to restrict
    the access by role. Note that the role id is defined in Site Administration > Users > Define roles
    """

    def __init__(self, jsonstr):
        self.jsonstr = jsonstr

        if jsonstr != '$@NULL@$':
            self.json_dict = json.loads(jsonstr)
            self.global_restrictions = self.get_restrictions(self.json_dict)
        else:
            self.global_restrictions = {}

    def get_restrictions(self, json_string):

        student_action, quantifier = None, None
        restrictions = []  # variable to collect all restrictions for operation

        # global availability
        if 'op' in json_string.keys():
            operator = json_string['op']
            if '&' in operator:
                student_action = 'must'
                quantifier = 'all'
            if '!' in operator:
                student_action = 'must not'
            if '|' in operator:
                quantifier = 'any'

        if 'c' in json_string.keys():
            conditions = json_string['c']
            for c in conditions:
                # completion
                course_module, completion = None, None
                # date
                date_from, date_to = None, None
                # grade
                grade_id, min_grade, max_grade = None, None, None
                # user profile
                address, country, department, email, firstname, idnumber = None, None, None, None, None, None
                city, institution, lastname, mobile, phone, skypeid, webpage = None, None, None, None, None, None, None
                profile_option, profile_value = None, None
                # group
                groupid = None
                # grouping
                groupingid = None
                # role
                role = None

                if 'type' in c.keys():
                    # completion
                    if c['type'] == 'completion':
                        course_module = c['cm']
                        if c['e'] == 1:
                            completion = 'must be marked complete'
                        elif c['e'] == 0:
                            completion = 'must not be marked complete'
                        elif c['e'] == 2:
                            completion = 'must be complete with pass grade'
                        elif c['e'] == 3:
                            completion = 'must be complete with fail grade'

                    # date
                    elif c['type'] == 'date':
                        if c['d'] == '>=':
                            date_from = datetime.fromtimestamp(c['t'])
                        elif c['d'] == '<':
                            date_to = datetime.fromtimestamp(c['t'])

                    # grade
                    elif c['type'] == 'grade':
                        grade_id = c['id']
                        # TODO associare questo id scorrendo le attività (dentro inforef.xml - grade_item - id)
                        if 'min' in c.keys():
                            min_grade = c['min']
                        if 'max' in c.keys():
                            max_grade = c['max']

                    # user profile
                    elif c['type'] == 'profile':
                        if 'sf' in c.keys():
                            # profile field
                            if c['sf'] == 'address':
                                address = c['sf']
                            elif c['sf'] == 'city':
                                city = c['sf']
                            elif c['sf'] == 'country':
                                country = c['sf']
                            elif c['sf'] == 'department':
                                department = c['sf']
                            elif c['sf'] == 'email':
                                email = c['sf']
                            elif c['sf'] == 'firstname':
                                firstname = c['sf']
                            elif c['sf'] == 'idnumber':
                                idnumber = c['sf']
                            elif c['sf'] == 'institution':
                                institution = c['sf']
                            elif c['sf'] == 'lastname':
                                lastname = c['sf']
                            elif c['sf'] == 'phone2':
                                mobile = c['sf']
                            elif c['sf'] == 'phone1':
                                phone = c['sf']
                        elif 'cf' in c.keys():
                            if c['cf'] == 'skype':
                                skypeid = c['cf']
                            elif c['cf'] == 'url':
                                webpage = c['cf']
                        # profile option
                        if c['op'] == 'isequalto':
                            profile_option = 'is equal to'
                        elif c['op'] == 'contains':
                            profile_option = 'contains'
                        elif c['op'] == 'doesnotcontain':
                            profile_option = 'does not contain'
                        elif c['op'] == 'startswith':
                            profile_option = 'starts with'
                        elif c['op'] == 'startswith':
                            profile_option = 'starts with'
                        elif c['op'] == 'endswith':
                            profile_option = 'ends with'
                        elif c['op'] == 'isempty':
                            profile_option = 'is empty'
                        elif c['op'] == 'isnotempty':
                            profile_option = 'is not empty'
                        # profile value
                        profile_value = c['v']

                    # group
                    elif c['type'] == 'group':
                        if 'id' in c.keys():
                            groupid = c['id']
                        else:
                            groupid = 'any'

                    # grouping
                    elif c['type'] == 'grouping':
                        groupingid = c['id']

                    # role
                    elif c['type'] == 'role':
                        if c['id'] == 1:
                            role = 'Manager'
                        elif c['id'] == 16:
                            role = 'Administrative'  # not standard Moodle role
                        elif c['id'] == 5:
                            role = 'Editing Teacher'
                        elif c['id'] == 7:
                            role = 'Teacher'
                        elif c['id'] == 9:
                            role = 'Student'
                        elif c['id'] == 20:
                            role = 'Extended student'  # not standard Moodle role
                        elif c['id'] == 11:
                            role = 'Guest'

                    restriction = dict(zip(('course_module', 'completion', 'date_from', 'date_to', 'grade_id',
                                            'min_grade', 'max_grade', 'address', 'city', 'country', 'department',
                                            'email', 'firstname', 'idnumber', 'institution', 'lastname',
                                            'mobile', 'phone', 'skypeid', 'webpage', 'profile_option',
                                            'profile_value', 'groupid', 'groupingid', 'role'),
                                           (course_module, completion, date_from, date_to, grade_id,
                                            min_grade, max_grade, address, city, country, department,
                                            email, firstname, idnumber, institution, lastname,
                                            mobile, phone, skypeid, webpage, profile_option,
                                            profile_value, groupid, groupingid, role)))

                    restrictions.append(restriction)

                # recursive call to handle nested conditions
                elif len(c.keys()) == 2:
                    restrictions.append(self.get_restrictions(c))

        restriction_set = [{'student_action': student_action}, {'quantifier': quantifier}, restrictions]

        return restriction_set

    def __str__(self):

        def recursive_print(restrictions, st):
            for item in restrictions:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if key == 'student_action' and value is not None:
                            st += f'Student {value} match'
                        elif key == 'quantifier':
                            if value is not None:
                                st += f' {value} of the following:'
                            else:
                                st += f' the following'

                else:
                    for sub_item in item:
                        if isinstance(sub_item, dict):

                            for key, value in sub_item.items():
                                if value is not None:
                                    # completion
                                    if key == 'course_module':
                                        st += f'\nActivity {str(value)} '
                                    if key == 'completion':
                                        st += f'{value}'

                                    # date
                                    if key == 'date_from':
                                        st += f'\nDate From {str(value)}'
                                    if key == 'date_to':
                                        st += f'\nDate To {str(value)}'

                                    # grade
                                    if key == 'grade_id':
                                        st += f'\nGrade ID {str(value)}'
                                    if key == 'min_grade':
                                        st += f' must be >= {str(value)}'
                                    if key == 'max_grade':
                                        st += f' must be < {str(value)}'

                                    # profile
                                    if key in ('address', 'city', 'country', 'department', 'email', 'firstname',
                                               'idnumber', 'institution', 'lastname', 'mobile', 'phone', 'skypeid',
                                               'webpage'):
                                        st += f'\nUser profile field {key}'
                                    if key == 'profile_option':
                                        st += f' {value}'
                                    if key == 'profile_value':
                                        st += f' {str(value)}'

                                    # role
                                    if key == 'role':
                                        st += f'\nRole {value}'

                        else:
                            # recursive call to handle nested conditions
                            st += '\nNested conditions {\n'
                            st = recursive_print(sub_item, st)
                            st += ' }'

            return st

        string = f"\n\n"
        return f"{recursive_print(self.global_restrictions, string)}"
