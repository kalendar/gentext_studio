from dataclasses import dataclass, field
from pathlib import Path
from typing import Type


@dataclass
class Topic:
    name: str
    context: str
    objectives: str


@dataclass
class Activity:
    name: str
    prompt: str
    description: str


@dataclass
class Course:
    path: Path
    name: str
    description: str
    system_prompt: str
    topics: dict[str, Topic] = field(default_factory=dict)
    activities: dict[str, Activity] = field(default_factory=dict)


@dataclass
class Library:
    courses: dict[str, Course] = field(default_factory=dict)

    def get_course(self, course_name: str) -> Course | None:
        return self.courses.get(course_name)

    def get_topic(self, course_name: str, topic_name: str) -> Topic | None:
        course = self.get_course(course_name)

        if course:
            return course.topics.get(topic_name)

        return None

    def get_activity(self, course_name: str, activity_name: str) -> Activity | None:
        course = self.get_course(course_name)

        if course:
            return course.activities.get(activity_name)

        return None

    def generate_prompt(
        self,
        course_name: str,
        topic_name: str,
        activity_name: str,
    ) -> str | None:
        "prompt objectives content"
        course = self.courses.get(course_name)
        if course is None:
            return

        topic = course.topics.get(topic_name)
        if topic is None:
            return

        activity = course.activities.get(activity_name)
        if activity is None:
            return

        return f"""
{activity.prompt}
<context>{topic.context}</context>
<objectives>{topic.objectives}</objectives>
        """


def create_library(path: Path):
    library = Library()
    course_paths = [
        course_path for course_path in path.iterdir() if course_path.is_dir()
    ]

    print(course_paths)

    for course_path in course_paths:
        course_name = course_path.name
        system_prompt_path = course_path / "system_prompt.md"
        description_path = course_path / "description.md"

        if not (system_prompt_path.exists() and system_prompt_path.is_file()):
            continue

        if not (description_path.exists() and description_path.is_file()):
            continue

        library.courses.update(
            {
                course_name: Course(
                    name=course_name,
                    path=course_path,
                    system_prompt=open(
                        system_prompt_path, "r", encoding="utf-8"
                    ).read(),
                    description=open(description_path, "r", encoding="utf-8").read(),
                )
            }
        )

    course_parser(library=library)

    return library


def course_parser(library: Library) -> None:
    for course in library.courses.values():
        topics_dir = course.path / "topics"
        topic_file_dictionary: dict[str, Path] = dict()

        [
            topic_file_dictionary.update({path.name: path})
            for path in topics_dir.iterdir()
            if path.is_file()
        ]

        activity_dir = course.path / "activities"
        activity_file_dictionary: dict[str, Path] = dict()

        [
            activity_file_dictionary.update({path.name: path})
            for path in activity_dir.iterdir()
            if path.is_file()
        ]

        file_pair_parser(
            primary_content_type="context",
            secondary_content_type="objectives",
            file_dictionary=topic_file_dictionary,
            course=course,
            type_=Topic,
        )

        file_pair_parser(
            primary_content_type="prompt",
            secondary_content_type="description",
            file_dictionary=activity_file_dictionary,
            course=course,
            type_=Activity,
        )


def file_pair_parser(
    primary_content_type: str,
    secondary_content_type: str,
    file_dictionary: dict[str, Path],
    course: Course,
    type_: Type[Activity | Topic],
) -> None:
    for key in file_dictionary.keys():
        parts = key.split("_")
        name = "_".join(parts[:-1])
        content_type = parts[-1].lower()

        if content_type == f"{primary_content_type.lower()}.md":
            primary_content_path = file_dictionary.get(key)
            secondary_content_path = file_dictionary.get(
                f"{name}_{secondary_content_type.lower()}.md", None
            )

            if secondary_content_path is None or primary_content_path is None:
                continue

            data = type_(
                name,
                open(primary_content_path, "r", encoding="utf-8").read(),
                open(secondary_content_path, "r", encoding="utf-8").read(),
            )

            if isinstance(data, Topic):
                course.topics.update({name: data})
            else:
                course.activities.update({name: data})
