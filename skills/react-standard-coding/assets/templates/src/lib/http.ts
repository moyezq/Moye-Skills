import { useSessionStore } from '@/stores/session-store'

export class HttpError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'HttpError'
    this.status = status
  }
}

export async function http<T>(path: string, init: RequestInit = {}): Promise<T> {
  const base = import.meta.env.VITE_API_BASE ?? ''
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${base}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })

  if (response.status === 401) {
    useSessionStore.getState().clearUser()
    throw new HttpError(401, 'Unauthorized')
  }
  if (!response.ok) {
    throw new HttpError(response.status, response.statusText)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
