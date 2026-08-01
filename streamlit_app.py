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
        width: 100%;
        height: 45px;
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
""", unsafe_allow_html=True)

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
            
            lat, lon = "40.1016", "-82.9850" # Default fallback
            display_name = address
            using_fallback_geo = False
            
            try:
                geo_res = requests.get(geocode_url, headers=headers, timeout=5).json()
                if geo_res:
                    lat = geo_res[0]["lat"]
                    lon = geo_res[0]["lon"]
                    display_name = geo_res[0]["display_name"]
                else:
                    using_fallback_geo = True
            except Exception:
                using_fallback_geo = True
                
            # 2. Call NREL PVWatts API with local mathematical fallback
            annual_kwh = None
            using_local_engine = False
            api_key = "DEMO_KEY"
            pvwatts_url = f"https://developer.nrel.gov/api/pvwatts/v8.json?api_key={api_key}&lat={lat}&lon={lon}&system_capacity={system_size}&azimuth=180&tilt=20&array_type=1&losses=14"
            
            try:
                # Try calling NREL API
                pv_res = requests.get(pvwatts_url, timeout=5).json()
                if "outputs" in pv_res:
                    annual_kwh = pv_res["outputs"]["ac"]
                else:
                    using_local_engine = True
            except Exception:
                using_local_engine = True
                
            # Local Math Fallback Engine (Runs if API fails or network timeout)
            if using_local_engine:
                try:
                    lat_f = float(lat)
                except ValueError:
                    lat_f = 40.0
                
                # Capacity factor based on latitude
                if lat_f > 50.0:  # UK / Scotland / Ireland
                    capacity_factor = 0.105 # ~10.5% capacity factor
                    region_name = "UK / Ireland (Northern Europe)"
                elif lat_f > 38.0: # US Midwest, Mountain, Pacific Northwest
                    capacity_factor = 0.145 # ~14.5% capacity factor
                    region_name = "US Midwest / Mountain / Pacific Northwest"
                else: # US Southern Sun Belt (Texas, Florida)
                    capacity_factor = 0.178 # ~17.8% capacity factor
                    region_name = "US Southern Sun Belt"
                
                annual_kwh = system_size * 8760 * capacity_factor
                st.info(f"ℹ️ Local Engine active for: {region_name} (Capacity Factor: {capacity_factor*100:.1f}%)")
            else:
                st.success("🛰️ Connected to Live NREL Database!")

            # 3. Calculate Financials
            grid_annual_cost = annual_kwh * current_rate
            ppa_rate = current_rate * (1 - (ppa_discount / 100))
            ppa_annual_cost = annual_kwh * ppa_rate
            
            annual_savings = grid_annual_cost - ppa_annual_cost
            co2_saved_tons = (annual_kwh * 0.85) / 2000
            
            # Display Beautiful Results
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
📍 Property: {display_name}
🛰️ Geo-Coordinates: Lat {float(lat):.4f}, Lon {float(lon):.4f}
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
