import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { apiPost } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const BANKS = ["Сбербанк", "Тинькофф", "Альфа-Банк", "Райффайзен", "СБП", "ВТБ"];
const RISKS = [
  { value: "low", label: "Консервативный", desc: "Только мерчанты с низким риском (1–3)" },
  { value: "medium", label: "Умеренный", desc: "Низкий и средний риск (1–7)" },
  { value: "high", label: "Агрессивный", desc: "Все мерчанты без ограничений" },
];

export function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [banks, setBanks] = useState<string[]>([]);
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [risk, setRisk] = useState("medium");
  const [commPct, setCommPct] = useState("");
  const [commFix, setCommFix] = useState("");
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const toggleBank = (b: string) => setBanks((prev) => prev.includes(b) ? prev.filter((x) => x !== b) : [...prev, b]);

  const complete = async (skip = false) => {
    setSaving(true);
    try {
      await apiPost("/api/v1/profile/onboarding", skip ? { payment_methods: [], risk_profile: "medium" } : {
        payment_methods: banks, min_amount: minAmount ? Number(minAmount) : null, max_amount: maxAmount ? Number(maxAmount) : null,
        risk_profile: risk, commission_percent: commPct ? Number(commPct) : null, commission_fixed: commFix ? Number(commFix) : null,
      });
      localStorage.setItem("onboarding_completed", "true");
      if (user) (user as unknown as Record<string, unknown>).onboarding_completed = true;
      navigate("/");
    } catch { /* silent */ }
    finally { setSaving(false); }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Настройка профиля</CardTitle>
          <p className="text-sm text-muted-foreground">Шаг {step} из 4</p>
          <Progress value={(step / 4) * 100} className="mt-2" />
        </CardHeader>
        <CardContent className="space-y-4">
          {step === 1 && (
            <div><Label className="mb-3 block">Выберите банки</Label><div className="space-y-2">{BANKS.map((b) => (
              <label key={b} className="flex items-center gap-2 text-sm"><Checkbox checked={banks.includes(b)} onCheckedChange={() => toggleBank(b)} />{b}</label>
            ))}</div></div>
          )}
          {step === 2 && (
            <div className="space-y-3"><Label>Диапазон сумм (₽)</Label>
              <div className="grid grid-cols-2 gap-3"><Input type="number" placeholder="От" value={minAmount} onChange={(e) => setMinAmount(e.target.value)} /><Input type="number" placeholder="До" value={maxAmount} onChange={(e) => setMaxAmount(e.target.value)} /></div>
            </div>
          )}
          {step === 3 && (
            <div className="space-y-3">{RISKS.map((r) => (
              <button key={r.value} onClick={() => setRisk(r.value)}
                className={`w-full rounded-lg border p-3 text-left transition-colors ${risk === r.value ? "border-primary bg-primary/10" : "border-border hover:bg-muted"}`}>
                <div className="font-medium">{r.label}</div><div className="text-xs text-muted-foreground">{r.desc}</div>
              </button>
            ))}</div>
          )}
          {step === 4 && (
            <div className="space-y-3"><Label>Комиссии банка (опционально)</Label>
              <Input type="number" placeholder="Комиссия (%)" value={commPct} onChange={(e) => setCommPct(e.target.value)} />
              <Input type="number" placeholder="Фикс. комиссия (₽)" value={commFix} onChange={(e) => setCommFix(e.target.value)} />
              <p className="text-xs text-muted-foreground">Можно указать позже в профиле</p>
            </div>
          )}

          <div className="flex justify-between pt-2">
            {step > 1 ? <Button variant="ghost" onClick={() => setStep((s) => s - 1)}>Назад</Button> : <div />}
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => complete(true)}>Пропустить</Button>
              {step < 4 ? <Button onClick={() => setStep((s) => s + 1)}>Далее</Button> : <Button onClick={() => complete(false)} disabled={saving}>{saving ? "..." : "Завершить"}</Button>}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
