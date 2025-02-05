from functools import lru_cache

import markdown


def to_title(string: str) -> str:
    return string.replace("_", " ").title()


def from_title(string: str) -> str:
    return string.replace(" ", "_").lower()


# Convert markdown to HTML with caching
@lru_cache(maxsize=100)
def markdown_to_html(content: str) -> str:
    # Strip whitespace from the beginning and end of the content
    content = content.strip()
    # Remove multiple consecutive newlines, replacing them with a single newline
    content = "\n".join(line for line in content.splitlines() if line.strip())
    # Convert to HTML with additional extensions for better formatting
    html = markdown.markdown(
        text=content,
        extensions=["fenced_code", "tables", "nl2br"],
        output_format="html",
    )

    return html
