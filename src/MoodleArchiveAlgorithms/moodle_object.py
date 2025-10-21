import os
from src.MoodleArchiveAlgorithms.settings import CourseSettings, SectionSettings, ActivitySettings
from src.MoodleArchiveAlgorithms.content import CourseContent, SectionContent, ActivityContent


class MoodleObject:
    """
    A Moodle object (a course, a section, an activity) is always made up of settings and content.
    This content is made up of none or some Moodle objects included in the object.
    """

    def __init__(self, object_dir):
        self.object_dir = object_dir


class MoodleCourse(MoodleObject):
    def __init__(self, object_dir):
        super().__init__(object_dir)
        self.settings = CourseSettings(self.object_dir, "course", "course.xml")
        self.content = CourseContent()


class MoodleSection(MoodleObject):
    def __init__(self, object_dir, section):
        super().__init__(object_dir)
        self.section = section
        self.settings = SectionSettings(self.object_dir, self.section, "section.xml")
        self.content = SectionContent()


class MoodleActivity(MoodleObject):
    def __init__(self, object_dir, activity):
        super().__init__(object_dir)
        self.activity = activity
        self.settings = ActivitySettings(self.object_dir, self.activity, "module.xml")
        self.content = ActivityContent()
