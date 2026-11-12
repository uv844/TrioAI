"""
Seeds MeetingDB with realistic, cohesive sample data matching the 3NF schema:
- Users (internal & external)
- Master Topics
- A complete Meeting with metadata
- Meeting Participants & speaking metrics
- Timestamped Transcript Segments with speaker attribution & sentiment
- AI Meeting Summary
- Action Items assigned to participants
- Key Decisions recorded
- Meeting Topics junction tags
"""
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from app.database.session import SessionLocal
from app.models.meeting_db import (
    User, Topic, MeetingModel, MeetingParticipant,
    TranscriptSegment, MeetingSummary, ActionItem, KeyDecision, MeetingTopic
)


def seed_database():
    db = SessionLocal()
    print("=" * 65)
    print("SEEDING MeetingDB WITH REALISTIC INTELLIGENCE DATA")
    print("=" * 65)

    try:
        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------
        # 1. SEED USERS / PARTICIPANTS
        # -------------------------------------------------------------
        print("[1/7] Seeding Users...")
        user_data = [
            {
                "full_name": "Sarthak Shrivastav",
                "email": "sarthak@trioai.com",
                "role_title": "AI Engineering Lead",
                "department": "Core Intelligence",
                "is_registered_user": True
            },
            {
                "full_name": "Priya Sharma",
                "email": "priya.sharma@trioai.com",
                "role_title": "Principal Product Manager",
                "department": "Product",
                "is_registered_user": True
            },
            {
                "full_name": "Alex Chen",
                "email": "alex.chen@cloudpartner.io",
                "role_title": "Solutions Architect",
                "department": "External Partner",
                "is_registered_user": False
            }
        ]

        users = []
        for u in user_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user_obj = User(**u)
                db.add(user_obj)
                db.flush()
                users.append(user_obj)
            else:
                users.append(existing)

        sarthak, priya, alex = users[0], users[1], users[2]
        print(f"      Users ready: {[u.full_name for u in users]}")

        # -------------------------------------------------------------
        # 2. SEED MASTER TOPICS
        # -------------------------------------------------------------
        print("[2/7] Seeding Master Topics...")
        topic_names = ["SSMS Integration", "FastAPI Architecture", "Vector RAG", "Q4 Roadmap", "Cloud Deployment"]
        topics = {}
        for name in topic_names:
            topic = db.query(Topic).filter(Topic.name == name).first()
            if not topic:
                topic = Topic(name=name)
                db.add(topic)
                db.flush()
            topics[name] = topic
        print(f"      Topics ready: {list(topics.keys())}")

        # -------------------------------------------------------------
        # 3. SEED COMPREHENSIVE MEETING
        # -------------------------------------------------------------
        print("[3/7] Creating Meeting Record...")
        start_time = now - timedelta(hours=2)
        end_time = now - timedelta(hours=1)

        raw_transcript_text = (
            "Priya: Welcome everyone. Today we are reviewing the SSMS SQL Server integration for Trio AI.\n"
            "Sarthak: Thanks Priya. We've normalized the schema into 9 3NF tables and verified connectivity on port 1434 with ODBC Driver 18.\n"
            "Alex: The cloud architecture looks solid. I suggest using Azure SQL managed instances once we deploy.\n"
            "Priya: Excellent. Sarthak, let's complete the API route layer by Friday, and Alex will review the cloud infrastructure specs."
        )

        meeting = MeetingModel(
            title="TrioAI Architecture & SSMS Integration Review",
            transcript=raw_transcript_text,
            scheduled_start=start_time,
            scheduled_end=end_time,
            actual_start=start_time,
            actual_end=end_time,
            status="completed",
            platform="Google Meet",
            meeting_url="https://meet.google.com/abc-trio-xyz",
            recording_url="https://storage.trioai.com/recordings/20261106-arch-review.mp4",
            raw_transcript=raw_transcript_text
        )
        db.add(meeting)
        db.flush()
        print(f"      Meeting created with ID: {meeting.id}")

        # -------------------------------------------------------------
        # 4. SEED PARTICIPANTS & SPEAK TIME
        # -------------------------------------------------------------
        print("[4/7] Attaching Participants...")
        participants = [
            MeetingParticipant(
                meeting_id=meeting.id,
                user_id=priya.id,
                role="organizer",
                attendance_status="attended",
                speak_time_seconds=780
            ),
            MeetingParticipant(
                meeting_id=meeting.id,
                user_id=sarthak.id,
                role="host",
                attendance_status="attended",
                speak_time_seconds=1420
            ),
            MeetingParticipant(
                meeting_id=meeting.id,
                user_id=alex.id,
                role="attendee",
                attendance_status="attended",
                speak_time_seconds=640
            )
        ]
        db.add_all(participants)

        # -------------------------------------------------------------
        # 5. SEED TIMESTAMPED TRANSCRIPT SEGMENTS
        # -------------------------------------------------------------
        print("[5/7] Inserting Timestamped Transcript Segments...")
        segments = [
            TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=priya.id,
                start_time_ms=0,
                end_time_ms=6200,
                text_content="Welcome everyone. Today we are reviewing the SSMS SQL Server integration for Trio AI.",
                sentiment_score=Decimal("0.650")
            ),
            TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=sarthak.id,
                start_time_ms=7100,
                end_time_ms=18500,
                text_content="Thanks Priya. We've normalized the schema into 9 3NF tables and verified connectivity on port 1434 with ODBC Driver 18.",
                sentiment_score=Decimal("0.850")
            ),
            TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=alex.id,
                start_time_ms=19000,
                end_time_ms=28400,
                text_content="The cloud architecture looks solid. I suggest using Azure SQL managed instances once we deploy.",
                sentiment_score=Decimal("0.700")
            ),
            TranscriptSegment(
                meeting_id=meeting.id,
                speaker_id=priya.id,
                start_time_ms=29000,
                end_time_ms=39500,
                text_content="Excellent. Sarthak, let's complete the API route layer by Friday, and Alex will review the cloud infrastructure specs.",
                sentiment_score=Decimal("0.800")
            )
        ]
        db.add_all(segments)

        # -------------------------------------------------------------
        # 6. SEED AI SUMMARY, ACTION ITEMS & DECISIONS
        # -------------------------------------------------------------
        print("[6/7] Generating AI Summaries, Actions & Decisions...")
        summary = MeetingSummary(
            meeting_id=meeting.id,
            executive_summary=(
                "The team reviewed and approved the 9-table normalized 3NF database schema for Trio AI's SSMS integration. "
                "Connectivity via ODBC Driver 18 on port 1434 was validated. Action items were allocated for API routing and Azure SQL cloud evaluation."
            ),
            detailed_notes=(
                "### Key Points:\n"
                "- **Database Progress**: 9 tables provisioned in MeetingDB with complete FK constraints and index cascades.\n"
                "- **Cloud Strategy**: Partner Alex Chen recommended Azure SQL managed instances for production.\n"
                "- **Next Milestones**: Target completion of Pydantic v2 schemas and FastAPI CRUD endpoints by Friday."
            ),
            model_used="gemini-1.5-pro",
            prompt_tokens=420,
            completion_tokens=185
        )
        db.add(summary)

        # Action Items
        action_items = [
            ActionItem(
                meeting_id=meeting.id,
                assignee_id=sarthak.id,
                title="Finalize FastAPI Route Layer for Intelligence Schema",
                description="Expose endpoints for participants, transcript segments, summaries, and action item status updates.",
                priority="high",
                status="in_progress",
                due_date=date.today() + timedelta(days=3)
            ),
            ActionItem(
                meeting_id=meeting.id,
                assignee_id=alex.id,
                title="Review Cloud Infrastructure & Azure SQL Specifications",
                description="Provide cost estimates and network topology for running SQL Server in hybrid cloud.",
                priority="medium",
                status="pending",
                due_date=date.today() + timedelta(days=7)
            )
        ]
        db.add_all(action_items)

        # Key Decisions
        decision = KeyDecision(
            meeting_id=meeting.id,
            proposed_by_id=sarthak.id,
            decision_text="Adopt ODBC Driver 18 with 3NF normalized schema across all agent persistence layers.",
            rationale="Eliminates string redundancy on topics and provides strict database-level constraint enforcement."
        )
        db.add(decision)

        # -------------------------------------------------------------
        # 7. SEED MEETING TOPIC TAGS
        # -------------------------------------------------------------
        print("[7/7] Linking Master Topics to Meeting...")
        meeting_topics = [
            MeetingTopic(meeting_id=meeting.id, topic_id=topics["SSMS Integration"].id, relevance_score=Decimal("0.980")),
            MeetingTopic(meeting_id=meeting.id, topic_id=topics["FastAPI Architecture"].id, relevance_score=Decimal("0.920")),
            MeetingTopic(meeting_id=meeting.id, topic_id=topics["Cloud Deployment"].id, relevance_score=Decimal("0.850")),
        ]
        db.add_all(meeting_topics)

        # Commit transaction
        db.commit()
        print("\n" + "=" * 65)
        print("[SUCCESS] All sample data successfully committed to MeetingDB!")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

