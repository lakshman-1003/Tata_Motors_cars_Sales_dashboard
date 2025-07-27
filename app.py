import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Set page layout to wide ---
st.set_page_config(layout="wide")

# --- Define File Paths ---
CSV_PATH = os.path.join("data", "tata_motors_sales_data.csv")

CAR_IMAGES = {
    "Tiago": os.path.join("images", "Tiago.jpeg"),
    "Tiago EV": os.path.join("images", "Tiago.jpeg"),
    "Harrier": os.path.join("images", "Harrier.jpeg"),
    "Safari": os.path.join("images", "Safari.jpeg"),
    "Nexon": os.path.join("images", "Nexon.jpeg"),
    "Punch": os.path.join("images", "Punch.jpeg"),
    "Curvv": os.path.join("images", "Curvv.jpeg")
}
TATA_LOGO = os.path.join("images", "Tata_Motors_logo.png")
DEFAULT_CAR_IMAGE = os.path.join("images", "All_tata_cars.jpeg")

# --- Load Data ---
df = pd.read_csv(CSV_PATH, parse_dates=['Date'])

# --- Sidebar Filters ---
st.sidebar.image(TATA_LOGO)  # removed use_container_width
st.sidebar.title("Filters")
city_options = ["All"] + sorted(df["City"].unique())
year_options = ["All"] + sorted(df["Date"].dt.year.astype(str).unique())
region_options = ["All"] + sorted(df["Region"].unique())
model_options = ["All"] + list(CAR_IMAGES.keys())
selected_city = st.sidebar.selectbox("City", city_options, key="city")
selected_year = st.sidebar.selectbox("Year", year_options, key="year")
selected_region = st.sidebar.selectbox("Region", region_options, key="region")
selected_model = st.sidebar.selectbox("Model", model_options, key="model")

# --- Data Filtering ---
filtered_df = df.copy()
if selected_city != "All":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["Date"].dt.year.astype(str) == selected_year]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_model != "All":
    filtered_df = filtered_df[filtered_df["Model"] == selected_model]

# --- Dashboard Header ---
st.markdown("<h1 style='font-size:2.6rem;margin-bottom:1.5rem;'>Tata Motors Sales Dashboard</h1>", unsafe_allow_html=True)

# --- KPI Metrics + Car Image ---
kpi_col1, kpi_col2, kpi_col3, kpi_col4, img_col = st.columns([1.2, 1.2, 1.2, 1.2, 2])
total_units = filtered_df["Units Sold"].sum()
total_revenue = filtered_df["Revenue"].sum()
active_models = filtered_df["Model"].nunique()
avg_price = total_revenue / total_units if total_units else 0

with kpi_col1:
    st.metric("Total Units Sold", f"{total_units:,}")
with kpi_col2:
    st.metric("Total Revenue", f"₹{total_revenue/1e7:.2f} Cr")
with kpi_col3:
    st.metric("Avg Price per Unit", f"₹{avg_price/1e5:.2f} L")
with kpi_col4:
    st.metric("Active Models", active_models)
with img_col:
    image_path = CAR_IMAGES.get(selected_model, DEFAULT_CAR_IMAGE)
    caption_text = selected_model if selected_model != "All" else "All Tata Models"
    st.image(image_path, caption=caption_text)  # removed use_column_width

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Row: Monthly Sales Trend, Top Models, Regional Share ---
trend_col, models_col, pie_col = st.columns([2, 2, 1.5])

with trend_col:
    st.subheader("Monthly Sales Trend")
    if not filtered_df.empty:
        df_trend = (
            filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))
            .agg({'Units Sold': 'sum'})
            .reset_index()
        )
        df_trend['Date'] = df_trend['Date'].astype(str)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_trend['Date'], df_trend['Units Sold'], marker='o', linewidth=2)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Units Sold', fontsize=12)
        ax.set_title('Monthly Sales Trend', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No data for selected filters.")

with models_col:
    st.subheader("Top 10 Models by Sales")
    top_models = df.groupby('Model')['Units Sold'].sum().sort_values(ascending=True).tail(10)
    fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
    ax_bar.barh(top_models.index, top_models.values, color='skyblue')
    ax_bar.set_xlabel("Units Sold")
    plt.tight_layout()
    st.pyplot(fig_bar)

with pie_col:
    st.subheader("Regional Share")
    region_perf = filtered_df.groupby('Region')['Units Sold'].sum()
    if not region_perf.empty:
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax2.pie(region_perf, labels=region_perf.index, autopct='%1.1f%%', startangle=140)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig2.gca().add_artist(centre_circle)
        ax2.axis('equal')
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.write("No data for pie chart.")

st.markdown("<br>", unsafe_allow_html=True)

