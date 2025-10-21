import os
from lxml import etree


class QuestionBank:
    def __init__(self, course_dir):
        self.course_dir = course_dir
        self.xml_root = self.__get_xml_root()
        self.categories = self.get_categories()
        self.questions = self.get_questions_last_version()

    def __str__(self):

        string = f"The question bank contains : {len(self.categories)} categories and {len(self.questions)} questions\n"
        string += f'Categories:\n'
        for key, value in self.categories.items():
            string += f"Category ID: {key}; Name: {value[0]}; Parent Category ID: {value[1]}\n"

        string += f'Questions:\n'
        for question in self.questions.items():
            string += f"{question[1]}\n"

        return f'{string}'

    def __get_xml_root(self):
        course_xml_name = os.path.join(self.course_dir, "questions.xml")
        xml = etree.parse(course_xml_name)
        xml_root = xml.getroot()

        return xml_root

    def get_categories(self):
        categories = {}

        for category in self.xml_root.findall('question_category'):
            category_id = category.get('id')
            category_name = category.find('name').text
            category_parent = category.find('parent').text
            categories[category_id] = (category_name, category_parent)

        return categories

    def get_questions_last_version(self):
        questions = {}

        for category in self.xml_root.findall('question_category'):
            question_bank_entries = category.find('question_bank_entries')
            if question_bank_entries is not None:
                for question_bank_entry in question_bank_entries:
                    q = Question()
                    q.category_id = question_bank_entry.find('questioncategoryid').text
                    question_version = question_bank_entry.find('question_version')
                    question_last_version = question_version.findall('question_versions')[-1]
                    question = question_last_version.find('questions').find('question')
                    q.question_id = question.get('id')
                    q.question_name = question.find('name').text
                    questions[q.question_id] = q
        return questions


class Question:
    def __init__(self, question_id=-1, category_id=-1, question_name=""):
        self.category_id = category_id
        self.question_id = question_id
        self.question_name = question_name

    def __str__(self):
        string = (f"Category ID: {self.category_id}; "
                  f"Question ID: {self.question_id}; "
                  f"Question Name: {self.question_name}")

        return f'{string}'
