import { QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'
import { RouterProvider } from 'react-router-dom'
import { BoundaryFallback } from '@/app/boundary-fallback'
import { router } from '@/app/router'
import { queryClient } from '@/lib/query-client'

export function AppProviders() {
  return (
    <ErrorBoundary FallbackComponent={BoundaryFallback}>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
