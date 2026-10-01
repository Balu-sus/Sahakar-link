-- Enable UUID extension for secure, non-sequential primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. USER MANAGEMENT & RBAC PROFILES
-- =============================================================================
CREATE TYPE user_role AS ENUM ('STUDENT', 'TRAINER', 'ADMIN', 'EMPLOYER');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    preferred_language VARCHAR(10) DEFAULT 'en', -- For IndicTrans2 routing
    role user_role NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE institution_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_name VARCHAR(255) NOT NULL,
    registration_code VARCHAR(100) UNIQUE NOT NULL,
    address TEXT,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 2. PROGRAMMES, BATCHES & LOGISTICS
-- =============================================================================
CREATE TABLE programmes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_days INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    programme_id UUID REFERENCES programmes(id) ON DELETE CASCADE,
    institution_id UUID REFERENCES institution_profiles(id) ON DELETE CASCADE,
    batch_code VARCHAR(50) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    capacity INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    nomination_status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
    completion_status VARCHAR(50) DEFAULT 'ENROLLED', -- ENROLLED, COMPLETED, DROPPED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, batch_id)
);

-- =============================================================================
-- 3. ATTENDANCE & RESILIENT MULTI-MODAL LOGS
-- =============================================================================
CREATE TYPE attendance_method AS ENUM ('FACE_ADA_FACE', 'QR_CODE', 'MANUAL_EXCEPTION');

CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    method attendance_method NOT NULL,
    liveness_score FLOAT, -- From anti-spoofing vision model
    verification_status VARCHAR(50) DEFAULT 'VERIFIED', -- VERIFIED, AUDIT_FLAGGED, REVIEWED
    is_offline_sync BOOLEAN DEFAULT FALSE, -- Identifies events synced from Local Fabric queue
    synced_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- 4. ASSESSMENTS & SECURE EXAMS
-- =============================================================================
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    total_marks INT NOT NULL,
    passing_marks INT NOT NULL,
    is_secure_mode_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessment_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    score_obtained FLOAT,
    security_flags_count INT DEFAULT 0, -- App switching, split-screen violations
    passed BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 5. CERTIFICATION & SKILL EVIDENCE GRAPH
-- =============================================================================
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    programme_id UUID REFERENCES programmes(id) ON DELETE CASCADE,
    certificate_number VARCHAR(100) UNIQUE NOT NULL,
    qr_verification_url TEXT NOT NULL,
    digital_signature TEXT NOT NULL, -- Cryptographic signature for tamper-proofing
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100)
);

CREATE TABLE skill_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    credential_id UUID REFERENCES credentials(id) ON DELETE CASCADE,
    assessment_submission_id UUID REFERENCES assessment_submissions(id) ON DELETE CASCADE,
    confidence_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 6. EMPLOYER DEMAND & JOB MATCHING
-- =============================================================================
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    employment_type VARCHAR(50) NOT NULL, -- FULL_TIME, PART_TIME, CONTRACT
    is_verified_employer BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_required_skills (
    job_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    match_score FLOAT, -- Calculated by Nemotron Reranker + Vector DB
    match_explanation TEXT, -- Grounded AI summary of matched evidence
    status VARCHAR(50) DEFAULT 'APPLIED', -- APPLIED, SHORTLISTED, SELECTED, JOINED
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
