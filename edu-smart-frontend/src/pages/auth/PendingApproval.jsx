import { Link } from 'react-router-dom'
import AuthLayout from '../../components/auth/AuthLayout'

export default function PendingApproval() {
  return (
    <AuthLayout mode="login">
      <div className="pending-card">
        <div className="pending-icon">✓</div>
        <span className="step-label">APPLICATION RECEIVED</span>
        <h2>Approval pending</h2>
        <p>Your account has been sent to the school director. You’ll receive access once it is approved.</p>
        <Link className="primary-button" to="/login">Back to sign in</Link>
      </div>
    </AuthLayout>
  )
}
