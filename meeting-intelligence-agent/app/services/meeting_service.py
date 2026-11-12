from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_db import MeetingModel
from app.models.meeting import MeetingCreate


def create_meeting(db: Session, meeting_data: MeetingCreate):
    db_meeting = MeetingModel(
        title=meeting_data.title,
        transcript=meeting_data.transcript
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def get_all_meetings(db: Session):
    return db.query(MeetingModel).all()


def get_meeting_by_id(db: Session, meeting_id: int):
    meeting = db.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    return meeting


def update_meeting(db: Session, meeting_id: int, meeting_data: MeetingCreate):
    meeting = get_meeting_by_id(db, meeting_id)
    meeting.title = meeting_data.title
    meeting.transcript = meeting_data.transcript
    db.commit()
    db.refresh(meeting)
    return meeting


def delete_meeting(db: Session, meeting_id: int):
    meeting = get_meeting_by_id(db, meeting_id)
    db.delete(meeting)
    db.commit()
    return {
        "message": "Meeting deleted successfully",
        "data": {
            "id": meeting.id,
            "title": meeting.title
        }
    }


def search_meeting(db: Session, keyword: str):
    search_pattern = f"%{keyword}%"
    return db.query(MeetingModel).filter(
        MeetingModel.title.like(search_pattern)
        | MeetingModel.transcript.like(search_pattern)
    ).all()
