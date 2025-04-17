from typing import Optional

from pydantic import BaseModel, Field


class RequestSession(BaseModel):
    user_email: Optional[str] = Field(default=None)
    user_authorizer: Optional[str] = Field(default=None)
