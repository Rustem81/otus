import { ExternalLink, Ban } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { RiskIndicator } from "@/components/risk-indicator";
import { StarRating } from "@/components/star-rating";
import { PaymentIcons } from "@/components/payment-icons";

export interface Ad {
    id: string;
    price: number;
    volume: number;
    min_limit: number;
    max_limit: number;
    direction: string;
    currency: string;
    payment_methods: string[];
    risk_score: number | null;
    risk_category: string | null;
    net_yield: number | null;
    spread: number | null;
    merchant: {
        id: string;
        name: string;
        rating: number | null;
        trades_count: number;
        success_rate: number;
        is_verified: boolean;
    };
}

interface AdCardProps {
    ad: Ad;
    isBest?: boolean;
    onClick?: () => void;
    onBlock?: () => void;
}

export function AdCard({ ad, isBest, onClick, onBlock }: AdCardProps) {
    const spreadColor = (ad.spread ?? 0) < 0 ? "text-green-400" : (ad.spread ?? 0) < 1 ? "text-yellow-400" : "text-red-400";

    return (
        <Card
            className={`cursor-pointer overflow-hidden border-border/50 bg-card transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 ${isBest ? "ring-2 ring-green-500/50" : ""}`}
            onClick={onClick}
        >
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10 border-2 border-border">
                            <AvatarFallback className="bg-muted text-xs">{ad.merchant.name.slice(0, 2).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div>
                            <div className="flex items-center gap-1">
                                <h3 className="font-semibold text-card-foreground text-sm">{ad.merchant.name}</h3>
                                {ad.merchant.is_verified && <Badge variant="outline" className="text-[10px] px-1 py-0 border-blue-500 text-blue-400">✓</Badge>}
                            </div>
                            <StarRating rating={ad.merchant.rating ?? 0} />
                        </div>
                    </div>
                    <Badge className={ad.direction === "BUY" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}>
                        {ad.direction}
                    </Badge>
                </div>

                <div className="mt-4 flex items-center justify-between">
                    <div>
                        <div className="flex items-baseline gap-1">
                            <span className="text-2xl font-bold text-primary">{ad.price.toFixed(2)}</span>
                            <span className="text-sm text-muted-foreground">₽</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-muted-foreground">Спред:</span>
                            <span className={spreadColor}>{ad.spread != null ? `${ad.spread >= 0 ? "+" : ""}${ad.spread.toFixed(2)}%` : "—"}</span>
                        </div>
                    </div>
                    <div className="flex flex-col items-center">
                        <RiskIndicator score={ad.risk_score ?? 5} />
                        <span className="mt-1 text-[10px] uppercase tracking-wider text-muted-foreground">Риск</span>
                    </div>
                </div>

                {ad.net_yield != null && (
                    <div className="mt-2 text-sm">
                        <span className="text-muted-foreground">Доходность: </span>
                        <span className={ad.net_yield >= 0 ? "text-green-400 font-medium" : "text-red-400 font-medium"}>
                            {ad.net_yield >= 0 ? "+" : ""}{ad.net_yield.toFixed(2)}%
                        </span>
                    </div>
                )}

                <div className="mt-2 text-xs text-muted-foreground">
                    {ad.min_limit.toLocaleString("ru-RU")} — {ad.max_limit.toLocaleString("ru-RU")} ₽
                </div>

                <div className="mt-3">
                    <PaymentIcons methods={ad.payment_methods} />
                </div>

                <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="destructive" className="flex-none" onClick={(e) => { e.stopPropagation(); onBlock?.(); }}>
                        <Ban className="h-4 w-4" />
                    </Button>
                    <Button size="sm" className="flex-1" onClick={(e) => { e.stopPropagation(); window.open("https://www.mexc.com/ru-RU/p2p", "_blank"); }}>
                        <ExternalLink className="mr-2 h-4 w-4" />
                        Открыть в MEXC
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
