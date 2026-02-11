import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. AYARLAR ---
st.set_page_config(page_title="SMK YATIRIM | Karbon Portalı", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"firma": "", "logo_bytes": None, "tesisler": []}

def tr_fix(text):
    maps = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c"}
    for key, val in maps.items(): text = str(text).replace(key, val)
    return text

# --- 2. PROFESYONEL PDF SINIFI ---
class SMK_PDF(FPDF):
    def add_header(self, logo_bytes, firma_adi):
        if logo_bytes:
            with open("temp_logo.png", "wb") as f:
                f.write(logo_bytes)
            self.image("temp_logo.png", 10, 8, 30)
        
        self.set_font("Arial", "B", 14)
        self.set_text_color(20, 40, 65)
        self.cell(0, 10, tr_fix(f"{firma_adi} - STRATEJIK KARBON RAPORU"), ln=True, align="R")
        self.set_font("Arial", "I", 9)
        self.cell(0, 10, tr_fix("SMK YATIRIM Analiz Servisi"), ln=True, align="R")
        self.ln(20)

# --- 3. GİRİŞ EKRANI ---
if not st.session_state['logged_in']:
    st.title("🛡️ SMK Karbon Portalı - Giriş")
    col_a, col_b = st.columns(2)
    with col_a:
        f_ad = st.text_input("Şirketinizin Tam Adı")
        f_logo = st.file_uploader("Şirket Logonuzu Yükleyin (PNG/JPG)", type=['png', 'jpg'])
    with col_b:
        st.info("Bu panel üzerinden şirketinizin tüm tesislerini harita üzerinde işaretleyebilir ve AB uyumlu karbon raporu alabilirsiniz.")
        if st.button("Sistemi Başlat"):
            if f_ad:
                st.session_state['user_data']['firma'] = f_ad
                if f_logo:
                    st.session_state['user_data']['logo_bytes'] = f_logo.getvalue()
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Lütfen şirket adını giriniz.")

# --- 4. ANA DASHBOARD ---
else:
    st.sidebar.title(st.session_state['user_data']['firma'])
    if st.session_state['user_data']['logo_bytes']:
        st.sidebar.image(st.session_state['user_data']['logo_bytes'])
    
    if st.sidebar.button("🔴 Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.session_state['user_data']['tesisler'] = []
        st.rerun()

    tab1, tab2 = st.tabs(["📍 Tesis Ekle & Harita", "📊 Portföy ve Rapor"])

    with tab1:
        st.subheader("Haritadan Tesis Konumu Seçin")
        col_harita, col_detay = st.columns([2, 1])
        
        with col_harita:
            # Türkiye Haritası
            m = folium.Map(location=[39.0, 35.0], zoom_start=6)
            m.add_child(folium.LatLngPopup())
            harita_verisi = st_folium(m, height=400, width=700)
            
            lat = harita_verisi['last_clicked']['lat'] if harita_verisi['last_clicked'] else 39.0
            lng = harita_verisi['last_clicked']['lng'] if harita_verisi['last_clicked'] else 35.0
            st.success(f"Seçilen Konum: {lat:.4f}, {lng:.4f}")

        with col_detay:
            t_adi = st.text_input("Tesis Adı (Örn: İstanbul Fabrika)")
            t_emisyon = st.number_input("Yıllık Emisyon (Ton CO2)", min_value=0, value=1000)
            t_ges = st.selectbox("Güneş Enerjisi (GES)", ["Mevcut Değil", "Mevcut"])
            
            if st.button("Tesisi Listeye Ekle"):
                st.session_state['user_data']['tesisler'].append({
                    "Ad": t_adi, "Emisyon": t_emisyon, "GES": t_ges, "Lat": lat, "Lng": lng
                })
                st.toast("Tesis Kaydedildi!")

    with tab2:
        if not st.session_state['user_data']['tesisler']:
            st.warning("Henüz hiç tesis eklemediniz.")
        else:
            st.subheader("Tesis Portföyü")
            tesisler_df = pd.DataFrame(st.session_state['user_data']['tesisler'])
            st.table(tesisler_df)
            
            toplam_co2 = tesisler_df["Emisyon"].sum()
            st.metric("Tüm Tesislerin Toplam Emisyonu", f"{toplam_co2:,} tCO2")
            
            if st.button("📄 Profesyonel PDF Raporu Oluştur"):
                pdf = SMK_PDF()
                pdf.add_page()
                pdf.add_header(st.session_state['user_data']['logo_bytes'], st.session_state['user_data']['firma'])
                
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, tr_fix("KURUMSAL TESIS ANALIZI"), ln=True)
                pdf.ln(5)
                
                # Tablo Yapısı
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(60, 10, "Tesis Adi", 1, 0, 'C', True)
                pdf.cell(50, 10, "Emisyon (tCO2)", 1, 0, 'C', True)
                pdf.cell(80, 10, "Konum (Enlem/Boylam)", 1, 1, 'C', True)
                
                pdf.set_font("Arial", "", 10)
                for t in st.session_state['user_data']['tesisler']:
                    pdf.cell(60, 10, tr_fix(t['Ad']), 1)
                    pdf.cell(50, 10, f"{t['Emisyon']:,}", 1, 0, 'C')
                    pdf.cell(80, 10, f"{t['Lat']:.3f} / {t['Lng']:.3f}", 1, 1, 'C')
                
                pdf.ln(10)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 10, tr_fix(f"TOPLAM KARBON YUKU: {toplam_co2:,} tCO2"), ln=True)
                
                pdf_dosyasi = pdf.output(dest="S").encode("latin-1", "ignore")
                st.download_button("📥 PDF Raporunu Bilgisayara İndir", pdf_dosyasi, "SMK_Rapor.pdf", "application/pdf")
