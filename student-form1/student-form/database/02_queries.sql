-- =====================================================================
-- 03_seed.sql : FICTIONAL test data for the school database + student form
-- Run AFTER 01_schema.sql:  psql -U postgres -d school_db -f 03_seed.sql
-- Subjects, hobbies, special_needs and study_problems are already seeded by 01_schema.sql.
-- password_hash values are placeholders (these accounts cannot log in).
-- =====================================================================
BEGIN;

-- ---------- 1. USERS (2 directors, 8 parents, 6 teachers, 12 students) ----------
INSERT INTO users (first_name, last_name, email, password_hash, phone, role) VALUES
 -- directors
 ('Salma','Gharbi',   'director.primary@school.tn', 'PLACEHOLDER_HASH', '+21671000001', 'director'),
 ('Hichem','Jlassi',  'director.lycee@school.tn',   'PLACEHOLDER_HASH', '+21671000002', 'director'),
 -- parents
 ('Mounir','Ben Ali',   'mounir.benali@mail.tn',    'PLACEHOLDER_HASH', '+21650100001', 'parent'),
 ('Leila','Trabelsi',   'leila.trabelsi@mail.tn',   'PLACEHOLDER_HASH', '+21650100002', 'parent'),
 ('Anis','Mezghani',    'anis.mezghani@mail.tn',    'PLACEHOLDER_HASH', '+21650100003', 'parent'),
 ('Hela','Chaabane',    'hela.chaabane@mail.tn',    'PLACEHOLDER_HASH', '+21650100004', 'parent'),
 ('Nabil','Ferchichi',  'nabil.ferchichi@mail.tn',  'PLACEHOLDER_HASH', '+21650100005', 'parent'),
 ('Samia','Dridi',      'samia.dridi@mail.tn',      'PLACEHOLDER_HASH', '+21650100006', 'parent'),
 ('Walid','Khelifi',    'walid.khelifi@mail.tn',    'PLACEHOLDER_HASH', '+21650100007', 'parent'),
 ('Rim','Hamdi',        'rim.hamdi@mail.tn',        'PLACEHOLDER_HASH', '+21650100008', 'parent'),
 -- teachers
 ('Amel','Ayari',       'amel.ayari@school.tn',     'PLACEHOLDER_HASH', '+21698200001', 'teacher'),
 ('Bechir','Sassi',     'bechir.sassi@school.tn',   'PLACEHOLDER_HASH', '+21698200002', 'teacher'),
 ('Karim','Zouari',     'karim.zouari@school.tn',   'PLACEHOLDER_HASH', '+21698200003', 'teacher'),
 ('Nour','Belhadj',     'nour.belhadj@school.tn',   'PLACEHOLDER_HASH', '+21698200004', 'teacher'),
 ('Slim','Jaziri',      'slim.jaziri@school.tn',    'PLACEHOLDER_HASH', '+21698200005', 'teacher'),
 ('Yosra','Mabrouk',    'yosra.mabrouk@school.tn',  'PLACEHOLDER_HASH', '+21698200006', 'teacher'),
 -- students
 ('Adam','Ben Ali',     'adam.benali@student.school.tn',     'PLACEHOLDER_HASH', NULL, 'student'),
 ('Yasmine','Ben Ali',  'yasmine.benali@student.school.tn',  'PLACEHOLDER_HASH', NULL, 'student'),
 ('Ines','Trabelsi',    'ines.trabelsi@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Omar','Mezghani',    'omar.mezghani@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Lina','Chaabane',    'lina.chaabane@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Mehdi','Ferchichi',  'mehdi.ferchichi@student.school.tn', 'PLACEHOLDER_HASH', NULL, 'student'),
 ('Rania','Dridi',      'rania.dridi@student.school.tn',     'PLACEHOLDER_HASH', NULL, 'student'),
 ('Youssef','Dridi',    'youssef.dridi@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Salma','Khelifi',    'salma.khelifi@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Hamza','Khelifi',    'hamza.khelifi@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Nesrine','Hamdi',    'nesrine.hamdi@student.school.tn',   'PLACEHOLDER_HASH', NULL, 'student'),
 ('Aymen','Hamdi',      'aymen.hamdi@student.school.tn',     'PLACEHOLDER_HASH', NULL, 'student');

