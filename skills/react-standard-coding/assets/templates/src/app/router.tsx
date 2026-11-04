import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/app/app-layout'
import { RouterErrorElement } from '@/app/router-error-element'
import { HomePage } from '@/routes/HomePage'
import { NotFoundPage } from '@/routes/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <RouterErrorElement />,
    children: [
      { index: true, element: <HomePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
