import * as Sentry from '@sentry/react'

function ErrorFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="max-w-md text-center space-y-4">
        <h1 className="text-2xl font-bold text-foreground">
          Что-то пошло не так
        </h1>
        <p className="text-muted-foreground">
          Произошла непредвиденная ошибка. Мы уже работаем над её устранением.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Перезагрузить страницу
        </button>
      </div>
    </div>
  )
}

export function AppErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <Sentry.ErrorBoundary fallback={<ErrorFallback />}>
      {children}
    </Sentry.ErrorBoundary>
  )
}
