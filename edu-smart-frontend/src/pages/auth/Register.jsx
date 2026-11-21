import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AuthLayout from '../../components/auth/AuthLayout'
import FormInput from '../../components/auth/FormInput'
import PasswordInput from '../../components/auth/PasswordInput'
import { useAuth } from '../../context/AuthContext'

const roles = [
  ['student', 'Student', 'I am learning'],
  ['parent', 'Parent', 'I support a learner'],
  ['teacher', 'Teacher', 'I teach a class'],
  ['director', 'Director', 'I manage a school'],
]

export default function Register() {
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', phone: '', role: 'student', level: '', parent_email: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const update = (field) => (event) => setForm((value) => ({ ...value, [field]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register({
        ...form,
        profile_data: { level: form.level || null, school_level: form.level || null },
      })
      navigate('/pending-approval')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout mode="register">
      <div className="form-heading">
        <span className="step-label">JOIN EDU SMART</span>
        <h2>Create your account</h2>
        <p>Tell us who you are and choose your level.</p>
      </div>
      <form className="auth-form register-form" onSubmit={submit}>
        <div className="role-grid">
          {roles.map(([value, label, caption]) => (
            <button type="button" key={value} className={`role-option ${form.role === value ? 'selected' : ''}`} onClick={() => setForm((current) => ({ ...current, role: value }))}>
              <strong>{label}</strong><small>{caption}</small>
            </button>
          ))}
        </div>
        <div className="form-grid">
          <FormInput label="First name" value={form.first_name} onChange={update('first_name')} placeholder="First name" required />
          <FormInput label="Last name" value={form.last_name} onChange={update('last_name')} placeholder="Last name" required />
        </div>
        <FormInput label="Email address" type="email" value={form.email} onChange={update('email')} placeholder="name@school.edu" required />
        <div className="form-grid">
          <PasswordInput value={form.password} onChange={update('password')} placeholder="At least 8 characters" minLength={8} required />
          <FormInput label="Phone number" type="tel" value={form.phone} onChange={update('phone')} placeholder="+213 ..." />
        </div>
        {form.role === 'student' && (
          <label className="field">
            <span>Level</span>
            <select value={form.level} onChange={update('level')} required>
              <option value="">Select your level</option>
              <option>Primary School</option>
              <option>Middle School</option>
              <option>High School</option>
              <option>University</option>
            </select>
          </label>
        )}
        {form.role === 'student' && (
          <FormInput label="Parent email" type="email" value={form.parent_email} onChange={update('parent_email')} placeholder="parent@email.com" required />
        )}
        {error && <div className="alert error" role="alert">{error}</div>}
        <button className="primary-button" type="submit" disabled={loading}>{loading ? 'Creating account...' : 'Create account'} <span>→</span></button>
      </form>
    </AuthLayout>
  )
}
