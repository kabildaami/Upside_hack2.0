"""Consent-aware session event example for your future frontend adapter."""
import argparse
from services.analytics import start_session, log_event, end_session,pacing

def main():
 p=argparse.ArgumentParser();p.add_argument('--student-id',type=int,required=True);p.add_argument('--thread-id',default='timing-demo')
 a=p.parse_args()
 r=start_session(a.student_id,a.thread_id,'Mathematics');sid=r['id']
 print('Session id:',sid)
 print('Log a five minute completed activity:',log_event(a.student_id,sid,'activity_completed',300))
 print('Log a two minute break:',log_event(a.student_id,sid,'break_ended',120))
 print('End:',end_session(a.student_id,sid))
 print('Pacing:',pacing(a.student_id))
if __name__=='__main__':main()
