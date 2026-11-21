import { Router } from "express";
import { z } from "zod";
import { pool } from "../db.js";

const router = Router();

const ids = z.array(z.number().int().positive()).default([]);
const schema = z.object({
  full_name: z.string().trim().min(2).max(120),
  age: z.number().int().min(10).max(99),
  contact: z.string().trim().max(120).optional().default(""),
  school: z.string().trim().min(2).max(150),
  field_of_study: z.string().trim().max(120).optional().default(""),
  level: z.string().trim().max(40).optional().default(""),
  other_hobbies: z.string().trim().max(500).optional().default(""),
  needs_details: z.string().trim().max(1000).optional().default(""),
  difficult_subjects: z.string().trim().max(500).optional().default(""),
  difficulty_level: z.number().int().min(1).max(5).default(3),
  help_wanted: z.string().trim().max(1000).optional().default(""),
  hobbies: ids,
  special_needs: ids,
  study_problems: ids,
  difficult_subject_ids: ids,
  consent: z.literal(true),
});

const requireAdmin = (req, res, next) =>
  req.get("x-admin-key") === process.env.ADMIN_KEY
    ? next()
    : res.status(401).json({ error: "Unauthorized" });

// Options for the checkboxes
router.get("/options", async (_req, res) => {
  const [h, n, p] = await Promise.all([
    pool.query("SELECT id, label FROM hobbies ORDER BY id"),
    pool.query("SELECT id, label FROM special_needs ORDER BY id"),
    pool.query("SELECT id, label FROM study_problems ORDER BY id"),
  ]);
  const s = await pool.query(
    "SELECT subject_id AS id, subject_name AS label, school_level FROM subjects ORDER BY school_level, subject_name"
  );
  res.json({
    hobbies: h.rows,
    special_needs: n.rows,
    study_problems: p.rows,
    subjects: s.rows,
  });
});

// Submit a form
router.post("/", async (req, res) => {
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: parsed.error.flatten() });
  const d = parsed.data;

  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(
      `INSERT INTO students (full_name, age, contact, school, field_of_study, level,
         other_hobbies, needs_details, difficult_subjects, difficulty_level, help_wanted, consent)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,TRUE) RETURNING id`,
      [d.full_name, d.age, d.contact, d.school, d.field_of_study, d.level,
       d.other_hobbies, d.needs_details, d.difficult_subjects, d.difficulty_level, d.help_wanted]
    );
    const id = rows[0].id;
    await client.query(
      "INSERT INTO student_hobbies SELECT $1, unnest($2::int[])", [id, d.hobbies]);
    await client.query(
      "INSERT INTO student_special_needs SELECT $1, unnest($2::int[])", [id, d.special_needs]);
    await client.query(
      "INSERT INTO student_study_problems SELECT $1, unnest($2::int[])", [id, d.study_problems]);
    await client.query(
      "INSERT INTO student_difficult_subjects SELECT $1, unnest($2::int[])",
      [id, d.difficult_subject_ids]
    );
    await client.query("COMMIT");
    res.status(201).json({ id });
  } catch (e) {
    await client.query("ROLLBACK");
    console.error(e);
    res.status(500).json({ error: "Server error" });
  } finally {
    client.release();
  }
});

// Admin: list all responses
router.get("/", requireAdmin, async (_req, res) => {
  const { rows } = await pool.query("SELECT * FROM v_student_overview ORDER BY created_at DESC");
  res.json(rows);
});

// Admin: quick stats
router.get("/stats", requireAdmin, async (_req, res) => {
  const [total, schools, problems] = await Promise.all([
    pool.query("SELECT COUNT(*)::int AS total, ROUND(AVG(age),1) AS avg_age FROM students"),
    pool.query("SELECT school, COUNT(*)::int AS nb FROM students GROUP BY school ORDER BY nb DESC"),
    pool.query(`SELECT p.label, COUNT(*)::int AS nb FROM student_study_problems sp
                JOIN study_problems p ON p.id = sp.problem_id GROUP BY p.label ORDER BY nb DESC`),
  ]);
  res.json({ ...total.rows[0], schools: schools.rows, problems: problems.rows });
});

export default router;
