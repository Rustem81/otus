"use client"

interface RiskIndicatorProps {
  score: number // 0-100
  size?: number
}

export function RiskIndicator({ score, size = 48 }: RiskIndicatorProps) {
  const getColor = (score: number) => {
    if (score <= 30) return "#22c55e" // green
    if (score <= 60) return "#eab308" // yellow
    return "#ef4444" // red
  }

  const color = getColor(score)
  const radius = (size - 8) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="none"
          className="text-muted/30"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="4"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: "stroke-dashoffset 0.5s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-semibold" style={{ color }}>
          {score}
        </span>
      </div>
    </div>
  )
}
