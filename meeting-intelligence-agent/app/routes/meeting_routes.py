from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.meeting import MeetingCreate, MeetingResponse
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


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_new_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    return create_meeting(db, meeting)


@router.get("/", response_model=List[MeetingResponse])
def get_meetings(db: Session = Depends(get_db)):
    return get_all_meetings(db)


@router.get("/search/", response_model=List[MeetingResponse])
def search_meetings(keyword: str, db: Session = Depends(get_db)):
    return search_meeting(db, keyword)


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    return get_meeting_by_id(db, meeting_id)


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_existing_meeting(meeting_id: int, meeting: MeetingCreate, db: Session = Depends(get_db)):
    return update_meeting(db, meeting_id, meeting)


@router.delete("/{meeting_id}")
def delete_existing_meeting(meeting_id: int, db: Session = Depends(get_db)):
    return delete_meeting(db, meeting_id)
