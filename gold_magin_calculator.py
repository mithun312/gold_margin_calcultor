import streamlit as st
import requests

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

def calculate_all(deposit, bonus_pct, use_bonus, trading_ratio, current_price, leverage, auto_max_ounces, manual_price_entered, ounces_to_trade_input):
    bonus_amount = deposit * bonus_pct / 100 if use_bonus else 0
    total_balance = deposit + bonus_amount
    trading_amount = total_balance * trading_ratio / 100
    balance_amount = total_balance - trading_amount

    ounces_max = trading_amount / current_price
    ounces_to_trade = ounces_to_trade_input if not auto_max_ounces else ounces_max

    used_margin = ounces_to_trade * current_price
    buying_power = used_margin * leverage
    free_margin = total_balance - used_margin
    margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

    pl_100_margin_call = used_margin
    pl_50_margin_call = used_margin * 0.5

    price_drop_liquidation = current_price * 0.5
    liquidation_price_level = current_price - price_drop_liquidation

    return dict(
        bonus_amount=bonus_amount,
        total_balance=total_balance,
        trading_amount=trading_amount,
        balance_amount=balance_amount,
        current_price=current_price,
        ounces_to_trade=ounces_to_trade,
        used_margin=used_margin,
        buying_power=buying_power,
        free_margin=free_margin,
        margin_level=margin_level,
        pl_100_margin_call=pl_100_margin_call,
        pl_50_margin_call=pl_50_margin_call,
        price_drop_liquidation=price_drop_liquidation,
        liquidation_price_level=liquidation_price_level,
    )

def main():
    st.title("Gold Trading Calculator with Live Price")

    st.sidebar.header("Settings")
    leverage = st.sidebar.selectbox("Select Leverage", options=[1, 10, 20, 50, 100], index=4)
    auto_max_ounces = st.sidebar.checkbox("Auto-calculate max ounces", value=True)

    deposit = st.number_input("Amount Deposited ($)", min_value=0.0, value=3000.0, step=10.0)

    use_bonus = st.checkbox("Use Bonus", value=True)
    bonus_pct = st.slider("Bonus Percentage (%)", min_value=0, max_value=100, value=30) if use_bonus else 0

    trading_ratio = st.selectbox(
        "Trading Ratio (%)", options=[10,20,30,40,50,60,70,80,90,100], index=3
    )

    # Try fetch live price
    price = get_gold_price(API_KEY)
    if price:
        st.success(f"Live Gold Price (XAU/USD): ${price:.2f}")
    else:
        st.warning("Unable to fetch live gold price.")

    # Manual price input toggle
    manual_entry = st.button("Enter Price Manually")
    manual_price = None
    if manual_entry:
        manual_price = st.number_input(
            "Enter Gold Price Manually (USD per ounce)",
            min_value=0.0,
            value=price if price else 3175.0,
            step=0.1,
            key="manual_price_input"
        )

    # Select which price to use: if manual price entered use that, else live price, else default
    current_price = manual_price if manual_price is not None else price if price else 3175.0

    # Ounces input if not auto max
    ounces_to_trade_input = None
    if not auto_max_ounces:
        ounces_to_trade_input = st.number_input("Enter ounces to trade", min_value=0.0, step=0.0001, key="ounces_input")

    # Initialize session state dict to store calculation
    if "calc_results" not in st.session_state:
        st.session_state.calc_results = None
        st.session_state.calculated_price = None

    # Calculate or Recalculate buttons
    col1, col2 = st.columns(2)
    calc_clicked = col1.button("Calculate")
    recalc_clicked = col2.button("Recalculate")

    if calc_clicked or recalc_clicked:
        # On calculate or recalc, save results to session state
        results = calculate_all(
            deposit=deposit,
            bonus_pct=bonus_pct,
            use_bonus=use_bonus,
            trading_ratio=trading_ratio,
            current_price=current_price,
            leverage=leverage,
            auto_max_ounces=auto_max_ounces,
            manual_price_entered=manual_price is not None,
            ounces_to_trade_input=ounces_to_trade_input if ounces_to_trade_input is not None else 0
        )
        st.session_state.calc_results = results
        st.session_state.calculated_price = current_price

    # Display results only if calculated before
    if st.session_state.calc_results is not None:
        r = st.session_state.calc_results
        st.subheader("Results")

        st.write(f"*Amount Deposited:* ${deposit:,.2f}")
        st.write(f"*Bonus Amount Given ({bonus_pct}%):* ${r['bonus_amount']:,.2f}")
        st.write(f"*Total Balance:* ${r['total_balance']:,.2f}")
        st.write(f"*Trading Ratio:* {trading_ratio}%")

        st.write(f"*Trading Amount:* ${r['trading_amount']:,.2f}")
        st.write(f"*Balance Amount:* ${r['balance_amount']:,.2f}")

        # Display price used for calculation (fixed until recalc)
        st.write(f"*Current Price of Gold:* ${st.session_state.calculated_price:.2f}")

        st.write(f"*Ounces that can be bought/traded:* {r['ounces_to_trade']:.4f} oz")

        st.write(f"*Leverage Given by Company:* 1:{leverage}")
        st.write(f"*Ounces that can be bought with leverage:* {(r['buying_power'] / st.session_state.calculated_price):.4f} oz")

        st.write(f"*Used Margin:* ${r['used_margin']:,.2f}")
        st.write(f"*Free Margin:* ${r['free_margin']:,.2f}")
        st.write(f"*Margin Level:* {r['margin_level']:.2f}%")

        st.write(f"*PL Needed for 100% Margin Call:* ${r['pl_100_margin_call']:,.2f}")
        st.write(f"*PL Needed for 50% Margin Call:* ${r['pl_50_margin_call']:,.2f}")

        st.write(f"*Price Drop Needed for Liquidation:* ${r['price_drop_liquidation']:,.2f}")
        st.write(f"*Liquidation Price Level:* ${r['liquidation_price_level']:,.2f}")

        st.subheader("Profit/Loss Move Simulator")
        pl_move = st.slider("Move in price per ounce ($)", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        pl_result = pl_move * r['ounces_to_trade'] * leverage
        st.write(f"Potential P/L for this move: ${pl_result:,.2f}")

if __name__ == "__main__":
    main()
