from fastapi import HTTPException

from app.database.fake_db import meetings


def create_meeting(meeting_data):
    meeting_id = len(meetings) + 1

    meetings[meeting_id] = {
        "id": meeting_id,
        "title": meeting_data.title,
        "transcript": meeting_data.transcript
    }

    return meetings[meeting_id]


def get_all_meetings():
    return list(meetings.values())


def get_meeting_by_id(meeting_id: int):
    if meeting_id not in meetings:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meetings[meeting_id]


def update_meeting(meeting_id: int, meeting_data):

    if meeting_id not in meetings:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    meetings[meeting_id] = {
        "id": meeting_id,
        "title": meeting_data.title,
        "transcript": meeting_data.transcript
    }

    return meetings[meeting_id]


def delete_meeting(meeting_id: int):

    if meeting_id not in meetings:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    deleted_meeting = meetings.pop(meeting_id)

    return {
        "message": "Meeting deleted successfully",
        "data": deleted_meeting
    }


def search_meeting(keyword: str):
    results = []

    for meeting in meetings.values():

        if (
            keyword.lower() in meeting["title"].lower()
            or keyword.lower() in meeting["transcript"].lower()
        ):
            results.append(meeting)

    return results