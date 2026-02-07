import re
import pandas as pd
import streamlit as st

import db
from datetime import date, timedelta
from db import get_conn, init_db, insert_order, fetch_latest

st.set_page_config(page_title="E-commerce Orders Form", page_icon="🧾", layout="centered")

# Initialize DB

# Cloud concept: Idempotency - safe to run multiple times
try:
    db.init_db()
except Exception as e:
    st.error("Database initialization failed.")
    st.exception(e)
    st.stop()

init_db()

st.title("🧾 E-commerce Orders Form")
st.caption("Submit the form. Data is saved to Postgres and shown below.")

customer_id_re = re.compile(r"^C\d{4}$")

# Default ship date = 2 days from today
default_ship_date = date.today() + timedelta(days=2)

# --- Form ---
with st.form("order_form", clear_on_submit=True):
    customer_id = st.text_input("Customer ID", placeholder="e.g., C1234")
    ship_date = st.date_input("Ship Date", value=default_ship_date, min_value=date.today())
    status = st.selectbox("Status", ["shipped", "paid", "refunded", "delivered", "cancelled", "pending", "unknown"])
    channel = st.selectbox("Channel", ["social", "partner", "web", "app", "mobile_app", "walkin"])
    total_amount_usd = st.number_input(
        "Total Amount (USD)",
        min_value=-5000.0,
        max_value=5000.0,
        value=0.0
    )
    discount_pct = st.number_input(
        "Discount",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
        help="Enter 0.10 for 10% discount"
    )
    payment_method = st.selectbox("Payment Method", ["bank_transfer", "credit_card", "e-wallet", "cash"])
    region = st.selectbox("Region", ["kandal", "takeo", "phnom_penh", "siem_reap", "preah_sihanouk", "battambang", "kampong_cham"])
    note = st.text_area("Notes", placeholder="Please input order description here")
    submitted = st.form_submit_button("Save to Database")

# --- Form submission ---
if submitted:
    customer_clean = customer_id.strip()
    order_date = date.today()

    valid = True

    # --- Validations ---
    if not customer_clean:
        st.error("Customer ID is required.")
        valid = False
    elif not customer_id_re.match(customer_clean):
        st.error("Please enter a valid customer ID. Should be something like C1234.")
        valid = False
    elif ship_date < order_date:
        st.error("Ship date cannot be before today (order date).")
        valid = False
    elif status != "refunded" and total_amount_usd < 0:
        st.error("Total amount cannot be negative unless the status is 'refunded'.")
        valid = False
    elif total_amount_usd == 0:
        st.error("Total amount cannot be zero.")
        valid = False
    elif not (0.0 <= discount_pct <= 1.0):
        st.error("Discount must be between 0 and 1 (e.g., 0.10 for 10%).")
        valid = False
    
    # --- Insert if valid ---
    if valid:
        new_id = insert_order(
            customer_id=customer_clean,
            ship_date=ship_date,
            status=status.lower().strip(),
            channel=channel.lower().strip(),
            total_amount_usd=total_amount_usd,
            discount_pct=discount_pct,
            payment_method=payment_method.lower().strip(),
            region=region.lower().strip(),
            note=note.strip() if note else None
        )

        st.success(f"✅ Saved to Postgres (id={new_id})")

# --- Display latest orders ---
st.divider()
st.subheader("📄 Latest Orders")

try:
    rows = fetch_latest(50)
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records yet. Submit the form above.")
except Exception as e:
    st.error("Could not fetch rows from the database.")
    st.code(str(e))
