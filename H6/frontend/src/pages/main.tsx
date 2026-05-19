import { useState, useEffect, useCallback } from "react";
import { RefreshCw, Clock, SearchX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AdCard, type Ad } from "@/components/ad-card";
import { AdDetailDialog } from "@/components/ad-detail-dialog";
import { apiGet, apiPost } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";

interface AdsResponse {
  items: Ad[];
  total: number;
  reference_price: number | null;
  last_updated: string | null;
}

export function MainPage() {
  const [ads, setAds] = useState<Ad[]>([]);
  const [total, setTotal] = useState(0);
  const [refPrice, setRefPrice] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [direction, setDirection] = useState<string>("BUY");
  const [updateAge, setUpdateAge] = useState(0);
  const [selectedAd, setSelectedAd] = useState<Ad | null>(null);

  const fetchAds = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<AdsResponse>(`/api/v1/advertisements?currency=RUB&direction=${direction}&limit=200`);
      setAds(data.items);
      setTotal(data.total);
      setRefPrice(data.reference_price);
      setUpdateAge(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [direction]);

  useEffect(() => { fetchAds(); }, [fetchAds]);
  useEffect(() => {
    const interval = setInterval(fetchAds, 15000);
    return () => clearInterval(interval);
  }, [fetchAds]);
  useEffect(() => {
    const tick = setInterval(() => setUpdateAge((a) => a + 1), 1000);
    return () => clearInterval(tick);
  }, []);

  const bestId = ads.length ? [...ads].sort((a, b) => (b.net_yield ?? 0) - (a.net_yield ?? 0))[0]?.id : null;
  const lowRisk = ads.filter((a) => a.risk_score != null && a.risk_score <= 3).length;

  const handleBlock = async (merchantId: string) => {
    try {
      await apiPost("/api/v1/blacklist", { merchant_id: merchantId });
      trackEvent("blacklist_add", { merchant_id: merchantId });
      setAds((prev) => prev.filter((a) => a.merchant.id !== merchantId));
    } catch { /* silent */ }
  };

  const handleView = async (ad: Ad) => {
    setSelectedAd(ad);
    try { await apiPost("/api/v1/history", { advertisement_id: ad.id }); } catch { /* silent */ }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <h2 className="text-xl font-bold">P2P Объявления</h2>
        <Badge variant="outline" className="border-muted-foreground/30">
          <Clock className="mr-1 h-3 w-3" />{updateAge} сек назад
        </Badge>
        <div className="ml-auto flex items-center gap-2">
          <Select value={direction} onValueChange={(v) => setDirection(v)}>
            <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="BUY">Покупка</SelectItem>
              <SelectItem value="SELL">Продажа</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={fetchAds} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Card><CardContent className="p-3 text-center"><div className="text-xs text-muted-foreground">Объявлений</div><div className="text-lg font-bold">{total}</div></CardContent></Card>
        <Card><CardContent className="p-3 text-center"><div className="text-xs text-muted-foreground">Лучшая цена</div><div className="text-lg font-bold text-green-400">{ads.length ? Math.min(...ads.map((a) => a.price)).toFixed(2) + " ₽" : "—"}</div></CardContent></Card>
        <Card><CardContent className="p-3 text-center"><div className="text-xs text-muted-foreground">Ref. цена</div><div className="text-lg font-bold">{refPrice?.toFixed(2) ?? "—"} ₽</div></CardContent></Card>
        <Card><CardContent className="p-3 text-center"><div className="text-xs text-muted-foreground">Низкий риск</div><div className="text-lg font-bold text-green-400">{lowRisk}</div></CardContent></Card>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error} <Button variant="link" size="sm" onClick={fetchAds}>Повторить</Button>
        </div>
      )}

      {/* Cards grid */}
      {ads.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ads.map((ad) => (
            <AdCard key={ad.id} ad={ad} isBest={ad.id === bestId} onClick={() => handleView(ad)} onBlock={() => handleBlock(ad.merchant.id)} />
          ))}
        </div>
      ) : !loading ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-border bg-card py-16">
          <SearchX className="h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">Нет объявлений</h3>
          <p className="mt-1 text-sm text-muted-foreground">Попробуйте изменить направление или подождите обновления</p>
        </div>
      ) : null}

      {/* Next update */}
      <p className="mt-4 text-center text-xs text-muted-foreground">Следующее обновление через {Math.max(0, 15 - updateAge)} сек</p>

      {/* Detail dialog */}
      <AdDetailDialog ad={selectedAd} open={!!selectedAd} onClose={() => setSelectedAd(null)} onBlock={handleBlock} />
    </div>
  );
}
