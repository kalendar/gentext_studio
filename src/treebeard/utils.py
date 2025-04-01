from functools import lru_cache

import markdown2  # type: ignore
import nh3
from markupsafe import Markup


@lru_cache(maxsize=100)
def markdown_to_html(content: str | Markup) -> str | Markup:
    if isinstance(content, Markup):
        return content

    content = content.strip()

    content = "\n".join(line for line in content.splitlines() if line.strip())

    html = nh3.clean(
        markdown2.markdown(  # type: ignore
            text=content,
            extras=["fenced-code-blocks", "tables", "strike"],
        )
    )

    return html
