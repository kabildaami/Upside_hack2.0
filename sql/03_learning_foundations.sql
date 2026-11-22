-- ADDITIVE scaffolding for future AI tutoring; no pgvector dependency.
BEGIN;
CREATE TABLE IF NOT EXISTS public.course_documents (
 document_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 school_id integer NOT NULL REFERENCES public.schools(school_id),
 uploaded_by_user_id integer NOT NULL REFERENCES public.users(user_id),
 subject_id integer REFERENCES public.subjects(subject_id),
 title text NOT NULL, storage_path text NOT NULL,
 sha256 char(64), created_at timestamptz DEFAULT now(),
 UNIQUE(school_id,sha256)
);
CREATE TABLE IF NOT EXISTS public.course_chunks (
 chunk_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 document_id bigint NOT NULL REFERENCES public.course_documents(document_id) ON DELETE CASCADE,
 chunk_index integer NOT NULL, content text NOT NULL,
 page_number integer, heading text,
 UNIQUE(document_id,chunk_index)
);
CREATE TABLE IF NOT EXISTS public.learning_objectives (
 objective_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 subject_id integer NOT NULL REFERENCES public.subjects(subject_id),
 grade_level varchar(40) NOT NULL,
 concept_key varchar(160) NOT NULL,
 title text NOT NULL,
 UNIQUE(subject_id,grade_level,concept_key)
);
CREATE TABLE IF NOT EXISTS public.assignments (
 assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 class_id integer NOT NULL REFERENCES public.classes(class_id),
 teacher_id integer NOT NULL REFERENCES public.teachers(teacher_id),
 title text NOT NULL, instructions text,
 due_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS public.student_mastery (
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 objective_id bigint NOT NULL REFERENCES public.learning_objectives(objective_id),
 attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
 correct integer NOT NULL DEFAULT 0 CHECK(correct>=0),
 hints_used integer NOT NULL DEFAULT 0 CHECK(hints_used>=0),
 updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(student_id,objective_id), CHECK(correct<=attempts)
);
CREATE TABLE IF NOT EXISTS public.student_goals (
 goal_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 title text NOT NULL, due_on date,
 completed_at timestamptz
);
CREATE TABLE IF NOT EXISTS public.quiz_questions (
 question_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 assignment_id bigint REFERENCES public.assignments(assignment_id) ON DELETE SET NULL,
 source_chunk_id bigint REFERENCES public.course_chunks(chunk_id),
 prompt text NOT NULL, options jsonb NOT NULL,
 answer_index integer NOT NULL CHECK(answer_index BETWEEN 0 AND 20),
 status varchar(20) NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved'))
);
CREATE TABLE IF NOT EXISTS public.quiz_attempts (
 attempt_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 question_id bigint NOT NULL REFERENCES public.quiz_questions(question_id),
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 selected_index integer NOT NULL, correct boolean NOT NULL,
 hints_used integer NOT NULL DEFAULT 0, answered_at timestamptz NOT NULL DEFAULT now()
);
-- Privately sensitive diary data is intentionally NOT part of the MVP.
COMMIT;
