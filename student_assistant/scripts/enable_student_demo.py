"""Explicit local demo opt-in only. Do not grant consent in real deployments without guardian workflow."""
import argparse
from services.db import require_student,query
from services.student import student_profile

def main():
 p=argparse.ArgumentParser();p.add_argument('--student-id',type=int,required=True)
 p.add_argument('--variant',choices=['junior','senior'],default='junior')
 p.add_argument('--grant-demo-consent',action='store_true',help='Only for fictional/demo students')
 a=p.parse_args();require_student(a.student_id)
 query('''INSERT INTO assistant.student_settings(student_id,age_variant)
  VALUES(%s,%s) ON CONFLICT(student_id) DO UPDATE SET age_variant=EXCLUDED.age_variant,updated_at=now()''',(a.student_id,a.variant),fetch='none')
 if a.grant_demo_consent:
  for purpose in ['learning_memory','pacing_analytics','curriculum_processing']:
   query('''INSERT INTO assistant.student_consents(student_id,purpose,granted) VALUES(%s,%s,true)
      ON CONFLICT(student_id,purpose) DO UPDATE SET granted=true,recorded_at=now()''',(a.student_id,purpose),fetch='none')
 print('Student config:',student_profile(a.student_id))
if __name__=='__main__':main()
