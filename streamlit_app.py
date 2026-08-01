import streamlit as st
import requests

# Set page configuration to be mobile-friendly and beautiful
st.set_page_config(
    page_title="GreenCruise AI - Solar Modeler",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Emerald/Teal Theme
st.markdown("""
    <style>
    .main {
        background-color: #0b1511;
        color: #e0f2f1;
    }
    h1, h2, h3 {
        color: #00bfa5 !important;
    }
    .stButton>button {
        background-color: #00bfa5;
        color: #0b1511;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #00897b;
        color: white;
    }
    .report-box {
        background-color: #12221c;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00bfa5;
        font-family: monospace;
        color: #a7ffeb;
    }
    </style>
""", unsafe_allow_headers=True)

st.title("☀️ GreenCruise AI")
st.subheader("Mobile Solar & PPA Feasibility Modeler")

st.markdown("""
Use this private tool to instantly calculate commercial solar potential, PPA rates, and 20-year savings for any address on Earth.
""")

# Input Fields
address = st.text_input("📍 Commercial Building Address", placeholder="e.g. 1105 Schrock Rd, Columbus, OH 43229")

# Sliders for easy adjustments on mobile touchscreens
system_size = st.slider("⚡ Target System Size (kW DC)", min_value=10, max_value=2000, value=250, step=10)
current_rate = st.slider("💵 Current Utility Rate ($/kWh)", min_value=0.05, max_value=0.50, value=0.18, step=0.01)
ppa_discount = st.slider("📉 Proposed PPA Discount (%)", min_value=10, max_value=50, value=30, step=5)

# Calculate Button
if st.button("🚀 Generate Savings Report"):
    if not address:
        st.error("Please enter a valid address first.")
    else:
        with st.spinner("Analyzing coordinates and simulating solar output..."):
            # 1. Geocode via OpenStreetMap (No API key required, mobile-friendly)
            geocode_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
            headers = {"User-Agent": "GreenCruise_AI_Mobile_App/1.0"}
            
            try:
                geo_res = requests.get(geocode_url, headers=headers).json()
                if not geo_res:
                    st.error("Address not found. Please try a more specific address.")
                else:
                    lat = geo_res[0]["lat"]
                    lon = geo_res[0]["lon"]
                    display_name = geo_res[0]["display_name"]
                    
                    # 2. Call NREL PVWatts API (Uses DEMO_KEY, free)
                    api_key = "DEMO_KEY"
                    pvwatts_url = f"https://developer.nrel.gov/api/pvwatts/v8.json?api_key={api_key}&lat={lat}&lon={lon}&system_capacity={system_size}&azimuth=180&tilt=20&array_type=1&losses=14"
                    
                    pv_res = requests.get(pvwatts_url).json()
                    annual_kwh = pv_res["outputs"]["ac"]
                    
                    # 3. Calculate Financials
                    grid_annual_cost = annual_kwh * current_rate
                    ppa_rate = current_rate * (1 - (ppa_discount / 100))
                    ppa_annual_cost = annual_kwh * ppa_rate
                    
                    annual_savings = grid_annual_cost - ppa_annual_cost
                    co2_saved_tons = (annual_kwh * 0.85) / 2000
                    
                    # Display Beautiful Results
                    st.success("Analysis Complete!")
                    
                    st.metric("Estimated Year 1 Savings", f"${annual_savings:,.2f}")
                    st.metric("Estimated 20-Year Savings", f"${annual_savings * 20:,.2f}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Annual Energy Generated", f"{annual_kwh:,.0f} kWh")
                        st.metric("Proposed PPA Rate", f"${ppa_rate:.3f}/kWh")
                    with col2:
                        st.metric("CO2 Saved Annually", f"{co2_saved_tons:.1f} Tons")
                        st.metric("System Size", f"{system_size} kW DC")
                    
                    # Generated Plain-Text Report for Easy Copy/Paste on Mobile
                    st.subheader("📋 Copyable Report Text")
                    report_text = f"""GREENCRUISE AI SOLAR FEASIBILITY REPORT
--------------------------------------------------
📍 Property: {address}
🛰️ Geo-Coordinates: Lat {lat[:7]}, Lon {lon[:7]}
⚡ Recommended Solar Array: {system_size} kW DC
📈 Annual Production: {annual_kwh:,.0f} kWh / year

FINANCIAL ANALYSIS ($0 UPFRONT CAPEX):
--------------------------------------------------
* Current Utility Rate: ${current_rate:.2f} / kWh
* Proposed PPA Rate: ${ppa_rate:.3f} / kWh ({ppa_discount}% Discount)
* Estimated Year 1 Savings: ${annual_savings:,.2f}
* Estimated 20-Year Savings: ${annual_savings * 20:,.2f}
* CO2 Footprint Reduction: {co2_saved_tons:.1f} Metric Tons / year

👉 100% Funded. $0 Installation. $0 Maintenance."""
                    
                    st.text_area("Tap and hold to copy directly to your email or WhatsApp:", value=report_text, height=300)
                    
            except Exception as e:
                st.error(f"Analysis failed. Please try again. Error: {e}")
