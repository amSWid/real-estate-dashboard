import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# ====================================
# PAGE CONFIG
# ====================================
st.set_page_config(
    page_title="Real Estate Dashboard",
    layout="wide"
)

# ====================================
# CUSTOM SIDEBAR WIDTH
# ====================================
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 380px !important;
}

section[data-testid="stSidebar"] > div {
    width: 380px !important;
}
</style>
""", unsafe_allow_html=True)



# ====================================
# LOAD DATA
# ====================================
@st.cache_data
def load_data():
    return pd.read_csv("real_estate_clean.csv")

df = load_data()

# ====================================
# HEADER
# ====================================
st.markdown(
    """
    <p style='font-size:20px;
              font-weight:500;
              color:gray;
              margin-bottom:-10px;'>
    Created by: <b>S.Widjaja</b>
    </p>
    """,
    unsafe_allow_html=True
)

st.title("🏠 Real Estate Dashboard")

st.markdown("""
### 📊 Market Analysis : 
**Before COVID (2006–2019)** vs  
**After COVID / Recovery (2020–2023)**

Market demand vs economic value of each residential type
            
""")

# ====================================
# PROJECT OVERVIEW
# ====================================
st.markdown("---")
st.header("🎯 Project Overview")

st.markdown("""
### Dashboard ini dapat digunakan untuk:

- 📈 **Investor** → mencari area premium & undervalued property  
- 🏛️ **Pemerintah** → melihat tren market property  
- 🏗️ **Developer** → memahami tipe rumah paling diminati  
- 🏦 **Bank** → melihat mismatch appraisal vs sale price  
- 🏘️ **Agen Properti** → mengetahui kota paling aktif  
- 🏡 **Calon Pemilik Rumah** → mencari area affordable
""")

# ====================================
# SIDEBAR FILTER
# ====================================
st.sidebar.header("🔎 Dashboard Filter")

selected_period = st.sidebar.radio(
    "Select Period",
    [
        "All Period (1999–2023)",
        "Before COVID (2006–2019)",
        "After COVID (2020–2023)"
    ]
)

# ====================================
# PERIOD FILTER
# ====================================

if selected_period == "All Period (1999–2023)":

    filtered_period = df[
        (df["year"] >= 1999) &
        (df["year"] <= 2023)
    ]

elif selected_period == "Before COVID (2006–2019)":

    filtered_period = df[
        (df["year"] >= 2006) &
        (df["year"] <= 2019)
    ]

else:

    filtered_period = df[
        (df["year"] >= 2020) &
        (df["year"] <= 2023)
    ]

# Town filter
selected_town = st.sidebar.multiselect(
    "Select Town",
    options=sorted(
        filtered_period[
            filtered_period["town"] != "***Unknown***"
        ]["town"].dropna().unique()
    ),
    default=sorted(
        filtered_period[
            filtered_period["town"] != "***Unknown***"
        ]["town"].dropna().unique()
    )
)


# Property filter
selected_property = st.sidebar.multiselect(
    "Property Type",
    options=sorted(
        filtered_period["property_type"]
        .dropna()
        .unique()
    ),
    default=sorted(
        filtered_period["property_type"]
        .dropna()
        .unique()
    )
)

# Final filtered dataframe
filtered_df = filtered_period[
    (
        filtered_period["town"]
        .isin(selected_town)
    )
    &
    (
        filtered_period["property_type"]
        .isin(selected_property)
    )
]

# ====================================
# DATA CLEANING SUMMARY
# ====================================
st.markdown("---")
st.header("🧹 Data Cleaning Summary")

raw_rows = 1_097_629
clean_rows = len(df)
removed_rows = raw_rows - clean_rows

col1, col2, col3 = st.columns(3)

col1.metric(
    "Raw Dataset",
    f"{raw_rows:,}"
)

col2.metric(
    "Clean Dataset",
    f"{clean_rows:,}"
)

col3.metric(
    "Rows Removed",
    f"{removed_rows:,}"
)

# ====================================
# DATASET STATISTICS
# ====================================
st.markdown("---")
st.header("📊 Dataset Statistics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Rows",
    f"{filtered_df.shape[0]:,}"
)

col2.metric(
    "Columns",
    filtered_df.shape[1]
)

col3.metric(
    "Missing Values",
    int(filtered_df.isnull().sum().sum())
)

col4.metric(
    "Duplicate Rows",
    int(filtered_df.duplicated().sum())
)

# ====================================
# MEDIAN PRICE TREND
# ====================================
st.markdown("---")
st.header("📈 Median Property Price Trend")

st.markdown("""
### Cara membaca chart:

