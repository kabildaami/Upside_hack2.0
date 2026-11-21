import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AuthLayout from '../../components/auth/AuthLayout'
import FormInput from '../../components/auth/FormInput'
import PasswordInput from '../../components/auth/PasswordInput'
import { useAuth } from '../../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      navigate(user.role === 'director' ? '/director/pending-accounts' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout mode="login">
      <div className="form-heading">
        <span className="step-label">WELCOME BACK</span>
        <h2>Sign in to Edu Smart</h2>
        <p>Use your school account to continue.</p>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <FormInput label="Email address" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@school.edu" required />
        <PasswordInput value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required />
        <div className="form-row">
          <label className="check"><input type="checkbox" /> <span>Remember me</span></label>
          <button type="button" className="text-button">Forgot password?</button>
        </div>
        {error && <div className="alert error" role="alert">{error}</div>}
        <button className="primary-button" type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'} <span>→</span></button>
      </form>
    </AuthLayout>
  )
}
