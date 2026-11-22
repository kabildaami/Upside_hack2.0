-- Journal AI replies belong only to the owner of their parent encrypted journal entry.
-- Apply only after sql/10_senior_agent.sql. Additive and idempotent.
BEGIN;
CREATE TABLE IF NOT EXISTS public.senior_diary_ai_turns (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entry_id uuid NOT NULL REFERENCES public.senior_diary(id) ON DELETE CASCADE,
  student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
  role varchar(12) NOT NULL CHECK(role IN ('student','assistant')),
  ciphertext bytea NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_senior_diary_ai_entry
ON public.senior_diary_ai_turns(student_id, entry_id, id);
COMMIT;
