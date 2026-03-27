from __future__ import annotations

import random
import time
from datetime import datetime

from app.merchants import get_random_merchants, get_random_payment_methods

# Base price for RUB/USDT (fluctuates around this)
BASE_PRICE_BUY = 92.5  # Users buying USDT
BASE_PRICE_SELL = 91.5  # Users selling USDT


def generate_advertisements(
    market: str = "mexc",
    fiat: str = "RUB",
    asset: str = "USDT",
    side: str = "BUY",
    limit: int = 50,
) -> list[dict]:
    """
    Generate realistic P2P advertisements.

    Args:
        market: Exchange name (mexc, binance, etc.)
        fiat: Fiat currency (RUB, USD, etc.)
        asset: Crypto asset (USDT, BTC, etc.)
        side: BUY or SELL (from user's perspective)
        limit: Number of ads to generate

    Returns:
        List of advertisement dictionaries
    """
    ads = []
    merchants = get_random_merchants(limit)

    # Determine base price based on side
    if side == "BUY":
        base_price = BASE_PRICE_BUY
    else:
        base_price = BASE_PRICE_SELL

    for pos, merchant_data in enumerate(merchants, 1):
        # Price varies with normal distribution around base
        price_variation = random.gauss(0, 0.8)
        price = round(base_price + price_variation, 2)

        # Volume varies by merchant activity
        base_volume = random.uniform(500, 5000)
        volume_multiplier = 1 + (merchant_data["orders"] / 100000)
        volume = round(base_volume * volume_multiplier, 2)

        # Limits based on volume
        min_fiat = random.choice([1000, 5000, 10000, 15000, 20000])
        max_fiat = min(round(volume * price * random.uniform(0.3, 0.9)), 500000)
        max_fiat = max(max_fiat, min_fiat * 2)

        ad = {
            "pos": pos,
            "updated_at": int(time.time()),
            "market": market,
            "asset": asset,
            "fiat": fiat,
            "side": side,
            "payment_methods": get_random_payment_methods(),
            "price": str(price),
            "surplus_amount": str(volume),
            "surplus_fiat": round(volume * price, 2),
            "min_fiat": str(min_fiat),
            "max_fiat": str(int(max_fiat)),
            "text": generate_ad_text(),
            "user_name": merchant_data["name"],
            "user_id": str(random.randint(10000, 99999)),
            "adv_id": str(generate_ad_id()),
            "user_orders": merchant_data["orders"],
            "user_rate": merchant_data["rate"],
            "is_merchant": merchant_data["is_merchant"],
        }
        ads.append(ad)

    # Sort by price (best first)
    if side == "BUY":
        ads.sort(key=lambda x: float(x["price"]))
    else:
        ads.sort(key=lambda x: float(x["price"]), reverse=True)

    # Reassign positions after sorting
    for i, ad in enumerate(ads, 1):
        ad["pos"] = i

    return ads


def generate_ad_id() -> int:
    """Generate unique advertisement ID."""
    return random.randint(1000000000000000000, 9999999999999999999)


def generate_ad_text() -> str:
    """Generate random advertisement text."""
    texts = [
        "Быстрая оплата, онлайн 24/7",
        "Перевод за 5 минут",
        "Работаю круглосуточно",
        "Без комиссии",
        "Надёжный обмен",
        "Моментальный перевод",
        "Проверенный трейдер",
        "Лучший курс гарантирую",
        "Опыт более 5 лет",
        "Быстро и безопасно",
        "Принимаю любые суммы",
        "VIP обслуживание",
        "Связь в Telegram",
        "Работаю без выходных",
        "Гарантия качества",
    ]
    return random.choice(texts)


def get_payment_methods() -> list[dict]:
    """Get list of popular payment methods."""
    return [
        {"id": "sbp", "name": "СБП", "fiat": "RUB"},
        {"id": "sberbank", "name": "Сбербанк", "fiat": "RUB"},
        {"id": "tinkoff", "name": "Тинькофф", "fiat": "RUB"},
        {"id": "alfa", "name": "Альфа-Банк", "fiat": "RUB"},
        {"id": "raiffeisen", "name": "Райффайзен", "fiat": "RUB"},
        {"id": "vtb", "name": "ВТБ", "fiat": "RUB"},
        {"id": "gazprombank", "name": "Газпромбанк", "fiat": "RUB"},
        {"id": "otkritie", "name": "Открытие", "fiat": "RUB"},
        {"id": "rosbank", "name": "Росбанк", "fiat": "RUB"},
        {"id": "sovcombank", "name": "Совкомбанк", "fiat": "RUB"},
    ]


def get_p2p_assets() -> list[dict]:
    """Get list of available crypto assets."""
    return [
        {"id": "USDT", "name": "Tether", "networks": ["ERC20", "TRC20", "BEP20"]},
        {"id": "BTC", "name": "Bitcoin", "networks": ["BTC"]},
        {"id": "ETH", "name": "Ethereum", "networks": ["ERC20"]},
    ]


def get_p2p_fiats() -> list[dict]:
    """Get list of available fiat currencies."""
    return [
        {"id": "RUB", "name": "Russian Ruble", "symbol": "₽"},
        {"id": "USD", "name": "US Dollar", "symbol": "$"},
        {"id": "EUR", "name": "Euro", "symbol": "€"},
    ]
