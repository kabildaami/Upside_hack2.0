-- ADDITIVE: admission requests are not authenticated students.
BEGIN;
CREATE TABLE IF NOT EXISTS public.student_admission_requests (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 school_id integer NOT NULL REFERENCES public.schools(school_id),
 full_name varchar(120) NOT NULL,
 age smallint NOT NULL CHECK(age BETWEEN 5 AND 99),
 contact varchar(120) NOT NULL,
 field_of_study varchar(120) NOT NULL DEFAULT '',
 level varchar(40) NOT NULL DEFAULT '',
 other_hobbies varchar(500) NOT NULL DEFAULT '',
 needs_details varchar(1000) NOT NULL DEFAULT '',
 difficult_subjects varchar(500) NOT NULL DEFAULT '',
 difficulty_level smallint NOT NULL DEFAULT 3 CHECK(difficulty_level BETWEEN 1 AND 5),
 help_wanted varchar(1000) NOT NULL DEFAULT '',
 hobbies integer[] NOT NULL DEFAULT '{}',
 special_needs integer[] NOT NULL DEFAULT '{}',
 study_problems integer[] NOT NULL DEFAULT '{}',
 difficult_subject_ids integer[] NOT NULL DEFAULT '{}',
 consent boolean NOT NULL CHECK(consent),
 guardian_consent_confirmed boolean NOT NULL DEFAULT false,
 status varchar(16) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','contacted','declined')),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 handled_by integer REFERENCES public.users(user_id)
);
CREATE INDEX IF NOT EXISTS idx_student_admission_school_status
 ON public.student_admission_requests(school_id, status, created_at DESC);
COMMIT;
