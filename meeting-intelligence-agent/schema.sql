-- =============================================================================
-- TRIO AI - MEETING INTELLIGENCE AGENT
-- COMPLETE NORMALIZED DATABASE SCHEMA (3NF) FOR SQL SERVER / SSMS
-- Target Database: MeetingDB
-- =============================================================================

USE [MeetingDB];
GO

-- -----------------------------------------------------------------------------
-- 1. USERS & PARTICIPANT DIRECTORY
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        full_name VARCHAR(150) NOT NULL,
        email VARCHAR(255) NOT NULL,
        role_title VARCHAR(100) NULL,
        department VARCHAR(100) NULL,
        is_registered_user BIT NOT NULL DEFAULT 0,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT UQ_users_email UNIQUE (email)
    );
    CREATE INDEX IX_users_email ON users(email);
    PRINT 'Table [users] created successfully.';
END
ELSE
    PRINT 'Table [users] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 2. MASTER TOPICS LOOKUP TABLE
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'topics')
BEGIN
    CREATE TABLE topics (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT UQ_topics_name UNIQUE (name)
    );
    CREATE INDEX IX_topics_name ON topics(name);
    PRINT 'Table [topics] created successfully.';
END
ELSE
    PRINT 'Table [topics] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 3. MEETINGS (CORE TABLE MIGRATION / ENHANCEMENT)
-- -----------------------------------------------------------------------------
-- Add newly required columns to existing meetings table if missing
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'meetings')
BEGIN
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'scheduled_start')
        ALTER TABLE meetings ADD scheduled_start DATETIME2 NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'scheduled_end')
        ALTER TABLE meetings ADD scheduled_end DATETIME2 NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'actual_start')
        ALTER TABLE meetings ADD actual_start DATETIME2 NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'actual_end')
        ALTER TABLE meetings ADD actual_end DATETIME2 NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'status')
        ALTER TABLE meetings ADD status VARCHAR(20) NOT NULL CONSTRAINT DF_meetings_status DEFAULT 'scheduled'
            CONSTRAINT CK_meetings_status CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled'));
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'platform')
        ALTER TABLE meetings ADD platform VARCHAR(50) NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'meeting_url')
        ALTER TABLE meetings ADD meeting_url VARCHAR(500) NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'recording_url')
        ALTER TABLE meetings ADD recording_url VARCHAR(500) NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'raw_transcript')
        ALTER TABLE meetings ADD raw_transcript NVARCHAR(MAX) NULL;
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'created_at')
        ALTER TABLE meetings ADD created_at DATETIME2 NOT NULL CONSTRAINT DF_meetings_created_at DEFAULT GETUTCDATE();
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('meetings') AND name = 'updated_at')
        ALTER TABLE meetings ADD updated_at DATETIME2 NOT NULL CONSTRAINT DF_meetings_updated_at DEFAULT GETUTCDATE();
    PRINT 'Table [meetings] updated with enterprise schema columns.';
END
GO

-- -----------------------------------------------------------------------------
-- 4. MEETING PARTICIPANTS (MANY-TO-MANY JUNCTION)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meeting_participants')
BEGIN
    CREATE TABLE meeting_participants (
        id INT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        user_id INT NOT NULL,
        role VARCHAR(20) NOT NULL CONSTRAINT DF_participants_role DEFAULT 'attendee'
            CONSTRAINT CK_participants_role CHECK (role IN ('organizer', 'host', 'attendee', 'observer')),
        attendance_status VARCHAR(20) NOT NULL CONSTRAINT DF_participants_status DEFAULT 'attended'
            CONSTRAINT CK_participants_status CHECK (attendance_status IN ('attended', 'absent', 'invited')),
        speak_time_seconds INT NOT NULL CONSTRAINT DF_participants_speak_time DEFAULT 0,
        CONSTRAINT FK_participants_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT FK_participants_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT UQ_meeting_participant UNIQUE (meeting_id, user_id)
    );
    CREATE INDEX IX_participants_meeting ON meeting_participants(meeting_id);
    CREATE INDEX IX_participants_user ON meeting_participants(user_id);
    PRINT 'Table [meeting_participants] created successfully.';
END
ELSE
    PRINT 'Table [meeting_participants] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 5. TRANSCRIPT SEGMENTS (TIMESTAMPED UTTERANCES)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'transcript_segments')