-- ---------- 2. SCHOOLS ----------
INSERT INTO schools (school_name, address, city, phone, email, educational_level, director_user_id)
SELECT v.name, v.addr, v.city, v.phone, v.email, v.lvl, u.user_id
FROM (VALUES
  ('Ibn Khaldoun Primary School', 'Avenue de la Liberté', 'Tunis', '+21671111111', 'contact@ibnkhaldoun.school.tn', 'primary',     'director.primary@school.tn'),
  ('Ibn Sina High School',        'Rue de la République', 'Tunis', '+21671222222', 'contact@ibnsina.school.tn',     'high_school', 'director.lycee@school.tn')
) AS v(name, addr, city, phone, email, lvl, director_email)
JOIN users u ON u.email = v.director_email;

-- ---------- 3. DIRECTORS / PARENTS ----------
INSERT INTO directors (user_id)
SELECT user_id FROM users WHERE role = 'director';

INSERT INTO parents (user_id, occupation)
SELECT u.user_id, v.occupation
FROM (VALUES
  ('mounir.benali@mail.tn',   'Engineer'),
  ('leila.trabelsi@mail.tn',  'Teacher'),
  ('anis.mezghani@mail.tn',   'Doctor'),
  ('hela.chaabane@mail.tn',   'Accountant'),
  ('nabil.ferchichi@mail.tn', 'Shop owner'),
  ('samia.dridi@mail.tn',     'Nurse'),
  ('walid.khelifi@mail.tn',   'Taxi driver'),
  ('rim.hamdi@mail.tn',       'Pharmacist')
) AS v(email, occupation)
JOIN users u ON u.email = v.email;

-- ---------- 4. TEACHERS ----------
INSERT INTO teachers (user_id, school_id, specialization, hire_date)
SELECT u.user_id, sc.school_id, v.spec, v.hire::date
FROM (VALUES
  ('amel.ayari@school.tn',    'Ibn Khaldoun Primary School', 'Primary education',        '2015-09-15'),
  ('bechir.sassi@school.tn',  'Ibn Khaldoun Primary School', 'Arabic and science',       '2018-09-10'),
  ('karim.zouari@school.tn',  'Ibn Sina High School',        'Mathematics',              '2012-09-20'),
  ('nour.belhadj@school.tn',  'Ibn Sina High School',        'Physics and chemistry',    '2019-09-12'),
  ('slim.jaziri@school.tn',   'Ibn Sina High School',        'Languages',                '2016-09-14'),
  ('yosra.mabrouk@school.tn', 'Ibn Sina High School',        'Natural sciences',         '2021-09-13')
) AS v(email, school_name, spec, hire)
JOIN users u    ON u.email = v.email
JOIN schools sc ON sc.school_name = v.school_name;

-- ---------- 5. CLASSES ----------
INSERT INTO classes (school_id, class_name, grade_level, academic_year, capacity)
SELECT sc.school_id, v.class_name, v.grade, '2026-2027', v.cap
FROM (VALUES
  ('Ibn Khaldoun Primary School', '3rd primary A', '3rd primary', 28),
  ('Ibn Khaldoun Primary School', '6th primary A', '6th primary', 28),
  ('Ibn Sina High School',        '7th grade A',   '7th grade',   30),
  ('Ibn Sina High School',        '10th grade A',  '10th grade',  30),
  ('Ibn Sina High School',        '12th grade A',  '12th grade',  30)
) AS v(school_name, class_name, grade, cap)
JOIN schools sc ON sc.school_name = v.school_name;

