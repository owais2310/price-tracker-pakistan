import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="SaleSpy: Dhoka Check", page_icon="🕵️‍♂️", layout="centered")

# --- HEADER ---
st.title("🕵️‍♂️ SaleSpy")
st.write("Paste a Khaadi product link to see its *real* price history.")

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

# --- SEARCH BAR ---
user_url = st.text_input("🔗 Paste Product URL to check history:", placeholder="https://pk.khaadi.com/...")

if user_url:
    if df.empty:
        st.error("⚠️ Database is empty. Please run the tracker first.")
    else:
        # Clean the input link
        clean_input = user_url.split('?')[0].strip()
        
        # Search in database
        product_data = df[df["Link"] == clean_input]
        
        if not product_data.empty:
            # Get latest details
            product_name = product_data.iloc[-1]["Name"]
            current_price = product_data.iloc[-1]["Price"]
            max_price = product_data["Price"].max()
            min_price = product_data["Price"].min()
            
            # Display Stats
            st.subheader(product_name)
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"Rs. {current_price}")
            c2.metric("Highest Price", f"Rs. {max_price}")
            c3.metric("Lowest Price", f"Rs. {min_price}")
            
            # Display Graph
            fig = px.line(product_data, x="Date", y="Price", markers=True)
            fig.update_yaxes(range=[0, float(max_price) * 1.2]) # Nice scaling
            st.plotly_chart(fig, use_container_width=True)
            
            # Verdict Logic
            curr_float = float(current_price)
            max_float = float(max_price)
            
            st.subheader("⚠️ Verdict")
            if curr_float < max_float:
                save = max_float - curr_float
                st.success(f"✅ **GOOD DEAL!** Cheaper by Rs. {save} compared to its history.")
            elif curr_float > float(min_price):
                st.warning(f"⚠️ **PRICE HIKE!** Expensive. Lowest was Rs. {min_price}.")
            else:
                st.info("ℹ️ **STANDARD PRICE.** No major changes detected.")

        else:
            st.warning("❌ **Product Not Found.**")
            st.write("We haven't tracked this specific link yet. Try another one!")

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
