-- EduNova Grade 11: additive, non-destructive. Run after migrations 09, 10, 11.
BEGIN;
CREATE TABLE IF NOT EXISTS public.senior_reasoning_quizzes (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 school_id integer NOT NULL REFERENCES public.schools(school_id),
 class_id integer NOT NULL,
 document_id bigint NOT NULL REFERENCES public.teacher_curriculum_documents(id) ON DELETE CASCADE,
 source_chunk_id bigint NOT NULL REFERENCES public.teacher_curriculum_chunks(id) ON DELETE CASCADE,
 teacher_id integer NOT NULL,
 subject_id integer NOT NULL REFERENCES public.subjects(subject_id),
 lesson_key varchar(60) NOT NULL,
 title varchar(220) NOT NULL,
 statement text NOT NULL,
 teacher_explanation text NOT NULL DEFAULT '',
 status varchar(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved')),
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(class_id,school_id) REFERENCES public.classes(class_id,school_id),
 FOREIGN KEY(teacher_id,school_id) REFERENCES public.teachers(teacher_id,school_id),
 UNIQUE(document_id,lesson_key,title)
);
CREATE INDEX IF NOT EXISTS idx_senior_reasoning_class ON public.senior_reasoning_quizzes(class_id,status,lesson_key);
CREATE TABLE IF NOT EXISTS public.senior_reasoning_steps (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 quiz_id bigint NOT NULL REFERENCES public.senior_reasoning_quizzes(id) ON DELETE CASCADE,
 position integer NOT NULL CHECK(position BETWEEN 1 AND 12),
 prompt text NOT NULL, expected_answer varchar(200) NOT NULL,
 check_type varchar(16) NOT NULL CHECK(check_type IN ('numeric','exact')),
 hint text NOT NULL, xp integer NOT NULL DEFAULT 8 CHECK(xp BETWEEN 0 AND 30),
 UNIQUE(quiz_id,position)
);
CREATE TABLE IF NOT EXISTS public.senior_reasoning_attempts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 step_id bigint NOT NULL REFERENCES public.senior_reasoning_steps(id) ON DELETE CASCADE,
 response_text varchar(200) NOT NULL,
 reasoning_text text NOT NULL DEFAULT '',
 is_correct boolean NOT NULL,
 teacher_feedback text, reviewed_at timestamptz, reviewed_by_user_id integer REFERENCES public.users(user_id),
 submitted_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_reasoning_attempt_student ON public.senior_reasoning_attempts(student_id,step_id);
CREATE TABLE IF NOT EXISTS public.senior_step_xp (
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 step_id bigint NOT NULL REFERENCES public.senior_reasoning_steps(id) ON DELETE CASCADE,
 points integer NOT NULL CHECK(points BETWEEN 0 AND 30),
 granted_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(student_id,step_id)
);
CREATE TABLE IF NOT EXISTS public.senior_reasoning_quiz_credit (
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 quiz_id bigint NOT NULL REFERENCES public.senior_reasoning_quizzes(id) ON DELETE CASCADE,
 task_id bigint NOT NULL REFERENCES public.edunova_plan_tasks(id) ON DELETE CASCADE,
 credited_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(student_id,quiz_id,task_id)
);
-- Existing tables already cover conversations, teacher weekly plans and diary.
-- Do not add diary ciphertext to regular student conversation search.
COMMIT;
-- Note: the deployment-specific assignment seed is in 13_exellence_grade11_math_assignment.sql.
