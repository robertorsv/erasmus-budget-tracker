# import budget_logic # Will be created later
# import data_manager # Will be created later
import streamlit as st
import pandas as pd
import budget_logic
import data_manager

# --- Page Configuration ---
st.set_page_config(
    page_title="Erasmus Budget",
    page_icon="💶",
    layout="centered", # Mobile-friendly
    initial_sidebar_state="collapsed"
)

# --- Theme Toggle & Settings ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Theme
    st.subheader("Appearance")
    mode = st.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "dark" else 1, horizontal=True)
    if mode == "Dark":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"
        
    st.divider()
    
    # Budget Configuration
    st.subheader("Budget Configuration")
    total_budget = st.number_input("Monthly Limit (€)", value=1000, step=50)
    
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# --- Dynamic CSS Injection (Polished) ---
if st.session_state.theme == "dark":
    bg_color = "#0E1117"
    card_bg = "#1E1E1E" # Softer dark
    text_color = "#FFFFFF"
    metric_color = "#E0E0E0"
else:
    bg_color = "#FFFFFF"
    card_bg = "#F8F9FA" # Clean light gray
    text_color = "#000000"
    metric_color = "#333333"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stMetric {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid {card_bg};
    }}
    [data-testid="stMetricLabel"] {{
        color: {metric_color} !important;
        font-size: 0.9rem;
    }}
    [data-testid="stMetricValue"] {{
        color: {text_color} !important;
        font-size: 1.8rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
st.title("💶 Erasmus Budget")

# Load Data
with st.spinner("Syncing..."):
    df = data_manager.get_transactions()
    rules = data_manager.get_budget_rules()
    
# Calculate Metrics
stats = budget_logic.calculate_burn_rate(df, limit=total_budget)

# Color Logic for Metric (Inverse: High Usage = Red)
delta_color = "normal" 
if stats['percent_used'] > 100:
    delta_color = "inverse" # Red
elif stats['percent_used'] == 0:
    delta_color = "off" # Grey
else:
    delta_color = "inverse" # Green to Red logic handled by streamlit inverse? No, inverse means positive is bad.
    # Actually, let's simplify. Standard Delta: Green is good.
    # We want "80% Used" to be potentially warning.
    
# Top Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    # Inverse: Positive delta (usage went up) is usually bad in budgeting? 
    # Let's just use normal colors but descriptive text.
    st.metric("Budget Left", f"€{stats['remaining']}", f"{stats['percent_used']}% Used", delta_color="inverse")
with col2:
    st.metric("Daily Limit", f"€{stats['daily_limit']}")
with col3:
    st.metric("Days Left", f"{stats['days_left']}")

# Traffic Light Progress Bar
progress_color = "green"
if stats['percent_used'] > 90:
    progress_color = "red"
elif stats['percent_used'] > 75:
    progress_color = "orange"

st.caption(f"Monthly Budget Usage ({stats['percent_used']}%)")
st.progress(min(stats['percent_used'] / 100, 1.0))
if stats['percent_used'] > 100:
    st.caption(":red[Over Budget!]")

# Warnings
if stats['status'] == "CRITICAL":
    st.error("🚨 CRITICAL: You have exceeded your budget!")
elif stats['status'] == "WARNING":
    st.warning("⚠️ Warning: Less than 10% of budget remaining.")


# --- Quick Add Transaction (Floating Action Button style simulation) ---
with st.expander("➕ Add Transaction", expanded=False):
    with st.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.01, step=1.0)
        currency = st.selectbox("Currency", ["EUR", "USD", "MXN", "CZK", "PLN", "GBP", "HUF"])
        category = st.selectbox("Category", ["Food", "Rent", "Travel", "Fun", "Other"])
        desc = st.text_input("Description")
        
        submitted = st.form_submit_button("Save Transaction", type="primary")
        if submitted:
            amount_eur = budget_logic.normalize_currency(amount, currency)
            if data_manager.add_transaction(date, amount, currency, category, desc, amount_eur):
                st.success(f"Added {amount} {currency} ({amount_eur} EUR)")
                st.cache_data.clear() # Clear cache to refresh data next time (if we used cache_data)
                st.rerun()
            else:
                st.error("Failed to save transaction.")

# --- Visualization (Mid Layer) ---
st.subheader("Spending Trends")

if not df.empty:
    # Daily Spending Trend
    daily_trend = df.groupby("Date")["Amount_EUR"].sum().reset_index()
    st.line_chart(daily_trend, x="Date", y="Amount_EUR")

st.subheader("Category Breakdown")
if not df.empty and not rules.empty:
    merged_status = budget_logic.check_category_limits(df, rules)
    
    if not merged_status.empty:
        # Simple Bar Chart for Categories
        # Using built-in bar_chart requires simple format or full altair/matplotlib
        # Let's use a dataframe with progress bars for limits? Or just a chart.
        
        # Prepare data for chart: Limit vs Spent
        chart_data = merged_status[["Category", "Amount_EUR", "Monthly_Limit"]].set_index("Category")
        st.bar_chart(chart_data, color=["#FF4B4B", "#00CC96"]) # Simple color diff
        
        # Detailed Limits Table
        st.caption("Category Limits vs Actual")
        st.dataframe(
            merged_status[["Category", "Amount_EUR", "Monthly_Limit", "Status", "Remaining"]],
            hide_index=True,
            use_container_width=True
        )

# --- Recent Transactions (Bottom Layer) ---
st.subheader("Recent Activity")
if not df.empty:
    # Sort by Date descending
    df_display = df.sort_values(by="Date", ascending=False).head(10)
    st.dataframe(
        df_display[["Date", "Amount", "Currency", "Category", "Description", "Amount_EUR"]], 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("No transactions yet.")


