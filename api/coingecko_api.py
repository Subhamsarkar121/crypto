from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_top_coins(vs_currency='usd', per_page=10, page=1):
    """
    Fetches top cryptocurrencies by market capitalization.
    Returns a list of coin data dictionaries (name, price, market cap, etc.).
    """
    return cg.get_coins_markets(
        vs_currency=vs_currency,
        order='market_cap_desc',
        per_page=per_page,
        page=page,
        sparkline=False
    )

def get_historical_prices(coin_id, vs_currency='usd', days=30):
    """
    Fetches historical market data for a given coin ID.
    Returns list of [timestamp, price] for the past 'days'.
    """
    data = cg.get_coin_market_chart_by_id(
        id=coin_id,
        vs_currency=vs_currency,
        days=days,
        interval='daily'
    )
    return data.get('prices', [])
