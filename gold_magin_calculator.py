import streamlit as st
import requests

st.set_page_config(page_title="Gold Margin Calculator with Leverage", layout="wide")

st.title("Gold Margin Calculator with Leverage")

# --- Sidebar ---
st.sidebar.header("Settings")
leverage = st.sidebar.selectbox("Select Leverage", options=[1, 5, 10, 20, 50, 100], index=5, help="Leverage given by company")
auto_max_ounces = st.sidebar.checkbox("Auto Max Ounces to Trade", value=True)

# --- Main Inputs ---
st.header("Inputs")

deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0, step=100.0)

bonus_enabled = st.checkbox("Apply Bonus", value=True)
bonus_percent = 30 if bonus_enabled else 0

if bonus_enabled:
    bonus_percent = st.slider("Bonus Percentage (%)", min_value=0, max_value=100, value=bonus_percent)
else:
    bonus_percent = 0

bonus_amount = deposit * bonus_percent / 100
total_balance = deposit + bonus_amount

trading_ratio = st.selectbox("Trading Ratio (Trading : Margin)", options=["20:80", "30:70", "50:50", "80:20"], index=0)
trading_percent = int(trading_ratio.split(":")[0])
margin_percent = int(trading_ratio.split(":")[1])

trading_amount = total_balance * trading_percent / 100
balance_amount = total_balance * margin_percent / 100

use_manual_price = st.checkbox("Enter Price Manually", value=False)
if use_manual_price:
    current_price = st.number_input("Enter Current Price of Gold (XAU/USD)", min_value=0.0, value=3175.0)
else:
    # Live price fetch from goldapi.io with your key
    try:
        headers = {'x-access-token': 'goldapi-2u42yussmappvwby-io'}
        response = requests.get("https://www.goldapi.io/api/XAU/USD", headers=headers)
        data = response.json()
        current_price = data.get('price', 0)
        if current_price == 0:
            st.warning("Live price not found in response. Please enter manually.")
            current_price = st.number_input("Enter Current Price of Gold (XAU/USD)", min_value=0.0, value=3175.0)
    except Exception:
        st.warning("Unable to fetch live gold price. Please enter manually.")
        current_price = st.number_input("Enter Current Price of Gold (XAU/USD)", min_value=0.0, value=3175.0)

# Calculate ounces without leverage
ounces_without_leverage = trading_amount / current_price if current_price > 0 else 0

# Calculate ounces with leverage
ounces_with_leverage = ounces_without_leverage * leverage

if auto_max_ounces:
    ounces_to_trade = ounces_with_leverage
else:
    ounces_to_trade = st.number_input("Enter Ounces to Trade", min_value=0.0, max_value=ounces_with_leverage, value=ounces_with_leverage)

# Margin and Equity calculations
used_margin = trading_amount
free_margin = total_balance - used_margin
margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

# PL needed for margin levels
# PL needed to get 100% margin level: equity = margin
pl_needed_100 = used_margin - total_balance

# PL needed to get 20% margin level (equity = 0.2 * margin)
pl_needed_20 = 0.2 * used_margin - total_balance

# Liquidation price calculation (price at which equity = 0)
liquidation_price = current_price - (total_balance / ounces_to_trade) if ounces_to_trade > 0 else 0
price_drop_liquidation = current_price - liquidation_price if liquidation_price > 0 else 0

# --- Display Results ---
st.header("Results")

st.markdown(f"**Amount Deposited:** ${deposit:,.2f}")
st.markdown(f"**Bonus Amount Given:** ${bonus_amount:,.2f} ({bonus_percent}%)")
st.markdown(f"**Total Balance:** ${total_balance:,.2f}")
st.markdown(f"**Trading Ratio:** {trading_ratio}")

st.markdown(f"**Trading Amount:** ${trading_amount:,.2f}")
st.markdown(f"**Balance Amount:** ${balance_amount:,.2f}")

st.markdown(f"**Current Price of Gold:** ${current_price:,.2f}")

st.markdown(f"**Ounces that can be bought (without leverage):** {ounces_without_leverage:,.4f} oz")
st.markdown(f"**Ounces that can be bought with leverage:** {ounces_with_leverage:,.4f} oz")
st.markdown(f"**Ounces to trade (selected):** {ounces_to_trade:,.4f} oz")

st.markdown(f"**Leverage Given by Company:** 1:{leverage}")

st.markdown(f"**Used Margin:** ${used_margin:,.2f}")
st.markdown(f"**Free Margin:** ${free_margin:,.2f}")
st.markdown(f"**Margin Level:** {margin_level:,.2f}%")

st.markdown(f"**PL Needed to get 100% Margin Level:** ${pl_needed_100:,.2f}")
st.markdown(f"**PL Needed to get 20% Margin Level:** ${pl_needed_20:,.2f}")

st.markdown(f"**Price Drop Needed for Liquidation:** ${price_drop_liquidation:,.2f}")
st.markdown(f"**Liquidation Price Level:** ${liquidation_price:,.2f}")

# --- PL Move Simulator ---
st.header("Profit/Loss Move Simulator")

price_move = st.number_input("Enter price move ($)", value=0.0, step=0.1)
if price_move != 0:
    new_price = current_price + price_move
    new_pl = price_move * ounces_to_trade
    new_equity = total_balance + new_pl
    new_margin_level = (new_equity / used_margin) * 100 if used_margin > 0 else 0
    st.markdown(f"**New Price:** ${new_price:,.2f}")
    st.markdown(f"**Profit/Loss from move:** ${new_pl:,.2f}")
    st.markdown(f"**New Equity:** ${new_equity:,.2f}")
    st.markdown(f"**New Margin Level:** {new_margin_level:,.2f}%")
