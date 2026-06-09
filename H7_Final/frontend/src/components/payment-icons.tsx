import { CreditCard, Building2, Smartphone, Wallet, Banknote } from "lucide-react";

const icons: Record<string, { icon: React.ElementType; label: string }> = {
  SBP: { icon: Smartphone, label: "СБП" },
  Sberbank: { icon: Building2, label: "Сбербанк" },
  Tinkoff: { icon: CreditCard, label: "Тинькофф" },
  "Alfa-Bank": { icon: Building2, label: "Альфа-Банк" },
  Raiffeisen: { icon: Building2, label: "Райффайзен" },
  VTB: { icon: Building2, label: "ВТБ" },
  Gazprombank: { icon: Building2, label: "Газпромбанк" },
  Cash: { icon: Banknote, label: "Наличные" },
};

export function PaymentIcons({ methods }: { methods: string[] }) {
  return (
    <div className="flex items-center gap-1.5">
      {methods.slice(0, 3).map((m) => {
        const p = icons[m] || { icon: Wallet, label: m };
        const Icon = p.icon;
        return (
          <div key={m} className="flex h-6 items-center gap-1 rounded bg-muted/50 px-1.5" title={p.label}>
            <Icon className="h-3 w-3 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">{p.label}</span>
          </div>
        );
      })}
      {methods.length > 3 && <span className="text-xs text-muted-foreground">+{methods.length - 3}</span>}
    </div>
  );
}
