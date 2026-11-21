import { useState } from 'react'

export default function PasswordInput({ label = 'Password', ...props }) {
  const [visible, setVisible] = useState(false)
  return (
    <label className="field">
      <span>{label}</span>
      <div className="password-wrap">
        <input {...props} type={visible ? 'text' : 'password'} />
        <button type="button" onClick={() => setVisible((value) => !value)} aria-label={visible ? 'Hide password' : 'Show password'}>
          {visible ? 'Hide' : 'Show'}
        </button>
      </div>
    </label>
  )
}
