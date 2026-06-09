import { useEffect, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { trackEvent } from "@/lib/analytics";

const ERROR_MESSAGES: Record<string, string> = {
  access_denied: "Авторизация отменена",
  auth_failed: "Ошибка авторизации. Попробуйте снова.",
  missing_params: "Некорректный ответ от Google",
};

function getCallbackState(searchParams: URLSearchParams): {
  status: "success" | "error";
  errorMessage: string;
} {
  const success = searchParams.get("success");
  const error = searchParams.get("error");

  if (success === "1") {
    return { status: "success", errorMessage: "" };
  }

  if (error) {
    return {
      status: "error",
      errorMessage: ERROR_MESSAGES[error] ?? "Произошла ошибка при входе",
    };
  }

  return { status: "error", errorMessage: "Некорректный запрос" };
}

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const { status, errorMessage } = useMemo(
    () => getCallbackState(searchParams),
    [searchParams],
  );

  useEffect(() => {
    if (status !== "success") {
      return;
    }

    trackEvent("oauth_login");
    const timer = setTimeout(() => {
      navigate("/", { replace: true });
    }, 1000);
    return () => clearTimeout(timer);
  }, [status, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-xl">
            {status === "success" && "Вход выполнен"}
            {status === "error" && "Ошибка"}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          {status === "success" && (
            <p className="text-muted-foreground">Перенаправление...</p>
          )}
          {status === "error" && (
            <div className="space-y-4">
              <p className="text-sm text-destructive">{errorMessage}</p>
              <button
                type="button"
                onClick={() => navigate("/login", { replace: true })}
                className="text-sm text-primary underline hover:no-underline"
              >
                Вернуться на страницу входа
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
