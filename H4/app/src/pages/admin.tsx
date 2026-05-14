import { useState, useEffect } from "react";
import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api";

interface HealthData { status: string; dependencies: Record<string, string>; }
interface ErrorStats { total: number; by_type: Record<string, number>; }

const statusIcon = (s: string) => s === "ok" ? <CheckCircle className="h-5 w-5 text-green-400" /> : s === "degraded" ? <AlertTriangle className="h-5 w-5 text-yellow-400" /> : <XCircle className="h-5 w-5 text-red-400" />;
const statusColor = (s: string) => s === "ok" ? "bg-green-500/10 border-green-500/30" : s === "degraded" ? "bg-yellow-500/10 border-yellow-500/30" : "bg-red-500/10 border-red-500/30";

export function AdminPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [errors, setErrors] = useState<ErrorStats | null>(null);

  useEffect(() => {
    apiGet<HealthData>("/health").then(setHealth).catch(() => {});
    apiGet<ErrorStats>("/api/v1/admin/errors").then(setErrors).catch(() => {});
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Панель администратора</h2>

      {/* Health */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 mb-6">
        {health && Object.entries(health.dependencies).map(([name, status]) => (
          <Card key={name} className={`border ${statusColor(status)}`}><CardContent className="flex items-center gap-3 p-4">
            {statusIcon(status)}
            <div><div className="font-medium capitalize">{name}</div><div className="text-xs text-muted-foreground">{status.toUpperCase()}</div></div>
          </CardContent></Card>
        ))}
      </div>

      {/* Errors */}
      <Card><CardHeader><CardTitle className="text-base">Ошибки за 24 часа</CardTitle></CardHeader><CardContent>
        <div className="flex items-center gap-4 mb-4">
          {statusIcon(errors?.total === 0 ? "ok" : "degraded")}
          <div><div className="text-3xl font-bold">{errors?.total ?? 0}</div><div className="text-xs text-muted-foreground">всего ошибок</div></div>
        </div>
        {errors?.by_type && Object.keys(errors.by_type).length > 0 ? (
          <div className="space-y-2">{Object.entries(errors.by_type).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between text-sm"><span>{type}</span><Badge variant="outline">{count}</Badge></div>
          ))}</div>
        ) : <p className="text-sm text-muted-foreground">Ошибок нет</p>}
      </CardContent></Card>
    </div>
  );
}
