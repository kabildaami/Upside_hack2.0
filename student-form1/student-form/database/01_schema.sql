-- =====================================================================
-- School database + student information form   (PostgreSQL)
-- Run: psql -U postgres -d school_db -f 01_schema.sql
-- =====================================================================

-- ---------- RESET (safe to re-run) ----------
DROP VIEW  IF EXISTS public.v_student_survey;
DROP TABLE IF EXISTS
  public.student_difficult_subjects, public.student_study_problems,
  public.student_special_needs, public.student_hobbies,
  public.study_problems, public.special_needs, public.hobbies,
  public.student_survey, public.teacher_classes, public.students,
  public.classes, public.subjects, public.teachers, public.directors,
  public.parents, public.schools, public.users CASCADE;

-- ---------- CORE SCHEMA (your original tables, in dependency order) ----------
CREATE TABLE public.users (
  user_id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  first_name    varchar(100) NOT NULL,
  last_name     varchar(100) NOT NULL,
  email         varchar(255) NOT NULL UNIQUE,
  password_hash text         NOT NULL,
  phone         varchar(30),
  role          varchar(20)  NOT NULL
                CHECK (role IN ('student','parent','teacher','director','admin')),
  is_active     boolean DEFAULT true,
  created_at    timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.schools (
  school_id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  school_name       varchar(200) NOT NULL,
  address           text,
  city              varchar(100),
  phone             varchar(30),
  email             varchar(255),
  educational_level varchar(20) NOT NULL
                    CHECK (educational_level IN ('primary', 'high_school')),
  director_user_id  integer NOT NULL UNIQUE REFERENCES public.users(user_id),
  created_at        timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.parents (
  parent_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id    integer NOT NULL UNIQUE REFERENCES public.users(user_id),
  occupation varchar(150)
);

CREATE TABLE public.directors (
  director_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     integer NOT NULL UNIQUE REFERENCES public.users(user_id),
  "position"  varchar(100) DEFAULT 'School Director'
);

CREATE TABLE public.teachers (
  teacher_id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id        integer NOT NULL UNIQUE REFERENCES public.users(user_id),
  school_id      integer NOT NULL REFERENCES public.schools(school_id),
  specialization varchar(150),
  hire_date      date,
  UNIQUE (teacher_id, school_id)
);

CREATE TABLE public.subjects (
  subject_id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  subject_name varchar(100) NOT NULL,
  description  text,
  school_level varchar(20) NOT NULL
               CHECK (school_level IN ('primary', 'high_school')),
  UNIQUE (subject_name, school_level)
);

CREATE TABLE public.classes (
  class_id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  school_id     integer NOT NULL REFERENCES public.schools(school_id),
  class_name    varchar(100) NOT NULL,
  grade_level   varchar(50),
  academic_year varchar(20),
  capacity      integer CHECK (capacity > 0),
  UNIQUE (class_id, school_id),
  UNIQUE (school_id, class_name, academic_year)
);

CREATE TABLE public.teacher_classes (
  assignment_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  teacher_id    integer NOT NULL,
  class_id      integer NOT NULL,
  school_id     integer NOT NULL,
  subject_id    integer NOT NULL REFERENCES public.subjects(subject_id),
  UNIQUE (teacher_id, class_id, subject_id),
  FOREIGN KEY (class_id, school_id)   REFERENCES public.classes(class_id, school_id),
  FOREIGN KEY (teacher_id, school_id) REFERENCES public.teachers(teacher_id, school_id)
);

CREATE TABLE public.students (
  student_id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id           integer NOT NULL UNIQUE REFERENCES public.users(user_id),
  parent_id         integer NOT NULL REFERENCES public.parents(parent_id),
  school_id         integer NOT NULL REFERENCES public.schools(school_id),
  date_of_birth     date,
  gender            varchar(30),
  address           text,
  registration_date date DEFAULT CURRENT_DATE,
  UNIQUE (student_id, school_id)
);
-- NOTE: parent_id is NOT NULL (as in your original). If some students are adults
-- with no parent on file, run:  ALTER TABLE students ALTER COLUMN parent_id DROP NOT NULL;

-- ---------- STUDENT INFORMATION FORM ----------
-- One survey answer per student (age comes from students.date_of_birth, school from school_id)
CREATE TABLE public.student_survey (
  student_id         integer PRIMARY KEY REFERENCES public.students(student_id) ON DELETE CASCADE,
  school_level       varchar(20) NOT NULL
                     CHECK (school_level IN ('primary', 'high_school')),
  grade_level        varchar(40) NOT NULL,
  CHECK (grade_level IN (
    '1st primary','2nd primary','3rd primary',
    '4th primary','5th primary','6th primary',
    '7th grade','8th grade','9th grade','10th grade',
    '11th grade','12th grade'
  )),
  field_of_study     varchar(120),
  other_hobbies      text,
  needs_details      text,
  difficulty_level   smallint CHECK (difficulty_level BETWEEN 1 AND 5),
  help_wanted        text,
  consent            boolean NOT NULL CHECK (consent),
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hobbies        (id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, label varchar(80) NOT NULL UNIQUE);
CREATE TABLE public.special_needs  (id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, label varchar(80) NOT NULL UNIQUE);
CREATE TABLE public.study_problems (id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, label varchar(80) NOT NULL UNIQUE);

CREATE TABLE public.student_hobbies (
  student_id integer REFERENCES public.students(student_id) ON DELETE CASCADE,
  hobby_id   integer REFERENCES public.hobbies(id)          ON DELETE CASCADE,
  PRIMARY KEY (student_id, hobby_id)
);
CREATE TABLE public.student_special_needs (
  student_id integer REFERENCES public.students(student_id)    ON DELETE CASCADE,
  need_id    integer REFERENCES public.special_needs(id)       ON DELETE CASCADE,
  PRIMARY KEY (student_id, need_id)
);
CREATE TABLE public.student_study_problems (
  student_id integer REFERENCES public.students(student_id)    ON DELETE CASCADE,
  problem_id integer REFERENCES public.study_problems(id)      ON DELETE CASCADE,
  PRIMARY KEY (student_id, problem_id)
);
-- "Most difficult subjects" reuses your subjects table
CREATE TABLE public.student_difficult_subjects (
  student_id integer REFERENCES public.students(student_id)    ON DELETE CASCADE,
  subject_id integer REFERENCES public.subjects(subject_id)    ON DELETE CASCADE,
  PRIMARY KEY (student_id, subject_id)
);

CREATE INDEX idx_students_school     ON public.students(school_id);
CREATE INDEX idx_survey_created      ON public.student_survey(created_at DESC);

-- ---------- SEED DATA (checkbox options) ----------
INSERT INTO public.hobbies(label) VALUES
 ('Sports'),('Music'),('Reading'),('Video games'),('Programming'),
 ('Drawing / art'),('Travel'),('Movies / series'),('Volunteering');

INSERT INTO public.subjects(subject_name, school_level) VALUES
 ('Mathematics', 'primary'), ('French', 'primary'), ('Arabic', 'primary'),
 ('Science', 'primary'), ('History and geography', 'primary'),
 ('Mathematics', 'high_school'), ('French', 'high_school'),
 ('English', 'high_school'), ('Natural sciences', 'high_school'),
 ('Physics', 'high_school'), ('Chemistry', 'high_school'),
 ('History and geography', 'high_school'), ('Computer science', 'high_school')
ON CONFLICT (subject_name, school_level) DO NOTHING;

INSERT INTO public.special_needs(label) VALUES
 ('None'),('Learning difficulty'),('Physical disability'),
 ('Visual / hearing disability'),('Psychological support'),
 ('Financial difficulties'),('Exam accommodations');

INSERT INTO public.study_problems(label) VALUES
 ('Lack of motivation'),('Organization / time management'),
 ('Comprehension difficulties'),('Stress / anxiety'),
 ('Concentration problems'),('Lack of resources / materials'),
 ('Language problems'),('Other');

-- ---------- OVERVIEW VIEW (one row per student) ----------
CREATE VIEW public.v_student_survey AS
SELECT
  s.student_id,
  u.first_name, u.last_name, u.email, u.phone,
  date_part('year', age(s.date_of_birth))::int AS age,
  s.gender, sc.school_name, sc.city,
  sv.school_level, sv.grade_level, sv.field_of_study,
  sv.other_hobbies, sv.needs_details,
  sv.difficulty_level, sv.help_wanted, sv.created_at,
  COALESCE((SELECT array_agg(h.label ORDER BY h.label) FROM student_hobbies x
            JOIN hobbies h ON h.id = x.hobby_id WHERE x.student_id = s.student_id), '{}') AS hobbies,
  COALESCE((SELECT array_agg(n.label ORDER BY n.label) FROM student_special_needs x
            JOIN special_needs n ON n.id = x.need_id WHERE x.student_id = s.student_id), '{}') AS special_needs,
  COALESCE((SELECT array_agg(p.label ORDER BY p.label) FROM student_study_problems x
            JOIN study_problems p ON p.id = x.problem_id WHERE x.student_id = s.student_id), '{}') AS study_problems,
  COALESCE((SELECT array_agg(j.subject_name ORDER BY j.subject_name) FROM student_difficult_subjects x
            JOIN subjects j ON j.subject_id = x.subject_id WHERE x.student_id = s.student_id), '{}') AS difficult_subjects
FROM students s
JOIN users u          ON u.user_id   = s.user_id
JOIN schools sc       ON sc.school_id = s.school_id
LEFT JOIN student_survey sv ON sv.student_id = s.student_id;
