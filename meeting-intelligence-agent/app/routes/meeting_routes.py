from fastapi import APIRouter, status

from app.models.meeting import MeetingCreate

from app.services.meeting_service import (
    create_meeting,
    get_all_meetings,
    get_meeting_by_id,
    update_meeting,
    delete_meeting,
    search_meeting
)

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_meeting( meeting: MeetingCreate ):
    return create_meeting(meeting)


@router.get("/")
def get_meetings():
    return get_all_meetings()


@router.get("/search/")
def search_meetings( keyword: str ):
    return search_meeting(keyword)


@router.get("/{meeting_id}")
def get_meeting(meeting_id: int):
    return get_meeting_by_id(meeting_id)


@router.put("/{meeting_id}")
def update_existing_meeting(meeting_id: int, meeting: MeetingCreate):
    return update_meeting(
        meeting_id,
        meeting
    )


@router.delete("/{meeting_id}")
def delete_existing_meeting(
    meeting_id: int
):
    return delete_meeting(meeting_id)