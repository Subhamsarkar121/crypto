import os
from datetime import datetime
import streamlit as st
import pandas as pd
from streamlit_chartjs.st_chart_component import st_chartjs

from api.coingecko_api import get_top_coins, get_historical_prices
from api.grok_api import get_groq_response

# Page config
st.set_page_config(page_title="Crypto Info Hub", layout="wide")

# CSS for chat bubbles and Bootstrap
st.markdown("""
<style>
.user-bubble {
    background-color: #DCF8C6;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
    max-width: 75%;
    text-align: left;
}
.bot-bubble {
    background-color: #F1F0F0;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 5px;
    max-width: 75%;
    text-align: left;
}
.user-container {
    display: flex;
    justify-content: flex-end;
}
.bot-container {
    display: flex;
    justify-content: flex-start;
}
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("Crypto Info Hub")
st.components.v1.html("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
<div class="jumbotron bg-primary text-white">
  <h1 class="display-4">Crypto Info Hub</h1>
  <p class="lead">Real-time crypto dashboard with AI chatbot.</p>
</div>
""", height=350)

# ----- Dashboard: Top 10 Cryptocurrencies -----
st.header("Top 10 Cryptocurrencies")
top_coins_full = get_top_coins(per_page=50)
top10_coins = top_coins_full[:10]
table_top10 = []
for coin in top10_coins:
    table_top10.append({
        "Name": coin.get("name"),
        "Symbol": coin.get("symbol").upper(),
        "Price (USD)": coin.get("current_price"),
        "Market Cap": coin.get("market_cap"),
        "24h Volume": coin.get("total_volume")
    })
st.table(table_top10)

# ----- Search Cryptocurrencies -----
st.header("Search Cryptocurrencies")
search_query = st.text_input("Search coins by name or symbol:")
if search_query:
    filtered_coins = [c for c in top_coins_full if search_query.lower() in c.get('name', '').lower() or search_query.lower() in c.get('symbol', '').lower()]
else:
    filtered_coins = top_coins_full

st.subheader("Search Results")
max_display = 20
table_search = []
for coin in filtered_coins[:max_display]:
    table_search.append({
        "Name": coin.get("name"),
        "Symbol": coin.get("symbol").upper(),
        "Price (USD)": coin.get("current_price"),
        "Market Cap": coin.get("market_cap"),
        "24h Volume": coin.get("total_volume")
    })
st.table(table_search)

# ----- Historical Price Chart -----
st.subheader("Price Trend for Selected Coin")
# Use filtered list for historical view if search applied, else top10
hist_coin_ids = [c.get("id") for c in filtered_coins] if search_query else [c.get("id") for c in top10_coins]
selected_coin = st.selectbox("Select a coin for the historical chart:", hist_coin_ids)
days = st.slider("Number of past days:", min_value=1, max_value=365, value=30, key="hist_days")

if selected_coin:
    prices = get_historical_prices(selected_coin, days=days)
    if prices:
        dates = [datetime.utcfromtimestamp(p[0] / 1000).strftime("%Y-%m-%d") for p in prices]
        values = [p[1] for p in prices]
        chart_data = {
            "labels": dates,
            "datasets": [{
                "label": f"{selected_coin.capitalize()} Price (USD)",
                "data": values,
                "borderColor": "rgba(75, 192, 192, 1)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderWidth": 2,
                "fill": False
            }]
        }
        st_chartjs(data=chart_data, chart_type="line", canvas_height=400)
    else:
        st.write("No historical data available for this coin.")

# ----- Compare Multiple Coins -----
st.header("Compare Multiple Coins")
coin_ids = [c.get("id") for c in top_coins_full]
selected_coins = st.multiselect("Select coins to compare:", options=coin_ids, default=["bitcoin", "ethereum"])
comp_days = st.slider("Select period (days):", min_value=1, max_value=365, value=30, key="comp_days")

if selected_coins:
    compare_data = {}
    for coin_id in selected_coins:
        prices = get_historical_prices(coin_id, days=comp_days)
        if prices:
            dates = [datetime.utcfromtimestamp(p[0] / 1000).strftime("%Y-%m-%d") for p in prices]
            values = [p[1] for p in prices]
            compare_data[coin_id.capitalize()] = {"dates": dates, "values": values}
    if compare_data:
        # Create DataFrame for multiple line chart
        df = pd.DataFrame(
            {name: data["values"] for name, data in compare_data.items()},
            index=next(iter(compare_data.values()))["dates"]
        )
        df.index = pd.to_datetime(df.index)
        st.line_chart(df)

# ----- AI Chatbot Interface -----
st.header("AI Chatbot")
st.write("Ask questions about cryptocurrencies (e.g., \"What is the price of Bitcoin?\").")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"<div class='user-container'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-container'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

# Chat input form



with st.form("chat_form"):
    question = st.text_input("Your question:")
    submit = st.form_submit_button("Send")
    if submit and question:
        try:
            answer = get_groq_response(question)
            st.write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