- Garis naik → harga rumah meningkat  
- Garis turun → market melemah  
- Garis merah = awal COVID (2020)
""")

yearly_price = (
    filtered_df.groupby("year")[
        "sale_amount"
    ]
    .median()
    .reset_index()
)

fig_line = px.line(
    yearly_price,
    x="year",
    y="sale_amount",
    markers=True,
    title="Median Property Price by Year"
)

fig_line.add_vline(
    x=2020,
    line_dash="dash",
    line_color="red",
    annotation_text="COVID Start"
)

fig_line.update_layout(
    xaxis_title="Year",
    yaxis_title="Median Sale Amount",
    hovermode="x unified"
)


st.plotly_chart(
    fig_line,
    use_container_width=True
)

# ====================================
# TOWN INVESTMENT ANALYSIS
# ====================================
st.markdown("---")
st.header("🏙️ Town Investment Analysis")

st.markdown("""
### Cara membaca chart:

- Kanan → harga rumah mahal  
- Atas → transaksi ramai  
- Bubble besar → market besar  

**Sweet Spot Investor:**  
kanan + atas + bubble besar
""")

town_analysis = (
    filtered_df.groupby("town")
    .agg(
        median_price=(
            "sale_amount",
            "median"
        ),
        total_transactions=(
            "sale_amount",
            "count"
        ),
        total_sales=(
            "sale_amount",
            "sum"
        )
    )
    .reset_index()
)

fig_bubble = px.scatter(
    town_analysis,
    x="median_price",
    y="total_transactions",
    size="total_sales",
    color="town",
    hover_name="town",
    title="Town Investment Opportunity Map"
)

st.plotly_chart(
    fig_bubble,
    use_container_width=True
)

# ====================================
# PROPERTY DISTRIBUTION
# ====================================
st.markdown("---")
st.header("📊 Property Price Distribution")

st.markdown("""
Melihat persebaran harga rumah berdasarkan tipe property.

### Cara membaca:
- Box tinggi → variasi harga besar  
- Box pendek → harga stabil  
- Titik outlier → transaksi ekstrem
""")

fig_box = px.box(
    filtered_df,
    x="residential_type",
    y="sale_amount",
    color="residential_type",
    title="Property Price Distribution by Residential Type"
)

st.plotly_chart(
    fig_box,
    use_container_width=True
)

# ====================================
# ASSESSED VS SALE AMOUNT
# ====================================
st.markdown("---")
st.header("💰 Assessed vs Sale Amount")

st.markdown("""
### Cara membaca:

- Di atas garis merah → overpriced  
- Di bawah garis merah → undervalued  
- Dekat garis → fair market value
""")

sample_df = filtered_df.sample(
    min(5000, len(filtered_df))
)

max_value = max(
    sample_df[
        "assessed_value"
    ].max(),
    sample_df[
        "sale_amount"
    ].max()
)

fig_scatter = px.scatter(
    sample_df,
    x="assessed_value",
    y="sale_amount",
    color="residential_type",
    opacity=0.5,
    title="Assessed Value vs Sale Amount"
)

fig_scatter.add_shape(
    type="line",
    x0=0,
    y0=0,
    x1=max_value,
    y1=max_value,
    line=dict(
        color="red",
        dash="dash"
    )
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# ====================================
# RESIDENTIAL ANALYSIS
# ====================================
st.markdown("---")
st.header("🏠 Residential Market Composition")

residential_summary = (
    filtered_df
    .groupby("residential_type")
    .agg(
        transactions=("sale_amount", "count"),
        median_price=("sale_amount", "median")
    )
    .reset_index()
)

# chart size
col1, col2 = st.columns(2)

# LEFT = market demand
with col1:

    fig_demand = px.bar(
        residential_summary,
        x="residential_type",
        y="transactions",
        color="residential_type",
        text_auto=True,
        title="Market Demand"
    )

    fig_demand.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_demand,
        use_container_width=True
    )

# RIGHT = economic value
with col2:

    fig_price = px.bar(
        residential_summary,
        x="residential_type",
        y="median_price",
        color="residential_type",
        text_auto=True,
        title="Median Property Price"
    )

    fig_price.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )


# ====================================
# TOP TOWNS ONLY (supaya tidak terlalu penuh)
# ====================================
top_town_list = (
    filtered_df["town"]
    .value_counts()
    .head(15)
    .index
)

town_property_df = filtered_df[
    filtered_df["town"].isin(top_town_list)
]

# ====================================
# GROUP DATA
# ====================================
town_property = (
    town_property_df.groupby(
        ["town", "residential_type"]
    )
    .size()
    .reset_index(name="transactions")
)

# ====================================
# 2 COLUMN LAYOUT
# ====================================
col1, col2 = st.columns(2)

# ====================================
# HEATMAP STYLE
# ====================================

# ====================================
# MOST ACTIVE TOWNS
# ====================================
st.markdown("---")
st.header("🏙️ Most Active Towns")

mode = st.toggle(
    "Show by Total Sales Value (USD)",
    value=False
)

if mode:

    town_activity = (
        filtered_df
        .groupby("town")[
            "sale_amount"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    fig_activity = px.bar(
        town_activity,
        x="town",
        y="sale_amount",
        title="Top 10 Towns by Total Sales (USD)",
        text_auto=True
    )

else:

    town_activity = (
        filtered_df["town"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    town_activity.columns = [
        "town",
        "transactions"
    ]

    fig_activity = px.bar(
        town_activity,
        x="town",
        y="transactions",
        title="Top 10 Towns by Transactions",
        text_auto=True
    )

st.plotly_chart(
    fig_activity,
    use_container_width=True
)

# ====================================
# PROPERTY TYPE VS TOWN ANALYSIS
# ====================================
st.markdown("---")
st.header("🏙️ Property Type Demand by Town")

st.markdown("""
Melihat **tipe property paling laku di setiap kota**.

