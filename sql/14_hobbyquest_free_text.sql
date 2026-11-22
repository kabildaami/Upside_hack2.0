-- Additive: distinguish existing legacy multiple-choice discovery from new HobbyQuest sessions.
BEGIN;
ALTER TABLE public.senior_hobby_sessions ADD COLUMN IF NOT EXISTS engine_version varchar(32) NOT NULL DEFAULT 'legacy_choice';
CREATE INDEX IF NOT EXISTS idx_hobbyquest_engine_version ON public.senior_hobby_sessions(engine_version);
COMMIT;
