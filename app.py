import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="SaleSpy: Dhoka Check", page_icon="🕵️‍♂️", layout="centered")

# --- HEADER ---
st.title("🕵️‍♂️ SaleSpy")
st.write("Track the *real* price history of Khaadi products.")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("prices.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SECTION 1: 🔥 HOT DEALS (The New Feature) ---
    st.header("🔥 Today's Price Drops")
    
    # 1. Find the latest date in the database
    latest_date = df["Date"].max()
    
    # 2. Get data for just today
    today_data = df[df["Date"] == latest_date]
    
    deals = []
    
    # 3. Check each product for a price drop
    for index, row in today_data.iterrows():
        product_name = row["Name"]
        current_price = float(row["Price"])
        link = row["Link"]
        
        # Get history for this specific product
        history = df[df["Name"] == product_name]
        
        # We need at least 2 days of data to compare
        if len(history) > 1:
            # Get the highest price in the last 30 days
            max_price_30d = history["Price"].max()
            
            # If current price is lower than the high, it's a Deal!
            if current_price < max_price_30d:
                saving = max_price_30d - current_price
                percent_off = int((saving / max_price_30d) * 100)
                deals.append({
                    "Product": product_name,
                    "New Price": f"Rs. {int(current_price)}",
                    "Was": f"Rs. {int(max_price_30d)}",
                    "Saving": f"Rs. {int(saving)} ({percent_off}%)",
                    "Link": link
                })
    
    # 4. Show the Deals
    if deals:
        deals_df = pd.DataFrame(deals)
        st.dataframe(deals_df, hide_index=True, use_container_width=True)
        st.caption(f"Found {len(deals)} items cheaper today than their recent high.")
    else:
        st.info("No price drops detected today. Khaadi is holding prices steady.")

    st.markdown("---")

# --- SECTION 2: SEARCH BAR (Existing Feature) ---
user_url = st.text_input("🔗 Paste Product URL to check history:", placeholder="https://pk.khaadi.com/...")

if user_url and not df.empty:
    clean_input = user_url.split('?')[0].strip()
    product_data = df[df["Link"] == clean_input]
    
    if not product_data.empty:
        product_name = product_data.iloc[-1]["Name"]
        current_price = product_data.iloc[-1]["Price"]
        max_price = product_data["Price"].max()
        min_price = product_data["Price"].min()
        
        st.subheader(product_name)
        c1, c2, c3 = st.columns(3)
        c1.metric("Current", f"Rs. {current_price}")
        c2.metric("Highest", f"Rs. {max_price}")
        c3.metric("Lowest", f"Rs. {min_price}")
        
        fig = px.line(product_data, x="Date", y="Price", markers=True)
        fig.update_yaxes(range=[0, float(max_price) * 1.2])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Product not found in database.")
# --- SIDEBAR INFO ---
with st.sidebar:
    st.header("ℹ️ About SaleSpy")
    st.write("""
    **SaleSpy** tracks prices daily to detect:
    * 📉 Real Price Drops
    * 📈 Hidden Price Hikes
    * ❌ Fake 'Sales'
    """)
    st.caption("Built by Owais Ahmad | Data updates daily at 10 AM PKT")
