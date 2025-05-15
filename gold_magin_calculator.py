import streamlit as st
import requests

st.set_page_config(page_title="Gold Margin Calculator with Leverage", layout="wide")

st.title("Gold Margin Calculator with Leverage")

# --- Sidebar: only leverage and ounces to trade (auto max) ---
st.sidebar.header("Settings")

leverage = st.sidebar.selectbox("Select Leverage", options=[1, 5, 10, 20, 50, 100], index=5, help="Leverage given by company")
auto_max_ounces = st.sidebar.checkbox("Auto Max Ounces to Trade", value=True)

# --- Main inputs ---
st.header("Inputs")

deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0, step=100.0)
bonus_enabled = st.checkbox("Apply Bonus", value=True)
bonus_percent = 30 if bonus_enabled else 0

bonus_amount = deposit * bonus_percent / 100
total_balance = deposit + bonus_amount

trading_ratio = st.selectbox("Trading Ratio (Trading : Margin)", options=["20:80", "30:70", "50:50", "80:20"], index=0)
trading_percent = int(trading_ratio.split(":")[0])
margin_percent = int(trading_ratio.split(":")[1])

trading_amount = total_balance * trading_percent / 100
balance_amount = total_balance * margin_percent / 100

# Price input
use_manual_price = st.checkbox("Enter Price Manually", value=False)
if use_manual_price:
    current_price = st.number_input("Enter Current Price of Gold (XAU/USD)", min_value=0.0, value=3175.0)
else:
    # Fetch live price
    try:
        response = requests.get("https://metals-api.com/api/latest?access_key=YOUR_API_KEY&base=USD&symbols=XAU")
        data = response.json()
        current_price = data['rates']['XAU']
    except Exception:
        st.warning("Unable to fetch live gold price. Please enter manually.")
        current_price = st.number_input("Enter Current Price of Gold (XAU/USD)", min_value=0.0, value=3175.0)

st.write(f"**Current Price of Gold (XAU/USD):** ${current_price:,.2f}")

# Calculate ounces without leverage
ounces_without_leverage = trading_amount / current_price if current_price > 0 else 0

# Ounces with leverage
ounces_with_leverage = ounces_without_leverage * leverage

# Ounces to trade selection
if auto_max_ounces:
    ounces_to_trade = ounces_with_leverage
else:
    ounces_to_trade = st.number_input("Enter Ounces to Trade", min_value=0.0, max_value=ounces_with_leverage, value=ounces_with_leverage)

# Calculations
used_margin = trading_amount  # margin portion put by user
buying_power = used_margin * leverage
free_margin = total_balance - used_margin
margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

# PL needed for margin levels (wanted equity to margin ratio)
# Margin level = (Equity / Margin) * 100
# For 100% margin level, Equity = Margin
pl_needed_100 = used_margin - total_balance  # How much PL to get equity = margin (margin call)
# For 20% margin level, Equity = 0.2 * Margin
pl_needed_20 = 0.2 * used_margin - total_balance

# Price drop for liquidation
# Liquidation means Equity = 0, so:
# Equity = Total Balance + PL = 0 => PL = -Total Balance
# PL = (New Price - Current Price) * Ounces to trade
# So solve for New Price:
liquidation_price = current_price - (total_balance / ounces_to_trade) if ounces_to_trade > 0 else 0
price_drop_liquidation = current_price - liquidation_price if liquidation_price > 0 else 0

# Display results in order requested

st.header("Results")

st.write(f"Amount Deposited: ${deposit:,.2f}")
st.write(f"Bonus Amount Given: ${bonus_amount:,.2f} ({bonus_percent}%)")
st.write(f"Total Balance: ${total_balance:,.2f}")
st.write(f"Trading Ratio: {trading_ratio}")

st.write(f"Trading Amount: ${trading_amount:,.2f}")
st.write(f"Balance Amount: ${balance_amount:,.2f}")

st.write(f"Current Price of Gold: ${current_price:,.2f}")

st.write(f"Ounces that can be bought with leverage: {ounces_to_trade:,.4f} oz")

st.write(f"Leverage Given by Company: 1:{leverage}")

st.write(f"Used Margin: ${used_margin:,.2f}")
st.write(f"Free Margin: ${free_margin:,.2f}")
st.write(f"Margin Level: {margin_level:,.2f}%")

st.write(f"PL Needed to get 100% Margin Level: ${pl_needed_100:,.2f}")
st.write(f"PL Needed to get 20% Margin Level: ${pl_needed_20:,.2f}")

st.write(f"Price Drop Needed for Liquidation: ${price_drop_liquidation:,.2f}")
st.write(f"Liquidation Price Level: ${liquidation_price:,.2f}")

# Profit/Loss move simulator
st.header("P/L Move Simulator")

price_move = st.number_input("Enter price move ($)", value=0.0, step=0.1)
if price_move != 0:
    new_price = current_price + price_move
    new_pl = price_move * ounces_to_trade
    new_equity = total_balance + new_pl
    new_margin_level = (new_equity / used_margin) * 100 if used_margin > 0 else 0
    st.write(f"New Price: ${new_price:,.2f}")
    st.write(f"Profit/Loss from move: ${new_pl:,.2f}")
    st.write(f"New Equity: ${new_equity:,.2f}")
    st.write(f"New Margin Level: {new_margin_level:,.2f}%")

# Buttons for calculation and recalculation can be added as needed.
