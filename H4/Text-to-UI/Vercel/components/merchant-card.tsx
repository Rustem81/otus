"use client"

import { ExternalLink } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { RiskIndicator } from "@/components/risk-indicator"
import { StarRating } from "@/components/star-rating"
import { PaymentIcons } from "@/components/payment-icons"

interface Merchant {
  id: string
  name: string
  avatar: string
  rating: number
  riskScore: number
  price: number
  currency: string
  spread: number
  paymentMethods: string[]
  direction: "buy" | "sell"
  minAmount: number
  maxAmount: number
}

interface MerchantCardProps {
  merchant: Merchant
}

export function MerchantCard({ merchant }: MerchantCardProps) {
  const spreadColor = merchant.spread < 1 ? "text-green-400" : merchant.spread < 2 ? "text-yellow-400" : "text-red-400"
  
  return (
    <Card className="overflow-hidden border-border/50 bg-card transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
      <CardContent className="p-4">
        {/* Header: Avatar, Name, Rating, Direction Badge */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10 border-2 border-border">
              <AvatarImage src={merchant.avatar} alt={merchant.name} />
              <AvatarFallback className="bg-muted text-xs">
                {merchant.name.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold text-card-foreground">{merchant.name}</h3>
              <StarRating rating={merchant.rating} />
            </div>
          </div>
          <Badge
            variant={merchant.direction === "buy" ? "default" : "secondary"}
            className={
              merchant.direction === "buy"
                ? "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
            }
          >
            {merchant.direction.toUpperCase()}
          </Badge>
        </div>

        {/* Price and Risk */}
        <div className="mt-4 flex items-center justify-between">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold text-primary">
                {merchant.price.toLocaleString()}
              </span>
              <span className="text-sm text-muted-foreground">{merchant.currency}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Spread:</span>
              <span className={spreadColor}>{merchant.spread.toFixed(2)}%</span>
            </div>
          </div>
          <div className="flex flex-col items-center">
            <RiskIndicator score={merchant.riskScore} />
            <span className="mt-1 text-[10px] uppercase tracking-wider text-muted-foreground">
              Risk
            </span>
          </div>
        </div>

        {/* Amount Range */}
        <div className="mt-3 text-xs text-muted-foreground">
          <span className="text-card-foreground">{merchant.minAmount.toLocaleString()}</span>
          {" - "}
          <span className="text-card-foreground">{merchant.maxAmount.toLocaleString()}</span>
          {" "}{merchant.currency}
        </div>

        {/* Payment Methods */}
        <div className="mt-3">
          <PaymentIcons methods={merchant.paymentMethods} />
        </div>

        {/* CTA Button */}
        <Button
          className="mt-4 w-full bg-primary text-primary-foreground hover:bg-primary/90"
          size="sm"
        >
          <ExternalLink className="mr-2 h-4 w-4" />
          Open in MEXC
        </Button>
      </CardContent>
    </Card>
  )
}
