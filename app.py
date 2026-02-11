import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. AYARLAR VE GÜVENLİK ---
st.set_page_config(page_title="CBAM HESAPLAYICI | Kurumsal Giriş", layout="wide")

# Veri saklama (Simüle edilmiş veritabanı)
if 'user_db' not in st.session_state:
    # Başlangıç için bir demo hesap ekleyelim
    st.session_state['user_db'] = {
        "admin": {"sifre": "admin123", "firma": "Merkez", "yetkili": "Yönetici"}
    }
if 'kayitli_datalar' not in st.session_state:
    st.session_state['kayitli_datalar'] = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'active_user' not in st.session_state:
    st.session_state['active_user'] = None
if 'tesisler' not in st.session_state:
    st.session_state['tesisler'] = []

AB_KARBON_FIYATI = 95.0 

def tr_fix(text):
    maps = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c"}
    for key, val in maps.items(): text = str(text).replace(key, val)
    return text

# --- 2. GİRİŞ VE KAYIT EKRANI ---
def login_signup_page():
    st.title("🛡️ CBAM HESAPLAYICI - Kurumsal Erişim")
    
    tab_login, tab_signup = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
    
    with tab_login:
        with st.form("login_form"):
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            login_btn = st.form_submit_button("Sisteme Giriş")
            
            if login_btn:
                if u_name in st.session_state['user_db'] and st.session_state['user_db'][u_name]['sifre'] == u_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['active_user'] = u_name
                    st.success("Giriş başarılı!")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")

    with tab_signup:
        st.info("Sisteme kayıt olarak tüm CBAM analiz araçlarını kullanabilirsiniz.")
        with st.form("signup_form"):
            new_u = st.text_input("Kullanıcı Adı Belirleyin*")
            new_p = st.text_input("Şifre Belirleyin*", type="password")
            f_ad = st.text_input("Firma Adı")
            f_sehir = st.text_input("Şehir")
            tel = st.text_input("Telefon")
            eposta = st.text_input("E-posta")
            
            signup_btn = st.form_submit_button("Kaydı Tamamla")
            
            if signup_btn:
                if new_u and new_p:
                    st.session_state['user_db'][new_u] = {
                        "sifre": new_p, "firma": f_ad, "sehir": f_sehir, 
                        "tel": tel, "eposta": eposta, "tarih": str(datetime.date.today())
                    }
                    st.success("Kayıt oluşturuldu! Şimdi giriş yapabilirsiniz.")
                else:
                    st.warning("Lütfen kullanıcı adı ve şifre giriniz.")

# --- 3. SEKTÖREL HESAPLAMA MOTORU ---
def render_sector_ui(sektor_adi, default_factor):
    st.subheader(f"{sektor_adi} Sektörü Analizi")
    c1, c2 = st.columns([1, 1])
    with c1:
        t_ad = st.text_input("Tesis/Hat Adı", key=sektor_adi+"_t")
        uretim = st.number_input("Üretim Miktarı (Ton)", min_value=0.0, key=sektor_adi+"_u")
        ef = st.number_input("Emisyon Yoğunluğu (tCO2/ton)", value=default_factor, key=sektor_adi+"_ef")
    with c2:
        toplam_co2 = uretim * ef
        maliyet = toplam_co2 * AB_KARBON_FIYATI
        st.metric("Hesaplanan Emisyon", f"{toplam_co2:,.2f} tCO2")
        st.metric("Tahmini CBAM Maliyeti", f"€ {maliyet:,.2f}")
        if st.button("Analizi Kaydet", key=sektor_adi+"_b"):
            st.session_state['tesisler'].append({
                "Kullanıcı": st.session_state['active_user'],
                "Sektör": sektor_adi, "Tesis": t_ad, "Emisyon": toplam_co2, "Maliyet": maliyet
            })
            st.toast("Veri kaydedildi.")

# --- 4. ANA DASHBOARD ---
def main_dashboard():
    u = st.session_state['active_user']
    user_data = st.session_state['user_db'][u]
    
    st.sidebar.title("CBAM PORTAL")
    st.sidebar.write(f"**Yetkili:** {u}")
    st.sidebar.write(f"**Firma:** {user_data['firma']}")
    
    if st.sidebar.button("🔴 Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.rerun()

    # AB Sektörleri
    tabs = st.tabs(["🏗️ Demir-Çelik", "⚪ Alüminyum", "🌱 Gübre", "🧱 Çimento", "⚡ Elektrik", "💧 Hidrojen", "⚙️ Admin"])

    with tabs[0]: render_sector_ui("Demir-Çelik", 1.9)
    with tabs[1]: render_sector_ui("Alüminyum", 4.2)
    with tabs[2]: render_sector_ui("Gübre", 2.1)
    with tabs[3]: render_sector_ui("Çimento", 0.9)
    with tabs[4]: render_sector_ui("Elektrik", 0.45)
    with tabs[5]: render_sector_ui("Hidrojen", 0.0)
    
    with tabs[6]:
        st.header("🔑 Yönetici Paneli")
        st.write("Sisteme kayıtlı kurumsal kullanıcıların listesi aşağıdadır.")
        admin_df = pd.DataFrame(st.session_state['user_db']).T
        st.dataframe(admin_df.drop(columns=["sifre"])) # Güvenlik için şifreyi gizle

# --- SAYFA AKIŞI ---
if not st.session_state['logged_in']:
    login_signup_page()
else:
    main_dashboard()


