import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. KOLUM STYLE TASARIM (CSS) ---
st.set_page_config(page_title="CBAM Analiz | Kolum Entegre", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .css-154489f { background-color: #1a1a1a; } /* Sidebar rengi */
    div.stButton > button:first-child { background-color: #000000; color: white; border-radius: 6px; border: none; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #1a1a1a; }
    </style>
    """, unsafe_allow_html=True)

# Veri Yapısı
if 'user_db' not in st.session_state: st.session_state['user_db'] = {}
if 'tesisler' not in st.session_state: st.session_state['tesisler'] = []
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- 2. AUTH (KAYIT & GİRİŞ) ---
def auth_module():
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2092/2092712.png", width=80)
        st.title("CBAM COMPLIANCE")
        st.write("Kolum standartlarında emisyon takibi ve raporlama.")
        
    with col2:
        mode = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"], horizontal=True)
        with st.form("auth"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if mode == "Kayıt Ol":
                firma = st.text_input("Şirket Unvanı")
                tel = st.text_input("İletişim")
            
            if st.form_submit_button("Devam Et"):
                if mode == "Kayıt Ol":
                    st.session_state['user_db'][u] = {"p": p, "firma": firma, "tel": tel}
                    st.success("Hesap oluşturuldu! Giriş yapın.")
                else:
                    if u in st.session_state['user_db'] and st.session_state['user_db'][u]['p'] == p:
                        st.session_state['logged_in'] = True
                        st.session_state['active_user'] = u
                        st.rerun()
                    else: st.error("Hatalı bilgiler.")

# --- 3. ANA DASHBOARD (KOLUM ENTEGRE) ---
def main_dashboard():
    u_info = st.session_state['user_db'][st.session_state['active_user']]
    
    # Sidebar
    st.sidebar.title("KOLUM | CBAM")
    st.sidebar.write(f"🏢 **{u_info['firma']}**")
    st.sidebar.markdown("---")
    choice = st.sidebar.selectbox("Navigasyon", ["Genel Bakış", "Tesis Ekle", "Hesaplama Araçları", "Raporlarım"])
    
    if st.sidebar.button("🔴 Oturumu Kapat"):
        st.session_state['logged_in'] = False
        st.rerun()

    if choice == "Genel Bakış":
        st.header("Sektörel Karbon Portföyü")
        if not st.session_state['tesisler']:
            st.info("Henüz veri girilmemiş. Tesis ekleyerek başlayın.")
        else:
            df = pd.DataFrame(st.session_state['tesisler'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Emisyon (tCO2)", f"{df['Emisyon'].sum():,.2f}")
            c2.metric("Tahmini Maliyet", f"€ {df['Maliyet'].sum():,.2f}")
            c3.metric("Tesis Sayısı", len(df))
            st.bar_chart(df.set_index("Tesis")["Emisyon"])

    elif choice == "Tesis Ekle":
        st.header("Yeni Kaynak Tanımlama")
        c1, c2 = st.columns([1.5, 1])
        with c1:
            m = folium.Map(location=[39.0, 35.0], zoom_start=6)
            res = st_folium(m, height=400, width=650)
        with c2:
            t_name = st.text_input("Tesis Adı")
            sektor = st.selectbox("Sektör", ["Demir-Çelik", "Alüminyum", "Çimento", "Gübre"])
            uretim = st.number_input("Yıllık Üretim (Ton)", min_value=1.0)
            yogunluk = st.number_input("Emisyon Yoğunluğu (tCO2/ton)", value=1.85)
            
            if st.button("Sisteme İşle"):
                emisyon = uretim * yogunluk
                st.session_state['tesisler'].append({
                    "Tesis": t_name, "Sektör": sektor, "Emisyon": emisyon, "Maliyet": emisyon * 90.0
                })
                st.toast("Veri Kolum standartlarında işlendi!")

# --- SAYFA AKIŞI ---
if not st.session_state['logged_in']: auth_module()
else: main_dashboard()



