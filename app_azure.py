import streamlit as st
import pymssql
import pandas as pd
from google import genai

# ---------------------------
# Load environment variables
# ---------------------------

 
DB_DRIVER = st.secrets["DB_DRIVER"]
DB_SERVER = st.secrets["DB_SERVER"]
DB_DATABASE = st.secrets["DB_DATABASE"]
DB_UID = st.secrets["DB_UID"]
DB_PWD = st.secrets["DB_PWD"]

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


# ---------------------------
# 1. Gemini Client
# ---------------------------

client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------
# 2. SQL Server Connection
# ---------------------------

conn = pymssql.connect(
    server=DB_SERVER,
    user=DB_UID,
    password=DB_PWD,
    database=DB_DATABASE
)

cursor = conn.cursor()

st.title("AI Stock Market Analyzer")

# ---------------------------
# 3. Fetch Symbols
# ---------------------------
cursor.execute("SELECT DISTINCT Symbol FROM StockPriceDaily")
symbols = [row[0] for row in cursor.fetchall()]

# ---------------------------
# 4. Selectbox for User Input
# ---------------------------
symbol = st.selectbox("Select Stock Symbol", symbols)

# ---------------------------
# 5. Analyze Button
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
    WHERE Symbol = ?
    ORDER BY TradeDate DESC
    """

    cursor.execute(query, symbol)
    rows = cursor.fetchall()

    if not rows:
        st.error("Stock not found in database")

    else:
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)

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