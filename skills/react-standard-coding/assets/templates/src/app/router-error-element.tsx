import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

export function RouterErrorElement() {
  const error = useRouteError()
  const message = isRouteErrorResponse(error)
    ? error.statusText
    : error instanceof Error
      ? error.message
      : '页面出错'
  return (
    <main className="p-6">
      <p>{message}</p>
    </main>
  )
}
