from __future__ import annotations

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.generator import (
    generate_advertisements,
    get_p2p_assets,
    get_p2p_fiats,
    get_payment_methods,
)


app = FastAPI(
    title="MEXC P2P Mock Server",
    version="0.1.0",
    description="Mock server emulating p2p.army API for local development",
)


class OrderBookRequest(BaseModel):
    market: str = "mexc"
    fiat: str = "RUB"
    asset: str = "USDT"
    side: str = "BUY"
    payment_method: str | None = None
    limit: int = 50


@app.get("/v1/api/ping")
async def ping() -> dict:
    """Health check endpoint."""
    return {"status": 1, "message": "pong"}


@app.post("/v1/api/get_p2p_order_book")
async def get_p2p_order_book(request: OrderBookRequest) -> dict:
    """
    Get P2P order book (advertisements).

    Emulates p2p.army API format.
    """
    ads = generate_advertisements(
        market=request.market,
        fiat=request.fiat,
        asset=request.asset,
        side=request.side,
        limit=request.limit,
    )

    # Filter by payment method if specified
    if request.payment_method:
        ads = [
            ad for ad in ads
            if request.payment_method.lower() in [pm.lower() for pm in ad["payment_methods"]]
        ]

    return {
        "status": 1,
        "ads": ads,
    }


@app.post("/v1/api/get_p2p_prices")
async def get_p2p_prices(
    market: str = "mexc",
    fiat: str = "RUB",
    asset: str = "USDT",
    payment_method: str | None = None,
) -> dict:
    """Get P2P prices and spreads."""
    buy_ads = generate_advertisements(market, fiat, asset, "BUY", 10)
    sell_ads = generate_advertisements(market, fiat, asset, "SELL", 10)

    buy_price = float(buy_ads[0]["price"]) if buy_ads else 0
    sell_price = float(sell_ads[0]["price"]) if sell_ads else 0
    spread = round(buy_price - sell_price, 2) if buy_price and sell_price else 0

    return {
        "status": 1,
        "market": market,
        "fiat": fiat,
        "asset": asset,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "spread": spread,
    }


@app.post("/v1/api/get_popular_p2p_payment_methods")
async def get_popular_p2p_payment_methods(
    fiat: str = "RUB",
) -> dict:
    """Get popular payment methods."""
    methods = get_payment_methods()
    return {
        "status": 1,
        "fiat": fiat,
        "methods": methods,
    }


@app.post("/v1/api/get_p2p_assets")
async def get_p2p_assets_endpoint() -> dict:
    """Get available crypto assets."""
    return {
        "status": 1,
        "assets": get_p2p_assets(),
    }


@app.get("/v1/api/get_p2p_fiats")
async def get_p2p_fiats_endpoint() -> dict:
    """Get available fiat currencies."""
    return {
        "status": 1,
        "fiats": get_p2p_fiats(),
    }
