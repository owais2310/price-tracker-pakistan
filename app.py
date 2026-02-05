import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SaleSpy: Dhoka Check", page_icon="🕵️‍♂️", layout="centered")

# --- CUSTOM CSS: DARK MODE & HACKER AESTHETIC ---
st.markdown("""
<style>
    /* 1. HIDE STREAMLIT BRANDING & MENU */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. HIDE THE RED 'DEPLOY' BUTTON (Admin View) */
    .stDeployButton {display:none;}

    /* 3. MAIN BACKGROUND & TEXT */
    .stApp {
        background-color: #000000; /* Pitch Black */
        color: #00FF41; /* Hacker Green */
    }

    /* 4. INPUT FIELD (SEARCH BAR) */
    div[data-baseweb="input"] {
        background-color: #111111 !important; /* Dark Grey */
        border: 1px solid #00FF41 !important; /* Green Border */
        color: #ffffff !important; /* White Text */
        border-radius: 5px;
    }
    
    /* 5. METRIC CARDS (Prices) */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important; /* White Numbers */
        font-family: 'Courier New', monospace; /* Hacker Font */
    }
    div[data-testid="stMetricLabel"] {
        color: #aaaaaa !important; /* Grey Labels */
    }

    /* 6. SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important; /* Very Dark Grey */
        border-right: 1px solid #333333;
    }

    /* 7. BUTTONS */
    button {
        border: 1px solid #00FF41 !important;
        color: #00FF41 !important;
        background-color: transparent !important;
    }
    button:hover {
        background-color: #00FF41 !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

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
        st.error("⚠️ Database is empty. Please wait for the tracker to run.")
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
            
            # Display Product Name & Stats
            st.markdown(f"### {product_name}")
            
            # Use columns for metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"Rs. {current_price}")
            c2.metric("Highest Price", f"Rs. {max_price}")
            c3.metric("Lowest Price", f"Rs. {min_price}")
            
            # --- NEON GRAPH LOGIC ---
            fig = px.line(product_data, x="Date", y="Price", markers=True)
            
            # Customize the Graph for Dark Mode
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',  
                font=dict(color="white"),      
                margin=dict(l=10, r=10, t=30, b=10), 
                xaxis=dict(showgrid=False, linecolor='#333333'),
                yaxis=dict(showgrid=True, gridcolor='#222222', zerolinecolor='#333333'),
                hovermode="x unified"
            )
            # FIX: Corrected line_width syntax here
            fig.update_traces(
                line_color='#00FF41', 
                line_width=3,  # <--- This was the fix
                marker=dict(size=8, color='#00FF41')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # --- VERDICT LOGIC ---
            curr_float = float(current_price)
            max_float = float(max_price)
            
            st.markdown("### ⚠️ Verdict")
            if curr_float < max_float:
                save = max_float - curr_float
                st.success(f"✅ **GOOD DEAL!** Cheaper by Rs. {save} compared to history.")
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
    st.markdown("""
    **SaleSpy** tracks prices daily to detect:
    * 📉 Real Price Drops
    * 📈 Hidden Price Hikes
    * ❌ Fake 'Sales'
    """)
    st.caption("Built by Owais Ahmad | Data updates daily at 10 AM PKT")
