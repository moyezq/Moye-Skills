import type { FallbackProps } from 'react-error-boundary'

export function BoundaryFallback({ error, resetErrorBoundary }: FallbackProps) {
  const message = error instanceof Error ? error.message : '页面出错'
  return (
    <main className="p-6">
      <p>{message}</p>
      <button type="button" onClick={resetErrorBoundary}>
        重试
      </button>
    </main>
  )
}
