import logging
import os
from functools import lru_cache

import markdown
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from groq import Groq

from models.template_system import TemplateSystem

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
template_system = TemplateSystem()

# Initialize conversation history
conversation_history = {}

# Add a constant for the model name
GROQ_MODEL = "llama-3.1-8b-instant"


# Convert markdown to HTML with caching
@lru_cache(maxsize=100)
def markdown_to_html(content: str) -> str:
    return markdown.markdown(content, extensions=["fenced_code", "tables"])


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    course_id: str = None,
    topic_id: str = None,
    activity_id: str = None,
):
    try:
        # If all parameters are provided, generate prompt and start chat
        if all([course_id, topic_id, activity_id]):
            logger.debug("Generating prompt for chat")
            initial_prompt = template_system.generate_prompt(
                course_id, topic_id, activity_id
            )

            # Get the topic text
            topic = template_system.get_topic(course_id, topic_id)
            topic_text = (
                topic.get_description(template_system.file_reader) if topic else ""
            )

            # Combine topic and activity text
            if topic_text:
                initial_prompt = f"Topic: {topic_text}\n\n{initial_prompt}"

            if initial_prompt:
                # Initialize conversation with system prompt
                conversation_key = f"{course_id}_{topic_id}_{activity_id}"
                conversation_history[conversation_key] = [
                    {"role": "system", "content": initial_prompt}
                ]

                # Get first response from AI
                chat_completion = groq_client.chat.completions.create(
                    messages=conversation_history[conversation_key],
                    model=GROQ_MODEL,
                )
                initial_response = chat_completion.choices[0].message.content

                # Add AI's response to conversation history
                conversation_history[conversation_key].append(
                    {"role": "assistant", "content": initial_response}
                )

                return templates.TemplateResponse(
                    "chat.html",
                    {
                        "request": request,
                        "initial_prompt": initial_response,
                        "course_id": course_id,
                        "topic_id": topic_id,
                        "activity_id": activity_id,
                        "markdown_to_html": markdown_to_html,
                    },
                )
            raise HTTPException(status_code=404, detail="Invalid parameters")

        # Get selected course if course_id is provided
        selected_course = template_system.get_course(course_id) if course_id else None
        logger.debug(f"Selected course: {selected_course}")
        selected_topic = (
            template_system.get_topic(course_id, topic_id)
            if course_id and topic_id
            else None
        )
        logger.debug(f"Selected topic: {selected_topic}")
        selected_activity = (
            template_system.get_activity(course_id, activity_id)
            if course_id and activity_id
            else None
        )
        logger.debug(f"Selected activity: {selected_activity}")

        context = {
            "request": request,
            "courses": template_system.courses,
            "selected_course": selected_course,
            "selected_topic": selected_topic,
            "selected_activity": selected_activity,
            "course_id": course_id,
            "topic_id": topic_id,
            "activity_id": activity_id,
            "markdown_to_html": markdown_to_html,
            "template_system": template_system,
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
    course_id: str = Form(...),
    topic_id: str = Form(...),
    activity_id: str = Form(...),
):
    try:
        logger.debug(f"Received message: {message}")

        conversation_key = f"{course_id}_{topic_id}_{activity_id}"

        # Initialize conversation history if it doesn't exist
        if conversation_key not in conversation_history:
            conversation_history[conversation_key] = [
                {
                    "role": "system",
                    "content": template_system.generate_prompt(
                        course_id, topic_id, activity_id
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
