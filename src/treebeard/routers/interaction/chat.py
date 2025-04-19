import json
import uuid
from datetime import datetime

from fastapi import Form, Request
from fastapi.responses import RedirectResponse
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
from treebeard.dependencies import (
    GroqClient,
    ReadSession,
    Templates,
    WriteSession,
    get_current_user,
)
from treebeard.settings import SETTINGS

router = APIRouter(prefix="/learning/chat")


@router.get("/textbook/{textbook_guid}/topic/{topic_guid}/activity{activity_guid}")
async def get_chat(
    request: Request,
    textbook_guid: uuid.UUID,
    topic_guid: uuid.UUID,
    activity_guid: uuid.UUID,
    templates: Templates,
    groq_client: GroqClient,
    read_session: ReadSession,
    write_session: WriteSession,
    chat_guid: uuid.UUID | None = None,
):
    current_user = await get_current_user(request=request, session=write_session)

    if not current_user or not current_user.chat_whitelisted:
        return RedirectResponse(request.url_for("root"))

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
            guid=uuid.uuid4(),
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

        if chat_completion.usage and chat_completion.usage.total_tokens:
            current_user.used_tokens += chat_completion.usage.total_tokens

    write_session.add(chat)
    write_session.add(current_user)

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
    current_user = await get_current_user(request=request, session=write_session)

    if (
        not current_user
        or not current_user.chat_whitelisted
        or current_user.used_tokens > SETTINGS.groq_max_tokens_per_user
    ):
        return templates.TemplateResponse(
            request=request,
            name="interaction/chat/messages.jinja",
            context={
                "messages": [
                    AssistantMessage(
                        content="You've hit the trial limit! Thank you for trying out GOLE Studio!"
                    )
                ],
            },
        )

    chat = get_chat_object(session=write_session, guid=chat_guid)

    if chat is None:
        raise ValueError(f"No chat with GUID: {chat_guid}.")

    messages = json.loads(chat.chat_data.model_dump_json())["messages"]

    messages.append({"role": "user", "content": message})

    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model=SETTINGS.groq_model,
    )

    assistant_response = chat_completion.choices[0].message.content
    if assistant_response is None:
        raise ValueError("No response from Groq!")

    new_messages: list[UserMessage | AssistantMessage] = [
        UserMessage(content=message),
        AssistantMessage(content=assistant_response),
    ]

    new_data = chat.chat_data.model_copy(deep=True)
    new_data.messages.extend(new_messages)
    chat.chat_data = new_data

    if chat_completion.usage and chat_completion.usage.total_tokens:
        current_user.used_tokens += chat_completion.usage.total_tokens

    write_session.add(chat)
    write_session.add(current_user)

    return templates.TemplateResponse(
        request=request,
        name="interaction/chat/messages.jinja",
        context={
            "messages": new_messages,
        },
    )
