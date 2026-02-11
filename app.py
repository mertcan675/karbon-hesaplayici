import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. AYARLAR VE VERİ SETLERİ ---
st.set_page_config(page_title="CBAM HESAPLAYICI | Yakıt ve Enerji Analizi", layout="wide")

# Yakıtların Karbon Emisyon Faktörleri (kg CO2 / birim)
# Kaynak: IPCC Standartları
YAKIT_FAKTORLERI = {
    "Doğalgaz (m³)": 1.90,
    "Linyit Kömürü (kg)": 1.10,
    "İthal Kömür (kg)": 2.40,
    "Motorin/Dizel (Litre)": 2.68,
    "Fuel Oil (Litre)": 2.95,
    "LPG (Litre)": 1.61
}

ENERJI_FAKTORLERI = {
    "Şebeke Elektriği (Türkiye Grid)": 0.45, # MWh başına ton CO2
    "Güneş Enerjisi (GES)": 0.0,
    "Rüzgar Enerjisi (RES)": 0.0,
    "Biyokütle": 0.05
}

AB_KARBON_FIYATI = 95.0 # Güncel EUR/ton tahmini

if 'page' not in st.session_state: st.session_state['page'] = 'dashboard'
if 'tesisler' not in st.session_state: st.session_state['tesisler'] = []

def tr_fix(text):
    maps = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c"}
    for key, val in maps.items(): text = str(text).replace(key, val)
    return text

# --- 2. ANA DASHBOARD ---
st.title("🛡️ CBAM HESAPLAYICI")
st.subheader("Yakıt ve Enerji Bazlı Karbon Maliyet Analizi")

tab1, tab2 = st.tabs(["🔥 Emisyon Kaynakları Girişi", "📊 Maliyet Analiz Raporu"])

with tab1:
    col_harita, col_input = st.columns([1, 1])
    
    with col_harita:
        st.write("### Tesis Konumu")
        m = folium.Map(location=[39.0, 35.0], zoom_start=6)
        harita = st_folium(m, height=400, width=600)
        lat = harita['last_clicked']['lat'] if harita['last_clicked'] else 39.0
        lng = harita['last_clicked']['lng'] if harita['last_clicked'] else 35.0

    with col_input:
        st.write("### Tesis ve Tüketim Verileri")
        t_ad = st.text_input("Tesis Adı", placeholder="Örn: Ankara Çelik Hattı")
        
        # Üretim Miktarı
        uretim = st.number_input("Yıllık Üretim Miktarı (Ton)", min_value=1)
        
        # Yakıt Tüketimi
        yakit_tipi = st.selectbox("Kullanılan Ana Yakıt Türü", list(YAKIT_FAKTORLERI.keys()))
        yakit_miktari = st.number_input(f"Yıllık {yakit_tipi} Miktarı", min_value=0.0)
        
        # Enerji Tüketimi
        enerji_tipi = st.selectbox("Elektrik Enerjisi Kaynağı", list(ENERJI_FAKTORLERI.keys()))
        enerji_miktari = st.number_input("Yıllık Elektrik Tüketimi (MWh)", min_value=0.0)

        # HESAPLAMA MOTORU
        dogrudan_emisyon = (yakit_miktari * YAKIT_FAKTORLERI[yakit_tipi]) / 1000 # tCO2'ye çevrim
        dolayli_emisyon = enerji_miktari * ENERJI_FAKTORLERI[enerji_tipi]
        toplam_emisyon = dogrudan_emisyon + dolayli_emisyon
        maliyet = toplam_emisyon * AB_KARBON_FIYATI
        
        if st.button("Verileri Kaydet ve Analiz Et"):
            if t_ad:
                st.session_state['tesisler'].append({
                    "Tesis": t_ad,
                    "Yakıt": yakit_tipi,
                    "Enerji": enerji_tipi,
                    "Emisyon (tCO2)": round(toplam_emisyon, 2),
                    "Maliyet (EUR)": round(maliyet, 2),
                    "Yoğunluk": round(toplam_emisyon / uretim, 3)
                })
                st.success("Analiz portföye eklendi.")

with tab2:
    if not st.session_state['tesisler']:
        st.warning("Henüz bir veri girişi yapılmadı.")
    else:
        df = pd.DataFrame(st.session_state['tesisler'])
        
        # Özet Tablo
        st.write("### Kurumsal Emisyon Envanteri")
        st.dataframe(df, use_container_width=True)
        
        # Metrikler
        c1, c2 = st.columns(2)
        toplam_maliyet = df["Maliyet (EUR)"].sum()
        c1.metric("Toplam Tahmini CBAM Vergisi", f"€ {toplam_maliyet:,.2f}")
        c2.metric("Ortalama Karbon Yoğunluğu", f"{df['Yoğunluk'].mean():,.2f} t/ton")
        
        # Görselleştirme
        st.write("### Tesis Bazlı Maliyet Dağılımı")
        st.bar_chart(df.set_index("Tesis")["Maliyet (EUR)"])

        # PDF Rapor Butonu
        if st.button("📄 Teknik Analiz Raporu İndir (PDF)"):
            st.info("Rapor oluşturma fonksiyonu hazır. (Gerekli kütüphaneler yüklü olmalıdır)")




