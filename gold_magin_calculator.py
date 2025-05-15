import streamlit as st
import requests

# Your GoldAPI key here
API_KEY = "goldapi-2u42yussmappvwby-io"

def get_gold_price(api_key):
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            price = data.get("price")
            if price:
                return price
        return None
    except Exception:
        return None

def main():
    st.title("Gold Trading Calculator with Live Price")

    # Sidebar - only leverage and auto max ounces toggle
    st.sidebar.header("Settings")
    leverage = st.sidebar.selectbox("Select Leverage", options=[1, 10, 20, 50, 100], index=4)
    auto_max_ounces = st.sidebar.checkbox("Auto-calculate max ounces", value=True)

    # Main inputs
    deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0, step=10.0)

    use_bonus = st.checkbox("Use Bonus", value=True)
    bonus_pct = st.slider("Bonus Percentage (%)", min_value=0, max_value=100, value=30) if use_bonus else 0

    trading_ratio = st.selectbox(
        "Trading Ratio (%)", options=[10,20,30,40,50,60,70,80,90,100], index=3
    )

    # Get live price or manual input option
    price = get_gold_price(API_KEY)
    if price:
        st.success(f"Live Gold Price (XAU/USD): ${price:.2f}")
    else:
        st.warning("Unable to fetch live gold price. Please enter manually.")

    manual_price = st.number_input(
        "Current Price of Gold (USD per ounce)", 
        min_value=0.0, 
        value=price if price else 3175.0, 
        step=0.1
    )

    # Decide which price to use (manual overrides live)
    current_price = manual_price

    # Ounces to trade input (disabled if auto)
    ounces_max = None  # will calculate after deposit etc.

    if not auto_max_ounces:
        ounces_to_trade = st.number_input("Enter ounces to trade", min_value=0.0, step=0.0001)
    else:
        ounces_to_trade = None  # will calculate after calc button pressed

    # Calculate button
    if st.button("Calculate"):

        # Calculations
        bonus_amount = deposit * bonus_pct / 100 if use_bonus else 0
        total_balance = deposit + bonus_amount
        trading_amount = total_balance * trading_ratio / 100
        balance_amount = total_balance - trading_amount

        ounces_max = trading_amount / current_price
        if auto_max_ounces:
            ounces_to_trade = ounces_max

        used_margin = ounces_to_trade * current_price
        buying_power = used_margin * leverage
        free_margin = total_balance - used_margin
        margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

        # P/L needed for margin calls (assuming margin calls at 100% and 50%)
        pl_100_margin_call = used_margin  # lose all margin
        pl_50_margin_call = used_margin * 0.5  # lose half margin

        # Price drop needed for liquidation (liquidation price level)
        # Assuming liquidation at 50% margin call level price drop
        price_drop_liquidation = current_price * 0.5
        liquidation_price_level = current_price - price_drop_liquidation

        # Results display in requested order
        st.subheader("Results")

        st.write(f"*Amount Deposited:* ${deposit:,.2f}")
        st.write(f"*Bonus Amount Given ({bonus_pct}%):* ${bonus_amount:,.2f}")
        st.write(f"*Total Balance:* ${total_balance:,.2f}")
        st.write(f"*Trading Ratio:* {trading_ratio}%")

        st.write(f"*Trading Amount:* ${trading_amount:,.2f}")
        st.write(f"*Balance Amount:* ${balance_amount:,.2f}")

        st.write(f"*Ounces that can be bought/traded:* {ounces_to_trade:.4f} oz")

        st.write(f"*Leverage Given by Company:* {leverage}:1")
        st.write(f"*Ounces that can be bought with leverage:* {(buying_power / current_price):.4f} oz")

        st.write(f"*Used Margin:* ${used_margin:,.2f}")
        st.write(f"*Free Margin:* ${free_margin:,.2f}")
        st.write(f"*Margin Level:* {margin_level:.2f}%")

        st.write(f"*PL Needed for 100% Margin Call:* ${pl_100_margin_call:,.2f}")
        st.write(f"*PL Needed for 50% Margin Call:* ${pl_50_margin_call:,.2f}")

        st.write(f"*Price Drop Needed for Liquidation:* ${price_drop_liquidation:,.2f}")
        st.write(f"*Liquidation Price Level:* ${liquidation_price_level:,.2f}")

        # PL move simulator
        st.subheader("Profit/Loss Move Simulator")
        pl_move = st.slider("Move in price per ounce ($)", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        pl_result = pl_move * ounces_to_trade * leverage
        st.write(f"Potential P/L for this move: ${pl_result:,.2f}")

if _name_ == "_main_":
    main()