Berguna untuk:

- **Investor** → mencari demand area
- **Developer** → membangun tipe rumah yang tepat
- **Agen Properti** → memahami karakter market tiap kota
""")

# ====================================
# PROPERTY TYPE VS TOWN
# ====================================
col1, col2 = st.columns(2)

# ====================================
# LEFT = HEATMAP
# ====================================
with col1:

    st.subheader(
        "🔥 Property Type Demand by Town"
    )

    st.caption(
        """
        Warna yang lebih gelap = lebih banyak transaksi. 
        Membantu mengidentifikasi jenis properti mana yang paling diminati di setiap kota..
        """
    )

    pivot_table = town_property.pivot(
        index="town",
        columns="residential_type",
        values="transactions"
    ).fillna(0)

    fig_heatmap = px.imshow(
        pivot_table,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues"
    )

    fig_heatmap.update_layout(
        title="Town vs Property Type Demand",
        height=600,
        coloraxis_colorbar_title="Transactions"
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )


# ====================================
# STACKED BAR
# ====================================
with col2:

    st.subheader(
        "📊 Property Mix by Town"
    )

    fig_bar = px.bar(
        town_property,
        x="town",
        y="transactions",
        color="residential_type",
        barmode="stack",
        title="Property Type Composition per Town"
    )

    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )


# ====================================
# DISCLAIMER / NOTES
# ====================================
st.markdown("---")
st.header("📝 Notes & Disclaimer")

st.info("""
### Catatan Penting Sebelum Menginterpretasikan Dasbor

1. **Dasbor ini didasarkan pada data transaksi historis**

dan **tidak menjamin kinerja properti di masa mendatang**.

        
2. **Harga median digunakan sebagai pengganti harga rata-rata**
        
untuk mengurangi distorsi yang disebabkan oleh transaksi yang sangat mahal atau tidak normal.

        
3. **Pemisahan periode COVID**

dibagi menjadi:

- **Sebelum COVID:** 2006–2019

- **Setelah COVID / Pemulihan:** 2020–2023

untuk mengamati potensi perubahan struktural pasar.

        
4. **Kota Paling Aktif**
mengacu pada **jumlah transaksi properti**

(**volume**) — **bukan nilai penjualan total dalam USD**.

        
5. **Komposisi Pasar Perumahan**
mewakili **permintaan pasar (volume transaksi)**,

sedangkan **harga median** mewakili

**nilai ekonomi setiap jenis properti**.

        
6. **Perbandingan Nilai Taksiran vs. Harga Jual**

digunakan untuk mengidentifikasi:

- kemungkinan **properti yang dinilai terlalu rendah**

- kemungkinan **properti yang dinilai terlalu tinggi**
- potensi **ketidaksesuaian penilaian**

Hal ini harus ditafsirkan dengan hati-hati,

karena penilaian pajak mungkin berbeda
dari harga pasar.


""")