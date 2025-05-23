import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import gspread
from kiteconnect import KiteConnect
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 Volume Shocker Screener (Zerodha)", layout="wide")

# Load API credentials from Google Sheet
SHEET_NAME = "ZerodhaTokenStore"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_kite_client():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1mANuCob4dz3jvjigeO1km96vBzZHr-4ZflZEXxR8-qU").sheet1
    api_key = sheet.cell(1, 1).value
    api_secret = sheet.cell(1, 2).value
    access_token = sheet.cell(1, 3).value

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite

# NIFTY150 symbols (example subset)
nifty150_symbols = [
    'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK',
    'BAJAJ_AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL',
    'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY',
    'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE',
    'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC',
    'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT',
    'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC',
    'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SUNPHARMA',
    'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM',
    'TITAN', 'ULTRACEMCO', 'UPL', 'WIPRO',
    'ABBOTINDIA', 'ALKEM', 'AMBUJACEM', 'AUROPHARMA', 'BANKBARODA',
    'BOSCHLTD', 'DABUR', 'DLF', 'GAIL', 'GODREJCP',
    'HAVELLS', 'ICICIPRULI', 'IDFCFIRSTB', 'INDIGO', 'IOC',
    'LTI', 'LUPIN', 'MARICO', 'MUTHOOTFIN', 'NAUKRI',
    'PEL', 'PETRONET', 'PIDILITIND', 'PIIND', 'PGHH',
    'PNB', 'SBICARD', 'SHREECEM', 'SIEMENS', 'SRF',
    'TORNTPHARM', 'TVSMOTOR', 'UBL', 'VEDL', 'VOLTAS',
    'ZYDUSLIFE',
    'ATGL', 'AUBANK', 'BANDHANBNK', 'BANKINDIA', 'BALKRISIND',
    'CHOLAFIN', 'CUMMINSIND', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC',
    'ICICIGI', 'ICICIPRULI', 'INDHOTEL', 'INDUSTOWER', 'JINDALSTEL',
    'LICHSGFIN', 'LODHA', 'MOTHERSON', 'MRF', 'MUTHOOTFIN',
    'OBEROIRLTY', 'PAGEIND', 'PERSISTENT', 'PIIND', 'PNB',
    'POLYCAB', 'RECLTD', 'SAIL', 'SHRIRAMFIN', 'TVSMOTOR',
    'TORNTPOWER', 'TRENT', 'UNIONBANK', 'VBL', 'VARUNBEV',
    'ZEEL', 'ZENSARTECH', 'CANBK', 'COFORGE', 'CROMPTON',
    'DEEPAKNTR', 'ESCORTS', 'HAL', 'IDFCFIRSTB', 'LTTS',
    'NMDC', 'PEL', 'PFIZER', 'SRF', 'SUNTV'
]

st.title("📈 NIFTY100+Midcap50 Volume Shocker Screener (Live from Zerodha)")

# Sector Mapping (sample mapping, can expand)
symbol_to_sector = {
    'RELIANCE': 'Energy', 'TCS': 'IT', 'INFY': 'IT', 'HDFCBANK': 'Bank', 'ICICIBANK': 'Bank',
    'KOTAKBANK': 'Bank', 'LT': 'Infra', 'SBIN': 'Bank', 'AXISBANK': 'Bank', 'HINDUNILVR': 'FMCG',
    'BAJFINANCE': 'NBFC', 'BAJAJFINSV': 'NBFC', 'HCLTECH': 'IT', 'WIPRO': 'IT', 'SUNPHARMA': 'Pharma',
    'DRREDDY': 'Pharma', 'TATAMOTORS': 'Auto', 'MARUTI': 'Auto', 'EICHERMOT': 'Auto', 'M&M': 'Auto',
    'ULTRACEMCO': 'Cement', 'NESTLEIND': 'FMCG', 'DIVISLAB': 'Pharma', 'POWERGRID': 'Power',
    'COALINDIA': 'Energy', 'NTPC': 'Power', 'JSWSTEEL': 'Metals', 'TATASTEEL': 'Metals',
    'ADANIENT': 'Conglomerate', 'ADANIPORTS': 'Infra', 'DABUR': 'FMCG', 'BRITANNIA': 'FMCG',
    'PIDILITIND': 'Chemicals', 'BERGEPAINT': 'Chemicals', 'HDFCLIFE': 'Insurance', 'ICICIPRULI': 'Insurance',
    'SBICARD': 'NBFC', 'LICHSGFIN': 'NBFC', 'PNB': 'Bank', 'BANKBARODA': 'Bank', 'IDFCFIRSTB': 'Bank'
    # and so on...
}

