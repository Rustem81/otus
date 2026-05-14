import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PaymentIcons } from "../payment-icons";

describe("PaymentIcons", () => {
  it("renders payment method labels", () => {
    render(<PaymentIcons methods={["Sberbank", "Tinkoff"]} />);
    expect(screen.getByText("Сбербанк")).toBeInTheDocument();
    expect(screen.getByText("Тинькофф")).toBeInTheDocument();
  });

  it("shows max 3 methods and +N for the rest", () => {
    render(<PaymentIcons methods={["Sberbank", "Tinkoff", "SBP", "VTB", "Cash"]} />);
    expect(screen.getByText("Сбербанк")).toBeInTheDocument();
    expect(screen.getByText("Тинькофф")).toBeInTheDocument();
    expect(screen.getByText("СБП")).toBeInTheDocument();
    expect(screen.getByText("+2")).toBeInTheDocument();
    // VTB and Cash should not be rendered
    expect(screen.queryByText("ВТБ")).not.toBeInTheDocument();
  });

  it("renders empty list without errors", () => {
    const { container } = render(<PaymentIcons methods={[]} />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("renders unknown method with fallback", () => {
    render(<PaymentIcons methods={["UnknownBank"]} />);
    expect(screen.getByText("UnknownBank")).toBeInTheDocument();
  });
});
