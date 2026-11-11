import os
import re
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PakSim Insights & AI Telecom Hub",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for an Advanced Modern UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .carrier-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        color: white;
    }
    .jazz-badge { background-color: #DC2626; }
    .zong-badge { background-color: #16A34A; }
    .ufone-badge { background-color: #EA580C; }
    .telenor-badge { background-color: #0284C7; }
    .scom-badge { background-color: #4F46E5; }
    .unknown-badge { background-color: #64748B; }
    .notice-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Operator Metadata & Prefix Allocation (PTA Standard)
CARRIER_DATA = {
    "Jazz": {
        "prefixes": ["0300", "0301", "0302", "0303", "0304", "0305", "0306", "0307", "0308", "0309",
                     "0320", "0321", "0322", "0323", "0324", "0325"],
        "color": "#DC2626",
        "badge_class": "jazz-badge",
        "helpline": "111",
        "ussd_balance": "*111#",
        "ussd_data": "*117*2#",
        "tagline": "Dunya Ko Bata Do"
    },
    "Zong": {
        "prefixes": ["0310", "0311", "0312", "0313", "0314", "0315", "0316", "0317", "0318"],
        "color": "#16A34A",
        "badge_class": "zong-badge",
        "helpline": "310",
        "ussd_balance": "*222#",
        "ussd_data": "*102#",
        "tagline": "A New Dream"
    },
    "Ufone": {
        "prefixes": ["0330", "0331", "0332", "0333", "0334", "0335", "0336", "0337"],
        "color": "#EA580C",
        "badge_class": "ufone-badge",
        "helpline": "333",
        "ussd_balance": "*124#",
        "ussd_data": "*706#",
        "tagline": "Tum Hi To Ho"
    },
    "Telenor": {
        "prefixes": ["0340", "0341", "0342", "0343", "0344", "0345", "0346", "0347", "0348", "0349"],
        "color": "#0284C7",
        "badge_class": "telenor-badge",
        "helpline": "345",
        "ussd_balance": "*444#",
        "ussd_data": "*999#",
        "tagline": "Jo Har Haal Mein Saath Nibhaye"
    },
    "SCOM": {
        "prefixes": ["0355"],
        "color": "#4F46E5",
        "badge_class": "scom-badge",
        "helpline": "111-726-626",
        "ussd_balance": "*125#",
        "ussd_data": "*125#",
        "tagline": "Connecting the Heights (AJK & GB)"
    }
}

def clean_phone_number(raw_num: str) -> str:
    """Normalize input into standard 03XXXXXXXXX format."""
    digits = re.sub(r"\D", "", raw_num)
    if digits.startswith("92") and len(digits) == 12:
        return "0" + digits[2:]
    if digits.startswith("0") and len(digits) == 11:
        return digits
    if len(digits) == 10 and digits.startswith("3"):
        return "0" + digits
    return digits

def detect_carrier(cleaned_num: str):
    """Identify issuing carrier based on the standard 4-digit prefix."""
    if len(cleaned_num) < 4:
        return None, "Invalid Length"
    prefix = cleaned_num[:4]
    for carrier, details in CARRIER_DATA.items():
        if prefix in details["prefixes"]:
            return carrier, details
    return "Unknown", None

def get_gemini_client(api_key: str):
    """Instantiate Gemini client supporting modern SDKs."""
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            return legacy_genai
        except Exception:
            return None

def query_gemini(client, prompt: str) -> str:
    """Query Gemini 2.5 Flash for package analysis or telecom assistance."""
    try:
        # Check if google-genai Client
        if hasattr(client, "models"):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        # Fallback to legacy SDK
        model = client.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

# Generate synthetic 7-day usage history based on phone seed
def generate_usage_history(phone_number: str):
    today = datetime.date.today()
    seed = sum(int(c) for c in phone_number if c.isdigit()) or 42
    
    dates = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    records = []
    
    base_mbs = (seed * 85) % 1200 + 400
    for i, d in enumerate(dates):
        daily_mb = int(base_mbs + ((i * 137 + seed * 19) % 850))
        day_mb = int(daily_mb * 0.65)
        night_mb = daily_mb - day_mb
        records.append({
            "Date": d.strftime("%a (%b %d)"),
            "Day Data (MB)": day_mb,
            "Night Data (MB)": night_mb,
            "Total (MB)": daily_mb
        })
    return pd.DataFrame(records)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sim-card-chip.png", width=64)
    st.title("Settings & Keys")
    
    api_key_env = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google AI Studio API Key",
        value=api_key_env,
        type="password",
        help="Get your free API key at aistudio.google.com"
    )
    st.markdown("---")
    
    st.subheader("Simulated Plan Specs")
    plan_type = st.selectbox("Active Plan Tier", ["Monthly Super Card", "Weekly Mega Plus", "Daily Heavy User", "Custom Plan"])
    
    allocated_mb = st.number_input("Allocated Data Quota (MB)", min_value=500, max_value=100000, value=15000, step=1000)
    allocated_onnet = st.number_input("Allocated On-Net Mins", min_value=0, max_value=10000, value=3000, step=250)
    allocated_offnet = st.number_input("Allocated Off-Net Mins", min_value=0, max_value=2000, value=300, step=50)

    st.markdown("---")
    st.info("💡 **Developer Notice:** In Pakistan, telecom operators (Jazz, Zong, Ufone, Telenor) do not provide public unauthenticated APIs to read live customer balances or call detail records (CDRs) due to PTA privacy rules. Live balance access requires subscriber OTP verification.")

# ==================== MAIN INTERFACE ====================
st.markdown('<div class="main-title">PakSim Network & Bundle Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Identify carrier prefix, monitor MBs & minutes, visualize 7-day usage trends, and analyze bundles with Gemini AI.</div>', unsafe_allow_html=True)

# Phone Input Form
col_input, col_action = st.columns([3, 1])
with col_input:
    user_phone = st.text_input(
        "Enter Pakistani Mobile Number",
        placeholder="e.g. 0300 1234567, +92312 9876543, or 03451234567",
        help="Supports standard formats with or without +92/dashes"
    )

with col_action:
    st.write("")
    st.write("")
    analyze_btn = st.button("🔍 Check Details", type="primary", use_container_width=True)

if user_phone:
    cleaned = clean_phone_number(user_phone)
    carrier_name, details = detect_carrier(cleaned)
    
    if len(cleaned) != 11 or not cleaned.startswith("03"):
        st.error("⚠️ Please enter a valid 11-digit Pakistani mobile number starting with 03 (e.g., 03001234567).")
    else:
        # Carrier Header Card
        badge_class = details["badge_class"] if details else "unknown-badge"
        color = details["color"] if details else "#475569"
        
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border-radius: 12px; padding: 20px; border-left: 6px solid {color}; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h3 style="margin: 0; color: #1E293B;">Subscriber Number: <span style="font-family: monospace;">{cleaned[:4]}-{cleaned[4:]}</span></h3>
                    <p style="margin: 4px 0 0 0; color: #64748B;">{details.get('tagline', '') if details else 'Unknown Network'}</p>
                </div>
                <div>
                    <span class="carrier-badge {badge_class}">
                        📶 {carrier_name} Network
                    </span>
                </div>
            </div>
            <div style="display: flex; gap: 24px; margin-top: 14px; font-size: 0.9rem; color: #334155; flex-wrap: wrap;">
                <div><strong>Prefix:</strong> {cleaned[:4]}</div>
                <div><strong>Helpline:</strong> {details['helpline'] if details else 'N/A'}</div>
                <div><strong>Balance USSD:</strong> <code>{details['ussd_balance'] if details else 'N/A'}</code></div>
                <div><strong>Data Check USSD:</strong> <code>{details['ussd_data'] if details else 'N/A'}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # MNP Disclaimer
        st.markdown("""
        <div class="notice-box">
            ℹ️ <strong>Portability Note:</strong> Network identification is computed from PTA's national prefix allocation. If this SIM was ported to another network via Mobile Number Portability (MNP), dial your carrier's balance USSD code above to confirm live ported status.
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Dashboard, History, and AI Assistant
        tab1, tab2, tab3 = st.tabs(["📊 Live Quotas & Balances", "📈 7-Day Usage History", "🤖 AI Telecom Studio"])
        
        # TAB 1: Live Quota & Usage
        with tab1:
            st.subheader(f"Current Package Balances ({plan_type})")
            
            # Deterministic simulation based on number seed
            num_seed = sum(int(c) for c in cleaned)
            spent_pct = 0.25 + (num_seed % 50) / 100.0
            remaining_mb = int(allocated_mb * (1.0 - spent_pct))
            spent_mb = allocated_mb - remaining_mb
            
            rem_onnet = int(allocated_onnet * (1.0 - (spent_pct * 0.8)))
            rem_offnet = int(allocated_offnet * (1.0 - (spent_pct * 1.1)))
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Remaining Data", f"{remaining_mb:,} MB", f"-{spent_mb:,} MB used", delta_color="inverse")
            with c2:
                st.metric("On-Net Minutes", f"{rem_onnet:,} Mins", f"{allocated_onnet - rem_onnet} used")
            with c3:
                st.metric("Off-Net Minutes", f"{rem_offnet:,} Mins", f"{allocated_offnet - rem_offnet} used")
            with c4:
                st.metric("SMS Balance", "1,850 SMS", "Valid for 14 Days")
            
            st.markdown("#### Quota Consumption Progress")
            mb_pct = (remaining_mb / allocated_mb) * 100
            st.write(f"**Data Remaining:** {remaining_mb:,} MB / {allocated_mb:,} MB ({mb_pct:.1f}%)")
            st.progress(remaining_mb / allocated_mb)
            
            onnet_pct = (rem_onnet / allocated_onnet) * 100
            st.write(f"**On-Net ({carrier_name} to {carrier_name}):** {rem_onnet:,} / {allocated_onnet:,} Mins ({onnet_pct:.1f}%)")
            st.progress(rem_onnet / allocated_onnet)
            
            offnet_pct = (rem_offnet / allocated_offnet) * 100
            st.write(f"**Off-Net (Other Networks):** {rem_offnet:,} / {allocated_offnet:,} Mins ({offnet_pct:.1f}%)")
            st.progress(rem_offnet / allocated_offnet)
            
        # TAB 2: Usage History & Visualizations
        with tab2:
            st.subheader("Last 7 Days Data Consumption History")
            df_history = generate_usage_history(cleaned)
            
            col_chart1, col_chart2 = st.columns([2, 1])
            
            with col_chart1:
                fig = px.bar(
                    df_history,
                    x="Date",
                    y=["Day Data (MB)", "Night Data (MB)"],
                    title="Daily Data Consumption (MBs)",
                    barmode="stack",
                    color_discrete_sequence=[color, "#94A3B8"]
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with col_chart2:
                app_breakdown = pd.DataFrame({
                    "Category": ["Social (WhatsApp/FB)", "Video (YouTube/TikTok)", "Browsing & Web", "Gaming & Other"],
                    "Share (MB)": [int(df_history['Total (MB)'].sum() * p) for p in [0.40, 0.35, 0.15, 0.10]]
                })
                pie_fig = px.pie(
                    app_breakdown,
                    names="Category",
                    values="Share (MB)",
                    title="Traffic Distribution",
                    hole=0.4,
                    color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]
                )
                pie_fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(pie_fig, use_container_width=True)
                
            st.markdown("##### Detailed Daily Log")
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            
        # TAB 3: AI Telecom Studio (Gemini Powered)
        with tab3:
            st.subheader("🤖 AI Telecom Assistant (Powered by Google AI Studio)")
            
            active_key = api_key_input or api_key_env
            gemini_client = get_gemini_client(active_key)
            
            if not active_key:
                st.warning("🔑 Please enter your Google AI Studio API key in the sidebar to activate the AI Package Advisor and SMS Parser.")
            else:
                ai_action = st.radio(
                    "Choose AI Capability:",
                    ["📄 Parse Carrier Confirmation SMS", "💡 Recommend Best Packages", "❓ General Telecom Inquiry"],
                    horizontal=True
                )
                
                if ai_action == "📄 Parse Carrier Confirmation SMS":
                    st.write("Paste any official SMS sent by your telecom operator to extract package details automatically:")
                    sample_sms = f"Muaziz Sarif, apka {carrier_name} Weekly Mega offer activate ho gaya hai. Apko mile hain 10,000 MBs, 1000 {carrier_name} Mins, aur 100 Offnet Mins taa-waqt 7 din."
                    sms_text = st.text_area("Carrier SMS Text", value=sample_sms, height=100)
                    
                    if st.button("🚀 Analyze SMS with Gemini"):
                        prompt = f"""
                        You are an expert telecom assistant in Pakistan.
                        Analyze the following confirmation SMS from network {carrier_name}:
                        "{sms_text}"
                        
                        Extract and format the response in clean Markdown with:
                        - Package Name
                        - Total MBs / Internet Quota
                        - On-Net Minutes
                        - Off-Net Minutes
                        - Validity / Expiry Date
                        - Estimated Value Rating (Good, Average, Excellent)
                        """
                        with st.spinner("Gemini is reading and structuring your package..."):
                            analysis = query_gemini(gemini_client, prompt)
                            st.markdown(analysis)
                            
                elif ai_action == "💡 Recommend Best Packages":
                    user_budget = st.slider("Select your budget (PKR)", 100, 2500, 450, step=50)
                    user_pref = st.multiselect("Key Requirements", ["High Speed 4G Data", "Social Media Only", "All-Net Calling", "Monthly Long Validity", "Night Data"], default=["High Speed 4G Data"])
                    
                    if st.button("✨ Find Best Packages"):
                        prompt = f"""
                        Act as an authoritative telecom package advisor for Pakistan.
                        User is on network: {carrier_name}.
                        Budget: PKR {user_budget}.
                        Key Priorities: {', '.join(user_pref)}.
                        
                        Recommend the top 2-3 current packages available on {carrier_name} matching this criteria.
                        Include package names, subscription USSD codes (e.g. *xxx#), price including tax, MBs, and minutes.
                        """
                        with st.spinner("Analyzing telecom bundles..."):
                            recs = query_gemini(gemini_client, prompt)
                            st.markdown(recs)
                            
                else:
                    user_query = st.text_input("Ask anything about SIMs, 4G APN settings, taxes, or bundles:", placeholder="e.g. How do I configure 4G APN settings for Zong?")
                    if user_query and st.button("Ask Gemini"):
                        prompt = f"""
                        You are a helpful telecom expert in Pakistan.
                        The user is asking about network {carrier_name}:
                        "{user_query}"
                        Provide a concise, practical, and step-by-step answer.
                        """
                        with st.spinner("Consulting AI..."):
                            ans = query_gemini(gemini_client, prompt)
                            st.markdown(ans)
else:
    st.info("👆 Enter your phone number above and click 'Check Details' to begin.")