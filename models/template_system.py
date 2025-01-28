from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel


class FileContent:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def read_file(self, file_path: str) -> str:
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_text()


class Activity(BaseModel):
    name: str
    description_file: str
    prompt_template_file: str
    _description: Optional[str] = None
    _prompt_template: Optional[str] = None

    def get_description(self, file_reader: FileContent) -> str:
        if self._description is None:
            self._description = file_reader.read_file(self.description_file)
        return self._description

    def get_prompt_template(self, file_reader: FileContent) -> str:
        if self._prompt_template is None:
            self._prompt_template = file_reader.read_file(self.prompt_template_file)
        return self._prompt_template

    def generate_prompt(
        self, file_reader: FileContent, course_name: str, topic_name: str
    ) -> str:
        template = self.get_prompt_template(file_reader)
        return template.format(course_name=course_name, topic_name=topic_name)


class Topic(BaseModel):
    name: str
    description_file: str
    _description: Optional[str] = None

    def get_description(self, file_reader: FileContent) -> str:
        if self._description is None:
            self._description = file_reader.read_file(self.description_file)
        return self._description


class Course(BaseModel):
    name: str
    description_file: str
    topics: Dict[str, Topic]
    activities: Dict[str, Activity]
    _description: Optional[str] = None

    def get_description(self, file_reader: FileContent) -> str:
        if self._description is None:
            self._description = file_reader.read_file(self.description_file)
        return self._description


class TemplateSystem:
    def __init__(self, config_path: str = "templates/courses.yaml"):
        self.base_path = Path(config_path).parent
        self.file_reader = FileContent(self.base_path)

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            self.courses: Dict[str, Course] = {
                k: Course(**v) for k, v in config["courses"].items()
            }

    def get_course(self, course_id: str) -> Optional[Course]:
        return self.courses.get(course_id)

    def get_topic(self, course_id: str, topic_id: str) -> Optional[Topic]:
        course = self.get_course(course_id)
        if course:
            return course.topics.get(topic_id)
        return None

    def get_activity(self, course_id: str, activity_id: str) -> Optional[Activity]:
        course = self.get_course(course_id)
        if course:
            return course.activities.get(activity_id)
        return None

    def generate_prompt(
        self, course_id: str, topic_id: str, activity_id: str
    ) -> Optional[str]:
        course = self.get_course(course_id)
        topic = self.get_topic(course_id, topic_id)
        activity = self.get_activity(course_id, activity_id)

        if all([course, topic, activity]):
            return activity.generate_prompt(self.file_reader, course.name, topic.name)
        return None
