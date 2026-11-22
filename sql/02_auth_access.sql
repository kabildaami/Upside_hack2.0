-- ADDITIVE ONLY: run after sql/initial.sql. Preserve existing records.
-- Test on a backed-up database first. Re-running is safe.
BEGIN;
CREATE TABLE IF NOT EXISTS public.student_enrollments (
 enrollment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 class_id integer NOT NULL REFERENCES public.classes(class_id) ON DELETE CASCADE,
 school_id integer NOT NULL,
 enrolled_at timestamptz NOT NULL DEFAULT now(),
 ended_at timestamptz,
 UNIQUE(student_id, class_id),
 FOREIGN KEY(student_id,school_id) REFERENCES public.students(student_id,school_id),
 FOREIGN KEY(class_id,school_id) REFERENCES public.classes(class_id,school_id),
 CHECK(ended_at IS NULL OR ended_at >= enrolled_at)
);
CREATE INDEX IF NOT EXISTS idx_enroll_class ON public.student_enrollments(class_id) WHERE ended_at IS NULL;
CREATE TABLE IF NOT EXISTS public.guardian_student_links (
 parent_id integer NOT NULL REFERENCES public.parents(parent_id) ON DELETE CASCADE,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 relationship varchar(40) NOT NULL DEFAULT 'parent',
 can_view_progress boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(parent_id,student_id)
);
-- IMPORTANT: auth sessions let logouts revoke tokens server-side.
CREATE TABLE IF NOT EXISTS public.auth_sessions (
 id uuid PRIMARY KEY,
 user_id integer NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
 token_sha256 char(64) NOT NULL UNIQUE,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 revoked_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON public.auth_sessions(user_id,expires_at DESC);
CREATE TABLE IF NOT EXISTS public.auth_audit_log (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 user_id integer REFERENCES public.users(user_id) ON DELETE SET NULL,
 email_attempt varchar(255),
 event varchar(40) NOT NULL CHECK(event IN ('login_success','login_failed','logout','forbidden')),
 occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_audit_time ON public.auth_audit_log(occurred_at DESC);
COMMIT;
