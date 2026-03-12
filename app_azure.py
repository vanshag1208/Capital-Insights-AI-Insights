import streamlit as st
import pymssql
import pandas as pd
from google import genai

# ---------------------------
# Secrets from Streamlit
# ---------------------------

DB_SERVER = st.secrets["DB_SERVER"]
DB_DATABASE = st.secrets["DB_DATABASE"]
DB_UID = st.secrets["DB_UID"]
DB_PWD = st.secrets["DB_PWD"]

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# ---------------------------
# Gemini Client
# ---------------------------

client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------
# SQL Server Connection
# ---------------------------

conn = pymssql.connect(
    server=DB_SERVER,
    user=DB_UID,
    password=DB_PWD,
    database=DB_DATABASE,
)

cursor = conn.cursor()

st.title("AI Stock Market Analyzer")

# ---------------------------
# Fetch Symbols
# ---------------------------

cursor.execute("SELECT DISTINCT Symbol FROM StockPriceDaily")
symbols = [row[0] for row in cursor.fetchall()]

# ---------------------------
# Selectbox
# ---------------------------

symbol = st.selectbox("Select Stock Symbol", symbols)

# ---------------------------
# Analyze Button
# ---------------------------

if st.button("Analyze Stock"):

    query = """
    SELECT TOP 10
        TradeDate,
        Symbol,
        OpenPrice,
        HighPrice,
        LowPrice,
        ClosePrice,
        Volume
    FROM StockPriceDaily
    WHERE Symbol = %s
    ORDER BY TradeDate DESC
    """

    cursor.execute(query, (symbol,))
    rows = cursor.fetchall()

    if not rows:
        st.error("Stock not found in database")

    else:
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        st.subheader("Stock Data")
        st.dataframe(df)

        stock_text = df.to_string(index=False)

        prompt = f"""
You are a financial analyst.

Analyze the following stock OHLCV data.

Provide:
1. Trend
2. Volatility
3. Short insight

Stock Data:
{stock_text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        st.subheader("AI Market Insight")
        st.write(response.text)