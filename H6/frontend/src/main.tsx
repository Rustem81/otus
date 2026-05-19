import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.tsx'
import { initMetrika } from './lib/analytics'

// Initialize Sentry (conditional on DSN being set)
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    integrations: [
      Sentry.browserTracingIntegration(),
    ],
    tracesSampleRate: 1.0,
    environment: import.meta.env.MODE,
  })
}

initMetrika()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
