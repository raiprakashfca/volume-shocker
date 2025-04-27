import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 Volume Shocker Screener", layout="wide")

# Load NIFTY100 symbols (hardcoded for now)
nifty100_symbols = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
    'KOTAKBANK.NS', 'LT.NS', 'SBIN.NS', 'AXISBANK.NS', 'HINDUNILVR.NS'
    # Add rest later for full list
]

st.title("📈 NIFTY100 Volume Shocker Screener")

# Surge Threshold Multiplier
threshold = st.slider("Select Surge Threshold (e.g., 2x, 3x)", 1.0, 5.0, 2.0, step=0.1)

# Refresh Button
if st.button("🔄 Refresh Data"):

    results = []
    progress = st.progress(0)

    for idx, symbol in enumerate(nifty100_symbols):
        progress.progress((idx + 1) / len(nifty100_symbols))

        try:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=15)

            data = yf.download(symbol, start=start_date, end=end_date, interval='1d')

            if data.empty or len(data) < 8:
                continue

            last_7_days = data.iloc[-8:-1]
            today = data.iloc[-1]

            avg_volume = last_7_days['Volume'].mean()
            today_volume = today['Volume']
            ltp = today['Close']
            pct_change = ((today['Close'] - today['Open']) / today['Open']) * 100

            surge_ratio = float(today_volume) / float(avg_volume) if avg_volume else 0

            if surge_ratio >= threshold:
                results.append({
                    "Symbol": symbol.replace(".NS", ""),
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
        st.dataframe(df_results, use_container_width=True)

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
