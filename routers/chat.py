import logging
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
chat_manager = EnhancedChatManager(library)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info("Generating prompt for chat")
    chat_config = chat_manager.initialize_chat(course_name, topic_name, activity_name)
    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        **chat_config["model_config"]
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
        logger.info(f"Received message: {message}")

        conversation_key = f"{course_name}_{topic_name}_{activity_name}"
    
    # Get current model type from conversation metadata
        current_model_type = conversation_metadata.get(conversation_key, {}).get("model_type", ModelType.GENERAL)
    
    # Check if we should switch models
        new_model_type = chat_manager.should_update_model(message, current_model_type)
        if new_model_type:
            model_config = ModelSelector.get_model_config(new_model_type)
        # Update conversation metadata with new model type
            conversation_metadata[conversation_key]["model_type"] = new_model_type
        else:
            model_config = ModelSelector.get_model_config(current_model_type)
    
    # Use the selected model configuration
        chat_completion = groq_client.chat.completions.create(
        messages=conversation_history[conversation_key],
        **model_config
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
            },
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
