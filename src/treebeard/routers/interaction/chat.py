import json
import uuid
from datetime import datetime

from fastapi import Form, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from treebeard.database.chat import (
    AssistantMessage,
    Chat,
    ChatMessages,
    SystemMessage,
    UserMessage,
)
from treebeard.database.queries import get_chat as get_chat_object
from treebeard.database.queries import get_textbook
from treebeard.dependencies import GroqClient, ReadSession, Templates, WriteSession
from treebeard.settings import SETTINGS

router = APIRouter(prefix="/chat")


@router.get("/textbook/{textbook_guid}/topic/{topic_guid}/activity{activity_guid}")
async def get_chat(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    topic_guid: uuid.UUID,
    activity_guid: uuid.UUID,
    templates: Templates,
    groq_client: GroqClient,
    write_session: WriteSession,
    chat_guid: uuid.UUID | None = None,
) -> HTMLResponse:
    textbook = get_textbook(session=read_session, guid=textbook_guid)
    topic = next(
        filter(lambda topic: topic.guid == topic_guid, list(textbook.topics)), None
    )
    if topic is None:
        raise ValueError(
            f"No topic with GUID: {topic_guid} found for textbook with GUID: {textbook_guid}"
        )

    activity = next(
        filter(lambda activity: activity.guid == activity_guid, list(topic.activities)),
        None,
    )
    if activity is None:
        raise ValueError(
            f"No activity with GUID: {activity_guid} found for topic with GUID: {topic_guid}"
        )

    chat: Chat | None = None

    if chat_guid is not None:
        chat = get_chat_object(session=write_session, guid=chat_guid)

    if chat is None:
        initial_prompt = f"""
{activity.prompt}
<content>{topic.summary}</content>
<outcomes>{topic.outcomes}</outcomes>
"""

        chat = Chat(
            textbook_guid=textbook_guid,
            topic_guid=topic_guid,
            activity_guid=activity_guid,
            start_time=datetime.now(),
            chat_data=ChatMessages(
                messages=[
                    SystemMessage(content=initial_prompt),
                ]
            ),
        )

        chat_completion = groq_client.chat.completions.create(
            messages=json.loads(chat.chat_data.model_dump_json())["messages"],
            model=SETTINGS.groq_model,
        )

        initial_response = chat_completion.choices[0].message.content
        if initial_response is None:
            raise ValueError("No response from Groq!")

        chat.chat_data.messages.append(AssistantMessage(content=initial_response))

    write_session.add(chat)
    write_session.flush([chat])

    return templates.TemplateResponse(
        request=request,
        name="interaction/chat/chat.jinja",
        context={
            "chat_guid": chat.guid,
            "activity_guid": activity_guid,
            "topic_guid": topic_guid,
            "textbook_guid": textbook_guid,
            "messages": chat.chat_data.messages,
        },
    )


@router.post("/post")
async def post_chat(
    request: Request,
    templates: Templates,
    write_session: WriteSession,
    groq_client: GroqClient,
    message: str = Form(),
    chat_guid: uuid.UUID = Form(),
):
    chat = get_chat_object(session=write_session, guid=chat_guid)

    if chat is None:
        raise ValueError(f"No chat with GUID: {chat_guid}.")

    messages = json.loads(chat.chat_data.model_dump_json())["messages"]

    messages.append({"role": "user", "content": message})

    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model=SETTINGS.groq_model,
    )

    initial_response = chat_completion.choices[0].message.content
    if initial_response is None:
        raise ValueError("No response from Groq!")

    new_messages: list[UserMessage | AssistantMessage] = [
        UserMessage(content=message),
        AssistantMessage(content=initial_response),
    ]

    new_data = chat.chat_data.model_copy(deep=True)
    new_data.messages.extend(new_messages)
    chat.chat_data = new_data

    write_session.add(chat)

    return templates.TemplateResponse(
        request=request,
        name="interaction/chat/messages.jinja",
        context={
            "messages": new_messages,
        },
    )
