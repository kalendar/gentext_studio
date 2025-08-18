import re
from functools import lru_cache
from math import ceil

import markdown2  # type: ignore
import nh3
from leaflock.sqlalchemy_tables import Activity, Topic
from markupsafe import Markup


@lru_cache(maxsize=100)
def markdown_to_html(content: str | Markup) -> str | Markup:
    if isinstance(content, Markup):
        return content

    content = content.strip()

    content = "\n\n".join(line for line in content.splitlines() if line.strip())

    html = nh3.clean(
        markdown2.markdown(  # type: ignore
            text=content,
            extras=["fenced-code-blocks", "tables", "strike"],
        )
    )

    return html


def striptags(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    # Simple regex to remove HTML tags
    return re.sub(r"<[^>]+>", "", text)


def truncate(text: str, length: int = 80, end: str = "...") -> str:
    """Truncate text to specified length."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[: length - len(end)] + end


def initial_prompt(topic: Topic, activity: Activity) -> str:
    return f"""
{activity.prompt}
<content>{topic.summary}</content>
<outcomes>{topic.outcomes}</outcomes>
"""


def token_estimate(string: str) -> int:
    word_count: int = 0
    lines = string.strip().split("\n")

    for line in lines:
        word_count += len([word for word in line.split(" ") if word])

    return ceil(word_count * 0.75)
