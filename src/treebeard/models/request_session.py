from typing import Optional

from pydantic import BaseModel, Field

from treebeard.groq_utils import GroqModels
from treebeard.settings import SETTINGS


class RequestSession(BaseModel):
    user_email: Optional[str] = Field(default=None)
    user_authorizer: Optional[str] = Field(default=None)
    user_model: GroqModels = Field(default=SETTINGS.groq_model)
