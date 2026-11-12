from pydantic import BaseModel, Field, ConfigDict


class MeetingCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100
    )
    transcript: str = Field(
        min_length=20,
        max_length=5000
    )


class MeetingResponse(MeetingCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
