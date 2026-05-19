import { useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { RiskIndicator } from "@/components/risk-indicator";
import { StarRating } from "@/components/star-rating";
import { PaymentIcons } from "@/components/payment-icons";
import { ExternalLink, Ban } from "lucide-react";
import { trackEvent } from "@/lib/analytics";
import type { Ad } from "@/components/ad-card";

interface Props {
  ad: Ad | null;
  open: boolean;
  onClose: () => void;
  onBlock: (merchantId: string) => void;
}

export function AdDetailDialog({ ad, open, onClose, onBlock }: Props) {
  useEffect(() => {
    if (open && ad) {
      trackEvent("view_ad", { ad_id: ad.id, merchant_id: ad.merchant.id });
    }
  }, [open, ad]);

  if (!ad) return null;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {ad.merchant.name}
            {ad.merchant.is_verified && <Badge variant="outline" className="border-blue-500 text-blue-400 text-[10px]">✓</Badge>}
            <Badge className={ad.direction === "BUY" ? "bg-green-500/20 text-green-400 ml-auto" : "bg-red-500/20 text-red-400 ml-auto"}>
              {ad.direction}
            </Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Price + Risk */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-primary">{ad.price.toFixed(2)} <span className="text-base text-muted-foreground">₽</span></div>
              <div className="text-sm text-muted-foreground">Объём: {ad.volume.toLocaleString("ru-RU")}</div>
            </div>
            <RiskIndicator score={ad.risk_score ?? 5} size={56} />
          </div>

          <Separator />

          {/* Merchant metrics */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-xs text-muted-foreground">Рейтинг</div>
              <StarRating rating={ad.merchant.rating ?? 0} />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Сделок</div>
              <div className="font-semibold">{ad.merchant.trades_count.toLocaleString("ru-RU")}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Успешных</div>
              <div className="font-semibold">{((ad.merchant.success_rate ?? 0) * 100).toFixed(0)}%</div>
            </div>
          </div>

          <Separator />

          {/* Limits + Spread + Yield */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-muted-foreground">Мин. сумма:</span> <span className="font-medium">{ad.min_limit.toLocaleString("ru-RU")} ₽</span></div>
            <div><span className="text-muted-foreground">Макс. сумма:</span> <span className="font-medium">{ad.max_limit.toLocaleString("ru-RU")} ₽</span></div>
            <div><span className="text-muted-foreground">Спред:</span> <span className={`font-medium ${(ad.spread ?? 0) < 0 ? "text-green-400" : "text-red-400"}`}>{ad.spread != null ? `${ad.spread.toFixed(2)}%` : "—"}</span></div>
            <div><span className="text-muted-foreground">Доходность:</span> <span className={`font-medium ${(ad.net_yield ?? 0) >= 0 ? "text-green-400" : "text-red-400"}`}>{ad.net_yield != null ? `${ad.net_yield.toFixed(2)}%` : "—"}</span></div>
          </div>

          <Separator />

          {/* Payment methods */}
          <div>
            <div className="text-xs text-muted-foreground mb-2">Способы оплаты</div>
            <PaymentIcons methods={ad.payment_methods} />
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button variant="destructive" size="sm" onClick={() => { onBlock(ad.merchant.id); onClose(); }}>
              <Ban className="mr-2 h-4 w-4" />Заблокировать
            </Button>
            <Button size="sm" className="flex-1" onClick={() => window.open("https://www.mexc.com/ru-RU/p2p", "_blank")}>
              <ExternalLink className="mr-2 h-4 w-4" />Открыть в MEXC
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
