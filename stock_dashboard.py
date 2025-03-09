import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database Connection (Modify with your DB credentials)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "MySQL1234"
DB_NAME = "stock_db"

# Create database connection
@st.cache_resource
def get_db_connection():
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    return engine

engine = get_db_connection()

# Fetch stock data from SQL
@st.cache_data
def load_data():
    query = "SELECT * FROM stocks"
    df = pd.read_sql(query, engine)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters 🎯")
selected_company = st.sidebar.selectbox("Select a Company", df["company"].unique())
selected_sector = st.sidebar.multiselect("Select Sector(s)", df["sector"].unique(), default=df["sector"].unique())

# Filter Data
filtered_data = df[(df["company"] == selected_company) & (df["sector"].isin(selected_sector))]

# Title
st.title(f"📈 {selected_company} Stock Analysis Dashboard")

# Display Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Close Price", f"${filtered_data['close_price'].iloc[-1]:,.2f}")
col2.metric("Market Cap", f"${filtered_data['market_cap'].iloc[-1]:,.2f} B")
col3.metric("P/E Ratio", f"{filtered_data['pe_ratio'].iloc[-1]:.2f}")
col4.metric("Trading Volume", f"{filtered_data['volume'].iloc[-1]:,}")

# Stock Price Trend
st.subheader("📊 Stock Price Trend")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(filtered_data["date"], filtered_data["open_price"], label="Open Price", marker="o")
ax.plot(filtered_data["date"], filtered_data["close_price"], label="Close Price", marker="o")
ax.fill_between(filtered_data["date"], filtered_data["low_price"], filtered_data["high_price"], color="gray", alpha=0.2)
ax.set_xlabel("Date")
ax.set_ylabel("Stock Price ($)")
ax.legend()
st.pyplot(fig)

# Volume vs. Close Price Scatter Plot
st.subheader("📉 Volume vs. Price Correlation")
fig, ax = plt.subplots(figsize=(8, 4))
sns.scatterplot(data=filtered_data, x="volume", y="close_price", hue="company", size="close_price", sizes=(20, 200), alpha=0.7)
ax.set_xlabel("Trading Volume")
ax.set_ylabel("Close Price ($)")
st.pyplot(fig)

# Market Cap by Sector
st.subheader("🏢 Sector-wise Market Cap Comparison")
sector_data = df.groupby("sector")["market_cap"].sum().reset_index()
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=sector_data, x="sector", y="market_cap", palette="coolwarm")
ax.set_xlabel("Sector")
ax.set_ylabel("Total Market Cap ($B)")
plt.xticks(rotation=45)
st.pyplot(fig)

# Display Filtered Data Table
st.subheader("📋 Stock Data Table")
st.dataframe(filtered_data)


