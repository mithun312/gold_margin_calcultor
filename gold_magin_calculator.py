import streamlit as st
import requests

# --- Function to fetch live gold price from goldapi.io ---
def fetch_live_gold_price(api_key):
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {'x-access-token': api_key, 'Content-Type': 'application/json'}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("price", None)
        else:
            return None
    except Exception:
        return None

# --- Calculation function ---
def calculate_all(deposit, bonus_pct, use_bonus, trading_ratio, current_price, leverage, auto_max_ounces, ounces_to_trade_input):
    bonus_amount = deposit * bonus_pct / 100 if use_bonus else 0
    total_balance = deposit + bonus_amount
    trading_amount = total_balance * trading_ratio / 100
    balance_amount = total_balance - trading_amount

    ounces_max = trading_amount / current_price if current_price > 0 else 0
    ounces_to_trade = ounces_to_trade_input if not auto_max_ounces else ounces_max

    used_margin = ounces_to_trade * current_price
    buying_power = used_margin * leverage
    free_margin = total_balance - used_margin
    margin_level = (total_balance / used_margin) * 100 if used_margin != 0 else 0

    # PL needed to reach margin levels (100% and 20%)
    pl_100_margin_level = used_margin - total_balance
    pl_20_margin_level = 0.2 * used_margin - total_balance

    price_drop_liquidation = current_price - (total_balance / ounces_to_trade) if ounces_to_trade > 0 else 0
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
        pl_100_margin_level=pl_100_margin_level,
        pl_20_margin_level=pl_20_margin_level,
        price_drop_liquidation=price_drop_liquidation,
        liquidation_price_level=liquidation_price_level,
    )

# --- Streamlit UI ---

st.title("Gold Margin Calculator")

# Sidebar for leverage and ounces
st.sidebar.header("Settings")
leverage_option = st.sidebar.selectbox("Select Leverage", options=[1, 10, 50, 100, 200], index=3)
auto_max_ounces = st.sidebar.checkbox("Auto max ounces to trade", value=True)

# Main input section
st.subheader("Deposit & Bonus")
deposit = st.number_input("Deposit Amount (USD)", min_value=0.0, value=3000.0, step=100.0)
use_bonus = st.checkbox("Use Bonus", value=True)
bonus_pct = 30  # fixed 30% bonus for this version
st.write(f"Bonus Percentage: {bonus_pct}%")

st.subheader("Trading Settings")
trading_ratio = st.selectbox("Trading Ratio (Trading Amount / Total Balance)", options=[20, 30, 40, 50, 60, 70, 80], index=1)

# Live price fetch with manual override toggle
st.subheader("Gold Price (XAU/USD)")
api_key = "goldapi-2u42yussmappvwby-io"  # replace with your key
live_price = fetch_live_gold_price(api_key)
manual_price_toggle = st.checkbox("Enter Price Manually", value=False)

if manual_price_toggle:
    current_price = st.number_input("Enter Current Gold Price", min_value=0.0, value=live_price if live_price else 3200.0)
else:
    if live_price:
        st.write(f"Live Gold Price: ${live_price:,.2f}")
        current_price = live_price
    else:
        st.warning("Unable to fetch live price, please enter manually.")
        current_price = st.number_input("Enter Current Gold Price", min_value=0.0, value=3200.0)

# Ounces to trade input if not auto max
if not auto_max_ounces:
    ounces_to_trade_input = st.number_input("Ounces to Trade", min_value=0.0, value=0.0, step=0.01)
else:
    ounces_to_trade_input = 0.0

if st.button("Calculate") or 'calculated' not in st.session_state:
    # Calculate results
    results = calculate_all(deposit, bonus_pct, use_bonus, trading_ratio, current_price, leverage_option, auto_max_ounces, ounces_to_trade_input)
    st.session_state['results'] = results
    st.session_state['calculated'] = True

if st.session_state.get('calculated', False):
    r = st.session_state['results']

    st.markdown("---")
    st.subheader("Calculation Results")

    st.write(f"**Amount Deposited:** ${deposit:,.2f}")
    st.write(f"**Bonus Amount Given:** ${r['bonus_amount']:,.2f} ({bonus_pct}%)" if use_bonus else "Bonus not used")
    st.write(f"**Total Balance:** ${r['total_balance']:,.2f}")
    st.write(f"**Trading Ratio:** {trading_ratio}%")
    st.write(f"**Trading Amount:** ${r['trading_amount']:,.2f}")
    st.write(f"**Balance Amount:** ${r['balance_amount']:,.2f}")
    st.write(f"**Current Price of Gold:** ${r['current_price']:,.2f}")
    st.write(f"**Ounces that can be bought/traded:** {r['ounces_to_trade']:,.4f} oz")
    st.write(f"**Leverage Given by Company:** 1:{leverage_option}")
    st.write(f"**Ounces that can be bought with leverage:** {r['ounces_to_trade'] * leverage_option:,.4f} oz")
    st.write(f"**Used Margin:** ${r['used_margin']:,.2f}")
    st.write(f"**Buying Power:** ${r['buying_power']:,.2f}")
    st.write(f"**Free Margin:** ${r['free_margin']:,.2f}")
    st.write(f"**Margin Level:** {r['margin_level']:,.2f}%")
    st.write(f"**PL Needed to Reach 100% Margin Level:** ${r['pl_100_margin_level']:,.2f}")
    st.write(f"**PL Needed to Reach 20% Margin Level:** ${r['pl_20_margin_level']:,.2f}")
    st.write(f"**Price Drop Needed for Liquidation:** ${r['price_drop_liquidation']:,.2f}")
    st.write(f"**Liquidation Price Level:** ${r['liquidation_price_level']:,.2f}")

    # PL move simulator
    st.subheader("PL Move Simulator")
    price_move = st.number_input("Enter price move (positive or negative)", value=0.0, step=0.1)
    if price_move != 0:
        new_price = current_price + price_move
        new_pl = (new_price - current_price) * r['ounces_to_trade']
        new_equity = r['total_balance'] + new_pl
        new_margin_level = (new_equity / r['used_margin']) * 100 if r['used_margin'] > 0 else 0
        st.write(f"New Price: ${new_price:,.2f}")
        st.write(f"Profit/Loss from move: ${new_pl:,.2f}")
        st.write(f"New Equity: ${new_equity:,.2f}")
        st.write(f"New Margin Level: {new_margin_level:,.2f}%")

if st.button("Recalculate"):
    st.session_state['calculated'] = False
    st.experimental_rerun()
