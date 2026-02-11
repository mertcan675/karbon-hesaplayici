
              import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="CBAM HESAPLAYICI | Kurumsal Portal", layout="wide")

# Kurumsal Stil Dokunuşu (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    h1 { color: #004a99; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Session State Yönetimi
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing' # 'landing', 'signup', 'dashboard'
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'tesisler' not in st.session_state:
    st.session_state['tesisler'] = []

def tr_fix(text):
    maps = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c"}
    for key, val in maps.items(): text = str(text).replace(key, val)
    return text

# --- 2. PROFESYONEL PDF SINIFI ---
class CBAM_PDF(FPDF):
    def add_header(self, firma):
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 74, 153)
        self.cell(0, 15, tr_fix(f"CBAM STRATEJIK ANALIZ RAPORU"), ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.set_text_color(100)
        self.cell(0, 5, tr_fix(f"Kurulus: {firma}"), ln=True, align="C")
        self.cell(0, 5, tr_fix("Olusturan: CBAM Hesaplayici AI Servisi"), ln=True, align="C")
        self.ln(10)

# --- 3. SAYFA YÖNETİMİ ---

# A. GİRİŞ (LANDING) SAYFASI
if st.session_state['page'] == 'landing':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://www.eubusiness.com/news-eu/carbon-border.219/image_preview", width=200) # Temsili CBAM Logosu
        st.title("CBAM HESAPLAYICI")
        st.subheader("Sınırda Karbon Düzenleme Mekanizması Analiz Platformu")
        st.write("Avrupa Birliği standartlarında karbon yükümlülüklerinizi hesaplayın, tesislerinizi yönetin ve profesyonel raporlar oluşturun.")
        
        if st.button("Hemen Başlayın (Ücretsiz Kayıt)"):
            st.session_state['page'] = 'signup'
            st.rerun()

# B. ÜYELİK (SIGNUP) SAYFASI
elif st.session_state['page'] == 'signup':
    st.title("🏦 Kurumsal Kayıt Paneli")
    st.write("Lütfen analiz raporlarında yer alacak kurumsal bilgileri eksiksiz doldurunuz.")
    
    with st.form("signup_form"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            firma = st.text_input("Şirket Tam Unvanı*")
            vergi_no = st.text_input("Vergi Numarası / VAT ID")
            sektor = st.selectbox("Ana Faaliyet Sektörü", ["Demir-Çelik", "Çimento", "Alüminyum", "Gübre", "Elektrik", "Hidrojen"])
        with col_s2:
            yetkili = st.text_input("Yetkili Ad Soyad*")
            eposta = st.text_input("Kurumsal E-posta Adresi*")
            ulke = st.selectbox("Merkez Ülke", ["Türkiye", "Almanya", "İtalya", "Diğer"])
            
        submitted = st.form_submit_button("Hesabı Oluştur ve Analize Başla")
        if submitted:
            if firma and yetkili and eposta:
                st.session_state['user_info'] = {"firma": firma, "yetkili": yetkili, "sektor": sektor}
                st.session_state['page'] = 'dashboard'
                st.rerun()
            else:
                st.error("Lütfen yıldızlı (*) alanları doldurun.")

# C. ANA DASHBOARD
elif st.session_state['page'] == 'dashboard':
    st.sidebar.title("CBAM AI Portal")
    st.sidebar.info(f"Firma: {st.session_state['user_info']['firma']}\n\nYetkili: {st.session_state['user_info']['yetkili']}")
    
    if st.sidebar.button("🔴 Oturumu Kapat"):
        st.session_state['page'] = 'landing'
        st.session_state['tesisler'] = []
        st.rerun()

    tab1, tab2 = st.tabs(["📍 Tesis Yönetimi & Harita", "📊 Portföy ve Raporlama"])

    with tab1:
        st.subheader("Yeni Tesis Tanımlama")
        col_h, col_d = st.columns([2, 1])
        
        with col_h:
            m = folium.Map(location=[39.0, 35.0], zoom_start=6)
            m.add_child(folium.LatLngPopup())
            harita_verisi = st_folium(m, height=450, width=750)
            lat = harita_verisi['last_clicked']['lat'] if harita_verisi['last_clicked'] else 39.0
            lng = harita_verisi['last_clicked']['lng'] if harita_verisi['last_clicked'] else 35.0

        with col_d:
            t_adi = st.text_input("Tesis Adı")
            t_emisyon = st.number_input("Yıllık Emisyon (tCO2e)", min_value=0)
            t_verim = st.slider("Enerji Verimlilik Skoru (%)", 0, 100, 50)
            
            if st.button("Tesisi Kaydet"):
                st.session_state['tesisler'].append({
                    "Tesis": t_adi, "Emisyon": t_emisyon, "Verim": t_verim, "Lat": lat, "Lng": lng
                })
                st.success(f"{t_adi} sisteme eklendi.")

    with tab2:
        if not st.session_state['tesisler']:
            st.warning("Görüntülenecek tesis verisi bulunamadı.")
        else:
            df = pd.DataFrame(st.session_state['tesisler'])
            st.dataframe(df, use_container_width=True)
            
            # Grafiksel İyileştirme
            st.bar_chart(df.set_index("Tesis")["Emisyon"])
            
            if st.button("📄 Kurumsal PDF Raporu İndir"):
                pdf = CBAM_PDF()
                pdf.add_page()
                pdf.add_header(st.session_state['user_info']['firma'])
                
                # Tablo tasarımı
                pdf.set_fill_color(0, 74, 153)
                pdf.set_text_color(255)
                pdf.cell(60, 10, "Tesis", 1, 0, 'C', True)
                pdf.cell(60, 10, "Emisyon (tCO2e)", 1, 0, 'C', True)
                pdf.cell(60, 10, "Verimlilik", 1, 1, 'C', True)
                
                pdf.set_text_color(0)
                for t in st.session_state['tesisler']:
                    pdf.cell(60, 10, tr_fix(t['Tesis']), 1)
                    pdf.cell(60, 10, f"{t['Emisyon']:,}", 1, 0, 'C')
                    pdf.cell(60, 10, f"%{t['Verim']}", 1, 1, 'C')
                
                pdf_out = pdf.output(dest="S").encode("latin-1", "ignore")
                st.download_button("📥 Raporu İndir", pdf_out, "CBAM_Stratejik_Rapor.pdf")



