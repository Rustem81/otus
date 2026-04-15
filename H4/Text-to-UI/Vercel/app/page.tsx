"use client"

import { useState, useMemo } from "react"
import { Save, TrendingUp, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { MerchantCard } from "@/components/merchant-card"
import { FilterBar } from "@/components/filter-bar"

// Mock data for merchants
const mockMerchants = [
  {
    id: "1",
    name: "CryptoKing_Pro",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=1",
    rating: 4.8,
    riskScore: 15,
    price: 43250,
    currency: "USD",
    spread: 0.45,
    paymentMethods: ["bank", "card", "mobile"],
    direction: "buy" as const,
    minAmount: 100,
    maxAmount: 50000,
  },
  {
    id: "2",
    name: "TraderMax",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=2",
    rating: 4.5,
    riskScore: 28,
    price: 43180,
    currency: "USD",
    spread: 0.62,
    paymentMethods: ["bank", "wallet"],
    direction: "sell" as const,
    minAmount: 500,
    maxAmount: 25000,
  },
  {
    id: "3",
    name: "BitcoinBaron",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=3",
    rating: 4.9,
    riskScore: 8,
    price: 43320,
    currency: "USD",
    spread: 0.38,
    paymentMethods: ["bank", "card", "mobile", "wallet"],
    direction: "buy" as const,
    minAmount: 50,
    maxAmount: 100000,
  },
  {
    id: "4",
    name: "FastTrade_X",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=4",
    rating: 4.2,
    riskScore: 45,
    price: 43100,
    currency: "USD",
    spread: 0.89,
    paymentMethods: ["mobile", "wallet"],
    direction: "sell" as const,
    minAmount: 200,
    maxAmount: 15000,
  },
  {
    id: "5",
    name: "CoinMaster_EU",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=5",
    rating: 4.7,
    riskScore: 22,
    price: 43280,
    currency: "USD",
    spread: 0.52,
    paymentMethods: ["bank", "card"],
    direction: "buy" as const,
    minAmount: 100,
    maxAmount: 75000,
  },
  {
    id: "6",
    name: "P2P_Veteran",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=6",
    rating: 4.6,
    riskScore: 35,
    price: 43150,
    currency: "USD",
    spread: 0.75,
    paymentMethods: ["bank", "mobile", "cash"],
    direction: "sell" as const,
    minAmount: 1000,
    maxAmount: 50000,
  },
  {
    id: "7",
    name: "QuickBTC",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=7",
    rating: 3.9,
    riskScore: 68,
    price: 42980,
    currency: "USD",
    spread: 1.25,
    paymentMethods: ["wallet", "mobile"],
    direction: "buy" as const,
    minAmount: 50,
    maxAmount: 5000,
  },
  {
    id: "8",
    name: "SafeTrader_99",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=8",
    rating: 5.0,
    riskScore: 5,
    price: 43400,
    currency: "USD",
    spread: 0.28,
    paymentMethods: ["bank", "card", "mobile", "wallet", "cash"],
    direction: "buy" as const,
    minAmount: 500,
    maxAmount: 200000,
  },
  {
    id: "9",
    name: "CryptoNinja",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=9",
    rating: 4.3,
    riskScore: 52,
    price: 43050,
    currency: "USD",
    spread: 0.95,
    paymentMethods: ["mobile", "wallet"],
    direction: "sell" as const,
    minAmount: 100,
    maxAmount: 10000,
  },
]

interface Filters {
  banks: string[]
  amountRange: string | null
  riskLevel: string | null
  direction: "all" | "buy" | "sell"
}

export default function P2PAggregator() {
  const [filters, setFilters] = useState<Filters>({
    banks: [],
    amountRange: null,
    riskLevel: null,
    direction: "all",
  })
  const [showSaveToast, setShowSaveToast] = useState(false)

  const filteredMerchants = useMemo(() => {
    return mockMerchants.filter((merchant) => {
      // Direction filter
      if (filters.direction !== "all" && merchant.direction !== filters.direction) {
        return false
      }

      // Risk level filter
      if (filters.riskLevel) {
        const riskRange = filters.riskLevel
        if (riskRange.includes("Low") && merchant.riskScore > 30) return false
        if (riskRange.includes("Medium") && (merchant.riskScore <= 30 || merchant.riskScore > 60)) return false
        if (riskRange.includes("High") && merchant.riskScore <= 60) return false
      }

      // Amount range filter
      if (filters.amountRange) {
        const range = filters.amountRange
        if (range === "$0 - $1,000" && merchant.maxAmount < 0) return false
        if (range === "$1,000 - $5,000" && (merchant.maxAmount < 1000 || merchant.minAmount > 5000)) return false
        if (range === "$5,000 - $10,000" && (merchant.maxAmount < 5000 || merchant.minAmount > 10000)) return false
        if (range === "$10,000+" && merchant.maxAmount < 10000) return false
      }

      return true
    })
  }, [filters])

  const handleSaveFilters = () => {
    setShowSaveToast(true)
    setTimeout(() => setShowSaveToast(false), 2000)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">P2P Aggregator</h1>
                <p className="text-xs text-muted-foreground">Find the best crypto deals</p>
              </div>
            </div>
            <Button variant="outline" size="sm" className="border-border bg-card text-card-foreground hover:bg-muted">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>
      </header>

      {/* Filter Bar */}
      <div className="sticky top-[73px] z-40 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto max-w-7xl px-4 py-3">
          <FilterBar onFiltersChange={setFilters} />
        </div>
      </div>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        {/* Results Count */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing <span className="font-semibold text-foreground">{filteredMerchants.length}</span> advertisements
          </p>
          <p className="text-xs text-muted-foreground">
            BTC/USD • Last updated: just now
          </p>
        </div>

        {/* Cards Grid */}
        {filteredMerchants.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredMerchants.map((merchant) => (
              <MerchantCard key={merchant.id} merchant={merchant} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-lg border border-border bg-card py-16">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-card-foreground">No results found</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Try adjusting your filters to find more advertisements
            </p>
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      <button
        onClick={handleSaveFilters}
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25 transition-transform hover:scale-105 active:scale-95"
        aria-label="Save filters"
      >
        <Save className="h-6 w-6" />
      </button>

      {/* Toast Notification */}
      {showSaveToast && (
        <div className="fixed bottom-24 right-6 animate-in fade-in slide-in-from-bottom-2 rounded-lg border border-border bg-card px-4 py-3 shadow-lg">
          <p className="text-sm text-card-foreground">Filters saved successfully!</p>
        </div>
      )}
    </div>
  )
}
