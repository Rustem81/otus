interface RiskIndicatorProps {
  score: number; // 1-10
  size?: number;
}

export function RiskIndicator({ score, size = 48 }: RiskIndicatorProps) {
  const getColor = (s: number) => {
    if (s <= 3) return "#22c55e";
    if (s <= 7) return "#eab308";
    return "#ef4444";
  };

  const color = getColor(score);
  const pct = (score / 10) * 100;
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="currentColor" strokeWidth="4" fill="none" className="text-muted/30" />
        <circle cx={size / 2} cy={size / 2} r={radius} stroke={color} strokeWidth="4" fill="none" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset} style={{ transition: "stroke-dashoffset 0.5s ease" }} />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-semibold" style={{ color }}>{score}</span>
      </div>
    </div>
  );
}
