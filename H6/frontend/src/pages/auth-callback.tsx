import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { trackEvent } from "@/lib/analytics";

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const success = searchParams.get("success");
    const error = searchParams.get("error");

    if (success === "1") {
      setStatus("success");
      trackEvent("oauth_login");
      // Redirect to home after brief delay to show success state
      const timer = setTimeout(() => {
        navigate("/", { replace: true });
      }, 1000);
      return () => clearTimeout(timer);
    }

    if (error) {
      setStatus("error");
      const messages: Record<string, string> = {
        access_denied: "Авторизация отменена",
        auth_failed: "Ошибка авторизации. Попробуйте снова.",
        missing_params: "Некорректный ответ от Google",
      };
      setErrorMessage(messages[error] || "Произошла ошибка при входе");
    } else {
      // No params — likely direct navigation
      setStatus("error");
      setErrorMessage("Некорректный запрос");
    }
  }, [searchParams, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-xl">
            {status === "loading" && "Авторизация..."}
            {status === "success" && "Вход выполнен"}
            {status === "error" && "Ошибка"}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          {status === "loading" && (
            <div className="flex justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          )}
          {status === "success" && (
            <p className="text-muted-foreground">Перенаправление...</p>
          )}
          {status === "error" && (
            <div className="space-y-4">
              <p className="text-sm text-destructive">{errorMessage}</p>
              <button
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
