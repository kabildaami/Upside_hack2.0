-- EduNova agent migration. ADDITIVE, safe to re-run. Requires 02,05,07,08.
BEGIN;
CREATE TABLE IF NOT EXISTS public.edunova_weekly_plans (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 school_id integer NOT NULL REFERENCES public.schools(school_id),
 class_id integer NOT NULL, subject_id integer NOT NULL REFERENCES public.subjects(subject_id),
 teacher_id integer NOT NULL,
 title varchar(240) NOT NULL, week_start date NOT NULL, week_end date NOT NULL,
 published boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK (week_end >= week_start AND week_end <= week_start + 13),
 FOREIGN KEY(class_id,school_id) REFERENCES public.classes(class_id,school_id),
 FOREIGN KEY(teacher_id,school_id) REFERENCES public.teachers(teacher_id,school_id),
 UNIQUE(class_id,subject_id,week_start)
);
CREATE TABLE IF NOT EXISTS public.edunova_plan_tasks (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 plan_id bigint NOT NULL REFERENCES public.edunova_weekly_plans(id) ON DELETE CASCADE,
 title varchar(240) NOT NULL,
 kind varchar(16) NOT NULL CHECK(kind IN ('lesson','quiz','practice')),
 lesson_key varchar(60) NOT NULL,
 document_id bigint REFERENCES public.teacher_curriculum_documents(id) ON DELETE SET NULL,
 target_correct smallint NOT NULL DEFAULT 1 CHECK(target_correct BETWEEN 1 AND 20),
 xp_reward integer NOT NULL DEFAULT 20 CHECK(xp_reward BETWEEN 0 AND 100),
 position smallint NOT NULL DEFAULT 0,
 UNIQUE(plan_id,kind,lesson_key)
);
CREATE TABLE IF NOT EXISTS public.edunova_student_task_progress (
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 task_id bigint NOT NULL REFERENCES public.edunova_plan_tasks(id) ON DELETE CASCADE,
 completed_at timestamptz,
 correct_count integer NOT NULL DEFAULT 0 CHECK(correct_count >= 0),
 PRIMARY KEY(student_id,task_id)
);
CREATE TABLE IF NOT EXISTS public.edunova_quiz_items (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 document_id bigint NOT NULL REFERENCES public.teacher_curriculum_documents(id) ON DELETE CASCADE,
 source_chunk_id bigint NOT NULL REFERENCES public.teacher_curriculum_chunks(id) ON DELETE CASCADE,
 teacher_id integer NOT NULL REFERENCES public.teachers(teacher_id),
 subject_id integer NOT NULL REFERENCES public.subjects(subject_id),
 lesson_key varchar(60) NOT NULL,
 template varchar(32) NOT NULL CHECK(template IN ('multiple_choice','number_input','true_false')),
 prompt text NOT NULL,
 options jsonb NOT NULL DEFAULT '[]'::jsonb,
 answer_text varchar(160) NOT NULL,
 hint text NOT NULL,
 explanation text NOT NULL,
 status varchar(16) NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved')),
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK ((template='number_input' AND jsonb_array_length(options)=0) OR
        (template='true_false' AND jsonb_array_length(options)=2) OR
        (template='multiple_choice' AND jsonb_array_length(options) BETWEEN 2 AND 6))
);
CREATE INDEX IF NOT EXISTS idx_edunova_quiz_lesson ON public.edunova_quiz_items(document_id,lesson_key,status);
CREATE TABLE IF NOT EXISTS public.edunova_quiz_attempts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 question_id bigint NOT NULL REFERENCES public.edunova_quiz_items(id) ON DELETE CASCADE,
 attempt_no smallint NOT NULL CHECK(attempt_no BETWEEN 1 AND 20),
 response_text text NOT NULL, is_correct boolean NOT NULL,
 hints_used smallint NOT NULL DEFAULT 0 CHECK(hints_used BETWEEN 0 AND 20),
 answered_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(student_id,question_id,attempt_no)
);
CREATE TABLE IF NOT EXISTS public.edunova_agent_conversations (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 title varchar(160) NOT NULL DEFAULT 'My study conversation',
 created_at timestamptz NOT NULL DEFAULT now(),updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_edunova_agent_threads ON public.edunova_agent_conversations(student_id,updated_at DESC);
CREATE TABLE IF NOT EXISTS public.edunova_agent_messages (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 conversation_id uuid NOT NULL REFERENCES public.edunova_agent_conversations(id) ON DELETE CASCADE,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 role varchar(12) NOT NULL CHECK(role IN ('student','assistant')),
 content text NOT NULL CHECK(length(content) <= 10000),
 sources jsonb NOT NULL DEFAULT '[]'::jsonb,
 tool_names jsonb NOT NULL DEFAULT '[]'::jsonb,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_edunova_agent_messages_thread ON public.edunova_agent_messages(conversation_id,id);
CREATE TABLE IF NOT EXISTS public.edunova_xp_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 task_id bigint REFERENCES public.edunova_plan_tasks(id) ON DELETE CASCADE,
 quiz_attempt_id bigint REFERENCES public.edunova_quiz_attempts(id) ON DELETE CASCADE,
 points integer NOT NULL CHECK(points BETWEEN 0 AND 100),
 reason varchar(100) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(student_id,task_id), UNIQUE(student_id,quiz_attempt_id)
);
CREATE TABLE IF NOT EXISTS public.edunova_study_breaks (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 session_id bigint NOT NULL REFERENCES public.student_learning_sessions(id) ON DELETE CASCADE,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 started_at timestamptz NOT NULL DEFAULT now(),
 ended_at timestamptz, CHECK(ended_at IS NULL OR ended_at>=started_at)
);
CREATE INDEX IF NOT EXISTS idx_edunova_breaks_session ON public.edunova_study_breaks(session_id,started_at DESC);
COMMIT;
