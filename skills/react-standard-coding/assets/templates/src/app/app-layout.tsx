import { Outlet } from 'react-router-dom'

export function AppLayout() {
  return (
    <div className="min-h-svh">
      <Outlet />
    </div>
  )
}
