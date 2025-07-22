[⬅Back](/README.md)

## Development Installation

Prerequisite: [Groq](https://console.groq.com/keys)

GenText Studio currently uses the Groq API for its integrated chat. In the future, GenTex Studio will support local models for the integrated chat as well.

### [uv](https://github.com/astral-sh/uv) (Recommended)

Prerequisites: [uv](https://github.com/astral-sh/uv) and [tailwindcss/cli](https://tailwindcss.com/docs/installation/tailwind-cli).

1. Clone this repo and enter the root directory.
2. Set environment variables, either in the terminal or in a `.env` file in the root directory.

Example env:

```sh
treebeard_sqlite_database_path = "ab\path\to\db.db"
treebeard_groq_api_key = "groq_key"
treebeard_groq_model = "llama-3.3-70b-versatile"
```

3. Run `dev.[ps1|sh]` in the root directory.

### pip (Alternative)

Prerequisites: Python 3.13

1. Clone this repo and enter the root directory.
2. Run `python -m venv .venv` in the root directory.
3. Enter the python venv with either `.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on Unix.
4. Run `pip install -r requirements.txt`.
5. Set environment variables, either in the terminal or in a `.env` file in the root directory.

Example env:

```sh
treebeard_sqlite_database_path = "ab\path\to\db.db"
treebeard_groq_api_key = "groq_key"
treebeard_groq_model = "llama-3.3-70b-versatile"
```

6. Run `fastapi dev .\src\treebeard\`.
