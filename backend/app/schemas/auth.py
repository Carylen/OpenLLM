from pydantic import BaseModel, Field


class CompleteOnboardingRequest(BaseModel):
    invite_code: str = Field(min_length=3, max_length=128)


class MessageResponse(BaseModel):
    message: str
