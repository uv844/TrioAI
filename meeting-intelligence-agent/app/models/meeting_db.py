from sqlalchemy import (
    Column, Integer, BIGINT, String, Text, DateTime, Date,
    DECIMAL, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    is_registered_user = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    participations = relationship("MeetingParticipant", back_populates="user", cascade="all, delete-orphan")
    assigned_action_items = relationship("ActionItem", back_populates="assignee")
    proposed_decisions = relationship("KeyDecision", back_populates="proposer")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    meeting_links = relationship("MeetingTopic", back_populates="topic", cascade="all, delete-orphan")


class MeetingModel(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    transcript = Column(Text, nullable=True)  # Backward compatibility
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="scheduled")
    platform = Column(String(50), nullable=True)
    meeting_url = Column(String(500), nullable=True)
    recording_url = Column(String(500), nullable=True)
    raw_transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    segments = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("MeetingSummary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("KeyDecision", back_populates="meeting", cascade="all, delete-orphan")
    topics = relationship("MeetingTopic", back_populates="meeting", cascade="all, delete-orphan")


class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, default="attendee")
    attendance_status = Column(String(20), nullable=False, default="attended")
    speak_time_seconds = Column(Integer, nullable=False, default=0)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="participants")
    user = relationship("User", back_populates="participations")

    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="UQ_meeting_participant"),
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(BIGINT, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    speaker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_time_ms = Column(Integer, nullable=False)
    end_time_ms = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    sentiment_score = Column(DECIMAL(4, 3), nullable=True)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="segments")
    speaker = relationship("User")


class MeetingSummary(Base):
    __tablename__ = "meeting_summaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True)
    executive_summary = Column(Text, nullable=False)
    detailed_notes = Column(Text, nullable=True)
    model_used = Column(String(50), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    generated_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="summary")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(15), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="pending")
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="action_items")
    assignee = relationship("User", back_populates="assigned_action_items")


class KeyDecision(Base):
    __tablename__ = "key_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    proposed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision_text = Column(String(1000), nullable=False)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="decisions")
    proposer = relationship("User", back_populates="proposed_decisions")


class MeetingTopic(Base):
    __tablename__ = "meeting_topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(DECIMAL(4, 3), nullable=False, default=1.000)

    # Relationships
    meeting = relationship("MeetingModel", back_populates="topics")
    topic = relationship("Topic", back_populates="meeting_links")

    __table_args__ = (
        UniqueConstraint("meeting_id", "topic_id", name="UQ_meeting_topic"),
    )
