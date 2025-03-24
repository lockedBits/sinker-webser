import requests

# Mode switch (True = live fetch from CoinGecko, False = static fallback)
USE_LIVE_PRICE = True

def get_sol_price_usd():
    if not USE_LIVE_PRICE:
        return 129.28  # fallback default

    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "solana",
                "vs_currencies": "usd"
            },
            timeout=5
        )
        data = response.json()
        return data.get("solana", {}).get("usd", 0.0)
    except Exception as e:
        print("Price fetch error:", e)
        return 0.0  # fallback on error
