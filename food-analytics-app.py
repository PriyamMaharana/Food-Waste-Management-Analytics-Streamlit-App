# app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# -------------------- PAGE CONFIG & THEME --------------------
st.set_page_config(
    page_title="Food Donation Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Subtle, modern CSS
st.markdown("""
<style>
/* === Main area: deep navy/indigo gradient, matching graph backgrounds === */
body, .main, .block-container, #root {
  background-color: #0E1117 !important;
  color: #e0e4ee;
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 1.05rem;
  min-height: 100vh;
}
.block-container {
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}
/* ==== SIDEBAR: Dark mirrored glass with deep blur, highly contrasted ==== */
section[data-testid="stSidebar"] {
    position: relative !important;
    background: linear-gradient(120deg, rgba(255,255,255,0.16) 0%, rgba(14,17,23,0.58) 25%, rgba(14,17,23,0.45) 85% );
    backdrop-filter: blur(14px) saturate(1.18);
    -webkit-backdrop-filter: blur(18px) saturate(1.18);
    box-shadow: 0 8px 32px 0 rgba(31,38,135,0.19), 0 1.5px 9px 0 rgba(32,34,51,0.27) inset;
    border-right: 2px solid rgba(255,255,255,0.12);
    min-height: 100vh !important;
    height: 100vh !important;
    padding-top: 3rem !important;
    width: 450px !important;
    transition: width 0.22s cubic-bezier(.32,1.13,.44,.99), left 0.19s cubic-bezier(.32,1.13,.44,.99);
    z-index: 1020 !important;
    overflow: hidden !important;
    font-size: 0.93rem !important;
}
/* Overlay mode (overlay/collapsible for width <1400px) */
@media (max-width: 1399px) {
    section[data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 85vw !important;
        min-width: 140px !important;
        max-width: 400px !important;
        height: 100vh !important;
        z-index: 3000 !important;
        box-shadow: 18px 0 44px 0 rgba(18,18,40,0.31)!important;
        overflow: hidden !important;
   }
  section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        left: 0 !important;
        z-index: 3000 !important;
        pointer-events: none !important;
  }
  .main, .block-container {
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: 100vw;
        margin: 0;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        transition: margin 0.22s cubic-bezier(.32,1.13,.44,.99);
  }
  button[data-testid="baseButton-sidebarCollapse"],
  button[data-testid="baseButton-sidebarClose"] {
        position: fixed !important;
        left: 15px !important;
        top: 22px !important;
        width: 45px !important;
        height: 45px !important;
        z-index: 1015  !important;
        background: #181b2b !important;
        color: #ecebf8 !important;
        border-radius: 14px 4px 14px 4px !important;
        opacity: 1 !important;
        display: block !important;
        box-shadow: 0 3px 28px rgba(24,20,40,0.25);
  }
}
@media (min-width: 1400px) {
    [data-testid="stAppViewContainer"],
    .block-container {
        max-width: 100vw !important;
        transition: margin 0.22s cubic-bezier(.32,1.13,.44,.99);
    }
    /* Keep padding on main content */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    [data-testid="stAppViewContainer"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* When sidebar collapsed, fill full width */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stAppViewContainer"],
    section[data-testid="stSidebar"][aria-expanded="false"] ~ .block-container,
    .block-container {
        margin: 0 auto !important;
        max-width: 100vw !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
}
/* Sidebar content enhancements */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
  color: #fafdff !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 900 !important;
  font-size: 1.95rem !important;
  letter-spacing: .07rem;
  padding: 1rem;
  padding-left: 0rem;
  text-shadow: 0 8px 32px #2a0d6099, 0 2px 12px #10162980;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown { color: #b6b4d7 !important; font-size: 1rem !important; margin-bottom: .08rem;}
section[data-testid="stSidebar"] label {
  color: #e4e6fa !important;
  font-size: 1.0rem !important;
  font-weight: 700 !important;
  margin-top: .89rem !important;
  letter-spacing: .04rem;
  padding-left: .75rem;
  display: block;
  text-shadow: 0 2px 10px #11123d71;
}
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] input[type="date"],
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stDateInput {
  background: rgba(15,17,28,0.99) !important;
  color: #ffffff !important;
  border: 1.5px solid #4965fb !important;
  border-radius: 15px !important;
  margin-bottom: .6rem !important;
  font-size: 0.95rem !important;
  box-shadow: 0 4px 24px rgba(31,60,120,0.19);
  padding: 7px 7px !important;
}
section[data-testid="stSidebar"] select:focus,
section[data-testid="stSidebar"] input[type="date"]:focus,
section[data-testid="stSidebar"] .stSelectbox:focus-within,
section[data-testid="stSidebar"] .stDateInput:focus-within {
  border: 2px solid #b38dfa !important;
  box-shadow: 0 0 12px 2px #9f61f5a0 !important;
  outline: none !important;
}
section[data-testid="stSidebar"] input::placeholder { color: #bbc7fd !important; }

/* === Cards, dataframes, KPI blocks === */
.kpi-card, .metric-card, .big-card {
  background: linear-gradient(121deg, #21233a 0%, #232756 100%);
  border-radius: 17px;
  padding: 19px 21px 15px 21px;
  margin-bottom: 21px;
  color: #fafdff !important;
  box-shadow: 0 7px 21px rgba(25,20,61,0.23);
  border: 2px solid #8cb6ff; 
}
.kpi-title { font-size: 1.05rem; color:#7c8cff; font-weight: 700; margin-bottom: 7px; letter-spacing:.055rem; }
.kpi-value { font-size: 2.22rem; font-weight: 900; letter-spacing:.045rem; margin-bottom: 8px; }
.kpi-sub { font-size: .97rem; color: #bdd3ea; }

div[data-testid="stDataFrame"] {
  background: linear-gradient(122deg, #202440 0%, #181929 120%);
  border-radius: 14px;
  box-shadow: 0 4px 12px #1c185a77;
  color: #e0eeff !important;
  font-size: 1.02rem !important;
  margin-bottom: 27px;
  overflow-x: auto;
  padding: 15px 8px !important;
}

/* === Tabs, Buttons, Headings as per your theme === */
.stTabs [role="tablist"] {
  font-weight: 600 !important;
  background: transparent !important;
  padding: 0 1rem !important;
  border: none !important;
}
.stTabs [role="tab"] {
  min-width: 120px !important;
  padding: 10px 15px !important;
  color: #b7bee3;
  border: none !important;
  border-bottom: 2px solid transparent;
  transition: color 0.22s, border 0.22s;
}
.stTabs [role="tab"][aria-selected="true"] {
  color: #ae7cf7 !important;
  border-bottom: 2.6px solid #bb7efd !important;
  font-weight: 800 !important;
}
.stTabs [role="tab"]:hover {
  color: #fff6fd;
  background: #322b4e38;
}
h1, h2, h3 {
    color: #e8ecff !important; 
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
.stButton > button {
  background: linear-gradient(125deg,#373ce8 25%, #946ef1 85%);
  color: #ecebfa;
  border-radius: 14px;
  padding: 0.54rem 1.26rem;
  font-weight: 800;
  border: none;
  font-size: 1.06em;
  box-shadow: 0 3px 14px #5f45e744;
  transition: background 0.19s, color 0.16s, box-shadow 0.09s;
}
.stButton > button:hover {
  background: #8057fc !important;
  color: #fff !important;
  box-shadow: 0 8px 26px #8350fda0;
}

/* --- Responsive tweaks --- */
@media (max-width: 900px) {
  .main { padding-top: 0.6rem; }
  .kpi-card, .metric-card, .big-card { padding: 13px !important; margin-bottom: 14px; }
}
@media (max-width: 600px) {
  section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
    font-size: 1.07rem !important;
    padding: 0 2px !important;
  }
  .kpi-card, .metric-card, .big-card { font-size: 0.92em !important; }
  div[data-testid="stDataFrame"] { font-size: 13px !important; }
  .stTabs [role="tablist"] {
    font-size: .98em !important;
    flex-wrap: wrap !important;
    padding-bottom: 6px !important;
  }
  .stTabs [role="tab"] { min-width: 95px !important; padding: 8px 7px !important; }
}

/* Copyright at bottom as visual footer - use ONLY CSS, not markdown! */
section[data-testid="stSidebar"]::after {
    content: "© Priyam Maharana";
    display: block;
    position: absolute;
    left: 0;
    right: 0;
    bottom: 18px;
    width: 95%;
    margin: 0 auto;
    text-align: center;
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: .88rem;
    color: #b8bde7;
    opacity: 0.73;
    font-weight: 500;
    pointer-events: none;
    z-index: 5000;
    padding-bottom: 2px;
    box-sizing: border-box;
    background: transparent;
}

@media (max-width: 600px) {
  section[data-testid="stSidebar"]::after {
      font-size: .75rem;
      padding-bottom: 5px;
  }
}

/* Make the tab labels larger, including emoji (default for desktop) */
@media (min-width: 1000px) {
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
    font-size: 1.45rem !important;
    gap: 18px !important;
    }
    [data-baseweb="tab"] {
        font-size: 1.40rem !important;
        font-weight: 600 !important;
        padding: 15px 20px !important;
        line-height: 1.05 !important;
        min-height: 55px;
        min-width: 85px;
    }
    [data-baseweb="tab"] > div {
    font-size: 1.68rem !important;
    font-weight: 600 !important;
    }
}

/* Responsive: Medium screens (tablet) */
@media (max-width: 999px) {
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    font-size: 1.09em !important;
    gap: 12px !important;
  }
  [data-baseweb="tab"] {
    font-size: 1.07em !important;
    padding: 9px 10px !important;
    min-width: 68px;
  }
  [data-baseweb="tab"] > div {
    font-size: 1.04em !important;
  }
}

/* Responsive: Small/mobile screens */
@media (max-width: 600px) {
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        font-size: 0.57rem !important;
        overflow-x: auto !important;    
        overflow-y: hidden !important;
        white-space: nowrap !important;  
        flex-wrap: nowrap !important;     
    }
    [data-baseweb="tab"][aria-selected="true"],
    .stTabs [role="tab"][aria-selected="true"] {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        padding: 5px 2px !important;
        min-width: 44px;
        flex: 0 0 auto !important;
    }
    [data-baseweb="tab"] > div {
        font-size: 1.18rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

# -------------------- DB CONNECTION --------------------
# engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/food_db')
engine = create_engine('postgresql://food_db_pl5v_user:AJUC866X0m9y76r1Pl9mneeghYCDiq95@dpg-d2fphi8dl3ps73eh4h6g-a.singapore-postgres.render.com/food_db_pl5v')

def run_query(query, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)

def execute_query(query, params=None):
    with engine.begin() as conn:
        conn.execute(text(query), params or {})

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.title("🍽️ Food Donation")
st.sidebar.caption("Filters apply to dashboards & insights")

# Load filter values (robust)
try:
    cities = run_query("SELECT DISTINCT city FROM provider_data WHERE city IS NOT NULL ORDER BY city")['city'].dropna().tolist()
    provider_types = run_query("SELECT DISTINCT provider_type FROM food_data WHERE provider_type IS NOT NULL ORDER BY provider_type")['provider_type'].dropna().tolist()
    food_types = run_query("SELECT DISTINCT food_type FROM food_data WHERE food_type IS NOT NULL ORDER BY food_type")['food_type'].dropna().tolist()
except Exception as err:
    st.sidebar.error(f"Filter load failed: {err}")
    cities, provider_types, food_types = [], [], []

filter_city = st.sidebar.selectbox("City", ["All"] + cities, index=0)
filter_ptype = st.sidebar.selectbox("Provider Type", ["All"] + provider_types, index=0)
filter_food = st.sidebar.selectbox("Food Type", ["All"] + food_types, index=0)

# Date range filter (for claims / wastage)
today = date.today()
default_from = date(today.year, 1, 1)
date_from, date_to = st.sidebar.date_input(
    "Date Range (claims/wastage)",
    value=(default_from, today)
) if "st.sidebar" else (default_from, today)
if isinstance(date_from, tuple): # older streamlit fallback
    date_from, date_to = date_from

# Helper to build WHERE snippets for food_data
food_where = ["1=1"]
food_params = {}
if filter_city != "All":
    food_where.append("f.location = :f_city")
    food_params["f_city"] = filter_city
if filter_ptype != "All":
    food_where.append("f.provider_type = :f_ptype")
    food_params["f_ptype"] = filter_ptype
if filter_food != "All":
    food_where.append("f.food_type = :f_food")
    food_params["f_food"] = filter_food
FOOD_WHERE_SQL = " AND ".join(food_where)

# Claims date filter (timestamp column)
claim_where = ["1=1", "c.timestamp::date BETWEEN :d_from AND :d_to"]
claim_params = {"d_from": date_from, "d_to": date_to}

# -------------------- HEADER --------------------
st.markdown("# Food Donation Analytics")
st.caption("Track donations, demand, and wastage to optimize distribution.")

# -------------------- KPI CARDS --------------------
kpi_cols = st.columns(4)
# Total providers
kpi_providers = run_query("SELECT COUNT(*) AS c FROM provider_data")["c"].iloc[0] if True else 0
# Total receivers
kpi_receivers = run_query("SELECT COUNT(*) AS c FROM receiver_data")["c"].iloc[0] if True else 0
# Total food quantity (available)
kpi_food_qty = run_query(f"SELECT COALESCE(SUM(quantity),0) AS qty FROM food_data f WHERE {FOOD_WHERE_SQL}", food_params)["qty"].iloc[0]
# Claims in date window
kpi_claims = run_query("SELECT COUNT(*) AS c FROM claim_data c WHERE " + " AND ".join(claim_where), claim_params)["c"].iloc[0]

with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Providers</div>
      <div class="kpi-value">{kpi_providers:,}</div>
      <div class="kpi-sub">Active donors</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Receivers</div>
      <div class="kpi-value">{kpi_receivers:,}</div>
      <div class="kpi-sub">Individuals & Orgs</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Availability</div>
      <div class="kpi-value">{kpi_food_qty:,}</div>
      <div class="kpi-sub">Filtered scope</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Claims</div>
      <div class="kpi-value">{kpi_claims:,}</div>
      <div class="kpi-sub">{date_from:%b-%Y} → {date_to:%b-%Y}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# -------------------- TABS --------------------
tab_dash, tab_listings, tab_contacts, tab_crud, tab_sql = st.tabs(
    ["📊 Dashboard", "📋 Listings", "📇 Contacts", "🛠️ CRUD", "🧠 SQL Insights"]
)

# -------------------- DASHBOARD --------------------
with tab_dash:
    colA, colB = st.columns([1.2, 1.0])

    # Top Providers by total quantity (filtered by sidebar)
    top_providers_sql = f"""
        SELECT p.name AS provider, SUM(f.quantity) AS total_quantity
        FROM food_data f
        JOIN provider_data p ON f.provider_id = p.provider_id
        WHERE {FOOD_WHERE_SQL}
        GROUP BY p.name
        ORDER BY total_quantity DESC
        LIMIT 10;
    """
    df_top_providers = run_query(top_providers_sql, food_params)

    # Highest Demand Locations (by completed claims in date window)
    top_locations_sql = f"""
        SELECT r.city, COUNT(*) AS total_claims
        FROM claim_data c
        JOIN receiver_data r ON c.receiver_id = r.receiver_id
        JOIN food_data f ON c.food_id = f.food_id
        WHERE c.status = 'Completed'
          AND {FOOD_WHERE_SQL.replace('f.', 'f.')}
          AND {claim_where[1]}
        GROUP BY r.city
        ORDER BY total_claims DESC
        LIMIT 10;
    """
    df_top_locations = run_query(top_locations_sql, {**food_params, **claim_params})

    with colA:
        st.subheader("Top Providers (by Quantity)")
        if not df_top_providers.empty:
            fig = px.bar(df_top_providers, x="provider", y="total_quantity", text_auto=True)
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for the selected filters.")

        st.subheader("Most Claimed Meal Types")
        meal_sql = f"""
            SELECT f.meal_type, COUNT(DISTINCT c.claim_id) AS total_claims
            FROM claim_data c
            JOIN food_data f ON c.food_id = f.food_id
            WHERE {claim_where[1]}
              AND {FOOD_WHERE_SQL}
            GROUP BY f.meal_type
            ORDER BY total_claims DESC;
        """
        df_meals = run_query(meal_sql, {**claim_params, **food_params})
        if not df_meals.empty:
            fig = px.pie(df_meals, names="meal_type", values="total_claims", hole=.45)
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No claims found in the date range.")

    with colB:
        st.subheader("Highest Demand Locations (Completed Claims)")
        if not df_top_locations.empty:
            fig = px.bar(df_top_locations, x="city", y="total_claims", text_auto=True)
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No location demand for selected filters/date range.")

        st.subheader("Wastage Trend (Expired & Unclaimed before Expiry)")
        wastage_sql = f"""
            WITH completed AS (
              SELECT food_id, MIN(timestamp) AS first_completed_at
              FROM claim_data
              WHERE status = 'Completed'
              GROUP BY food_id
            )
            SELECT DATE_TRUNC('month', f.expiry_date)::date AS month,
                   COUNT(*) AS items_wasted,
                   COALESCE(SUM(f.quantity),0) AS qty_wasted
            FROM food_data f
            LEFT JOIN completed c ON c.food_id = f.food_id
            WHERE f.expiry_date < CURRENT_DATE
              AND ({FOOD_WHERE_SQL})
              AND (c.first_completed_at IS NULL OR c.first_completed_at > f.expiry_date)
              AND f.expiry_date BETWEEN :w_from AND :w_to
            GROUP BY month
            ORDER BY month;
        """
        df_waste = run_query(wastage_sql, {**food_params, "w_from": date_from, "w_to": date_to})
        if not df_waste.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_waste["month"], y=df_waste["qty_wasted"], mode="lines+markers", name="Qty Wasted"))
            fig.update_layout(height=380, xaxis_title="Month", yaxis_title="Quantity", margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No wastage detected in the date range.")

# -------------------- LISTINGS --------------------
with tab_listings:
    st.subheader("Filtered Food Listings")
    list_sql = f"""
        SELECT f.*
        FROM food_data f
        WHERE {FOOD_WHERE_SQL}
        ORDER BY f.expiry_date NULLS LAST;
    """
    food_df = run_query(list_sql, food_params)
    st.dataframe(food_df, use_container_width=True)

# -------------------- CONTACTS --------------------
def generate_contact_html_table(df, city_col_exists=True):
    html = """
    <div style="overflow-y:auto; max-height:360px; border:1px solid #e5e7eb; border-radius:12px;">
    <table style="width:100%; border-collapse:collapse; font-family:Inter, Arial; font-size:14px;">
      <thead>
        <tr style="position:sticky; top:0; background:#111827; color:#fff;">
          <th style="padding:10px; text-align:left;">Name</th>
          <th style="padding:10px; text-align:left;">Contact</th>
          <th style="padding:10px; text-align:left;">Address</th>"""
    if city_col_exists:
        html += "<th style='padding:10px; text-align:left;'>City</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        contact_str = str(row.get('contact', ''))
        contact_link = f'<a href="tel:{contact_str}" style="color:#60a5fa; text-decoration:none;">{contact_str}</a>'
        html += f"<tr><td style='padding:10px;'>{row.get('name','')}</td><td style='padding:10px;'>{contact_link}</td><td style='padding:10px;'>{row.get('address','')}</td>"
        if city_col_exists:
            html += f"<td style='padding:10px;'>{row.get('city','')}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    return html

with tab_contacts:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Providers")
        prov_city = st.selectbox("City", ["All"] + cities, key="prov_city_ui")
        if prov_city == "All":
            prov_df = run_query("SELECT name, contact, address, city FROM provider_data")
        else:
            prov_df = run_query("SELECT name, contact, address, city FROM provider_data WHERE city = :pcity", {"pcity": prov_city})
        st.markdown(generate_contact_html_table(prov_df), unsafe_allow_html=True)

    with c2:
        st.markdown("### Receivers")
        receiver_cities = run_query("SELECT DISTINCT city FROM receiver_data ORDER BY city")['city'].tolist()
        rec_city = st.selectbox("City", ["All"] + receiver_cities, key="rec_city_ui")
        if rec_city == "All":
            rec_df = run_query("SELECT name, contact, city FROM receiver_data")
        else:
            rec_df = run_query("SELECT name, contact, city FROM receiver_data WHERE city = :rcity", {"rcity": rec_city})
        st.markdown(generate_contact_html_table(rec_df, city_col_exists=True), unsafe_allow_html=True)

# -------------------- CRUD (kept from your app, lightly polished) --------------------
with tab_crud:
    st.subheader("Manage Data")
    table = st.selectbox("Table", ["provider_data", "receiver_data", "food_data", "claim_data"], index=0)
    crud_action = st.radio("Action", ["Insert", "Read", "Update", "Delete"], horizontal=True)

    def input_text(label, value=''):
        return st.text_input(label, value)

    def input_select(label, options, index=0):
        return st.selectbox(label, options, index=index)

    def input_number(label, value=0, min_value=None, max_value=None):
        return st.number_input(label, value=value, min_value=min_value, max_value=max_value)

    def input_date(label, value=None):
        return st.date_input(label, value)

    def input_datetime(label, value=None):
        return st.date_input(label, value if value else datetime.now())

    if table == "provider_data":
        if crud_action == "Insert":
            st.markdown("#### Add Provider")
            with st.form("provider_insert_form"):
                name = input_text("Name")
                ptype = input_select("Type", ['Restaurant', 'Supermarket', 'Grocery Store', 'Catering Service'])
                contact = input_text("Contact")
                address = input_text("Address")
                city = input_text("City")
                if st.form_submit_button("Add"):
                    if not name.strip():
                        st.error("Name is required")
                    else:
                        execute_query("""
                            INSERT INTO provider_data (name, type, contact, address, city)
                            VALUES (:name, :type, :contact, :address, :city)
                        """, {"name": name, "type": ptype, "contact": contact, "address": address, "city": city})
                        st.success("Provider added")

        elif crud_action == "Read":
            st.markdown("#### Providers")
            df = run_query("SELECT * FROM provider_data")
            st.dataframe(df, use_container_width=True)

        elif crud_action == "Update":
            st.markdown("#### Update Provider")
            df = run_query("SELECT * FROM provider_data")
            if df.empty:
                st.info("No providers to update.")
            else:
                provider_ids = df['provider_id'].tolist()
                selected_id = st.selectbox("Select", provider_ids)
                provider = df[df['provider_id'] == selected_id].iloc[0]
                with st.form("provider_update_form"):
                    name = input_text("Name", provider["name"])
                    options = ['Restaurant', 'Supermarket', 'Grocery Store', 'Catering Service']
                    idx = options.index(provider["type"]) if provider["type"] in options else 0
                    ptype = input_select("Type", options, idx)
                    contact = input_text("Contact", provider["contact"])
                    address = input_text("Address", provider["address"])
                    city = input_text("City", provider["city"])
                    if st.form_submit_button("Update"):
                        execute_query("""
                            UPDATE provider_data
                            SET name = :name, type = :type, contact = :contact, address = :address, city = :city
                            WHERE provider_id = :provider_id
                        """, {"name": name, "type": ptype, "contact": contact, "address": address, "city": city, "provider_id": selected_id})
                        st.success("Provider updated")

        elif crud_action == "Delete":
            st.markdown("#### Delete Provider")
            df = run_query("SELECT * FROM provider_data")
            if df.empty:
                st.info("No providers to delete.")
            else:
                selected_id = st.selectbox("Select", df['provider_id'].tolist())
                if st.button("Delete"):
                    execute_query("DELETE FROM provider_data WHERE provider_id = :provider_id", {"provider_id": selected_id})
                    st.success("Provider deleted")

    elif table == "receiver_data":
        if crud_action == "Insert":
            st.markdown("#### Add Receiver")
            with st.form("receiver_insert_form"):
                name = input_text("Name")
                rtype = input_select("Type", ['Individual', 'NGO', 'Charity', 'Shelter'])
                contact = input_text("Contact")
                city = input_text("City")
                if st.form_submit_button("Add"):
                    if not name.strip():
                        st.error("Name is required")
                    else:
                        execute_query("""
                            INSERT INTO receiver_data (name, type, contact, city)
                            VALUES (:name, :type, :contact, :city)
                        """, {"name": name, "type": rtype, "contact": contact, "city": city})
                        st.success("Receiver added")

        elif crud_action == "Read":
            st.markdown("#### Receivers")
            st.dataframe(run_query("SELECT * FROM receiver_data"), use_container_width=True)

        elif crud_action == "Update":
            st.markdown("#### Update Receiver")
            df = run_query("SELECT * FROM receiver_data")
            if df.empty:
                st.info("No receivers to update.")
            else:
                selected_id = st.selectbox("Select", df['receiver_id'].tolist())
                receiver = df[df['receiver_id'] == selected_id].iloc[0]
                with st.form("receiver_update_form"):
                    name = input_text("Name", receiver["name"])
                    options = ['Individual', 'NGO', 'Charity', 'Shelter']
                    idx = options.index(receiver["type"]) if receiver["type"] in options else 0
                    rtype = input_select("Type", options, idx)
                    contact = input_text("Contact", receiver["contact"])
                    city = input_text("City", receiver["city"])
                    if st.form_submit_button("Update"):
                        execute_query("""
                            UPDATE receiver_data
                            SET name = :name, type = :type, contact = :contact, city = :city
                            WHERE receiver_id = :receiver_id
                        """, {"name": name, "type": rtype, "contact": contact, "city": city, "receiver_id": selected_id})
                        st.success("Receiver updated")

        elif crud_action == "Delete":
            st.markdown("#### Delete Receiver")
            df = run_query("SELECT * FROM receiver_data")
            if df.empty:
                st.info("No receivers to delete.")
            else:
                selected_id = st.selectbox("Select", df['receiver_id'].tolist())
                if st.button("Delete"):
                    execute_query("DELETE FROM receiver_data WHERE receiver_id = :receiver_id", {"receiver_id": selected_id})
                    st.success("Receiver deleted")

    elif table == "food_data":
        if crud_action == "Insert":
            st.markdown("#### Add Food Listing")
            with st.form("food_insert_form"):
                food_name = input_text("Food Name")
                expiry_date = input_date("Expiry Date")
                quantity = input_number("Quantity", min_value=1, value=1)
                provider_id = input_number("Provider ID", min_value=1, value=1)
                provider_type = input_select("Provider Type", provider_types if provider_types else ["Restaurant"])
                location = input_text("Location (City)")
                food_type_ = input_select("Food Type", food_types if food_types else ["Vegetarian", "Non Vegetarian", "Vegan"])
                meal_type = input_select("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                if st.form_submit_button("Add"):
                    if not food_name.strip():
                        st.error("Food name is required")
                    else:
                        execute_query("""
                            INSERT INTO food_data (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                            VALUES (:food_name, :quantity, :expiry_date, :provider_id, :provider_type, :location, :food_type, :meal_type)
                        """, {
                            "food_name": food_name, "quantity": quantity, "expiry_date": expiry_date,
                            "provider_id": provider_id, "provider_type": provider_type,
                            "location": location, "food_type": food_type_, "meal_type": meal_type
                        })
                        st.success("Food listing added")

        elif crud_action == "Read":
            st.markdown("#### Food Listings")
            st.dataframe(run_query("SELECT * FROM food_data"), use_container_width=True)

        elif crud_action == "Update":
            st.markdown("#### Update Food Listing")
            df = run_query("SELECT * FROM food_data")
            if df.empty:
                st.info("No food listings to update.")
            else:
                selected_id = st.selectbox("Select", df['food_id'].tolist())
                food = df[df['food_id'] == selected_id].iloc[0]
                with st.form("food_update_form"):
                    food_name = input_text("Food Name", food["food_name"])
                    expiry_date = input_date("Expiry Date", food["expiry_date"])
                    quantity = input_number("Quantity", min_value=1, value=int(food["quantity"]))
                    provider_id = input_number("Provider ID", min_value=1, value=int(food["provider_id"]))
                    options_pt = provider_types if provider_types else [food.get("provider_type","")]
                    idx_pt = options_pt.index(food["provider_type"]) if food["provider_type"] in options_pt else 0
                    provider_type = input_select("Provider Type", options_pt, idx_pt)
                    location = input_text("Location (City)", food["location"])
                    options_ft = food_types if food_types else [food.get("food_type","")]
                    idx_ft = options_ft.index(food["food_type"]) if food["food_type"] in options_ft else 0
                    food_type_ = input_select("Food Type", options_ft, idx_ft)
                    options_mt = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                    idx_mt = options_mt.index(food["meal_type"]) if food["meal_type"] in options_mt else 0
                    meal_type = input_select("Meal Type", options_mt, idx_mt)
                    if st.form_submit_button("Update"):
                        execute_query("""
                            UPDATE food_data
                            SET food_name = :food_name, quantity = :quantity, expiry_date = :expiry_date,
                                provider_id = :provider_id, provider_type = :provider_type, location = :location,
                                food_type = :food_type, meal_type = :meal_type
                            WHERE food_id = :food_id
                        """, {
                            "food_name": food_name, "quantity": quantity, "expiry_date": expiry_date,
                            "provider_id": provider_id, "provider_type": provider_type,
                            "location": location, "food_type": food_type_, "meal_type": meal_type,
                            "food_id": int(selected_id)
                        })
                        st.success("Food listing updated")

        elif crud_action == "Delete":
            st.markdown("#### Delete Food Listing")
            df = run_query("SELECT * FROM food_data")
            if df.empty:
                st.info("No food listings to delete.")
            else:
                selected_id = st.selectbox("Select", df['food_id'].tolist())
                if st.button("Delete"):
                    execute_query("DELETE FROM food_data WHERE food_id = :food_id", {"food_id": selected_id})
                    st.success("Food listing deleted")

    elif table == "claim_data":
        if crud_action == "Insert":
            st.markdown("#### Add Claim")
            with st.form("claim_insert_form"):
                food_id = input_number("Food ID", min_value=1, value=1)
                receiver_id = input_number("Receiver ID", min_value=1, value=1)
                timestamp = input_datetime("Timestamp", datetime.now())
                status = input_select("Status", ["Pending", "Completed", "Cancelled"])
                if st.form_submit_button("Add"):
                    execute_query("""
                        INSERT INTO claim_data (food_id, receiver_id, status, timestamp)
                        VALUES (:food_id, :receiver_id, :status, :timestamp)
                    """, {"food_id": food_id, "receiver_id": receiver_id, "status": status, "timestamp": timestamp})
                    st.success("Claim added")

        elif crud_action == "Read":
            st.markdown("#### Claims")
            st.dataframe(run_query("SELECT * FROM claim_data"), use_container_width=True)

        elif crud_action == "Update":
            st.markdown("#### Update Claim")
            df = run_query("SELECT * FROM claim_data")
            if df.empty:
                st.info("No claims to update.")
            else:
                selected_id = st.selectbox("Select", df['claim_id'].tolist())
                claim = df[df['claim_id'] == selected_id].iloc[0]
                with st.form("claim_update_form"):
                    food_id = input_number("Food ID", min_value=1, value=int(claim["food_id"]))
                    receiver_id = input_number("Receiver ID", min_value=1, value=int(claim["receiver_id"]))
                    timestamp = input_datetime("Timestamp", claim["timestamp"])
                    options = ["Pending", "Completed", "Cancelled"]
                    idx = options.index(claim["status"]) if claim["status"] in options else 0
                    status = input_select("Status", options, idx)
                    if st.form_submit_button("Update"):
                        execute_query("""
                            UPDATE claim_data
                            SET food_id = :food_id, receiver_id = :receiver_id, status = :status, timestamp = :timestamp
                            WHERE claim_id = :claim_id
                        """, {"food_id": food_id, "receiver_id": receiver_id, "status": status, "timestamp": timestamp, "claim_id": int(selected_id)})
                        st.success("Claim updated")

        elif crud_action == "Delete":
            st.markdown("#### Delete Claim")
            df = run_query("SELECT * FROM claim_data")
            if df.empty:
                st.info("No claims to delete.")
            else:
                selected_id = st.selectbox("Select", df['claim_id'].tolist())
                if st.button("Delete"):
                    execute_query("DELETE FROM claim_data WHERE claim_id = :claim_id", {"claim_id": selected_id})
                    st.success("Claim deleted")

# -------------------- SQL INSIGHTS --------------------
with tab_sql:
    st.subheader("One-click SQL Insights")
    insights = {
        "Providers & Receivers per City": """
            SELECT p.city,
                   COUNT(DISTINCT p.provider_id) AS provider_count,
                   COUNT(DISTINCT r.receiver_id) AS receiver_count
            FROM provider_data p
            LEFT JOIN receiver_data r ON p.city = r.city
            GROUP BY p.city
            ORDER BY p.city;
        """,
        "Provider Type Contributing Most Food": f"""
            SELECT f.provider_type, SUM(f.quantity) AS total_quantity
            FROM food_data f
            WHERE {FOOD_WHERE_SQL}
            GROUP BY f.provider_type
            ORDER BY total_quantity DESC;
        """,
        "Receivers Who Claimed the Most Food": f"""
            SELECT r.name, r.city, SUM(f.quantity) AS total_claimed
            FROM claim_data c
            JOIN receiver_data r ON c.receiver_id = r.receiver_id
            JOIN food_data f ON c.food_id = f.food_id
            WHERE {claim_where[1]} AND {FOOD_WHERE_SQL}
            GROUP BY r.name, r.city
            ORDER BY total_claimed DESC;
        """,
        "Total Quantity of Food Available": f"""
            SELECT COALESCE(SUM(quantity),0) AS total_food_available
            FROM food_data f
            WHERE {FOOD_WHERE_SQL};
        """,
        "City with Highest Number of Food Listings": f"""
            SELECT f.location, COUNT(*) AS listing_count
            FROM food_data f
            WHERE {FOOD_WHERE_SQL}
            GROUP BY f.location
            ORDER BY listing_count DESC;
        """,
        "Most Commonly Available Food Types": f"""
            SELECT f.food_type, COUNT(*) AS count_available
            FROM food_data f
            WHERE {FOOD_WHERE_SQL}
            GROUP BY f.food_type
            ORDER BY count_available DESC;
        """,
        "Number of Food Claims per Food Item": f"""
            SELECT f.food_name, COUNT(DISTINCT c.claim_id) AS total_claims
            FROM claim_data c
            JOIN food_data f ON c.food_id = f.food_id
            WHERE {claim_where[1]} AND {FOOD_WHERE_SQL}
            GROUP BY f.food_name, f.food_id
            ORDER BY total_claims DESC;
        """,
        "Provider with Highest Number of Successful Food Claims": f"""
            SELECT p.name AS donor, COUNT(c.claim_id) AS successful_donated
            FROM claim_data c
            JOIN food_data f ON c.food_id = f.food_id
            JOIN provider_data p ON f.provider_id = p.provider_id
            WHERE c.status = 'Completed' AND {claim_where[1].replace('c.', 'c.')}
              AND {FOOD_WHERE_SQL}
            GROUP BY p.provider_id, p.name
            ORDER BY successful_donated DESC;
        """,
        "Percentage of Food Claims by Status": f"""
            SELECT c.status,
                   ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM claim_data c2 WHERE {claim_where[1]}),0), 2) AS percentage
            FROM claim_data c
            WHERE {claim_where[1]}
            GROUP BY c.status;
        """,
        "Average Quantity Claimed per Receiver": f"""
            SELECT r.name AS receiver_name, ROUND(AVG(f.quantity), 2) AS avg_qty_claimed
            FROM claim_data c
            JOIN receiver_data r ON c.receiver_id = r.receiver_id
            JOIN food_data f ON c.food_id = f.food_id
            WHERE {claim_where[1]} AND {FOOD_WHERE_SQL}
            GROUP BY r.receiver_id, r.name
            ORDER BY avg_qty_claimed DESC;
        """,
        "Most Claimed Meal Type": f"""
            SELECT f.meal_type, COUNT(DISTINCT c.claim_id) AS total_claims
            FROM claim_data c
            JOIN food_data f ON c.food_id = f.food_id
            WHERE {claim_where[1]} AND {FOOD_WHERE_SQL}
            GROUP BY f.meal_type
            ORDER BY total_claims DESC;
        """,
        "Total Quantity Donated by Each Provider": f"""
            SELECT p.name AS provider_name, SUM(f.quantity) AS total_qty_donated
            FROM food_data f
            JOIN provider_data p ON f.provider_id = p.provider_id
            WHERE {FOOD_WHERE_SQL}
            GROUP BY p.provider_id, p.name
            ORDER BY total_qty_donated DESC;
        """,
        "Highest Demand Locations Based on Claims": f"""
            SELECT r.city, COUNT(c.claim_id) AS total_claims
            FROM claim_data c
            JOIN receiver_data r ON c.receiver_id = r.receiver_id
            JOIN food_data f ON c.food_id = f.food_id
            WHERE c.status = 'Completed' AND {claim_where[1]} AND {FOOD_WHERE_SQL}
            GROUP BY r.city
            ORDER BY total_claims DESC;
        """,
        "Food Wastage by Location (Expired & Unclaimed)": f"""
            WITH completed AS (
              SELECT food_id, MIN(timestamp) AS first_completed_at
              FROM claim_data
              WHERE status = 'Completed'
              GROUP BY food_id
            )
            SELECT f.location, COUNT(DISTINCT f.food_id) AS wasted_items, COALESCE(SUM(f.quantity),0) AS qty_wasted
            FROM food_data f
            LEFT JOIN completed c ON c.food_id = f.food_id
            WHERE f.expiry_date < CURRENT_DATE
              AND ({FOOD_WHERE_SQL})
              AND (c.first_completed_at IS NULL OR c.first_completed_at > f.expiry_date)
              AND f.expiry_date BETWEEN :w_from AND :w_to
            GROUP BY f.location
            ORDER BY wasted_items DESC;
        """,
    }

    # Run selected insight
    selected = st.selectbox("Pick an insight", list(insights.keys()), index=0)
    params = {**food_params, **claim_params, "w_from": date_from, "w_to": date_to}
    if st.button("Run Insight"):
        try:
            df = run_query(insights[selected], params)
            st.dataframe(df, use_container_width=True)
            # Optional chart for common shapes
            if "total_quantity" in df.columns or "total_qty_donated" in df.columns:
                ycol = "total_quantity" if "total_quantity" in df.columns else "total_qty_donated"
                xcol = [c for c in df.columns if c != ycol][0]
                st.plotly_chart(px.bar(df, x=xcol, y=ycol, text_auto=True), use_container_width=True)
            elif "percentage" in df.columns and "status" in df.columns:
                st.plotly_chart(px.pie(df, names="status", values="percentage", hole=.45), use_container_width=True)
        except Exception as e:
            st.error(f"Error running query: {e}")