BEGIN
    CREATE TABLE transcript_segments (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        speaker_id INT NULL,
        start_time_ms INT NOT NULL,
        end_time_ms INT NOT NULL,
        text_content NVARCHAR(MAX) NOT NULL,
        sentiment_score DECIMAL(4,3) NULL CONSTRAINT CK_segments_sentiment CHECK (sentiment_score BETWEEN -1.000 AND 1.000),
        CONSTRAINT FK_segments_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT FK_segments_speaker FOREIGN KEY (speaker_id) REFERENCES users(id) ON DELETE SET NULL
    );
    CREATE INDEX IX_segments_meeting_time ON transcript_segments(meeting_id, start_time_ms);
    PRINT 'Table [transcript_segments] created successfully.';
END
ELSE
    PRINT 'Table [transcript_segments] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 6. MEETING SUMMARIES (AI-GENERATED INTELLIGENCE)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meeting_summaries')
BEGIN
    CREATE TABLE meeting_summaries (
        id INT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        executive_summary NVARCHAR(MAX) NOT NULL,
        detailed_notes NVARCHAR(MAX) NULL,
        model_used VARCHAR(50) NULL,
        prompt_tokens INT NULL,
        completion_tokens INT NULL,
        generated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT FK_summaries_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT UQ_summaries_meeting UNIQUE (meeting_id)
    );
    CREATE INDEX IX_summaries_meeting ON meeting_summaries(meeting_id);
    PRINT 'Table [meeting_summaries] created successfully.';
END
ELSE
    PRINT 'Table [meeting_summaries] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 7. ACTION ITEMS (DELIVERABLES & ASSIGNEES)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'action_items')
BEGIN
    CREATE TABLE action_items (
        id INT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        assignee_id INT NULL,
        title VARCHAR(255) NOT NULL,
        description NVARCHAR(MAX) NULL,
        priority VARCHAR(15) NOT NULL CONSTRAINT DF_action_items_priority DEFAULT 'medium'
            CONSTRAINT CK_action_items_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
        status VARCHAR(20) NOT NULL CONSTRAINT DF_action_items_status DEFAULT 'pending'
            CONSTRAINT CK_action_items_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
        due_date DATE NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        completed_at DATETIME2 NULL,
        CONSTRAINT FK_action_items_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT FK_action_items_assignee FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
    );
    CREATE INDEX IX_action_items_meeting ON action_items(meeting_id);
    CREATE INDEX IX_action_items_assignee ON action_items(assignee_id);
    PRINT 'Table [action_items] created successfully.';
END
ELSE
    PRINT 'Table [action_items] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 8. KEY DECISIONS (CONSENSUS TRACKING)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'key_decisions')
BEGIN
    CREATE TABLE key_decisions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        proposed_by_id INT NULL,
        decision_text NVARCHAR(1000) NOT NULL,
        rationale NVARCHAR(MAX) NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT FK_key_decisions_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT FK_key_decisions_user FOREIGN KEY (proposed_by_id) REFERENCES users(id) ON DELETE SET NULL
    );
    CREATE INDEX IX_key_decisions_meeting ON key_decisions(meeting_id);
    PRINT 'Table [key_decisions] created successfully.';
END
ELSE
    PRINT 'Table [key_decisions] already exists.';
GO

-- -----------------------------------------------------------------------------
-- 9. MEETING TOPICS (JUNCTION TABLE)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'meeting_topics')
BEGIN
    CREATE TABLE meeting_topics (
        id INT IDENTITY(1,1) PRIMARY KEY,
        meeting_id INT NOT NULL,
        topic_id INT NOT NULL,
        relevance_score DECIMAL(4,3) NOT NULL DEFAULT 1.000
            CONSTRAINT CK_meeting_topics_score CHECK (relevance_score BETWEEN 0.000 AND 1.000),
        CONSTRAINT FK_meeting_topics_meeting FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
        CONSTRAINT FK_meeting_topics_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
        CONSTRAINT UQ_meeting_topic UNIQUE (meeting_id, topic_id)
    );
    CREATE INDEX IX_meeting_topics_meeting ON meeting_topics(meeting_id);
    CREATE INDEX IX_meeting_topics_topic ON meeting_topics(topic_id);
    PRINT 'Table [meeting_topics] created successfully.';
END
ELSE
    PRINT 'Table [meeting_topics] already exists.';
GO

