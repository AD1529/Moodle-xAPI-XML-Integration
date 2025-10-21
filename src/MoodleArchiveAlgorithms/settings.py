import os
import ipywidgets.widgets as widgets
from lxml import etree
from src.MoodleArchiveAlgorithms.availability import Availability
from datetime import datetime


class MoodleObjectSettings:
    def __init__(self, object_dir, folder, xmlfile):
        self.object_dir = object_dir  # path of the object directory
        self.folder = folder  # folder inside the directory
        self.xmlfile = xmlfile  # name of the xml file
        self.xml_root = self.__get_xml_root()  # root of the xml file

    def __get_xml_root(self):
        """ Return the root of the xml file """
        xml_name = os.path.join(self.object_dir, self.folder, self.xmlfile)
        xml = etree.parse(xml_name)
        xml_root = xml.getroot()
        return xml_root


class CourseSettings(MoodleObjectSettings):
    """
    The settings correspond to the *Setting* menu in a Moodle course.
    They are extracted from the archive in the `course` folder.
    To retrieve their values from an archive, simply browse the `course.xml` file at the root of the archive.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.courseid = int(self.xml_root.get("id"))
        self.name = self.xml_root.find("fullname").text
        self.visible = self.xml_root.find("visible").text == '1'  # visible: 1, hidden: 0
        self.shortname = self.xml_root.find("shortname").text
        self.contextid = self.xml_root.get("contextid")
        self.idnumber = self.xml_root.find("idnumber").text
        self.summary = self.xml_root.find("summary").text
        self.format = self.xml_root.find("format").text
        self.startdate = datetime.fromtimestamp(int(self.xml_root.find("startdate").text))
        self.enddate = datetime.fromtimestamp(int(self.xml_root.find("enddate").text))

    def __str__(self):
        return f"""
        courseid : {self.courseid}
        name : {self.name}
        visible : {self.visible}
        contextid : {self.contextid}
        idnumber : {self.idnumber}
        format : {self.format}
        startdate : {self.startdate}
        enddate : {self.enddate}"""


class SectionSettings(MoodleObjectSettings):
    """
    This Section folder includes a set of subfolders whose name follows the format section_sectionId. The inforef.xml file
    indicates which files are contained in a specific section and in what order. The section.xml file provides
    information on the section number, name, description (if any), whether it is visible (a section, like a module,
    can be hidden from students), the cmids in the order in which they appear, and any access restrictions. Depending on
    the course format, additional information can be stored in this file. For example, in the Flexible sections and
    Grid formats, the tags <name> and <value> allows reconstructing the nested structure of the course.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.sectionid = self.xml_root.get("id")
        self.name = self.get_section_name()
        self.visible = self.xml_root.find("visible").text == '1'  # visible: 1, hidden: 0
        self.number = int(self.xml_root.find("number").text)
        self.summary = self.xml_root.find("summary").text
        self.sequence = self.add_sequence()
        self.availability = Availability(self.xml_root.find("availabilityjson").text)
        self.parent_section_number = self.add_parent_section_number()
        self.is_chapter = self.add_is_chapter()
        self.sub_sections = []  # filled through moodle_archive.add_subsections()
        self.depth = 0  # TODO Yves
        self.chapterString = ""  # TODO Yves

    def get_section_name(self):
        name = self.xml_root.find("name").text
        if name == '$@NULL@$' or name is None:
            return 'General'

        return name

    def add_sequence(self):
        sequence = self.xml_root.find("sequence").text
        if sequence:
            return ['activity_' + i for i in sequence.split(',')]

        return []

    def add_parent_section_number(self):

        parent_section_number = -1
        if self.xml_root.find("course_format_options") is not None:
            for option in self.xml_root.findall("course_format_options"):
                # course format: flexible sections / # course format: onetopic
                if option.find("name").text == "parent" or option.find("name").text == "level":
                    parent_section_number = int(option.find("value").text)

        return parent_section_number

    def add_is_chapter(self):
        is_chapter = False
        if self.parent_section_number == 0 or self.parent_section_number == -1:
            is_chapter = widgets.Checkbox(
                value=True,
                description=self.name,
                disabled=False)

        return is_chapter

    def __str__(self):
        return f"""
        sectionid : {self.sectionid}
        name : {self.name}
        visible : {self.visible}
        number : {self.number}
        summary : {self.summary}
        sequence : {self.sequence}
        parent_section_number : {self.parent_section_number}
        sub_sections : {self.sub_sections}
        availability : {self.availability}"""


class ActivitySettings(MoodleObjectSettings):
    """
    The Activity folder contains a set of folders representing all the resources and activities modules of the course.
    Each folder in turn is named according to the format moduleType_courseModuleId. For example, ‘assign_2817’
    represents the assignment with course module id (cmid) 2817. Please note that cmids are sequentially assigned in
    the entire platform according to the datetime of creation. Hence missing numbers do not represent deleted modules,
    but modules stored in other courses. The folder of each module contains in turn a set of XML files that depends on
    the module type.
    """

    def __init__(self, *args):
        super().__init__(*args)

        # from module.xml
        self.visible = self.xml_root.find("visible").text == '1'  # visible: 1, hidden: 0
        self.moduleid = self.xml_root.get("id")
        self.activitytype = self.xml_root.find("modulename").text
        self.sectionid = self.xml_root.find("sectionid").text
        self.sectionnumber = int(self.xml_root.find("sectionnumber").text)
        self.completion = self.xml_root.find("completion").text
        self.availability = Availability(self.xml_root.find("availability").text)

        # from activitytype.xml
        self.activitytype_xmlroot = self.get_from_type_xml(self.object_dir, self.folder)
        self.contextid = self.activitytype_xmlroot.get("./" + self.activitytype + "/contextid")
        self.intro = self.activitytype_xmlroot.find("./" + self.activitytype + "/intro").text
        self.activityid = self.activitytype_xmlroot.get("id")
        self.name = self.activitytype_xmlroot.find("./" + self.activitytype + "/name").text
        if self.moduleid != self.activitytype_xmlroot.get("moduleid") \
                or self.activitytype != self.activitytype_xmlroot.get("modulename"):
            raise ValueError(f"inconsistency between files {self.activitytype}.xml and module.xml")

    def get_from_type_xml(self, dir_name, activity_dir_name):
        activitytype_xml_name = os.path.join(dir_name, activity_dir_name, self.activitytype + ".xml")
        xml = etree.parse(activitytype_xml_name)
        activitytype_xml_root = xml.getroot()

        return activitytype_xml_root

    def __str__(self):
        return f"""
        activityid : {self.activityid}
        name : {self.name}
        visible : {self.visible}
        moduleid : {self.moduleid}
        activitytype : {self.activitytype}
        contextid : {self.contextid}
        intro : {self.intro}
        sectionid : {self.sectionid}
        sectionnumber : {self.sectionnumber}
        completion : {self.completion}
        availability : {self.availability}"""
