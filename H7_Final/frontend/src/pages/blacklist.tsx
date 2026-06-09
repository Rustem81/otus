import { useState, useEffect } from "react";
import { CheckCircle, ArrowLeft, Unlock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { apiGet, apiDelete } from "@/lib/api";
import { Link } from "react-router-dom";

interface BlacklistEntry { merchant_id: string; created_at: string | null; }

export function BlacklistPage() {
  const [items, setItems] = useState<BlacklistEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<{ items: BlacklistEntry[] }>("/api/v1/blacklist").then((d) => setItems(d.items)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const unblock = async (id: string) => {
    try {
      await apiDelete(`/api/v1/blacklist/${id}`);
      setItems((prev) => prev.filter((e) => e.merchant_id !== id));
    } catch { /* silent */ }
  };

  if (loading) return <div className="flex justify-center py-16"><div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" /></div>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <h2 className="text-xl font-bold">Чёрный список</h2>
        <Badge variant="outline" className="border-destructive/50 text-destructive">Объявления скрыты</Badge>
      </div>

      {items.length === 0 ? (
        <Card className="py-16 text-center"><CardContent>
          <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
          <h3 className="mt-4 text-lg font-semibold">Чёрный список пуст</h3>
          <p className="mt-1 text-sm text-muted-foreground">Заблокируйте мерчанта из карточки объявления</p>
          <Button variant="outline" className="mt-4" asChild><Link to="/"><ArrowLeft className="mr-2 h-4 w-4" />К объявлениям</Link></Button>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((e) => (
            <Card key={e.merchant_id}><CardContent className="flex items-center gap-3 p-4">
              <Avatar className="h-10 w-10 bg-destructive/20"><AvatarFallback className="text-destructive text-xs">BL</AvatarFallback></Avatar>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-mono truncate">{e.merchant_id.slice(0, 12)}...</div>
                <div className="text-xs text-muted-foreground">{e.created_at ? new Date(e.created_at).toLocaleDateString("ru-RU") : "—"}</div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => unblock(e.merchant_id)}><Unlock className="h-4 w-4 text-green-400" /></Button>
            </CardContent></Card>
          ))}
        </div>
      )}
    </div>
  );
}
