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
        # Load the CSV
        df = pd.read_csv("prices.csv")
        # Convert Date column to actual Date format
        df["Date"] = pd.to_datetime(df["Date"])
        # Sort by date
        df = df.sort_values("Date")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

# --- SEARCH BAR ---
# The user pastes a link here
user_url = st.text_input("🔗 Paste Product URL here:", placeholder="https://pk.khaadi.com/...")

if user_url:
    if df.empty:
        st.error("⚠️ Database is empty. Please run the tracker first.")
    else:
        # --- SMART CLEANING ---
        # The user might paste a link with "?start=24" or "?source=fb"
        # We strip that off to match your clean database links.
        clean_input = user_url.split('?')[0].strip()
        
        # Search for the link in your database
        product_data = df[df["Link"] == clean_input]
        
        if not product_data.empty:
            # Get Product Details from the latest entry
            product_name = product_data.iloc[-1]["Name"]
            current_price = product_data.iloc[-1]["Price"]
            
            # Calculate Stats
            max_price = product_data["Price"].max()
            min_price = product_data["Price"].min()
            
            # --- DISPLAY RESULT ---
            st.subheader(f"History for: {product_name}")
            
            # Stats Columns
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"Rs. {current_price}")
            c2.metric("Highest Price", f"Rs. {max_price}")
            c3.metric("Lowest Price", f"Rs. {min_price}")
            
            # --- THE GRAPH ---
            # We explicitly set the range to 0 so the graph doesn't look misleading
            fig = px.line(product_data, x="Date", y="Price", markers=True)
            fig.update_yaxes(range=[0, float(max_price) * 1.2]) # Scale y-axis nicely
            st.plotly_chart(fig, use_container_width=True)
            
            # --- DHOKA VERDICT ---
            st.subheader("⚠️ Verdict")
            try:
                curr_float = float(current_price)
                max_float = float(max_price)
                min_float = float(min_price)

                if curr_float < max_float:
                    savings = max_float - curr_float
                    st.success(f"✅ **GOOD DEAL!** This item is **Rs. {savings} cheaper** than its usual price.")
                elif curr_float > min_float:
                    st.warning(f"⚠️ **PRICE HIKE!** This item is currently expensive. Lowest recorded was Rs. {min_float}.")
                else:
                    st.info("ℹ️ **STANDARD PRICE.** This is the normal price for this item.")
            except:
                st.info("Price data is stable.")

        else:
            # If link not found
            st.warning("❌ **Product Not Found.**")
            st.write(f"We are not tracking this exact link yet. Try checking the URL.")
            st.write(f"**Your Input:** {clean_input}")

else:
    # Optional: Show a "How it works" when empty
    st.info("👈 Paste a link above to start the Dhoka Check.")
