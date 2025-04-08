# ETF FIRE Tracker App (Streamlit)

import streamlit as st
import pandas as pd
from datetime import date
import os
import requests
import time

st.set_page_config(page_title="ETF FIRE Tracker", layout="wide")

# --- Theme Toggle ---
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=1)

if theme == "Light":
    st.markdown("""
        <style>
        .stApp, .css-1d391kg, .css-18ni7ap { background-color: #ffffff !important; color: #000000 !important; }
        .stDataFrame, .css-1lcbmhc { background-color: #ffffff !important; color: #000000 !important; }
        .metric-value, .metric-label { color: #000000 !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp, .css-1d391kg, .css-18ni7ap { background-color: #0e1117 !important; color: #fafafa !important; }
        .stDataFrame, .css-1lcbmhc { background-color: #0e1117 !important; color: #fafafa !important; }
        .metric-value, .metric-label { color: #fafafa !important; }
        </style>
    """, unsafe_allow_html=True)

st.title("📈 ETF FIRE Tracker - RNovaDigital")
st.caption("Digital Income. Minimal Time. Maximum Freedom.")

# --- Portfolio Setup ---
st.sidebar.header("Your ETF Portfolio")
etfs = st.sidebar.text_area(
    "Enter ETF tickers (comma separated)",
    value="VXUS,ACWI,VOO,VTI"
).upper().replace(" ", "").split(",")

# Investment amounts
amounts = {}
st.sidebar.subheader("Investment per ETF")
for etf in etfs:
    amt = st.sidebar.number_input(f"${etf} Amount Invested", min_value=0, value=0, step=100)
    amounts[etf] = amt

# FIRE Goal Input
st.sidebar.header("Your FIRE Goal")
f_target = st.sidebar.number_input("FIRE Goal ($)", min_value=1000, value=1000000, step=5000)

# --- Fetch Live Prices ---
FMP_API_KEY = os.getenv("FMP_API_KEY")
today_prices = {}

for etf in etfs:
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{etf}?apikey={FMP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        time.sleep(1)  # rate-limit friendly

        if response.status_code == 200 and data:
            price = data[0].get("price", 0)
            today_prices[etf] = price
        else:
            st.warning(f"{etf} returned no price data.")
            today_prices[etf] = 0
    except Exception as e:
        st.warning(f"Error fetching data for {etf}: {e}")
        today_prices[etf] = 0

# --- Display Portfolio Table ---
portfolio_data = []
total_invested = 0
total_value = 0
for etf in etfs:
    invested = amounts.get(etf, 0)
    price = today_prices.get(etf, 0)
    units = invested / price if price else 0
    value = units * price
    total_invested += invested
    total_value += value
    portfolio_data.append({
        'ETF': etf,
        'Invested ($)': invested,
        'Current Price ($)': round(price, 2),
        'Units': round(units, 4),
        'Current Value ($)': round(value, 2)
    })

df = pd.DataFrame(portfolio_data)
st.subheader("💼 Your Portfolio")
st.dataframe(df, use_container_width=True)

# --- FIRE Progress ---
progress = round(total_value / f_target * 100, 2)
st.subheader("🔥 FIRE Goal Progress")
st.metric("Total Invested", f"${total_invested:,.2f}")
st.metric("Current Value", f"${total_value:,.2f}")
st.metric("FIRE Goal", f"${f_target:,.0f}")

# Dynamic color logic
color = "#ff4b4b" if progress < 25 else "#f9c74f" if progress < 75 else "#4caf50"
st.markdown(f"""
    <div style='background-color:{color}; height:24px; border-radius:5px; width:{min(progress, 100)}%; text-align:center; color:white; font-weight:bold;'>
        {progress}% to FIRE
    </div>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by [RnovaDigital](https://www.rnovadigital.com)")
