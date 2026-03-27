"""Scoring service - generated WITHOUT project rules (minimal prompt)."""

# Промпт: "Напиши сервис расчёта риск-скора для P2P-объявлений"

import openai
import json
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def calculate_risk_score(merchant_data):
    """Calculate risk score for a merchant."""
    rating = merchant_data.get('rating', 0)
    trades = merchant_data.get('trades', 0)
    success_rate = merchant_data.get('success_rate', 0)

    # Simple weighted calculation
    score = rating * 0.3 + (trades / 1000) * 0.25 + success_rate * 0.3

    if score > 0.7:
        return {'score': 2, 'category': 'low'}
    elif score > 0.4:
        return {'score': 5, 'category': 'medium'}
    else:
        return {'score': 8, 'category': 'high'}


def get_explanation(merchant_id, merchant_data, score):
    """Get LLM explanation for the score."""
    # Check cache
    cached = r.get(f'score:{merchant_id}')
    if cached:
        return json.loads(cached)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Explain risk score {score} for merchant with rating {merchant_data['rating']}"}
            ]
        )
        explanation = response.choices[0].message.content
        r.setex(f'score:{merchant_id}', 600, json.dumps(explanation))
        return explanation
    except:
        return None
