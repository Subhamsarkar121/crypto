import pytest
from api.coingecko_api import get_top_coins, get_historical_prices

class DummyCG:
    def get_coins_markets(self, **kwargs):
        return [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc",
                 "current_price": 50000, "market_cap": 900000000, "total_volume": 25000000}]
    def get_coin_market_chart_by_id(self, id, vs_currency, days, interval):
        return {"prices": [[1609459200000, 29000], [1609545600000, 30000]]}

@pytest.fixture(autouse=True)
def mock_coingecko(monkeypatch):
    dummy = DummyCG()
    # Patch the CoinGeckoAPI instance in our module
    monkeypatch.setattr('api.coingecko_api.cg', dummy)

def test_get_top_coins():
    coins = get_top_coins(per_page=1, page=1)
    assert isinstance(coins, list)
    assert coins[0]["id"] == "bitcoin"
    assert "current_price" in coins[0]

def test_get_historical_prices():
    prices = get_historical_prices("bitcoin", days=2)
    assert isinstance(prices, list) and len(prices) == 2
    # Check structure of prices
    ts, price = prices[0]
    assert isinstance(ts, (int, float))
    assert isinstance(price, (int, float))

