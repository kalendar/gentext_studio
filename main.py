import logging
import os
from functools import lru_cache
from pathlib import Path

import markdown
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from groq import Groq
from groq.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from models import create_library

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize template system with caching
library = create_library(path=Path(__name__).parent / "templates/courses")

# Initialize conversation history
# TODO Make non-global
conversation_history: dict[str, list[ChatCompletionMessageParam]] = {}

# Add a constant for the model name
GROQ_MODEL = "llama-3.1-8b-instant"


# Convert markdown to HTML with caching
@lru_cache(maxsize=100)
def markdown_to_html(content: str) -> str:
    # Strip whitespace from the beginning and end of the content
    content = content.strip()
    # Remove multiple consecutive newlines, replacing them with a single newline
    content = "\n".join(line for line in content.splitlines() if line.strip())
    # Convert to HTML with additional extensions for better formatting
    html = markdown.markdown(
        content, extensions=["fenced_code", "tables", "nl2br"], output_format="html5"
    )
    # Clean up any remaining whitespace around the HTML content
    html = html.strip()
    return html


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    course_name: str | None = None,
    topic_name: str | None = None,
    activity_name: str | None = None,
):
    try:
        # If all parameters are provided, generate prompt and start chat
        if course_name and topic_name and activity_name:
            logger.debug("Generating prompt for chat")
            initial_prompt = library.generate_prompt(
                course_name, topic_name, activity_name
            )

            # Get the topic text
            topic = library.get_topic(course_name, topic_name)
            if not topic:
                raise ValueError

            if initial_prompt:
                # Initialize conversation with system prompt
                conversation_key = f"{course_name}_{topic_name}_{activity_name}"

                conversation_history.update(
                    {conversation_key: [{"role": "system", "content": initial_prompt}]}
                )

                # Get first response from AI
                messages = conversation_history.get(conversation_key)
                if not messages:
                    raise KeyError

                chat_completion = groq_client.chat.completions.create(
                    messages=messages,
                    model=GROQ_MODEL,
                )
                initial_response = chat_completion.choices[0].message.content.strip()

                # Add AI's response to conversation history
                conversation_history[conversation_key].append(
                    {"role": "assistant", "content": initial_response}
                )

                return templates.TemplateResponse(
                    "chat.html",
                    {
                        "request": request,
                        "initial_prompt": initial_response,
                        "course_name": course_name,
                        "topic_name": topic_name,
                        "activity_name": activity_name,
                        "markdown_to_html": markdown_to_html,
                    },
                )
            raise HTTPException(status_code=404, detail="Invalid parameters")

        # Get selected course if course_id is provided
        selected_course = library.get_course(course_name) if course_name else None

        logger.debug(f"Selected course: {selected_course}")

        selected_topic = (
            library.get_topic(course_name, topic_name)
            if course_name and topic_name
            else None
        )

        logger.debug(f"Selected topic: {selected_topic}")
        selected_activity = (
            library.get_activity(course_name, activity_name)
            if course_name and activity_name
            else None
        )

        logger.debug(f"Selected activity: {selected_activity}")

        context = {
            "request": request,
            "courses": library.courses,
            "selected_course": selected_course,
            "selected_topic": selected_topic,
            "selected_activity": selected_activity,
            "course_id": course_name,
            "topic_id": topic_name,
            "activity_id": activity_name,
            "markdown_to_html": markdown_to_html,
            "template_system": library,
        }

        logger.debug("Rendering template with context")
        return templates.TemplateResponse("select.html", context)

    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_class=HTMLResponse)
async def chat(
    request: Request,
    message: str = Form(...),
    course_name: str = Form(...),
    topic_name: str = Form(...),
    activity_name: str = Form(...),
):
    try:
        logger.debug(f"Received message: {message}")

        conversation_key = f"{course_name}_{topic_name}_{activity_name}"

        # Initialize conversation history if it doesn't exist
        if conversation_key not in conversation_history:
            conversation_history[conversation_key] = [
                {
                    "role": "system",
                    "content": library.generate_prompt(
                        course_name, topic_name, activity_name
                    ),
                }
            ]

        # Add user message to history
        conversation_history[conversation_key].append(
            {"role": "user", "content": message}
        )

        # Get chat completion from Groq with max tokens limit
        chat_completion = groq_client.chat.completions.create(
            messages=conversation_history[conversation_key],
            model=GROQ_MODEL,
            max_tokens=150,  # Reduced token limit
            temperature=0.7,
        )

        # Extract the response
        ai_response = chat_completion.choices[0].message.content

        # Add AI response to history
        conversation_history[conversation_key].append(
            {"role": "assistant", "content": ai_response}
        )

        logger.debug(f"Rendering template with user_message: {message}")
        logger.debug(f"Rendering template with ai_response: {ai_response}")

        return templates.TemplateResponse(
            "chat_messages.html",
            {
                "request": request,
                "user_message": message,
                "ai_response": ai_response,
                "markdown_to_html": markdown_to_html,
            },
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
