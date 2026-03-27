from __future__ import annotations

import random


MERCHANT_POOL = [
    {"name": "CryptoMaster", "orders": 15234, "rate": 99, "is_merchant": 1},
    {"name": "FastTrader", "orders": 8932, "rate": 98, "is_merchant": 1},
    {"name": "BitcoinPro", "orders": 4567, "rate": 97, "is_merchant": 0},
    {"name": "P2PKing", "orders": 23145, "rate": 99, "is_merchant": 1},
    {"name": "QuickExchange", "orders": 3456, "rate": 96, "is_merchant": 0},
    {"name": "CryptoWhale", "orders": 56789, "rate": 99, "is_merchant": 1},
    {"name": "SafeTrader", "orders": 1234, "rate": 95, "is_merchant": 0},
    {"name": "SpeedyPay", "orders": 7890, "rate": 98, "is_merchant": 1},
    {"name": "CoinMaster", "orders": 2345, "rate": 97, "is_merchant": 0},
    {"name": "TrustExchange", "orders": 11234, "rate": 99, "is_merchant": 1},
    {"name": "FastCrypto", "orders": 567, "rate": 94, "is_merchant": 0},
    {"name": "ProTrader", "orders": 34567, "rate": 99, "is_merchant": 1},
    {"name": "EasyCoins", "orders": 890, "rate": 96, "is_merchant": 0},
    {"name": "SuperExchange", "orders": 22345, "rate": 98, "is_merchant": 1},
    {"name": "BitHunter", "orders": 1567, "rate": 97, "is_merchant": 0},
    {"name": "MegaTrader", "orders": 44567, "rate": 99, "is_merchant": 1},
    {"name": "CoinBase", "orders": 234, "rate": 93, "is_merchant": 0},
    {"name": "EliteExchange", "orders": 67890, "rate": 99, "is_merchant": 1},
    {"name": "CryptoStar", "orders": 1234, "rate": 96, "is_merchant": 0},
    {"name": "PrimeTrader", "orders": 33456, "rate": 98, "is_merchant": 1},
    {"name": "FastBit", "orders": 789, "rate": 95, "is_merchant": 0},
    {"name": "GoldExchange", "orders": 55678, "rate": 99, "is_merchant": 1},
    {"name": "SilverTrader", "orders": 3456, "rate": 97, "is_merchant": 0},
    {"name": "DiamondCrypto", "orders": 28901, "rate": 99, "is_merchant": 1},
    {"name": "BronzeExchange", "orders": 567, "rate": 94, "is_merchant": 0},
    {"name": "PlatinumPay", "orders": 41234, "rate": 98, "is_merchant": 1},
    {"name": "CopperCoins", "orders": 1890, "rate": 96, "is_merchant": 0},
    {"name": "RubyTrader", "orders": 36789, "rate": 99, "is_merchant": 1},
    {"name": "SapphirePay", "orders": 2345, "rate": 97, "is_merchant": 0},
    {"name": "EmeraldExchange", "orders": 52345, "rate": 99, "is_merchant": 1},
    {"name": "TopazCrypto", "orders": 1234, "rate": 95, "is_merchant": 0},
    {"name": "AmberTrader", "orders": 44567, "rate": 98, "is_merchant": 1},
    {"name": "JadePay", "orders": 890, "rate": 96, "is_merchant": 0},
    {"name": "PearlExchange", "orders": 31234, "rate": 99, "is_merchant": 1},
    {"name": "OnyxCrypto", "orders": 1567, "rate": 97, "is_merchant": 0},
    {"name": "QuartzTrader", "orders": 27890, "rate": 98, "is_merchant": 1},
    {"name": "OpalPay", "orders": 678, "rate": 94, "is_merchant": 0},
    {"name": "GarnetExchange", "orders": 48901, "rate": 99, "is_merchant": 1},
    {"name": "ZirconCrypto", "orders": 2345, "rate": 96, "is_merchant": 0},
    {"name": "TurquoisePay", "orders": 35678, "rate": 99, "is_merchant": 1},
    {"name": "AmethystTrader", "orders": 1123, "rate": 95, "is_merchant": 0},
    {"name": "CoralExchange", "orders": 42345, "rate": 98, "is_merchant": 1},
    {"name": "JasperCrypto", "orders": 1890, "rate": 97, "is_merchant": 0},
    {"name": "AgatePay", "orders": 56789, "rate": 99, "is_merchant": 1},
    {"name": "MalachiteTrader", "orders": 789, "rate": 94, "is_merchant": 0},
    {"name": "LapisExchange", "orders": 33456, "rate": 98, "is_merchant": 1},
    {"name": "ObsidianPay", "orders": 2456, "rate": 96, "is_merchant": 0},
    {"name": "CitrineTrader", "orders": 47890, "rate": 99, "is_merchant": 1},
    {"name": "MoonstoneCrypto", "orders": 1345, "rate": 95, "is_merchant": 0},
    {"name": "SunstonePay", "orders": 38901, "rate": 99, "is_merchant": 1},
]

PAYMENT_METHODS = [
    ["SBP"],
    ["Sberbank"],
    ["Tinkoff"],
    ["Alfa-Bank"],
    ["Raiffeisen"],
    ["VTB"],
    ["SBP", "Sberbank"],
    ["SBP", "Tinkoff"],
    ["SBP", "Alfa-Bank"],
    ["Sberbank", "Tinkoff"],
    ["SBP", "Sberbank", "Tinkoff"],
    ["Gazprombank"],
    ["Otkritie"],
    ["Rosbank"],
    ["Sovcombank"],
    ["SBP", "Raiffeisen"],
    ["Tinkoff", "Alfa-Bank"],
    ["Sberbank", "Alfa-Bank"],
    ["Cash"],
    ["SBP", "VTB"],
]


def get_random_merchants(count: int = 30) -> list[dict]:
    """Get random selection of merchants."""
    return random.sample(MERCHANT_POOL, min(count, len(MERCHANT_POOL)))


def get_random_payment_methods() -> list[str]:
    """Get random payment methods."""
    return random.choice(PAYMENT_METHODS)