# Sector Filter
available_sectors = list(set(symbol_to_sector.values()))
selected_sectors = st.sidebar.multiselect("Select Sectors", options=available_sectors, default=available_sectors)

st.caption(f"Last updated at {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh every 5 minutes automatically
count = st_autorefresh(interval=300000, limit=None, key="auto_refresh")

threshold = st.slider("Select Surge Threshold (e.g., 2x, 3x)", 1.0, 5.0, 2.0, step=0.1)
interval = st.selectbox("Select Time Interval", ["5minute", "15minute"], index=1)

if st.button("🔄 Refresh Data"):

    kite = get_kite_client()

    # Load instrument dump
    instruments = kite.instruments(exchange="NSE")
    df_instruments = pd.DataFrame(instruments)

    results = []

    for idx, symbol in enumerate(nifty150_symbols):
        sector = symbol_to_sector.get(symbol, 'Others')
        if sector not in selected_sectors:
            continue

        with st.spinner(f"Scanning {symbol} ({idx+1}/{len(nifty150_symbols)})..."):
            try:
                row = df_instruments[df_instruments['tradingsymbol'] == symbol]
                if row.empty:
                    continue

                token = int(row['instrument_token'].values[0])

                today = datetime.now()
                from_date = today - timedelta(days=7)

                historical = kite.historical_data(
                    instrument_token=token,
                    from_date=from_date,
                    to_date=today,
                    interval=interval
                )

                df = pd.DataFrame(historical)

                if df.empty:
                    continue

                df['date'] = pd.to_datetime(df['date'])
                df_today = df[df['date'].dt.date == today.date()]

                if df_today.empty:
                    continue

                today_volume = df_today['volume'].sum()

                historical_days = df['date'].dt.date.unique()
                historical_days = [d for d in historical_days if d != today.date()]

                cumulative_volumes = []
                for day in historical_days:
                    day_volume = df[(df['date'].dt.date == day) & (df['date'].dt.time <= datetime.now().time())]['volume'].sum()
                    cumulative_volumes.append(day_volume)

                avg_volume = sum(cumulative_volumes) / len(cumulative_volumes) if cumulative_volumes else 0

                ltp = df_today['close'].iloc[-1]
                pct_change = ((df_today['close'].iloc[-1] - df_today['open'].iloc[0]) / df_today['open'].iloc[0]) * 100

                surge_ratio = today_volume / avg_volume if avg_volume else 0

                if surge_ratio >= threshold:
                    results.append({
                        "Symbol": symbol,
                        "LTP": round(ltp, 2),
                        "Today's Volume": int(today_volume),
                        "7-Day Avg Volume": int(avg_volume),
                        "Surge Ratio": round(surge_ratio, 2),
                        "% Change": round(pct_change, 2)
                    })

            except Exception as e:
                st.warning(f"⚠️ Skipping {symbol}: {e}")

    if results:
        df_results = pd.DataFrame(results).sort_values(by="Surge Ratio", ascending=False)
        st.success(f"✅ {len(df_results)} stocks found above {threshold}x surge.")
        styled_df = df_results.style.apply(lambda x: ['background-color: lightgreen' if v >= threshold * 1.5 else ('background-color: lightyellow' if v >= threshold else '') for v in x['Surge Ratio']], axis=1)
        st.dataframe(styled_df, use_container_width=True)

        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="volume_shockers.csv",
            mime='text/csv'
        )
    else:
        st.info("No stocks found meeting the volume surge criteria.")

else:
    st.info("Click '🔄 Refresh Data' to run the screener.")
