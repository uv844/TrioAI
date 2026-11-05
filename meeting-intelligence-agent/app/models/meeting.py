from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=100
    )

    transcript: str = Field(
        min_length=20,
        max_length=5000
    )