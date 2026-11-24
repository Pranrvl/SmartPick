# 📱 SmartPick 
### Sistem Pendukung Keputusan (SPK) Rekomendasi Smartphone Berbasis K-Means Clustering & TOPSIS

<p align="center">
  <img src="assets/logo_full.png" alt="SmartPick Logo" width="380"/>
</p>

---

## 📌 Tentang SmartPick
**SmartPick Informatika** adalah platform berbasis web interaktif yang dirancang untuk membantu pengguna menentukan pilihan smartphone terbaik yang paling sesuai dengan kebutuhan fungsional dan batasan anggarannya. 

Aplikasi ini menggabungkan:
1. **K-Means Clustering:** Mengelompokkan 758 smartphone ke dalam klaster karakteristik spesifikasi (Flagship Tier vs. Mid-Range Tier).
2. **TOPSIS (*Technique for Order of Preference by Similarity to Ideal Solution*):** Melakukan perangkingan multi-kriteria berbasis kedekatan relatif terhadap solusi ideal positif ($D^+$) dan solusi ideal negatif ($D^-$).
3. **Data Ilmiah Teruji:** Bobot 7 kriteria teknis dibakukan secara objektif melalui kuesioner preferensi pengguna.

---

## ✨ Fitur Utama
- 🎨 **Apple Minimalist Design:** Antarmuka modern, bersih, intuitif, dan responsif.
- ⚡ **Liquid Motion Transition:** Animasi perpindahan antar-halaman yang mulus.
- 🖼️ **Foto Smartphone Asli:** Kartu hasil rekomendasi terintegrasi dengan foto fisik smartphone resmi dari basis data.
- 🔍 **Filter Fleksibel:** Penyesuaian rentang anggaran (Entry-Level, Mid-Range, hingga Flagship) serta fokus aktivitas harian (Gaming, Fotografi, Produktivitas, dsb).
- 📊 **Detail Analisis Matematis:** Visualisasi skor preferensi ($V_i$), jarak Euclidean, serta spesifikasi lengkap perangkat.

---

## 📐 7 Parameter Kriteria Keputusan

| Kode | Kriteria | Sifat (Attribute) | Satuan | Deskripsi |
| :---: | :--- | :---: | :---: | :--- |
| **C1** | **Harga** | *Cost* | IDR | Anggaran pembelian; nilai lebih rendah diprioritaskan. |
| **C2** | **RAM** | *Benefit* | GB | Kelancaran multitasking dan performa aplikasi berat. |
| **C3** | **Penyimpanan (ROM)** | *Benefit* | GB | Kapasitas instalasi game, aplikasi, dan media. |
| **C4** | **Clock Speed CPU** | *Benefit* | GHz | Kecepatan pemrosesan inti prosesor. |
| **C5** | **Kapasitas Baterai** | *Benefit* | mAh | Ketahanan penggunaan harian. |
| **C6** | **Kamera Utama** | *Benefit* | MP | Resolusi sensor kamera utama untuk foto & video. |
| **C7** | **Fast Charging** | *Benefit* | Watt | Efisiensi kecepatan pengisian daya baterai. |

---

## 🚀 Panduan Menjalankan Aplikasi Secara Lokal

### 1. Clone Repositori
```bash
git clone https://github.com/Pranrvl/SmartPick.git
cd SmartPick
```

### 2. Buat & Aktifkan Virtual Environment (Opsional tapi Disarankan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi Streamlit
```bash
streamlit run app.py
```
Buka browser di `http://localhost:8501`.

---

## 🛠️ Tech Stack
- **Framework:** Streamlit (Python)
- **Data & Algoritma:** Pandas, NumPy, Scikit-learn (KMeans, StandardScaler)
- **Desain & UI:** Custom CSS (Apple Design System, responsive Flexbox/Grid)
