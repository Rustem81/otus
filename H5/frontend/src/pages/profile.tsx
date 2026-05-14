import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { apiGet, apiPut } from "@/lib/api";

const BANKS = ["Сбербанк", "Тинькофф", "Альфа-Банк", "Райффайзен", "СБП", "ВТБ", "Газпромбанк"];

export function ProfilePage() {
  const [profile, setProfile] = useState({ payment_methods: [] as string[], min_amount: "", max_amount: "", risk_profile: "medium", commission_percent: "", commission_fixed: "", kyc_level: "", country: "RU", kyc_limit_warning: "" });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiGet<Record<string, unknown>>("/api/v1/profile/").then((d) => {
      setProfile((p) => ({ ...p, ...Object.fromEntries(Object.entries(d).map(([k, v]) => [k, v ?? ""])) }));
    }).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true); setMsg("");
    try {
      // Convert empty strings to null for numeric fields
      const payload = {
        ...profile,
        min_amount: profile.min_amount ? Number(profile.min_amount) : null,
        max_amount: profile.max_amount ? Number(profile.max_amount) : null,
        commission_percent: profile.commission_percent ? Number(profile.commission_percent) : null,
        commission_fixed: profile.commission_fixed ? Number(profile.commission_fixed) : null,
        kyc_limit_warning: profile.kyc_limit_warning ? Number(profile.kyc_limit_warning) : null,
        kyc_level: profile.kyc_level || null,
      };
      await apiPut("/api/v1/profile/", payload);
      setMsg("Сохранено");
    } catch { setMsg("Ошибка"); }
    finally { setSaving(false); }
  };

  const toggleBank = (bank: string) => {
    setProfile((p) => ({
      ...p,
      payment_methods: p.payment_methods.includes(bank) ? p.payment_methods.filter((b) => b !== bank) : [...p.payment_methods, bank],
    }));
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Профиль трейдера</h2>
      <Tabs defaultValue="settings">
        <TabsList><TabsTrigger value="settings">Настройки</TabsTrigger><TabsTrigger value="filters">Фильтры</TabsTrigger><TabsTrigger value="kyc">KYC</TabsTrigger></TabsList>

        <TabsContent value="settings">
          <Card><CardHeader><CardTitle className="text-base">Настройки торговли</CardTitle></CardHeader><CardContent className="space-y-4 max-w-md">
            <div><Label>Банки</Label><div className="mt-2 space-y-2">{BANKS.map((b) => (
              <label key={b} className="flex items-center gap-2 text-sm"><Checkbox checked={profile.payment_methods.includes(b)} onCheckedChange={() => toggleBank(b)} />{b}</label>
            ))}</div></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Мин. сумма (₽)</Label><Input type="number" value={profile.min_amount} onChange={(e) => setProfile((p) => ({ ...p, min_amount: e.target.value }))} /></div>
              <div><Label>Макс. сумма (₽)</Label><Input type="number" value={profile.max_amount} onChange={(e) => setProfile((p) => ({ ...p, max_amount: e.target.value }))} /></div>
            </div>
            <div><Label>Риск-профиль</Label>
              <Select value={profile.risk_profile} onValueChange={(v) => setProfile((p) => ({ ...p, risk_profile: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="low">Консервативный</SelectItem><SelectItem value="medium">Умеренный</SelectItem><SelectItem value="high">Агрессивный</SelectItem></SelectContent>
              </Select></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Комиссия (%)</Label><Input type="number" value={profile.commission_percent} onChange={(e) => setProfile((p) => ({ ...p, commission_percent: e.target.value }))} /></div>
              <div><Label>Фикс. комиссия (₽)</Label><Input type="number" value={profile.commission_fixed} onChange={(e) => setProfile((p) => ({ ...p, commission_fixed: e.target.value }))} /></div>
            </div>
            {msg && <p className={`text-sm ${msg === "Сохранено" ? "text-green-400" : "text-destructive"}`}>{msg}</p>}
            <Button onClick={save} disabled={saving}>{saving ? "Сохранение..." : "Сохранить"}</Button>
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="filters"><Card><CardHeader><CardTitle className="text-base">Фильтры по умолчанию</CardTitle></CardHeader><CardContent><p className="text-sm text-muted-foreground">Автоматически применяются при входе. Настройте на главной странице и нажмите «Сохранить».</p></CardContent></Card></TabsContent>

        <TabsContent value="kyc">
          <Card><CardHeader><CardTitle className="text-base">KYC и лимиты</CardTitle></CardHeader><CardContent className="space-y-4 max-w-md">
            <div><Label>KYC-уровень</Label>
              <Select value={profile.kyc_level || ""} onValueChange={(v) => setProfile((p) => ({ ...p, kyc_level: v }))}>
                <SelectTrigger><SelectValue placeholder="Не указан" /></SelectTrigger>
                <SelectContent><SelectItem value="none">Не пройден</SelectItem><SelectItem value="basic">Базовый</SelectItem><SelectItem value="advanced">Расширенный</SelectItem><SelectItem value="full">Полный</SelectItem></SelectContent>
              </Select></div>
            <div><Label>Страна</Label>
              <Select value={profile.country} onValueChange={(v) => setProfile((p) => ({ ...p, country: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="RU">Россия</SelectItem><SelectItem value="KZ">Казахстан</SelectItem><SelectItem value="BY">Беларусь</SelectItem></SelectContent>
              </Select></div>
            <div><Label>Порог предупреждения (₽)</Label><Input type="number" value={profile.kyc_limit_warning} onChange={(e) => setProfile((p) => ({ ...p, kyc_limit_warning: e.target.value }))} /></div>
            <Button onClick={save} disabled={saving}>{saving ? "Сохранение..." : "Сохранить"}</Button>
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
