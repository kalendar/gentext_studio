from typing import Literal

from pydantic import BaseModel, Field

from treebeard.utils import token_estimate


class GroqModel(BaseModel):
    display_name: str
    key: str
    developer: str
    input_token_price: float = Field(gt=0, description="Per 1 mil. tokens.")
    output_token_price: float = Field(gt=0, description="Per 1 mil. tokens.")

    def price_of_string(self, string: str) -> float:
        return self.price_of_tokens(tokens=token_estimate(string=string))

    def price_of_tokens(self, tokens: int) -> float:
        return tokens * (self.input_token_price / 1_000_000)


# https://console.groq.com/docs/models
# "Production" models only
GroqModels = Literal[
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-guard-3-8b",
    "llama3-70b-8192",
    "llama3-8b-8192",
]

GROQ_MODELS: dict[GroqModels, GroqModel] = {
    "gemma2-9b-it": GroqModel(
        display_name="Gemma 2 9B 8k",
        key="gemma2-9b-it",
        developer="Google",
        input_token_price=0.2,
        output_token_price=0.2,
    ),
    "llama-3.3-70b-versatile": GroqModel(
        display_name="Llama 3.3 70B Versatile 128k",
        key="llama-3.3-70b-versatile",
        developer="Meta",
        input_token_price=0.59,
        output_token_price=0.79,
    ),
    "llama-3.1-8b-instant": GroqModel(
        display_name="Llama 3.1 8B Instant 128k",
        key="llama-3.1-8b-instant",
        developer="Meta",
        input_token_price=0.05,
        output_token_price=0.08,
    ),
    "llama-guard-3-8b": GroqModel(
        display_name="Llama Guard 3 8B 8k",
        key="llama-guard-3-8b",
        developer="Meta",
        input_token_price=0.2,
        output_token_price=0.2,
    ),
    "llama3-70b-8192": GroqModel(
        display_name="Llama 3 70B 8k",
        key="llama3-70b-8192",
        developer="Meta",
        input_token_price=0.59,
        output_token_price=0.79,
    ),
    "llama3-8b-8192": GroqModel(
        display_name="Llama 3 8B 8k",
        key="llama3-8b-8192",
        developer="Meta",
        input_token_price=0.05,
        output_token_price=0.08,
    ),
}
