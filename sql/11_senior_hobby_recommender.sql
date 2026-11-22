-- Additive hobby discovery migration. Never resets existing users or curricula.
BEGIN;
CREATE TABLE IF NOT EXISTS public.senior_hobby_sessions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 status varchar(16) NOT NULL DEFAULT 'active' CHECK(status IN ('active','completed')),
 summary text,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 completed_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_senior_hobby_session_student ON public.senior_hobby_sessions(student_id, created_at DESC);
CREATE TABLE IF NOT EXISTS public.senior_hobby_answers (
 session_id uuid NOT NULL REFERENCES public.senior_hobby_sessions(id) ON DELETE CASCADE,
 question_index smallint NOT NULL CHECK (question_index BETWEEN 0 AND 5),
 question_id varchar(40) NOT NULL,
 option_id varchar(40) NOT NULL,
 option_label text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(session_id,question_index)
);
CREATE TABLE IF NOT EXISTS public.senior_hobby_recommendations (
 session_id uuid NOT NULL REFERENCES public.senior_hobby_sessions(id) ON DELETE CASCADE,
 rank smallint NOT NULL CHECK(rank IN (1,2)),
 hobby_name varchar(80) NOT NULL,
 score integer NOT NULL CHECK(score BETWEEN 0 AND 100),
 description text NOT NULL,
 reason text NOT NULL,
 evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
 PRIMARY KEY(session_id,rank)
);
COMMIT;
