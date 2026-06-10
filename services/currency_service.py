import os
import requests
import json
import logging
from cachetools import TTLCache
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache for 1 hour
currency_cache = TTLCache(maxsize=10, ttl=3600)
CACHE_KEY = "latest_rates_usd"

class CurrencyService:
    def __init__(self):
        self.api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")
        self.fallback_path = Path(__file__).parent.parent / "db" / "currency_fallback.json"

    def get_latest_rates(self):
        """Fetch latest rates from API or cache, with local fallback."""
        if CACHE_KEY in currency_cache:
            return currency_cache[CACHE_KEY]

        if self.api_key and self.api_key != "YOUR_API_KEY":
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                if data.get("result") == "success":
                    currency_cache[CACHE_KEY] = data
                    return data
            except Exception as e:
                logger.error(f"Error fetching from Currency API: {e}")

        # Fallback to local JSON
        return self._get_fallback_rates()

    def _get_fallback_rates(self):
        """Load rates from local JSON file."""
        try:
            with open(self.fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading fallback rates: {e}")
            # Absolute emergency fallback
            return {
                "result": "success",
                "conversion_rates": {"USD": 1.0, "MAD": 10.0, "EUR": 0.9},
                "currency_names": {"USD": "USD", "MAD": "MAD", "EUR": "EUR"}
            }

    def convert(self, amount: float, from_curr: str, to_curr: str):
        """Perform conversion between two currencies."""
        data = self.get_latest_rates()
        rates = data.get("conversion_rates", {})

        if from_curr not in rates or to_curr not in rates:
            return None, f"Currency {from_curr} or {to_curr} not found."

        # Convert to USD base first, then to target
        amount_in_usd = amount / rates[from_curr]
        result = amount_in_usd * rates[to_curr]
        
        return result, None

    def get_history(self, from_curr: str, to_curr: str, days: int = 30):
        """Generate simulated historical data for the last X days."""
        import random
        from datetime import datetime, timedelta

        base_rate, error = self.convert(1.0, from_curr, to_curr)
        if error or base_rate is None:
            return None

        history = []
        current_rate = base_rate
        # Generate data from past to present
        for i in range(days, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            # Random variation ±1% per day
            variation = random.uniform(-0.012, 0.012)
            current_rate = current_rate * (1 + variation)
            history.append({
                "date": date,
                "value": round(current_rate, 4)
            })
            
        # Ensure the last point is exactly today's correct rate
        history[-1]["value"] = round(base_rate, 4)
        return history

currency_service = CurrencyService()
