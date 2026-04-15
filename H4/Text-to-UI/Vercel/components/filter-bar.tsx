"use client"

import { useState } from "react"
import { Building2, DollarSign, Shield, ArrowUpDown, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const banks = ["Chase", "Bank of America", "Wells Fargo", "Citi", "Capital One"]
const amountRanges = ["$0 - $1,000", "$1,000 - $5,000", "$5,000 - $10,000", "$10,000+"]
const riskLevels = ["Low (0-30)", "Medium (31-60)", "High (61-100)"]

interface FilterBarProps {
  onFiltersChange: (filters: {
    banks: string[]
    amountRange: string | null
    riskLevel: string | null
    direction: "all" | "buy" | "sell"
  }) => void
}

export function FilterBar({ onFiltersChange }: FilterBarProps) {
  const [selectedBanks, setSelectedBanks] = useState<string[]>([])
  const [selectedAmount, setSelectedAmount] = useState<string | null>(null)
  const [selectedRisk, setSelectedRisk] = useState<string | null>(null)
  const [direction, setDirection] = useState<"all" | "buy" | "sell">("all")

  const updateFilters = (updates: Partial<{
    banks: string[]
    amountRange: string | null
    riskLevel: string | null
    direction: "all" | "buy" | "sell"
  }>) => {
    const newFilters = {
      banks: updates.banks ?? selectedBanks,
      amountRange: updates.amountRange !== undefined ? updates.amountRange : selectedAmount,
      riskLevel: updates.riskLevel !== undefined ? updates.riskLevel : selectedRisk,
      direction: updates.direction ?? direction,
    }
    onFiltersChange(newFilters)
  }

  const toggleBank = (bank: string) => {
    const newBanks = selectedBanks.includes(bank)
      ? selectedBanks.filter((b) => b !== bank)
      : [...selectedBanks, bank]
    setSelectedBanks(newBanks)
    updateFilters({ banks: newBanks })
  }

  const setAmountRange = (range: string | null) => {
    setSelectedAmount(range)
    updateFilters({ amountRange: range })
  }

  const setRiskLevel = (level: string | null) => {
    setSelectedRisk(level)
    updateFilters({ riskLevel: level })
  }

  const setDirectionFilter = (dir: "all" | "buy" | "sell") => {
    setDirection(dir)
    updateFilters({ direction: dir })
  }

  const clearFilters = () => {
    setSelectedBanks([])
    setSelectedAmount(null)
    setSelectedRisk(null)
    setDirection("all")
    onFiltersChange({
      banks: [],
      amountRange: null,
      riskLevel: null,
      direction: "all",
    })
  }

  const hasFilters = selectedBanks.length > 0 || selectedAmount || selectedRisk || direction !== "all"

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Bank Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="border-border bg-card text-card-foreground hover:bg-muted">
            <Building2 className="mr-2 h-4 w-4" />
            Banks
            {selectedBanks.length > 0 && (
              <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary">
                {selectedBanks.length}
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="border-border bg-card">
          {banks.map((bank) => (
            <DropdownMenuCheckboxItem
              key={bank}
              checked={selectedBanks.includes(bank)}
              onCheckedChange={() => toggleBank(bank)}
              className="text-card-foreground"
            >
              {bank}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Amount Range Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="border-border bg-card text-card-foreground hover:bg-muted">
            <DollarSign className="mr-2 h-4 w-4" />
            Amount
            {selectedAmount && (
              <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary">
                1
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="border-border bg-card">
          {amountRanges.map((range) => (
            <DropdownMenuCheckboxItem
              key={range}
              checked={selectedAmount === range}
              onCheckedChange={() => setAmountRange(selectedAmount === range ? null : range)}
              className="text-card-foreground"
            >
              {range}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Risk Level Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="border-border bg-card text-card-foreground hover:bg-muted">
            <Shield className="mr-2 h-4 w-4" />
            Risk Level
            {selectedRisk && (
              <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary">
                1
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="border-border bg-card">
          {riskLevels.map((level) => (
            <DropdownMenuCheckboxItem
              key={level}
              checked={selectedRisk === level}
              onCheckedChange={() => setRiskLevel(selectedRisk === level ? null : level)}
              className="text-card-foreground"
            >
              {level}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Direction Filter */}
      <div className="flex overflow-hidden rounded-md border border-border">
        {(["all", "buy", "sell"] as const).map((dir) => (
          <Button
            key={dir}
            variant="ghost"
            size="sm"
            onClick={() => setDirectionFilter(dir)}
            className={`rounded-none px-3 ${
              direction === dir
                ? dir === "buy"
                  ? "bg-green-500/20 text-green-400"
                  : dir === "sell"
                  ? "bg-red-500/20 text-red-400"
                  : "bg-primary/20 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-card-foreground"
            }`}
          >
            <ArrowUpDown className="mr-1 h-3 w-3" />
            {dir.charAt(0).toUpperCase() + dir.slice(1)}
          </Button>
        ))}
      </div>

      {/* Clear Filters */}
      {hasFilters && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearFilters}
          className="text-muted-foreground hover:text-destructive"
        >
          <X className="mr-1 h-4 w-4" />
          Clear
        </Button>
      )}
    </div>
  )
}
