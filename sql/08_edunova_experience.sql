-- EduNova UI preferences and actual learning-session lifecycle; additive only.
BEGIN;
CREATE TABLE IF NOT EXISTS public.student_ui_preferences (
 student_id integer PRIMARY KEY REFERENCES public.students(student_id) ON DELETE CASCADE,
 avatar_key varchar(32) NOT NULL DEFAULT 'fox' CHECK (avatar_key IN ('fox','rabbit','penguin','turtle','cat','owl')),
 preferred_style varchar(32) NOT NULL DEFAULT 'quest' CHECK (preferred_style IN ('quest','story','draw','guided','focus','review')),
 read_aloud boolean NOT NULL DEFAULT false,
 easy_words boolean NOT NULL DEFAULT false,
 short_sessions boolean NOT NULL DEFAULT true,
 calm_mode boolean NOT NULL DEFAULT false,
 large_text boolean NOT NULL DEFAULT false,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS public.student_learning_sessions (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 subject_name varchar(100) NOT NULL,
 activity_type varchar(32) NOT NULL CHECK (activity_type IN ('quest','guided','focus','review')),
 started_at timestamptz NOT NULL DEFAULT now(),
 ended_at timestamptz,
 CHECK (ended_at IS NULL OR ended_at >= started_at)
);
CREATE INDEX IF NOT EXISTS idx_edunova_sessions_student ON public.student_learning_sessions(student_id, started_at DESC);
COMMIT;
