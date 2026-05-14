import { useState, useEffect } from "react";
import { EyeOff, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api";
import { Link } from "react-router-dom";

interface HistoryEntry { advertisement_id: string; viewed_at: string; }

export function HistoryPage() {
  const [items, setItems] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<{ items: HistoryEntry[] }>("/api/v1/history").then((d) => setItems(d.items)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const grouped = items.reduce<Record<string, HistoryEntry[]>>((acc, e) => {
    const date = new Date(e.viewed_at).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
    (acc[date] ??= []).push(e);
    return acc;
  }, {});

  if (loading) return <div className="flex justify-center py-16"><div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" /></div>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <h2 className="text-xl font-bold">История просмотров</h2>
        <Badge variant="outline">Последние 50</Badge>
      </div>

      {items.length === 0 ? (
        <Card className="py-16 text-center"><CardContent>
          <EyeOff className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">Вы ещё не просматривали объявления</h3>
          <p className="mt-1 text-sm text-muted-foreground">Откройте карточку объявления — она появится здесь</p>
          <Button variant="outline" className="mt-4" asChild><Link to="/"><ArrowLeft className="mr-2 h-4 w-4" />К объявлениям</Link></Button>
        </CardContent></Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([date, entries]) => (
            <div key={date}>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">{date}</h3>
              <div className="space-y-2">
                {entries.map((e, i) => (
                  <Card key={i}><CardContent className="flex items-center justify-between p-3">
                    <span className="text-sm font-mono">{e.advertisement_id.slice(0, 12)}...</span>
                    <span className="text-xs text-muted-foreground">{new Date(e.viewed_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}</span>
                  </CardContent></Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
