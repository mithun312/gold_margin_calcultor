import streamlit as st
import requests

# API setup
api_key = "goldapi-2u42yussmappvwby-io"
api_url = "https://www.goldapi.io/api/XAU/USD"
headers = {"x-access-token": api_key, "Content-Type": "application/json"}

# Function to fetch current gold price
def fetch_gold_price():
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        return data["price"]
    except:
        return None

# Sidebar: Leverage and Ounces
st.sidebar.title("Settings")
leverage = st.sidebar.selectbox("Select Leverage", [50, 100, 200, 500], index=1)
ounces_to_trade = st.sidebar.number_input("Ounces to Trade (optional)", min_value=0.0, value=0.0, step=0.1)

# Title
st.title("Gold Margin Calculator")

# Account Setup Inputs
deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0, step=100.0)
use_bonus = st.checkbox("Use Bonus?", value=True)
if use_bonus:
    bonus_percent = st.slider("Bonus Percentage", 0, 100, 30)
else:
    bonus_percent = 0

trading_ratio = st.selectbox("Trading Ratio (Trading % : Margin %)", [(20, 80), (50, 50), (80, 20)])

use_live_price = st.checkbox("Fetch Live Gold Price?", value=True)
if use_live_price:
    current_price = fetch_gold_price()
    if current_price is None:
        st.error("Unable to fetch live gold price.")
        current_price = st.number_input("Enter Gold Price Manually ($)", min_value=0.0, value=3175.0)
else:
    current_price = st.number_input("Enter Gold Price Manually ($)", min_value=0.0, value=3175.0)

# Calculate button
if st.button("Calculate"):

    # Bonus and Balance
    bonus_amount = deposit * (bonus_percent / 100)
    total_balance = deposit + bonus_amount

    # Trading and Balance amounts
    trading_amount = total_balance * (trading_ratio[0] / 100)
    balance_amount = total_balance - trading_amount

    # Buyable ounces
    ounces_buyable = trading_amount / current_price

    # Leveraged ounces
    leveraged_ounces = ounces_buyable * leverage if ounces_to_trade == 0 else ounces_to_trade

    # Margin Calculations
    used_margin = (leveraged_ounces * current_price) / leverage
    free_margin = total_balance - used_margin
    equity = total_balance
    margin_level = (equity / used_margin) * 100 if used_margin != 0 else 0

    # Price drop for 100% and 50% Margin Level
    price_drop_100 = (total_balance - used_margin) / leveraged_ounces
    price_drop_50 = (total_balance - (used_margin * 0.5)) / leveraged_ounces

    price_at_100 = current_price - price_drop_100
    price_at_50 = current_price - price_drop_50

    # Display Results
    st.subheader("Results")
    st.markdown(f"**Amount Deposited:** **${deposit:.2f}**")
    st.markdown(f"**Bonus Amount Given ({bonus_percent}%):** **${bonus_amount:.2f}**")
    st.markdown(f"**Total Balance:** **${total_balance:.2f}**")
    st.markdown(f"**Trading Ratio:** **{trading_ratio[0]}:{trading_ratio[1]}**")
    st.markdown(f"**Trading Amount:** **${trading_amount:.2f}**")
    st.markdown(f"**Balance Amount:** **${balance_amount:.2f}**")
    st.markdown(f"**Current Gold Price (XAU/USD):** **${current_price:.2f}**")
    st.markdown(f"**Ounces That Can Be Bought:** **{ounces_buyable:.2f} oz**")
    st.markdown(f"**Leverage Given by Company:** **1:{leverage}**")
    st.markdown(f"**Ounces That Can Be Bought with Leverage:** **{leveraged_ounces:.2f} oz**")
    st.markdown(f"**Used Margin:** **${used_margin:.2f}**")
    st.markdown(f"**Free Margin:** **${free_margin:.2f}**")
    st.markdown(f"**Margin Level:** **{margin_level:.2f}%**")
    st.markdown(f"**Gold Price Drop Needed for 100% Margin Level:** **${current_price - price_at_100:.2f}**")
    st.markdown(f"**Gold Price Drop Needed for 50% Margin Level:** **${current_price - price_at_50:.2f}**")

    # P/L Simulator
    price_move = st.number_input("Enter Price Move ($) to Simulate P/L", value=0.0, step=0.1)
    simulated_pl = leveraged_ounces * price_move
    st.markdown(f"**Profit/Loss from Move:** **${simulated_pl:.2f}**")

# Recalculate Button
if st.button("Recalculate"):
    st.experimental_rerun()