-- ---------- 6. TEACHER ASSIGNMENTS ----------
INSERT INTO teacher_classes (teacher_id, class_id, school_id, subject_id)
SELECT t.teacher_id, c.class_id, c.school_id, sj.subject_id
FROM (VALUES
  ('amel.ayari@school.tn',    'Ibn Khaldoun Primary School', '3rd primary A', 'Mathematics'),
  ('amel.ayari@school.tn',    'Ibn Khaldoun Primary School', '3rd primary A', 'French'),
  ('bechir.sassi@school.tn',  'Ibn Khaldoun Primary School', '6th primary A', 'Arabic'),
  ('bechir.sassi@school.tn',  'Ibn Khaldoun Primary School', '6th primary A', 'Science'),
  ('karim.zouari@school.tn',  'Ibn Sina High School',        '10th grade A',  'Mathematics'),
  ('karim.zouari@school.tn',  'Ibn Sina High School',        '12th grade A',  'Mathematics'),
  ('nour.belhadj@school.tn',  'Ibn Sina High School',        '10th grade A',  'Physics'),
  ('nour.belhadj@school.tn',  'Ibn Sina High School',        '12th grade A',  'Chemistry'),
  ('slim.jaziri@school.tn',   'Ibn Sina High School',        '7th grade A',   'French'),
  ('slim.jaziri@school.tn',   'Ibn Sina High School',        '7th grade A',   'English'),
  ('yosra.mabrouk@school.tn', 'Ibn Sina High School',        '10th grade A',  'Natural sciences')
) AS v(teacher_email, school_name, class_name, subject_name)
JOIN users u    ON u.email = v.teacher_email
JOIN teachers t ON t.user_id = u.user_id
JOIN schools sc ON sc.school_name = v.school_name AND sc.school_id = t.school_id
JOIN classes c  ON c.school_id = sc.school_id AND c.class_name = v.class_name
JOIN subjects sj ON sj.subject_name = v.subject_name AND sj.school_level = sc.educational_level;

-- ---------- 7. STUDENTS ----------
INSERT INTO students (user_id, parent_id, school_id, date_of_birth, gender, address)
SELECT su.user_id, p.parent_id, sc.school_id, v.dob::date, v.gender, v.city
FROM (VALUES
  ('adam.benali@student.school.tn',     'mounir.benali@mail.tn',   'Ibn Khaldoun Primary School', '2018-03-12', 'M', 'Tunis'),
  ('yasmine.benali@student.school.tn',  'mounir.benali@mail.tn',   'Ibn Khaldoun Primary School', '2015-06-20', 'F', 'Tunis'),
  ('ines.trabelsi@student.school.tn',   'leila.trabelsi@mail.tn',  'Ibn Khaldoun Primary School', '2018-01-30', 'F', 'Ariana'),
  ('omar.mezghani@student.school.tn',   'anis.mezghani@mail.tn',   'Ibn Khaldoun Primary School', '2015-11-02', 'M', 'Tunis'),
  ('lina.chaabane@student.school.tn',   'hela.chaabane@mail.tn',   'Ibn Khaldoun Primary School', '2018-07-19', 'F', 'La Marsa'),
  ('mehdi.ferchichi@student.school.tn', 'nabil.ferchichi@mail.tn', 'Ibn Sina High School',        '2013-02-14', 'M', 'Tunis'),
  ('rania.dridi@student.school.tn',     'samia.dridi@mail.tn',     'Ibn Sina High School',        '2010-05-23', 'F', 'Ben Arous'),
  ('youssef.dridi@student.school.tn',   'samia.dridi@mail.tn',     'Ibn Sina High School',        '2008-12-03', 'M', 'Ben Arous'),
  ('salma.khelifi@student.school.tn',   'walid.khelifi@mail.tn',   'Ibn Sina High School',        '2010-09-30', 'F', 'Tunis'),
  ('hamza.khelifi@student.school.tn',   'walid.khelifi@mail.tn',   'Ibn Sina High School',        '2013-06-08', 'M', 'Tunis'),
  ('nesrine.hamdi@student.school.tn',   'rim.hamdi@mail.tn',       'Ibn Sina High School',        '2008-03-17', 'F', 'Ariana'),
  ('aymen.hamdi@student.school.tn',     'rim.hamdi@mail.tn',       'Ibn Sina High School',        '2010-12-21', 'M', 'Ariana')
) AS v(student_email, parent_email, school_name, dob, gender, city)
JOIN users su   ON su.email = v.student_email
JOIN users pu   ON pu.email = v.parent_email
JOIN parents p  ON p.user_id = pu.user_id
JOIN schools sc ON sc.school_name = v.school_name;

-- ---------- 8. FORM ANSWERS (student_survey) ----------
INSERT INTO student_survey (student_id, school_level, grade_level, field_of_study,
                            other_hobbies, needs_details, difficulty_level, help_wanted, consent)
