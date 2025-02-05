[⬅Back](/README.md)
## Development Installation
### [uv](https://github.com/astral-sh/uv) (Recommended)
1. Clone this repo and enter the root directory.
2. Run `uv sync` in the root directory.
3. Enter the python venv with either `.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on Unix.
4. Set the `GROQ_API_KEY` environment variable, either in the terminal or in a `.env` file in the root directory.
4. Run `fastapi dev`.

### pip (Alternative)
Prerequisite - Python 3.13
1. Clone this repo and enter the root directory.
2. Run `python -m venv .venv` in the root directory.
3. Enter the python venv with either `.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on Unix.
4. Run `pip install -r requirements.txt`.
5. Set the `GROQ_API_KEY` environment variable, either in the terminal or in a `.env` file in the root directory.
6. Run `fastapi dev`.