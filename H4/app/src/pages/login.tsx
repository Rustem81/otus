import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/stores/auth";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const { login, register, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok = isRegister ? await register(email, password) : await login(email, password);
    if (ok) {
      if (isRegister) {
        setIsRegister(false);
      } else {
        const onboarded = localStorage.getItem("onboarding_completed");
        navigate(onboarded === "true" ? "/" : "/onboarding");
      }
    }
  };

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">MEXC P2P Aggregator</CardTitle>
        <CardDescription>
          {isRegister ? "Создание аккаунта" : "Вход в систему"}
        </CardDescription>
        <Badge variant="outline" className="mx-auto mt-2 border-yellow-500/50 text-yellow-500 text-[10px]">READ-ONLY</Badge>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="test@test.com" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Минимум 8 символов" required minLength={8} />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Загрузка..." : isRegister ? "Зарегистрироваться" : "Войти"}
          </Button>
          <Button type="button" variant="ghost" className="w-full" onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? "Уже есть аккаунт" : "Создать аккаунт"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