SELECT s.student_id, v.lvl, v.grade, v.field, v.other_hobbies, v.needs_details,
       v.diff, v.help, TRUE
FROM (VALUES
  ('adam.benali@student.school.tn',     'primary',     '3rd primary', NULL::text,         'Football cards',  NULL::text,                      2, 'More reading practice'),
  ('yasmine.benali@student.school.tn',  'primary',     '6th primary', NULL,               'Piano',           NULL,                            3, 'Help with exam stress'),
  ('ines.trabelsi@student.school.tn',   'primary',     '3rd primary', NULL,               NULL,              'Needs to sit near the board',   3, 'Extra help in French'),
  ('omar.mezghani@student.school.tn',   'primary',     '6th primary', NULL,               'Robotics club',   NULL,                            1, NULL),
  ('lina.chaabane@student.school.tn',   'primary',     '3rd primary', NULL,               'Painting',        NULL,                            4, 'Help staying focused in class'),
  ('mehdi.ferchichi@student.school.tn', 'high_school', '7th grade',   NULL,               NULL,              NULL,                            3, 'Tutoring in mathematics'),
  ('rania.dridi@student.school.tn',     'high_school', '10th grade',  'Common core',      'Photography',     NULL,                            4, 'Study method and organization'),
  ('youssef.dridi@student.school.tn',   'high_school', '12th grade',  'Experimental sciences', NULL,        'Needs extra time in exams',     5, 'Support for the baccalaureate'),
  ('salma.khelifi@student.school.tn',   'high_school', '10th grade',  'Common core',      'Volunteering',    NULL,                            2, NULL),
  ('hamza.khelifi@student.school.tn',   'high_school', '7th grade',   NULL,               'Chess',           NULL,                            3, 'Help with English'),
  ('nesrine.hamdi@student.school.tn',   'high_school', '12th grade',  'Mathematics',      'Reading',         NULL,                            4, 'Stress management before exams'),
  ('aymen.hamdi@student.school.tn',     'high_school', '10th grade',  'Common core',      'Coding side projects', NULL,                       2, 'Advanced exercises')
) AS v(student_email, lvl, grade, field, other_hobbies, needs_details, diff, help)
JOIN users u    ON u.email = v.student_email
JOIN students s ON s.user_id = u.user_id;

-- ---------- 9. LINK TABLES ----------
INSERT INTO student_hobbies (student_id, hobby_id)
SELECT s.student_id, h.id
FROM (VALUES
  ('adam.benali@student.school.tn','Sports'), ('adam.benali@student.school.tn','Video games'),
  ('yasmine.benali@student.school.tn','Music'), ('yasmine.benali@student.school.tn','Reading'),
  ('ines.trabelsi@student.school.tn','Drawing / art'),
  ('omar.mezghani@student.school.tn','Programming'), ('omar.mezghani@student.school.tn','Video games'),
  ('lina.chaabane@student.school.tn','Drawing / art'), ('lina.chaabane@student.school.tn','Movies / series'),
  ('mehdi.ferchichi@student.school.tn','Sports'),
  ('rania.dridi@student.school.tn','Travel'), ('rania.dridi@student.school.tn','Music'),
  ('youssef.dridi@student.school.tn','Sports'), ('youssef.dridi@student.school.tn','Video games'),
  ('salma.khelifi@student.school.tn','Volunteering'), ('salma.khelifi@student.school.tn','Reading'),
  ('hamza.khelifi@student.school.tn','Video games'), ('hamza.khelifi@student.school.tn','Sports'),
  ('nesrine.hamdi@student.school.tn','Reading'), ('nesrine.hamdi@student.school.tn','Movies / series'),
  ('aymen.hamdi@student.school.tn','Programming'), ('aymen.hamdi@student.school.tn','Video games')
) AS v(email, label)
JOIN users u    ON u.email = v.email
JOIN students s ON s.user_id = u.user_id
JOIN hobbies h  ON h.label = v.label;

