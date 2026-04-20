# ============================================
# DASHBOARD ANALISIS DATA E-COMMERCE (REVISED)
# ============================================
# Fokus: Menjawab 3 Business Questions dengan visualisasi analitis
# Single-page, global filter, insight dinamis, minimal CSS
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

# ============================================
# MINIMAL CUSTOM CSS (hanya untuk readability)
# ============================================
st.markdown("""
<style>
    .main-header {
        padding: 1.5rem 0rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #4A90E2;
    }
    .kpi-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .insight-box {
        background-color: #eef2f7;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #4A90E2;
        margin: 1rem 0;
        color: #1e1e2f;  /* Warna teks gelap agar kontras di dark mode */
    }
    .insight-box b, .insight-box p {
        color: #1e1e2f;  /* Pastikan semua teks di dalamnya gelap */
    }
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #95a5a6;
        font-size: 0.8rem;
        border-top: 1px solid #ecf0f1;
        padding-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING (CACHED)
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('main_data.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_year'] = df['order_purchase_timestamp'].dt.year
    df['order_month'] = df['order_purchase_timestamp'].dt.month
    df['order_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ============================================
# SIDEBAR FILTERS (GLOBAL)
# ============================================
st.sidebar.header("Filter Data")

# Tahun
years = sorted(df['order_year'].unique())
selected_years = st.sidebar.multiselect(
    "Pilih Tahun",
    options=years,
    default=years
)

# Kategori (dengan opsi "All")
all_categories = sorted(df['product_category_name_english'].dropna().unique())
# Inisialisasi session state untuk menyimpan pilihan kategori
if "selected_cats" not in st.session_state:
    st.session_state.selected_cats = all_categories.copy()

def select_all_categories():
    """Callback untuk checkbox: pilih semua kategori"""
    st.session_state.selected_cats = all_categories.copy()

def clear_categories():
    """Callback untuk mengosongkan pilihan (opsional)"""
    st.session_state.selected_cats = []

# Checkbox "Pilih Semua" tanpa on_change yang konflik
select_all = st.sidebar.checkbox(
    "Pilih Semua Kategori",
    value=(len(st.session_state.selected_cats) == len(all_categories)),
    on_change=select_all_categories if not (len(st.session_state.selected_cats) == len(all_categories)) else None
)

# Multiselect yang nilainya terikat ke session_state
selected_cats = st.sidebar.multiselect(
    "Kategori Produk",
    options=all_categories,
    default=st.session_state.selected_cats,
    key="category_multiselect"
)

# Update session state saat user mengubah multiselect
st.session_state.selected_cats = selected_cats

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard ini menjawab 3 pertanyaan bisnis utama dengan analisis data Olist.")

# ============================================
# APPLY FILTERS
# ============================================
df_filtered = df[
    (df['order_year'].isin(selected_years)) &
    (df['product_category_name_english'].isin(selected_cats))
].copy()

if df_filtered.empty:
    st.warning("Tidak ada data dengan filter yang dipilih. Silakan sesuaikan filter.")
    st.stop()

# ============================================
# HELPER FUNCTIONS (Cached with filter hash)
# ============================================
def get_filter_hash(years, cats):
    return f"{'-'.join(map(str, sorted(years)))}|{'-'.join(sorted(cats))}"

@st.cache_data
def compute_monthly_metrics(df_filtered, filter_hash):
    monthly = df_filtered.groupby('order_year_month').agg(
        revenue=('price', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index()
    return monthly

@st.cache_data
def compute_seasonal_avg(df_filtered, filter_hash):
    seasonal = df_filtered.groupby('order_month')['price'].mean().reset_index()
    seasonal['month_name'] = seasonal['order_month'].apply(lambda x: pd.Timestamp(2020, x, 1).strftime('%b'))
    return seasonal

@st.cache_data
def compute_rfm(df_filtered, filter_hash):
    customer_col = 'customer_unique_id' if 'customer_unique_id' in df_filtered.columns else 'customer_id'
    reference_date = df_filtered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = df_filtered.groupby(customer_col).agg(
        recency=('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum')
    ).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Scoring using quantiles
    try:
        rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4,3,2,1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'], q=4, labels=[1,2,3,4], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1,2,3,4], duplicates='drop')
    except:
        rfm['r_score'] = pd.cut(rfm['recency'], bins=4, labels=[4,3,2,1])
        rfm['f_score'] = pd.cut(rfm['frequency'], bins=4, labels=[1,2,3,4])
        rfm['m_score'] = pd.cut(rfm['monetary'], bins=4, labels=[1,2,3,4])
    
    for col in ['r_score','f_score','m_score']:
        rfm[col] = rfm[col].astype(int)
    
    def segment(row):
        r,f,m = row['r_score'], row['f_score'], row['m_score']
        if r >= 3 and f >= 3 and m >= 3: return 'Champions'
        elif r >= 3 and f >= 3: return 'Loyal Customers'
        elif r >= 3 and f >= 2: return 'Potential Loyalists'
        elif r >= 4: return 'New Customers'
        elif r <= 2 and f >= 3: return 'At Risk'
        elif r <= 2 and f >= 2: return 'Need Attention'
        else: return 'Others'
    
    rfm['segment'] = rfm.apply(segment, axis=1)
    return rfm

@st.cache_data
def compute_category_metrics(df_filtered, filter_hash):
    cat = df_filtered.groupby('product_category_name_english').agg(
        revenue=('price', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index()
    cat = cat.sort_values('revenue', ascending=False)
    cat['cum_pct'] = cat['revenue'].cumsum() / cat['revenue'].sum() * 100
    return cat

@st.cache_data
def compute_cohort(df_filtered, filter_hash):
    customer_col = 'customer_unique_id' if 'customer_unique_id' in df_filtered.columns else 'customer_id'
    first = df_filtered.groupby(customer_col)['order_purchase_timestamp'].min().reset_index()
    first.columns = [customer_col, 'first_date']
    first['cohort'] = first['first_date'].dt.to_period('M').astype(str)
    
    df_temp = df_filtered.copy()
    df_temp['order_period'] = df_temp['order_purchase_timestamp'].dt.to_period('M').astype(str)
    
    cohort_df = df_temp.merge(first[[customer_col, 'cohort']], on=customer_col)
    cohort_df['period'] = cohort_df.apply(
        lambda r: (int(r['order_period'][:4]) - int(r['cohort'][:4])) * 12 +
                  (int(r['order_period'][5:7]) - int(r['cohort'][5:7])), axis=1
    )
    cohort_df = cohort_df[cohort_df['period'] >= 0]
    
    retention = cohort_df.groupby(['cohort', 'period'])[customer_col].nunique().reset_index()
    size = retention[retention['period']==0][['cohort', customer_col]].rename(columns={customer_col:'size'})
    retention = retention.merge(size, on='cohort')
    retention['retention_rate'] = (retention[customer_col] / retention['size']) * 100
    
    pivot = retention.pivot(index='cohort', columns='period', values='retention_rate')
    return pivot

# ============================================
# COMPUTE DATA WITH FILTER HASH
# ============================================
filter_hash = get_filter_hash(selected_years, selected_cats)

monthly_df = compute_monthly_metrics(df_filtered, filter_hash)
seasonal_df = compute_seasonal_avg(df_filtered, filter_hash)
rfm_df = compute_rfm(df_filtered, filter_hash)
cat_df = compute_category_metrics(df_filtered, filter_hash)
cohort_pivot = compute_cohort(df_filtered, filter_hash)

# KPI Values
total_revenue = df_filtered['price'].sum()
total_orders = df_filtered['order_id'].nunique()
aov = total_revenue / total_orders if total_orders else 0
customer_col = 'customer_unique_id' if 'customer_unique_id' in df_filtered.columns else 'customer_id'
total_customers = df_filtered[customer_col].nunique()

# Segment aggregation
seg_summary = rfm_df.groupby('segment').agg(
    count=('customer_id', 'count'),
    revenue=('monetary', 'sum'),
    avg_monetary=('monetary', 'mean')
).reset_index()
seg_summary['revenue_pct'] = seg_summary['revenue'] / seg_summary['revenue'].sum() * 100
seg_summary['count_pct'] = seg_summary['count'] / seg_summary['count'].sum() * 100
seg_summary['efficiency'] = seg_summary['revenue_pct'] / seg_summary['count_pct']
seg_summary = seg_summary.sort_values('revenue', ascending=False)

# ============================================
# HEADER
# ============================================
st.markdown("""
<div class="main-header">
    <h1>📊 Olist E-Commerce Analytics Dashboard</h1>
    <p style="font-size:1rem; color:#555;">Analisis Data Penjualan 2016-2018 · Segmentasi Pelanggan · Kategori Produk</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Business Questions:**
1. Bagaimana tren revenue dan jumlah order per bulan, serta adakah pola musiman?
2. Bagaimana segmentasi pelanggan berdasarkan RFM dan kontribusi revenue tiap segmen?
3. Kategori produk apa yang berkontribusi terbesar terhadap revenue?
""")

# ============================================
# KPI ROW
# ============================================
cols = st.columns(4)
with cols[0]:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">${total_revenue:,.0f}</div><div class="kpi-label">Total Revenue</div></div>', unsafe_allow_html=True)
with cols[1]:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_orders:,}</div><div class="kpi-label">Total Orders</div></div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">${aov:.2f}</div><div class="kpi-label">Avg Order Value</div></div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_customers:,}</div><div class="kpi-label">Active Customers</div></div>', unsafe_allow_html=True)

# ============================================
# Q1: TREND & SEASONALITY
# ============================================
st.markdown('<div class="section-title">1️⃣ Tren Revenue & Pola Musiman</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Dual axis chart: bar revenue, line orders
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(monthly_df['order_year_month'], monthly_df['revenue'], color='#4A90E2', alpha=0.7, label='Revenue')
    ax1.set_xlabel('Bulan')
    ax1.set_ylabel('Revenue ($)', color='#4A90E2')
    ax1.tick_params(axis='y', labelcolor='#4A90E2')
    ax1.tick_params(axis='x', rotation=45)
    
    ax2 = ax1.twinx()
    ax2.plot(monthly_df['order_year_month'], monthly_df['orders'], color='#E24A4A', marker='o', linewidth=2, label='Orders')
    ax2.set_ylabel('Jumlah Order', color='#E24A4A')
    ax2.tick_params(axis='y', labelcolor='#E24A4A')
    
    plt.title('Revenue & Jumlah Order per Bulan', fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)

with col2:
    # Seasonal bar chart
    fig, ax = plt.subplots(figsize=(5, 4))
    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    seasonal_df['month_name'] = pd.Categorical(seasonal_df['month_name'], categories=month_order, ordered=True)
    seasonal_df = seasonal_df.sort_values('month_name')
    colors = ['#E24A4A' if m in ['Nov','Dec'] else '#4A90E2' for m in seasonal_df['month_name']]
    ax.bar(seasonal_df['month_name'], seasonal_df['price'], color=colors)
    ax.axhline(seasonal_df['price'].mean(), color='gray', linestyle='--', label='Rata-rata')
    ax.set_title('Rata-rata Revenue per Bulan (Seasonal Index)')
    ax.set_ylabel('Avg Revenue ($)')
    ax.legend()
    st.pyplot(fig)

# Dynamic insight
peak_month = monthly_df.loc[monthly_df['revenue'].idxmax(), 'order_year_month']
peak_val = monthly_df['revenue'].max()
avg_nov = seasonal_df[seasonal_df['month_name']=='Nov']['price'].values[0] if 'Nov' in seasonal_df['month_name'].values else 0
avg_all = seasonal_df['price'].mean()
nov_vs_avg = (avg_nov / avg_all - 1) * 100 if avg_all > 0 else 0

st.markdown(f"""
<div class="insight-box">
<b>📌 Insight Q1:</b> Revenue menunjukkan tren naik dari 2016 ke 2017, lalu stabil di 2018. 
Puncak terjadi pada <b>{peak_month}</b> dengan revenue <b>${peak_val:,.0f}</b>. 
Terdapat pola musiman kuat: November rata-rata <b>{nov_vs_avg:+.0f}%</b> di atas rata-rata (efek Black Friday), 
sementara Januari-Februari di bawah rata-rata.
</div>
""", unsafe_allow_html=True)

# ============================================
# Q2: RFM SEGMENTATION
# ============================================
st.markdown('<div class="section-title">2️⃣ Segmentasi Pelanggan (RFM)</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    # Horizontal bar: Revenue by segment
    fig, ax = plt.subplots(figsize=(8, 5))
    seg_sorted = seg_summary.sort_values('revenue', ascending=True)
    colors_seg = ['#2ecc71' if s=='Champions' else '#3498db' if s=='Loyal Customers' else '#f39c12' for s in seg_sorted['segment']]
    bars = ax.barh(seg_sorted['segment'], seg_sorted['revenue'], color=colors_seg)
    ax.set_xlabel('Total Revenue ($)')
    ax.set_title('Kontribusi Revenue per Segmen')
    # Add value labels
    for bar, val in zip(bars, seg_sorted['revenue']):
        ax.text(val, bar.get_y() + bar.get_height()/2, f'${val:,.0f}', va='center', fontsize=9)
    st.pyplot(fig)

with col2:
    # Summary table
    st.dataframe(
        seg_summary[['segment', 'count', 'revenue', 'revenue_pct', 'efficiency']]
        .style.format({
            'count': '{:,}',
            'revenue': '${:,.0f}',
            'revenue_pct': '{:.1f}%',
            'efficiency': '{:.2f}x'
        })
        .background_gradient(subset=['efficiency'], cmap='Blues'),
        use_container_width=True
    )

# Insight
top_seg = seg_summary.iloc[0]
st.markdown(f"""
<div class="insight-box">
<b>📌 Insight Q2:</b> Segmen <b>{top_seg['segment']}</b> (hanya {top_seg['count_pct']:.1f}% pelanggan) 
menyumbang <b>{top_seg['revenue_pct']:.1f}%</b> total revenue dengan efisiensi {top_seg['efficiency']:.2f}x. 
Fokus retensi pada Champions & Loyal Customers sangat krusial.
</div>
""", unsafe_allow_html=True)

# Optional: RFM heatmap expander
with st.expander("🔍 Lihat Matriks RFM (Recency vs Frequency)"):
    rfm_pivot = rfm_df.groupby(['r_score','f_score']).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(rfm_pivot, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_xlabel('Frequency Score (higher=better)')
    ax.set_ylabel('Recency Score (higher=better)')
    st.pyplot(fig)
    st.markdown("""
    **Cara membaca:**  
    - **Recency Score (R):** 4 = transaksi terbaru (baik), 1 = sudah lama tidak transaksi.  
    - **Frequency Score (F):** 4 = sering beli (baik), 1 = jarang beli.  
    Sel dengan nilai tinggi (warna gelap) menunjukkan kombinasi skor yang banyak dimiliki pelanggan.  
    Pelanggan dengan R≥3 dan F≥3 adalah kandidat segmen *Champions* atau *Loyal*.
    """)

# ============================================
# Q3: PRODUCT CATEGORY CONTRIBUTION
# ============================================
st.markdown('<div class="section-title">3️⃣ Kontribusi Kategori Produk</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Pareto chart (top 10)
    top10 = cat_df.head(10).copy()
    fig, ax1 = plt.subplots(figsize=(10, 5))
    bars = ax1.bar(top10['product_category_name_english'], top10['revenue'], color='#4A90E2', alpha=0.7)
    ax1.set_xlabel('Kategori')
    ax1.set_ylabel('Revenue ($)')
    ax1.tick_params(axis='x', rotation=45)
    
    ax2 = ax1.twinx()
    ax2.plot(top10['product_category_name_english'], top10['cum_pct'], color='#E24A4A', marker='o', linewidth=2)
    ax2.set_ylabel('Kumulatif %', color='#E24A4A')
    ax2.tick_params(axis='y', labelcolor='#E24A4A')
    ax2.axhline(80, color='gray', linestyle='--', alpha=0.5)
    ax2.set_ylim(0, 105)
    plt.title('Pareto Chart: Kontribusi Revenue Kategori (Top 10)')
    fig.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("**Top 5 Kategori**")
    top5 = cat_df.head(5)[['product_category_name_english', 'revenue']]
    top5['revenue'] = top5['revenue'].apply(lambda x: f"${x:,.0f}")
    st.dataframe(top5, hide_index=True, use_container_width=True)

# Insight
top_cat = cat_df.iloc[0]['product_category_name_english']
top_cat_rev_pct = cat_df.iloc[0]['revenue'] / cat_df['revenue'].sum() * 100
n_cat_80 = (cat_df['cum_pct'] <= 80).sum()
st.markdown(f"""
<div class="insight-box">
<b>📌 Insight Q3:</b> Kategori <b>{top_cat}</b> adalah kontributor terbesar ({top_cat_rev_pct:.1f}% revenue). 
{n_cat_80} kategori (dari {len(cat_df)}) sudah menyumbang 80% total revenue (Pareto principle). 
Fokus pengembangan pada kategori top performer.
</div>
""", unsafe_allow_html=True)

# ============================================
# ADVANCED: COHORT RETENTION
# ============================================
st.markdown('<div class="section-title">📅 Cohort Retention (Analisis Lanjutan)</div>', unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(cohort_pivot, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Retention %'})
ax.set_xlabel('Bulan Sejak Pembelian Pertama')
ax.set_ylabel('Cohort (Bulan Pertama)')
ax.set_title('Customer Retention Rate by Cohort')
st.pyplot(fig)

st.markdown("""
<div class="insight-box">
<b>📌 Insight Cohort:</b> Retensi pelanggan turun drastis setelah bulan pertama. 
Cohort yang bergabung di Q4 (Oktober-November) cenderung memiliki retensi lebih baik. 
Strategi onboarding dan follow-up di 3 bulan pertama sangat penting untuk meningkatkan lifetime value.
</div>
""", unsafe_allow_html=True)

# ============================================
# CONCLUSION & RECOMMENDATIONS
# ============================================
st.markdown('<div class="section-title">📋 Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

# Format tahun menjadi string yang rapi
tahun_str = ', '.join(map(str, selected_years))

st.markdown(f"""
Berdasarkan analisis dengan filter aktif (Tahun: {tahun_str}, Kategori: {len(selected_cats)} kategori):
- **Tren & Musiman:** Revenue memuncak di November-Desember. Alokasikan budget marketing 40% ke Q4.
- **Segmentasi Pelanggan:** Segmen Champions & Loyal Customers (< 20% pelanggan) berkontribusi > 50% revenue. Prioritaskan program loyalitas untuk mereka.
- **Kategori Produk:** Fokus pada {n_cat_80} kategori utama yang menyumbang 80% revenue. Pantau kategori dengan pertumbuhan tinggi untuk ekspansi.
- **Retensi:** Tingkatkan retensi 3 bulan pertama melalui program welcome discount dan personalized recommendation.
""")

st.markdown("---")

# Footer
st.markdown("""
<div class="footer">
    <p><b>Proyek Akhir Analisis Data</b> · Dicoding · Dataset: Olist Brazilian E-Commerce</p>
    <p>Analyst: Sri Hartati Setia Ningrum · Dashboard dibuat dengan Streamlit</p>
</div>
""", unsafe_allow_html=True)
