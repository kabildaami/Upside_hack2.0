import { Link } from 'react-router-dom'

export default function AuthLayout({ children, mode = 'login' }) {
  return (
    <main className="auth-shell">
      <section className="auth-brand" aria-label="Edu Smart introduction">
        <Link className="brand" to="/" aria-label="Edu Smart home">
          <span className="brand-mark">E</span>
          <span>Edu Smart</span>
        </Link>
        <div className="brand-copy">
          <span className="eyebrow">A smarter way to learn</span>
          <h1>Every learner.<br />Every level.<br /><em>One platform.</em></h1>
          <p>Manage school activity, track progress and keep your learning community connected.</p>
        </div>
        <div className="brand-orbit orbit-one"></div>
        <div className="brand-orbit orbit-two"></div>
      </section>

      <section className="auth-panel">
        <div className="auth-mobile-brand">
          <span className="brand-mark">E</span>
          <span>Edu Smart</span>
        </div>
        <div className="auth-card">{children}</div>
        {mode === 'login' ? (
          <p className="auth-switch">New to Edu Smart? <Link to="/register">Create an account</Link></p>
        ) : (
          <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
        )}
      </section>
    </main>
  )
}
