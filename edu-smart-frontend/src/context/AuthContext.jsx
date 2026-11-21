import { createContext, useContext, useMemo, useState } from 'react'
import { login as loginRequest, register as registerRequest } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('edu_smart_user')
    return stored ? JSON.parse(stored) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('edu_smart_token'))

  const saveSession = (data) => {
    localStorage.setItem('edu_smart_token', data.access_token)
    localStorage.setItem('edu_smart_user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
  }

  const login = async (email, password) => {
    const data = await loginRequest(email, password)
    saveSession(data)
    return data.user
  }

  const register = async (payload) => {
    const data = await registerRequest(payload)
    saveSession(data)
    return data
  }

  const logout = () => {
    localStorage.removeItem('edu_smart_token')
    localStorage.removeItem('edu_smart_user')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, token, login, register, logout }),
    [user, token],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
