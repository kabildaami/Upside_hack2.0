import {useState} from 'react';
import {ArrowRight, UserRoundPlus} from 'lucide-react';
import {StudentAdmission} from './StudentAdmission';
import './student-admission.css';

/** Public registration entry rendered immediately after the *active* login form.
 * Self-contained state deliberately avoids touching EduNova's App login hooks. */
export function PublicAdmissionEntry(){
  const [open,setOpen]=useState(false);
  return <>
    <div className="ad-entry-divider" aria-hidden="true"><span>NEW TO EDUNOVA?</span></div>
    <button type="button" className="ad-signup-entry" onClick={()=>setOpen(true)}
      aria-haspopup="dialog" aria-label="Sign up: request student admission">
      <span className="ad-entry-symbol"><UserRoundPlus size={20}/></span>
      <span className="ad-entry-text"><strong>New student? Sign up</strong><small>Request admission to Exellence Academy</small></span>
      <ArrowRight className="ad-entry-arrow" size={18}/>
    </button>
    {open&&<StudentAdmission onClose={()=>setOpen(false)}/>}
  </>;
}
