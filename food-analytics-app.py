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
/* === App wide spacing and sidebar background === */
.main { padding-top: 1rem; }
section[data-testid="stSidebar"] { background: #0b1324; }
.st-emotion-cache-1wbqy5l { padding-top: 0 !important; }

/* === KPI Cards styling === */
.kpi-card {
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  color: #fff;
  box-shadow: 0 8px 18px rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 16px;
}
.kpi-title {
  font-size: 13px;
  color: #93c5fd;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 4px;
}
.kpi-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
}
.kpi-sub {
  font-size: 12px;
  color: #d1d5db;
}

/* === Dataframes styling === */
div[data-testid="stDataFrame"] {
  border-radius: 12px;
  overflow-x: auto;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

/* === Headings custom color === */
h1, h2, h3 {
  color: #FFFFFF !important;
}

/* === Buttons styling === */
.stButton > button {
  border-radius: 10px;
  padding: 0.6rem 1rem;
  font-weight: 600;
}

/* === Responsive layout adjustments === */

/* Stack columns vertically and add gap on smaller than 900px */
@media (max-width: 900px) {
  .st-emotion-cache-1wbqy5l section[data-testid="column"],
  .st-emotion-cache-1wbqy5l section[data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 18px !important;
  }
  .kpi-card {
    margin-bottom: 20px !important;
  }
}

/* Mobile specific adjustments for devices <=600px */
@media (max-width: 600px) {
  .kpi-card {
    padding: 12px !important;
    font-size: 15px !important;
  }
  h1, h2, h3 {
    font-size: 1.6em !important;
    padding-top: 6px !important;
    padding-bottom: 4px !important;
  }
  div[data-testid="stDataFrame"] {
    font-size: 13px !important;
    max-width: 98vw;
  }
  .stTabs [role="tablist"] {
    flex-wrap: wrap !important;
  }
}

/* Make tabs more readable with minimum width */
.stTabs [role="tab"] {
  min-width: 120px !important;
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
      <div class="kpi-title">Available Quantity</div>
      <div class="kpi-value">{kpi_food_qty:,}</div>
      <div class="kpi-sub">Filtered scope</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Claims</div>
      <div class="kpi-value">{kpi_claims:,}</div>
      <div class="kpi-sub">{date_from:%d-%b-%Y} → {date_to:%d-%b-%Y}</div>
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

