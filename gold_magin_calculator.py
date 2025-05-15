import streamlit as st
import requests

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
            return data.get("price")
        else:
            st.error("Failed to fetch live gold price. Using manual input.")
            return None
    except Exception as e:
        st.error(f"Error fetching gold price: {e}")
        return None

def main():
    st.title("Gold Trading Calculator with Live Price")

    # Sidebar - only leverage and ounces to trade
    st.sidebar.header("Settings")
    leverage = st.sidebar.selectbox("Select Leverage", options=[1, 10, 50, 100], index=3)
    ounces_to_trade_auto = st.sidebar.checkbox("Auto-calculate max ounces", value=True)
    manual_ounces = st.sidebar.number_input("Enter ounces to trade (if auto off)", min_value=0.0, step=0.01)

    # Main UI inputs
    deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0)
    bonus_pct = st.slider("Bonus Percentage (%)", min_value=0, max_value=100, value=30)
    use_bonus = st.checkbox("Use Bonus", value=True)
    trading_ratio = st.selectbox("Trading Ratio (%)", options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], index=3)

    # Session state for API key
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    st.session_state.api_key = st.text_input("Enter your GoldAPI Key", value=st.session_state.api_key)

    # Fetch live price or manual input
    price = None
    if st.session_state.api_key:
        price = get_gold_price(st.session_state.api_key)
    if price is None:
        price = st.number_input("Current Price of Gold (USD per ounce)", min_value=0.0, value=3175.0)

    # Calculate values
    bonus_amount = deposit * bonus_pct / 100 if use_bonus else 0
    total_balance = deposit + bonus_amount
    trading_amount = total_balance * trading_ratio / 100
    balance_amount = total_balance - trading_amount

    ounces_max = trading_amount / price
    ounces_to_trade = ounces_max if ounces_to_trade_auto else manual_ounces

    buying_power = ounces_to_trade * price * leverage

    used_margin = ounces_to_trade * price
    free_margin = total_balance - used_margin
    margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

    liquidation_price_100 = price * 0.5  # assuming 50% margin call price drop
    liquidation_price_50 = price * 0.75  # assuming 25% margin call price drop

    # Display results
    st.subheader("Results")

    st.write(f"Amount Deposited: ${deposit:.2f}")
    st.write(f"Bonus Amount Given ({bonus_pct}%): ${bonus_amount:.2f}")
    st.write(f"Total Balance: ${total_balance:.2f}")
    st.write(f"Trading Ratio: {trading_ratio}%")
    st.write(f"Trading Amount: ${trading_amount:.2f}")
    st.write(f"Balance Amount: ${balance_amount:.2f}")
    st.write(f"Ounces that can be bought/traded: {ounces_to_trade:.4f} oz")
    st.write(f"Leverage Given by Company: {leverage}:1")
    st.write(f"Ounces that can be bought with leverage: {buying_power / price:.4f} oz")
    st.write(f"Used Margin: ${used_margin:.2f}")
    st.write(f"Free Margin: ${free_margin:.2f}")
    st.write(f"Margin Level: {margin_level:.2f}%")
    st.write(f"PL Needed for 100% Margin Call: ${used_margin:.2f}")
    st.write(f"PL Needed for 50% Margin Call: ${used_margin * 0.5:.2f}")
    st.write(f"Price Drop Needed for Liquidation (50% margin call): ${price - liquidation_price_100:.2f}")
    st.write(f"Liquidation Price Level: ${liquidation_price_100:.2f}")

    # PL move simulator
    st.subheader("Profit/Loss Move Simulator")
    pl_move = st.slider("Move in price per ounce ($)", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
    pl_result = pl_move * ounces_to_trade * leverage
    st.write(f"Potential P/L for this move: ${pl_result:.2f}")

if _name_ == "_main_":
    main()
