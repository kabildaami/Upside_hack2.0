-- Read-only checks for migration + course ingestion
SELECT (SELECT count(*) FROM public.students) AS school_students,
       (SELECT count(*) FROM assistant.course_documents) AS courses,
       (SELECT count(*) FROM assistant.course_chunks) AS indexed_chunks;
SELECT filename, subject, (SELECT count(*) FROM assistant.course_chunks c WHERE c.document_id=d.id) AS chunk_count
 FROM assistant.course_documents d ORDER BY subject;
SELECT student_id,age_variant,preferred_activity_minutes,pacing_opt_in,memory_opt_in
 FROM assistant.student_settings ORDER BY student_id LIMIT 15;
