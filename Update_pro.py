import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(page_title=" Live Crypto Dashboard", layout="wide")

@st.cache_data(ttl=30)
def get_coins(vs_currency="usd", top=10):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": top,
        "page": 1,
        "sparkline": "false"
    }
    return pd.DataFrame(requests.get(url, params=params).json())

# ------------------- Live Trend Chart Function -------------------
def live_trend_chart(coin_name, current_price, color):
    prices = [current_price * (0.95 + i * 0.01) for i in range(10)]
    dates = [f"Day {i+1}" for i in range(10)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=prices,
        marker_color=color,
        name=f"{coin_name} Price",
        text=[f"${p:,.2f}" for p in prices],
        textposition='auto',
        hovertemplate="%{x}: %{y:$,.2f}<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=40, b=20),
        height=350,
        xaxis_title="Days",
        yaxis_title="Price (USD)",
        title=dict(text=f"📊 {coin_name} Price Trend", x=0.5),
        font=dict(family="Arial", size=14),
        plot_bgcolor="#a8ebe7",
        paper_bgcolor="#c6ebee"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------- Sidebar Filters -------------------
st.sidebar.title("⚙️ Filters")
search = st.sidebar.text_input("🔍 Search Crypto", "")
vs_currency = st.sidebar.selectbox("💵 Display Price In:", ["usd", "eur", "try", "toman"])
top_n = st.sidebar.slider(" Number of Cryptos", min_value=5, max_value=20, value=10)
sort_by = st.sidebar.selectbox("🔄 Sort By:", ["market_cap", "total_volume", "current_price"])
st.sidebar.info("⏱ Auto-refresh every 30 seconds")

# ------------------- Fetch Data -------------------
data = get_coins(vs_currency, top_n)

# ------------------- Apply Search -------------------
if search:
    data = data[data['name'].str.contains(search, case=False, na=False)]

# ------------------- Sorting -------------------
data = data.sort_values(by=sort_by, ascending=False).reset_index(drop=True)

# ------------------- Page Title -------------------
st.markdown(
    "<h1 style='text-align:center'> Professional Live Crypto Dashboard</h1>",
    unsafe_allow_html=True
)

# ------------------- Top Cryptos Cards -------------------
coins = data["name"].tolist()
volumes = data["total_volume"].tolist()
prices = data["current_price"].tolist()
colors = [
    "#f97316","#3b82f6","#22c55e","#eab308","#ec4899","#06b6d4",
    "#8b5cf6","#ef4444","#10b981","#6366f1","#f59e0b","#14b8a6",
    "#a855f7","#f43f5e","#0ea5e9","#84cc16","#f87171","#7c3aed",
    "#facc15","#2563eb"
]


st.subheader(" Top Cryptocurrencies")
cols = st.columns(5)
for idx, row in data.iterrows():
    with cols[idx % 5]:
        st.markdown(f"### {row['name']} ({row['symbol'].upper()})")
        st.metric("💵 Price", f"${row['current_price']:,.2f}", f"{row['price_change_percentage_24h']:.2f}%")
        st.metric("📊 24h Volume", f"${row['total_volume']/1e9:.2f}B")




st.subheader(" 24h Trading Volume Comparison")
bar_fig = go.Figure(data=[
    go.Bar(
        x=coins,
        y=volumes,
        text=[f"${v:,.0f}" for v in volumes],
        textposition='auto',
        marker=dict(
            color=colors[:len(coins)],
            line=dict(color='white', width=1),
            opacity=0.9
        ),
        hovertemplate='%{x}<br>Volume: %{y:$,.0f}<extra></extra>'  
    )
])

bar_fig.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=50, b=20),
    height=500,
    xaxis_title="Cryptocurrency",
    yaxis_title="24h Volume (USD)",
    title=dict(text="💹 24h Trading Volume", x=0.5),
    font=dict(family="Arial", size=14),
    plot_bgcolor="#e3e5e8",  
    paper_bgcolor="#69f1a4"
)

st.plotly_chart(bar_fig, use_container_width=True)


# ------------------- 24h Volume Pie Chart -------------------
st.subheader(" Market Share of Cryptos (24h Volume)")
pie_fig = go.Figure(data=[
    go.Pie(
        labels=coins,
        values=volumes,
        hole=0.4,
        marker=dict(colors=colors[:len(coins)]),
        textinfo="label+percent",
        pull=[0.05]*len(coins)
    )
])
pie_fig.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=40, b=20),
    height=500,
    title=dict(text=" Market Share (24h Volume)", x=0.5),
    font=dict(family="Arial", size=14)
)
st.plotly_chart(pie_fig, use_container_width=True)

# ------------------- Auto-refresh -------------------
try:
    st.autorefresh(interval=30_000, key="datarefresh")
except AttributeError:
    try:
        st.experimental_autorefresh(interval=30_000, key="datarefresh")
    except AttributeError:
        st.markdown("<meta http-equiv='refresh' content='70'>", unsafe_allow_html=True)

# ------------------- Last Update -------------------
st.info(f"⏰ Last Updated: {time.strftime('%Y-%m-%d ** %H:%M:%S')}")
