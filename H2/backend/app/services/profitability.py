from __future__ import annotations

from decimal import Decimal


class ProfitabilityService:
    """
    Calculate profitability metrics.

    Net yield formula:
    net_yield = ((ref_price - ad_price) / ad_price - commission_pct) * 100
                - commission_fix / deal_amount * 100
    """

    def calculate_net_yield(
        self,
        ad_price: float,
        ref_price: float | None,
        commission_pct: float | None,
        commission_fixed: float | None,
        deal_amount: float | None = None,
    ) -> float | None:
        """
        Calculate net yield for advertisement.

        Args:
            ad_price: Advertisement price
            ref_price: Reference price (average market price)
            commission_pct: Commission percentage (e.g., 0.5 for 0.5%)
            commission_fixed: Fixed commission amount
            deal_amount: Deal amount for fixed commission calculation

        Returns:
            Net yield in percentage points, or None if ref_price not available
        """
        if ref_price is None or ad_price == 0:
            return None

        # Spread component
        spread = ((ref_price - ad_price) / ad_price) * 100

        # Commission component (percentage)
        commission_pct_value = commission_pct or 0.0

        # Fixed commission component
        commission_fixed_value = 0.0
        if commission_fixed and deal_amount and deal_amount > 0:
            commission_fixed_value = (commission_fixed / deal_amount) * 100

        # Net yield
        net_yield = spread - commission_pct_value - commission_fixed_value

        return round(net_yield, 2)

    def calculate_spread(
        self,
        ad_price: float,
        ref_price: float | None,
    ) -> float | None:
        """Calculate spread from reference price."""
        if ref_price is None or ad_price == 0:
            return None

        spread = ((ad_price - ref_price) / ref_price) * 100
        return round(spread, 2)
