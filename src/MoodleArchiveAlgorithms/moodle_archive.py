import os
import re
import tarfile
from src.MoodleArchiveAlgorithms.moodle_object import MoodleCourse, MoodleSection, MoodleActivity
from src.MoodleArchiveAlgorithms.question_bank import QuestionBank


class MoodleArchive:
    """
    A Moodle course can be saved through the course backup functionality from the course navigation menu by
    selecting More > Course reuse > Backup. A backup file is characterised
    by the MBZ extension and its name follows the format backup-moodle2-courseid-coursename-date-hour.mbz, ending
    with -nu.mbz for backups without user data and -an.mbz when the option ‘Anonymize user information’ is checked.
    After unzipping the backup file, it is made up of a list of XML files and folders containing additional folders
    and XML files. There are four folders: activities, course, files, and sections
    """

    def __init__(self, backup_path, backup_filename, archive_destination_path=""):
        self.backup_path = backup_path
        self.backup_filename = backup_filename
        self.archive_destination_path = backup_path if archive_destination_path == "" else archive_destination_path
        self.archive_dir_name = self.get_archive_dir_name()
        self.archive_dir = os.path.join(self.archive_destination_path, self.archive_dir_name)
        self.extract()
        self.course = self.get_course()
        self.sections = self.get_sections()
        self.activities = self.get_activities()
        self.questionBank = self.get_question_bank()
        self.section_list = self.add_section_correspondence()
        self.add_subsections()
        # self.files = self.get_files()

    def get_archive_dir_name(self):
        match = re.search(r"(\w)-course-(\d+)", self.backup_filename)
        if match:
            course_id = match.group(2)
            return f"MoodleCourseID{course_id}"
        else:
            return None

    def extract(self):
        """Extract the compressed file"""
        archive = os.path.join(self.backup_path, self.backup_filename)
        if os.path.exists(self.archive_dir):
            print(f"The file '{self.archive_dir}' already exists.")
        elif os.path.exists(self.archive_destination_path):
            os.makedirs(self.archive_dir, exist_ok=True)
            try:
                with tarfile.open(archive, "r:gz") as tar:
                    tar.extractall(path=self.archive_dir)  # Extract all files in the current directory
                    print(f"The file {archive} has been successfully extracted into the {self.archive_dir}.")
            except tarfile.TarError as e:
                print(f"Error extracting file {archive}: {e}")

    def get_course(self):
        course = MoodleCourse(self.archive_dir)
        return course

    def get_sections(self):
        """
        Get the sections for a course
        """
        sections = {}
        sections_dir = os.path.join(self.archive_dir, "sections")
        for section in os.listdir(sections_dir):
            s = MoodleSection(sections_dir, section)
            sections[section] = s
        return sections

    def get_activities(self):
        """
        Get the list of activities for each section
        """
        activities = {}
        activities_dir = os.path.join(self.archive_dir, "activities")
        for activity in os.listdir(activities_dir):
            a = MoodleActivity(activities_dir, activity)
            activities[activity] = a
        return activities

    def get_question_bank(self):
        question_bank = QuestionBank(self.archive_dir)
        return question_bank

    def get_files(self):
        pass

    def add_section_correspondence(self):
        """
        Return the list of sections for a course

        """
        number_of_sections = len(self.sections)
        section_list = [None] * number_of_sections

        for section in self.sections.values():
            section_list[section.settings.number] = section

        return section_list

    def add_subsections(self):
        """
        Add all the subsections of a section in a course
        """
        if self.course.settings.format == 'flexsections':
            for parent_section in range(len(self.section_list)):  # for each potentially parent section
                children_sections = []  # list of potentially children sections
                for section in range(1, len(self.section_list)):  # for each potentially child section
                    if self.section_list[section].settings.parent_section_number == parent_section:
                        children_sections.append(section)  # it is a child section
                self.section_list[parent_section].settings.sub_sections = children_sections
        elif self.course.settings.format == 'onetopic':
            for parent in range(len(self.section_list)):  # for each potentially parent section
                children_sections = []  # list of potentially children sections
                for child in range(parent + 1, len(self.section_list)):  # for each potentially child section
                    # parent section of the potential child
                    cpsn = self.section_list[child].settings.parent_section_number
                    # parent section of the potential parent
                    ppsn = self.section_list[parent].settings.parent_section_number
                    if cpsn < 1 or ppsn == 1:
                        break
                    else:
                        children_sections.append(child)  # it is a child section
                    self.section_list[parent].settings.sub_sections = children_sections
