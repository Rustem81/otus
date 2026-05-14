import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { RiskIndicator } from "../risk-indicator";

describe("RiskIndicator", () => {
  it("renders the score value", () => {
    render(<RiskIndicator score={3} />);
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("uses green color for low risk (1-3)", () => {
    const { container } = render(<RiskIndicator score={2} />);
    const scoreEl = container.querySelector("span");
    expect(scoreEl).toHaveStyle({ color: "#22c55e" });
  });

  it("uses yellow color for medium risk (4-7)", () => {
    const { container } = render(<RiskIndicator score={5} />);
    const scoreEl = container.querySelector("span");
    expect(scoreEl).toHaveStyle({ color: "#eab308" });
  });

  it("uses red color for high risk (8-10)", () => {
    const { container } = render(<RiskIndicator score={9} />);
    const scoreEl = container.querySelector("span");
    expect(scoreEl).toHaveStyle({ color: "#ef4444" });
  });

  it("renders SVG with correct size", () => {
    const { container } = render(<RiskIndicator score={5} size={64} />);
    const svg = container.querySelector("svg");
    expect(svg).toHaveAttribute("width", "64");
    expect(svg).toHaveAttribute("height", "64");
  });
});
