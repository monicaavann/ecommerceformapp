import os
import psycopg2
import psycopg2.extras

def get_db_url():
    # Cloud concept: Configuration outside code (Secrets)
    # 1) Local/server environment variable
    url = os.environ.get("NEON_DATABASE_URL")
    if url:
        return url

    # 2) Streamlit Cloud Secrets
    try:
        import streamlit as st
        url = st.secrets.get("NEON_DATABASE_URL")
        if url:
            return url
    except Exception:
        pass

    return None

DB_URL = get_db_url()
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ecommerceorders (
  id SERIAL PRIMARY KEY,
  customer_id TEXT NOT NULL,
  order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ship_date TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  channel TEXT NOT NULL,
  total_amount_usd NUMERIC(10, 2) NOT NULL,
  discount_pct NUMERIC(4, 2) DEFAULT 0,
  payment_method TEXT NOT NULL,
  region TEXT NOT NULL,
  note TEXT
);
"""

INSERT_SQL = """
INSERT INTO ecommerceorders (customer_id, ship_date, status, channel, total_amount_usd, discount_pct, payment_method, region, note)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id;
"""

SELECT_LATEST_SQL = """
SELECT id, customer_id, order_date, ship_date, status, channel, total_amount_usd, discount_pct, payment_method, region, note
FROM ecommerceorders
ORDER BY id DESC
LIMIT %s;
"""

def get_conn():
    if not DB_URL:
        raise ValueError("NEON_DATABASE_URL is not set. Add it in Colab Secrets or os.environ.")
    return psycopg2.connect(DB_URL)

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()

def insert_order(customer_id: str, ship_date: date, status: str, channel: str, total_amount_usd: float, discount_pct: float, payment_method: str, region: str, note: str = None) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(INSERT_SQL, (customer_id, ship_date, status, channel, total_amount_usd, discount_pct, payment_method, region, note))
            new_id = cur.fetchone()[0]
            return int(new_id)

def fetch_latest(limit: int = 50):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SELECT_LATEST_SQL, (limit,))
            return cur.fetchall()
