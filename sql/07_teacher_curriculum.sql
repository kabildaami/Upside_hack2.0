-- Run AFTER 05_exellence_school.sql / 03_learning_foundations.sql.
-- Additive, preserves existing accounts and course_documents.
BEGIN;
CREATE TABLE IF NOT EXISTS public.teacher_curriculum_documents (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    school_id integer NOT NULL REFERENCES public.schools(school_id),
    class_id integer NOT NULL,
    teacher_id integer NOT NULL,
    subject_id integer NOT NULL REFERENCES public.subjects(subject_id),
    uploaded_by_user_id integer NOT NULL REFERENCES public.users(user_id),
    title varchar(240) NOT NULL,
    original_filename varchar(255) NOT NULL,
    media_type varchar(90) NOT NULL CHECK (media_type IN (
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    )),
    file_size integer NOT NULL CHECK (file_size > 0 AND file_size <= 10485760),
    file_sha256 char(64) NOT NULL,
    file_bytes bytea NOT NULL,
    extracted_chars integer NOT NULL DEFAULT 0 CHECK(extracted_chars >= 0),
    chunk_count integer NOT NULL DEFAULT 0 CHECK(chunk_count >= 0),
    status varchar(20) NOT NULL DEFAULT 'ready' CHECK (status IN ('ready','archived')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (teacher_id,class_id,subject_id,file_sha256),
    FOREIGN KEY (class_id,school_id) REFERENCES public.classes(class_id,school_id),
    FOREIGN KEY (teacher_id,school_id) REFERENCES public.teachers(teacher_id,school_id)
);
CREATE TABLE IF NOT EXISTS public.teacher_curriculum_chunks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES public.teacher_curriculum_documents(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL CHECK (chunk_index >= 0),
    page_number integer CHECK (page_number > 0),
    heading text,
    content text NOT NULL CHECK (length(btrim(content)) > 0),
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple',content)) STORED,
    UNIQUE(document_id,chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_teacher_curriculum_school ON public.teacher_curriculum_documents(school_id,class_id,subject_id,status);
CREATE INDEX IF NOT EXISTS idx_teacher_curriculum_teacher ON public.teacher_curriculum_documents(teacher_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_teacher_curriculum_chunks_fts ON public.teacher_curriculum_chunks USING GIN(search_vector);
COMMIT;
