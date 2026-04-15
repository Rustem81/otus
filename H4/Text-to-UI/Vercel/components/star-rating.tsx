import { Star } from "lucide-react"

interface StarRatingProps {
  rating: number
  maxRating?: number
}

export function StarRating({ rating, maxRating = 5 }: StarRatingProps) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: maxRating }).map((_, i) => (
        <Star
          key={i}
          className={`h-3 w-3 ${
            i < Math.floor(rating)
              ? "fill-yellow-400 text-yellow-400"
              : i < rating
              ? "fill-yellow-400/50 text-yellow-400"
              : "fill-muted text-muted"
          }`}
        />
      ))}
      <span className="ml-1 text-xs text-muted-foreground">
        {rating.toFixed(1)}
      </span>
    </div>
  )
}
