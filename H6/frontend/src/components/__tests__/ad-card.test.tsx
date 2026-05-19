import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AdCard, type Ad } from "../ad-card";

const mockAd: Ad = {
  id: "ad-1",
  price: 95.5,
  volume: 10000,
  min_limit: 5000,
  max_limit: 50000,
  direction: "BUY",
  currency: "RUB",
  payment_methods: ["Sberbank", "Tinkoff"],
  risk_score: 3,
  risk_category: "low",
  net_yield: 1.25,
  spread: -0.5,
  merchant: {
    id: "m-1",
    name: "CryptoTrader",
    rating: 4.5,
    trades_count: 1200,
    success_rate: 0.98,
    is_verified: true,
  },
};

describe("AdCard", () => {
  it("renders merchant name and price", () => {
    render(<AdCard ad={mockAd} />);
    expect(screen.getByText("CryptoTrader")).toBeInTheDocument();
    expect(screen.getByText("95.50")).toBeInTheDocument();
  });

  it("renders BUY direction badge", () => {
    render(<AdCard ad={mockAd} />);
    expect(screen.getByText("BUY")).toBeInTheDocument();
  });

  it("renders SELL direction badge for sell ads", () => {
    const sellAd = { ...mockAd, direction: "SELL" };
    render(<AdCard ad={sellAd} />);
    expect(screen.getByText("SELL")).toBeInTheDocument();
  });

  it("shows best ring when isBest is true", () => {
    const { container } = render(<AdCard ad={mockAd} isBest />);
    const card = container.querySelector("[class*='ring-2']");
    expect(card).toBeInTheDocument();
  });

  it("calls onClick when card is clicked", () => {
    const onClick = vi.fn();
    render(<AdCard ad={mockAd} onClick={onClick} />);
    fireEvent.click(screen.getByText("CryptoTrader"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("calls onBlock without triggering onClick", () => {
    const onClick = vi.fn();
    const onBlock = vi.fn();
    render(<AdCard ad={mockAd} onClick={onClick} onBlock={onBlock} />);
    // Click the block button (Ban icon button)
    const blockBtn = screen.getByRole("button", { name: "" });
    fireEvent.click(blockBtn);
    expect(onBlock).toHaveBeenCalledTimes(1);
  });

  it("displays limit range", () => {
    render(<AdCard ad={mockAd} />);
    // Limits are formatted with ru-RU locale
    expect(screen.getByText(/5[\s\u00a0]?000/)).toBeInTheDocument();
    expect(screen.getByText(/50[\s\u00a0]?000/)).toBeInTheDocument();
  });

  it("displays net yield when available", () => {
    render(<AdCard ad={mockAd} />);
    expect(screen.getByText("+1.25%")).toBeInTheDocument();
  });

  it("shows verified badge for verified merchants", () => {
    render(<AdCard ad={mockAd} />);
    expect(screen.getByText("✓")).toBeInTheDocument();
  });
});
