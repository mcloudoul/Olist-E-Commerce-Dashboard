# 🛒 E-Commerce Public Data Analysis Dashboard

## 📌 Deskripsi Proyek

Proyek ini menganalisis performa **e-commerce** dari **Brazilian E-Commerce Public Dataset by Olist** selama periode **September 2016 – Agustus 2018**. Analisis mencakup tren penjualan, segmentasi pelanggan menggunakan metode **RFM (Recency, Frequency, Monetary)**, kontribusi kategori produk, serta analisis retensi pelanggan melalui **Cohort Analysis**. Seluruh proses dilakukan dengan **Python** (Pandas, Matplotlib, Seaborn, SciPy) dan hasilnya divisualisasikan dalam **dashboard interaktif** menggunakan **Streamlit**.

Dashboard ini memungkinkan pengguna untuk mengeksplorasi data secara dinamis melalui filter tahun dan kategori produk, serta menyajikan insight yang diperbarui secara otomatis sesuai filter yang dipilih.

---

## 👤 Informasi Pembuat

**Nama:** Sri Hartati Setia Ningrum  
**Email:** CDCC200D6X1030@student.devacademy.id  
**ID Dicoding:** CDCC200D6X1030  

---

## 🎯 Pertanyaan Bisnis

1. Bagaimana **tren total revenue dan jumlah order per bulan** selama periode 2016–2018, serta apakah terdapat **pola musiman** yang dapat dimanfaatkan untuk strategi penjualan?

2. Bagaimana **segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary (RFM)**, dan kelompok pelanggan mana yang memberikan **kontribusi terbesar** terhadap total revenue?

3. **Kategori produk** apa yang memberikan kontribusi terbesar terhadap total revenue, dan bagaimana **distribusi kontribusi** tersebut selama periode 2016–2018?

---

## 🔍 Analisis Lanjutan (Cohort Retention)

Untuk melengkapi analisis RFM, dilakukan **Cohort Analysis** guna memahami pola retensi pelanggan berdasarkan waktu akuisisi pertama mereka. Metrik yang dianalisis meliputi:

- **Customer Retention Rate** per bulan sejak pembelian pertama
- **Cohort Size** (jumlah pelanggan baru per bulan)
- **Average Revenue per Customer (ARPC)** untuk mengukur kualitas pelanggan dari sisi nilai transaksi

Analisis ini mengidentifikasi bahwa pelanggan yang diperoleh pada periode musiman (Q4) cenderung memiliki retensi lebih tinggi.

---

## 📊 Insight Utama

### 1. Tren Revenue & Musiman

* Revenue tumbuh pesat pada 2017 (+49,9% YoY) dan stabil di 2018.
* Pola musiman kuat: puncak di **November–Desember** (Black Friday & liburan), penurunan di **Januari–Februari**.
* **Rekomendasi:** Alokasikan 40% budget pemasaran ke Q4.

### 2. Segmentasi Pelanggan (RFM)

* **Champions & Loyal Customers** (hanya ~20% pelanggan) menyumbang **>50% total revenue**.
* Segmen *At Risk* dan *Need Attention* memiliki potensi churn tinggi dan perlu reaktivasi.
* **Efisiensi kontribusi** Champions mencapai >4x dibandingkan segmen lain.

### 3. Kontribusi Kategori Produk

* Prinsip **Pareto (80/20)** berlaku: 12 kategori (18%) menyumbang 80% revenue.
* Kategori **health_beauty** (19,5%) dan **computers_accessories** (14,8%) adalah kontributor utama.
* **watches_gifts** tercatat sebagai *rising star* dengan pertumbuhan +63% (2017–2018).

### 4. Retensi Pelanggan (Cohort)

* Retensi turun drastis pada bulan pertama (*early churn*).
* Cohort yang bergabung pada **Oktober–November** memiliki retensi lebih baik.
* Pelanggan yang bertahan hingga bulan ke-3 cenderung memiliki nilai transaksi yang lebih tinggi.

---

## ⚙️ Fitur Utama Dashboard

* 🎛️ **Filter Global Interaktif**  
  * Pilih tahun (2016–2018)  
  * Pilih kategori produk (dengan opsi "Pilih Semua")

* 📈 **Visualisasi Analitis**  
  * Tren revenue & jumlah order (dual-axis chart)  
  * Pola musiman rata-rata per bulan  
  * Kontribusi revenue per segmen RFM (bar chart + tabel efisiensi)  
  * Pareto chart kontribusi kategori produk  
  * Heatmap cohort retention

* 💡 **Insight Dinamis**  
  * Setiap insight box diperbarui otomatis sesuai filter yang dipilih  
  * Menampilkan persentase dan nilai absolut yang relevan

* 🧩 **Expandable Section**  
  * Matriks RFM (Recency vs Frequency) dapat dilihat secara opsional

---

## 🗂️ Struktur Direktori

```
submission
├── dashboard
│   ├── main_data.csv          # Data final hasil cleaning
│   └── dashboard.py           # Kode dashboard Streamlit
├── data                       
│   ├── customers_dataset.csv
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   └── product_category_name_translation.csv
├── notebook.ipynb             # Proses analisis data lengkap
├── README.md
├── requirements.txt
└── url.txt                    # Link deployment
```

---

## 🚀 Cara Menjalankan Dashboard

### 1. Clone Repository

```bash
git clone https://github.com/username/ecommerce-analysis-dashboard.git
cd ecommerce-analysis-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Masuk ke Folder Dashboard dan Jalankan Streamlit

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka secara otomatis di browser pada `http://localhost:8501`.

---

## 🧰 Library yang Digunakan

* `pandas` – manipulasi data  
* `numpy` – operasi numerik  
* `matplotlib` & `seaborn` – visualisasi data  
* `scipy.stats` – uji statistik (Chi-Square, Shapiro-Wilk)  
* `streamlit` – framework dashboard interaktif  

---

## 📌 Catatan Tambahan

* Dataset asli berasal dari [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) di Kaggle.
* Data telah melalui proses **Data Wrangling** (gathering, assessing, cleaning) serta **Exploratory Data Analysis (EDA)** yang komprehensif (univariate, multivariate, numerik, kategorikal).
* Kode pada `notebook.ipynb` berisi seluruh langkah analisis dari awal hingga menghasilkan `main_data.csv` yang digunakan dashboard.

---

## 🌐 Deployment

[Olist E-Commerce Dashboard](https://olist-e-commerce-dashboard-shstian.streamlit.app/)

---

## © Copyright

© 2026 Sri Hartati Setia Ningrum
```

