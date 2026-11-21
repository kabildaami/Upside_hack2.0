CREATE TABLE parents (
  id SERIAL PRIMARY KEY, name TEXT, email TEXT, phone TEXT
);
CREATE TABLE students (
  id SERIAL PRIMARY KEY, name TEXT NOT NULL,
  school_level TEXT CHECK (school_level IN ('primary','high_school')),
  hobbies TEXT, difficulties TEXT,
  parent_id INT REFERENCES parents(id)
);
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id),
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE messages (
  id SERIAL PRIMARY KEY, conversation_id INT REFERENCES conversations(id),
  role TEXT CHECK (role IN ('user','assistant')), content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE memory (
  student_id INT PRIMARY KEY REFERENCES students(id), summary TEXT
);
CREATE TABLE alerts (
  id SERIAL PRIMARY KEY, student_id INT REFERENCES students(id),
  level TEXT, sent_to TEXT, status TEXT, created_at TIMESTAMPTZ DEFAULT now()
);
-- demo data
INSERT INTO parents(name,email) VALUES ('Parent Demo','parent@example.com');
INSERT INTO students(name,school_level,hobbies,difficulties,parent_id)
VALUES ('Sami','high_school','football, music','low confidence',1);
