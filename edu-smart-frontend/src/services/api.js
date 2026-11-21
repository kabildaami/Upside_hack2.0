const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('edu_smart_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  const text = await response.text()
  const data = text ? JSON.parse(text) : null

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Something went wrong')
  }
  return data
}