INSERT INTO student_special_needs (student_id, need_id)
SELECT s.student_id, n.id
FROM (VALUES
  ('adam.benali@student.school.tn','None'),
  ('yasmine.benali@student.school.tn','None'),
  ('ines.trabelsi@student.school.tn','Visual / hearing disability'),
  ('omar.mezghani@student.school.tn','None'),
  ('lina.chaabane@student.school.tn','Learning difficulty'),
  ('mehdi.ferchichi@student.school.tn','None'),
  ('rania.dridi@student.school.tn','Financial difficulties'),
  ('youssef.dridi@student.school.tn','Exam accommodations'),
  ('salma.khelifi@student.school.tn','None'),
  ('hamza.khelifi@student.school.tn','Financial difficulties'),
  ('nesrine.hamdi@student.school.tn','Psychological support'),
  ('aymen.hamdi@student.school.tn','None')
) AS v(email, label)
JOIN users u          ON u.email = v.email
JOIN students s       ON s.user_id = u.user_id
JOIN special_needs n  ON n.label = v.label;

INSERT INTO student_study_problems (student_id, problem_id)
SELECT s.student_id, p.id
FROM (VALUES
  ('adam.benali@student.school.tn','Comprehension difficulties'),
  ('yasmine.benali@student.school.tn','Stress / anxiety'),
  ('ines.trabelsi@student.school.tn','Language problems'),
  ('lina.chaabane@student.school.tn','Concentration problems'),
  ('lina.chaabane@student.school.tn','Lack of motivation'),
  ('mehdi.ferchichi@student.school.tn','Comprehension difficulties'),
  ('rania.dridi@student.school.tn','Organization / time management'),
  ('rania.dridi@student.school.tn','Lack of resources / materials'),
  ('youssef.dridi@student.school.tn','Stress / anxiety'),
  ('youssef.dridi@student.school.tn','Concentration problems'),
  ('hamza.khelifi@student.school.tn','Language problems'),
  ('nesrine.hamdi@student.school.tn','Stress / anxiety'),
  ('nesrine.hamdi@student.school.tn','Organization / time management')
) AS v(email, label)
JOIN users u           ON u.email = v.email
JOIN students s        ON s.user_id = u.user_id
JOIN study_problems p  ON p.label = v.label;

INSERT INTO student_difficult_subjects (student_id, subject_id)
SELECT s.student_id, sj.subject_id
FROM (VALUES
  ('adam.benali@student.school.tn','Arabic'),
  ('yasmine.benali@student.school.tn','Mathematics'),
  ('ines.trabelsi@student.school.tn','French'),
  ('lina.chaabane@student.school.tn','Mathematics'),
  ('lina.chaabane@student.school.tn','French'),
  ('mehdi.ferchichi@student.school.tn','Mathematics'),
  ('rania.dridi@student.school.tn','Physics'),
  ('youssef.dridi@student.school.tn','Physics'),
  ('youssef.dridi@student.school.tn','Chemistry'),
  ('hamza.khelifi@student.school.tn','English'),
  ('nesrine.hamdi@student.school.tn','Mathematics'),
  ('aymen.hamdi@student.school.tn','French')
) AS v(email, subject_name)
JOIN users u     ON u.email = v.email
JOIN students s  ON s.user_id = u.user_id
JOIN schools sc  ON sc.school_id = s.school_id
JOIN subjects sj ON sj.subject_name = v.subject_name AND sj.school_level = sc.educational_level;

COMMIT;

-- ---------- QUICK CHECK ----------
SELECT 'users' AS tbl, COUNT(*) FROM users
UNION ALL SELECT 'schools', COUNT(*) FROM schools
UNION ALL SELECT 'teachers', COUNT(*) FROM teachers
UNION ALL SELECT 'classes', COUNT(*) FROM classes
UNION ALL SELECT 'teacher_classes', COUNT(*) FROM teacher_classes
UNION ALL SELECT 'students', COUNT(*) FROM students
UNION ALL SELECT 'student_survey', COUNT(*) FROM student_survey
UNION ALL SELECT 'student_hobbies', COUNT(*) FROM student_hobbies
UNION ALL SELECT 'student_special_needs', COUNT(*) FROM student_special_needs
UNION ALL SELECT 'student_study_problems', COUNT(*) FROM student_study_problems
UNION ALL SELECT 'student_difficult_subjects', COUNT(*) FROM student_difficult_subjects;

SELECT student_id, first_name, last_name, age, school_name, grade_level,
       hobbies, special_needs, study_problems, difficult_subjects
FROM v_student_survey ORDER BY student_id;