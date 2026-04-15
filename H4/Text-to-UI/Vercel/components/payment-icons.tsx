import { CreditCard, Building2, Smartphone, Wallet, Banknote } from "lucide-react"

const paymentMethods: Record<string, { icon: React.ElementType; label: string }> = {
  bank: { icon: Building2, label: "Bank Transfer" },
  card: { icon: CreditCard, label: "Card" },
  mobile: { icon: Smartphone, label: "Mobile Payment" },
  wallet: { icon: Wallet, label: "E-Wallet" },
  cash: { icon: Banknote, label: "Cash" },
}

interface PaymentIconsProps {
  methods: string[]
}

export function PaymentIcons({ methods }: PaymentIconsProps) {
  return (
    <div className="flex items-center gap-1.5">
      {methods.slice(0, 4).map((method) => {
        const payment = paymentMethods[method]
        if (!payment) return null
        const Icon = payment.icon
        return (
          <div
            key={method}
            className="flex h-6 w-6 items-center justify-center rounded bg-muted/50"
            title={payment.label}
          >
            <Icon className="h-3.5 w-3.5 text-muted-foreground" />
          </div>
        )
      })}
      {methods.length > 4 && (
        <span className="text-xs text-muted-foreground">
          +{methods.length - 4}
        </span>
      )}
    </div>
  )
}
