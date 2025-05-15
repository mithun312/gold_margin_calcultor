import streamlit as st
import requests

# Function to fetch live gold price from Finnhub
def fetch_live_gold_price():
    try:
        response = requests.get(
            "https://finnhub.io/api/v1/quote?symbol=OANDA:XAU_USD&token=d0j2v11r01ql09hprm30d0j2v11r01ql09hprm3g"
        )
        data = response.json()
        return data["c"]
    except:
        return None

st.title("Gold Margin Trading Calculator")

# Sidebar Inputs
st.sidebar.header("Leverage & Trade Size")
leverage = st.sidebar.number_input("Leverage (e.g., 100 for 1:100)", min_value=1, value=100)

# Placeholder for max ounces
selected_ounces_placeholder = st.sidebar.empty()

# Main Inputs
st.header("Trading Parameters")

deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0)

use_bonus = st.checkbox("Apply Bonus?", value=True)
bonus_percent = st.slider("Bonus Percentage (%)", 0, 100, 30) if use_bonus else 0

trading_ratio = st.selectbox("Trading Ratio (Trading:Balance)", ["20:80", "30:70", "50:50"])
trading_ratio_value = float(trading_ratio.split(":")[0]) / 100

use_live_price = st.checkbox("Use Live Gold Price (XAU/USD)?", value=True)

if use_live_price:
    gold_price = fetch_live_gold_price()
    if gold_price:
        st.write(f"*Current Live Gold Price:* ${gold_price}")
    else:
        st.error("Unable to fetch live gold price — check connection.")
        gold_price = st.number_input("Enter Gold Price per Ounce ($)", min_value=0.0, value=3175.0)
else:
    gold_price = st.number_input("Enter Gold Price per Ounce ($)", min_value=0.0, value=3175.0)

# Calculate Button
if st.button("Calculate"):
    bonus = deposit * (bonus_percent / 100) if use_bonus else 0
    total_balance = deposit + bonus

    trading_funds = total_balance * trading_ratio_value
    balance_amount = total_balance - trading_funds

    buying_power = trading_funds * leverage
    max_ounces = round(buying_power / gold_price, 2)

    # Update max ounces input
    selected_ounces = selected_ounces_placeholder.number_input(
        f"Ounces to Trade (max {max_ounces} oz)", min_value=0.0, value=max_ounces, max_value=max_ounces, key="trade_ounces"
    )

    used_margin = (selected_ounces * gold_price) / leverage
    free_margin = total_balance - used_margin
    margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

    # Liquidation Calculations
    margin_call_100 = 100
    margin_call_50 = 50

    equity_at_100 = used_margin * (margin_call_100 / 100)
    pl_needed_100 = equity_at_100 - total_balance

    equity_at_50 = used_margin * (margin_call_50 / 100)
    pl_needed_50 = equity_at_50 - total_balance

    per_dollar_move = selected_ounces
    price_drop_100 = abs(pl_needed_100) / per_dollar_move if per_dollar_move != 0 else 0
    price_drop_50 = abs(pl_needed_50) / per_dollar_move if per_dollar_move != 0 else 0

    liquidation_price_100 = gold_price - price_drop_100
    liquidation_price_50 = gold_price - price_drop_50

    # Results Display
    st.subheader("Result Summary")

    st.write(f"*Amount Deposited:* ${deposit:,.2f}")
    st.write(f"*Bonus Amount Given:* ${bonus:,.2f} ({bonus_percent}%)")
    st.write(f"*Total Balance:* ${total_balance:,.2f}")
    st.write(f"*Trading Ratio:* {trading_ratio}")

    st.write(f"*Trading Amount (Funds):* ${trading_funds:,.2f}")
    st.write(f"*Balance Amount (Non-Trading):* ${balance_amount:,.2f}")

    st.write(f"*Max Ounces You Can Buy:* {max_ounces:,.4f} oz")
    st.write(f"*Leverage Given by Company:* 1:{leverage}")
    st.write(f"*Ounces Selected to Trade:* {selected_ounces:,.4f} oz")

    st.write(f"*Used Margin:* ${used_margin:,.2f}")
    st.write(f"*Free Margin:* ${free_margin:,.2f}")
    st.write(f"*Margin Level:* {margin_level:,.2f}%")

    st.write(f"*P/L Needed for 100% Margin Call:* ${pl_needed_100:,.2f}")
    st.write(f"*P/L Needed for 50% Margin Call:* ${pl_needed_50:,.2f}")

    st.write(f"*Price Drop Needed for 100% Liquidation:* ${price_drop_100:,.2f}")
    st.write(f"*Liquidation Price at 100% Margin Call:* ${liquidation_price_100:,.2f}")

    # P/L Move Simulator
    st.subheader("P/L Move Simulator")
    price_move = st.number_input("Price Move in $ (up/down)", value=10)
    pl_change = selected_ounces * price_move
    st.write(f"*P/L for ${price_move} move:* ${pl_change:,.2f}")
    
