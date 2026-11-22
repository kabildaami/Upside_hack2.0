from sqlalchemy import inspect, text
from backend.app.db.session import engine, SessionLocal

EXPECTED_TABLES = {"users", "schools", "parents", "directors", "teachers", "subjects", "classes", "teacher_classes", "students", "student_survey", "hobbies", "special_needs", "study_problems", "student_hobbies", "student_special_needs", "student_study_problems", "student_difficult_subjects"}

def main():
    with engine.connect() as conn:
        print("CONNECTED:", conn.execute(text("SELECT current_database(), current_user, version()" )).one())
    present = set(inspect(engine).get_table_names(schema="public"))
    missing = EXPECTED_TABLES - present
    print(f"TABLES: {len(present & EXPECTED_TABLES)}/{len(EXPECTED_TABLES)} required")
    if missing:
        print("MISSING:", ", ".join(sorted(missing)))
        raise SystemExit("Run sql/initial.sql using psql first.")
    with SessionLocal() as db:
        for table in ("hobbies", "subjects", "special_needs", "study_problems"):
            print(table, db.execute(text(f'SELECT COUNT(*) FROM public.{table}')).scalar_one())
        print("VIEW:", db.execute(text("SELECT count(*) FROM public.v_student_survey")).scalar_one())
    print("SUCCESS: connection, ORM session, tables, seeds, view all work")

if __name__ == "__main__":
    main()
