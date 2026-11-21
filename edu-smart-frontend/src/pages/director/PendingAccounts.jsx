import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '../../services/api'
import { useAuth } from '../../context/AuthContext'

export default function PendingAccounts() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { logout } = useAuth()
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    try {
      setAccounts(await apiRequest('/users/pending'))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const decide = async (account, action) => {
    try {
      await apiRequest(`/users/${account.id}/${action}`, { method: 'POST' })
      setAccounts((current) => current.filter((item) => item.id !== account.id))
    } catch (err) {
      setError(err.message)
    }
  }

  const signOut = () => {
    logout()
    navigate('/login')
  }

  return (
    <main className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="brand dashboard-brand"><span className="brand-mark">E</span><span>Edu Smart</span></div>
        <nav>
          <button className="nav-item active">Pending accounts <span>{accounts.length}</span></button>
        </nav>
        <button className="nav-item sign-out" onClick={signOut}>Sign out</button>
      </aside>
      <section className="dashboard-content">
        <header className="dashboard-header">
          <div><span className="step-label">DIRECTOR SPACE</span><h1>Pending accounts</h1></div>
          <button className="refresh-button" onClick={load}>Refresh</button>
        </header>
        {error && <div className="alert error" role="alert">{error}</div>}
        {loading ? (
          <div className="empty-state">Loading accounts...</div>
        ) : accounts.length === 0 ? (
          <div className="empty-state"><div className="pending-icon">✓</div><h2>All caught up</h2><p>There are no accounts waiting for approval.</p></div>
        ) : (
          <div className="account-list">
            {accounts.map((account) => (
              <article className="account-row" key={account.id}>
                <div className="avatar">{account.full_name?.charAt(0) || 'U'}</div>
                <div className="account-info"><h3>{account.full_name}</h3><p>{account.email}</p></div>
                <span className="role-badge">{account.role}</span>
                <div className="account-actions">
                  <button className="reject-button" onClick={() => decide(account, 'reject')}>Reject</button>
                  <button className="approve-button" onClick={() => decide(account, 'approve')}>Approve</button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}
