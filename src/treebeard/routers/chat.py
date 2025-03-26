from typing import Annotated

from fastapi import Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from groq.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from groq.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)

from dependencies import GroqClientDep, LibraryDep, TemplatesDep

router = APIRouter(prefix="/chat")

# Initialize conversation history
# TODO Make non-global
conversation_history: dict[str, list[ChatCompletionMessageParam]] = {}

# Add a constant for the model name
# TODO move to optional env var
GROQ_MODEL = "llama-3.3-70b-versatile"


@router.get("/{course_name}/{topic_name}/{activity_name}", response_model=None)
async def chat(
    request: Request,
    library: LibraryDep,
    templates: TemplatesDep,
    groq_client: GroqClientDep,
    course_name: str,
    topic_name: str,
    activity_name: str,
) -> HTMLResponse:
    initial_prompt = library.generate_prompt(course_name, topic_name, activity_name)

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

        initial_response = chat_completion.choices[0].message.content
        if initial_response is None:
            raise ValueError("No response from Groq!")

        initial_response = initial_response.strip()

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
            },
        )
    raise HTTPException(status_code=404, detail="Invalid parameters")


@router.post("/", response_model=None)
async def chat_post(
    request: Request,
    library: LibraryDep,
    templates: TemplatesDep,
    groq_client: GroqClientDep,
    message: Annotated[str, Form()],
    course_name: Annotated[str, Form()],
    topic_name: Annotated[str, Form()],
    activity_name: Annotated[str, Form()],
) -> HTMLResponse:
    global conversation_history, GROQ_MODEL

    try:
        conversation_key = f"{course_name}_{topic_name}_{activity_name}"

        # Initialize conversation history if it doesn't exist
        if conversation_key not in conversation_history:
            system_message = ChatCompletionSystemMessageParam(
                content=library.generate_prompt(course_name, topic_name, activity_name),
                role="system",
            )

            conversation_history[conversation_key] = [system_message]

        # Add user message to history
        conversation_history[conversation_key].append(
            {"role": "user", "content": message}
        )

        # Get chat completion from Groq with max tokens limit
        chat_completion = groq_client.chat.completions.create(
            messages=conversation_history[conversation_key],
            model=GROQ_MODEL,
            max_tokens=500,
            temperature=0.7,
        )

        # Extract the response
        ai_response = chat_completion.choices[0].message.content

        # Add AI response to history
        conversation_history[conversation_key].append(
            {"role": "assistant", "content": ai_response}
        )

        return templates.TemplateResponse(
            "chat_messages.html",
            {
                "request": request,
                "user_message": message,
                "ai_response": ai_response,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
