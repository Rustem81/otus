import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StarRating } from "../star-rating";

describe("StarRating", () => {
  it("renders the numeric rating", () => {
    render(<StarRating rating={4.5} />);
    expect(screen.getByText("4.5")).toBeInTheDocument();
  });

  it("renders 5 stars by default", () => {
    const { container } = render(<StarRating rating={3} />);
    const stars = container.querySelectorAll("svg");
    expect(stars).toHaveLength(5);
  });

  it("renders custom number of stars", () => {
    const { container } = render(<StarRating rating={3} max={10} />);
    const stars = container.querySelectorAll("svg");
    expect(stars).toHaveLength(10);
  });

  it("fills correct number of stars", () => {
    const { container } = render(<StarRating rating={3} />);
    const filledStars = container.querySelectorAll(".fill-yellow-400");
    expect(filledStars).toHaveLength(3);
  });

  it("renders zero rating correctly", () => {
    render(<StarRating rating={0} />);
    expect(screen.getByText("0.0")).toBeInTheDocument();
  });
});
