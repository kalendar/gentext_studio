import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv

# Load environment variables
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from groq import Groq

from models import Library, create_library
from utils import from_title, markdown_to_html, to_title

load_dotenv()

# Create groq client
__groq_api_key: str | None = os.getenv("GROQ_API_KEY", None)
if __groq_api_key is None:
    raise ValueError("No GROQ_API_KEY environment variable!")

__groq_client: Groq = Groq(api_key=__groq_api_key)


# Create library
__course_path: str | None = os.getenv("COURSES_PATH", None)
if __course_path is None:
    # Default courses path
    __course_path = "courses"

__library: Library | None = create_library(Path(__course_path))


# Create template environment
__templates = Jinja2Templates(directory="templates")
__templates.env.globals.update(  # type: ignore
    {
        "to_title": to_title,
        "from_title": from_title,
        "markdown_to_html": markdown_to_html,
    }
)


async def __get_groq_client():
    global __groq_client
    return __groq_client


async def __get_library():
    global __library
    return __library


async def __get_templates():
    global __templates
    return __templates


GroqClientDep = Annotated[Groq, Depends(__get_groq_client)]
LibraryDep = Annotated[Library, Depends(__get_library)]
TemplatesDep = Annotated[Jinja2Templates, Depends(__get_templates)]
