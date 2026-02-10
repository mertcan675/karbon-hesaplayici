import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="SMK YATIRIM | Karbon Portalı", layout="wide", page_icon="🛡️")

# --- SMK KURUMSAL PDF SINIFI ---
class SMK_Report(FPDF):
    def header(self):
        self.set_fill_color(20, 40, 65)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 18)
        self.cell(0, 20, "SMK YATIRIM - STRATEJIK ANALIZ RAPORU", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "SMK YATIRIM © 2026 - Gizli ve Stratejik Analiz Belgesidir.", align="C")

# --- ANA PROGRAM ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    st.sidebar.markdown("<h1 style='color: #142841; text-align: center;'>SMK YATIRIM</h1>", unsafe_content_allowed=True)
    st.sidebar.markdown("<p style='text-align: center;'>Stratejik Karbon Yönetimi</p>", unsafe_content_allowed=True)
   
    menu = ["Giriş Yap", "Ücretsiz Kayıt Ol"]
    choice = st.sidebar.selectbox("Hesap Paneli", menu)

    # --- 1. ÜCRETSİZ KAYIT EKRANI ---
    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 SMK Portalı'na Ücretsiz Kayıt")
        st.info("Sisteme erişmek için kurumsal profilinizi oluşturun. Verileriniz SMK veri merkezinde güvenle saklanır.")
       
        with st.form("kayit_formu"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Kurumsal E-posta (Kullanıcı Adı)")
                sifre = st.text_input("Şifre Belirleyin", type='password')
                firma_adi = st.text_input("Firma Tam Adı")
                telefon = st.text_input("Telefon (GSM)")
            with col2:
                sektor = st.selectbox("Sektör", ["Demir-Çelik", "Alüminyum", "Gübre", "Çimento", "Hidrojen", "Diğer"])
                departman = st.selectbox("Departmanınız", ["Sürdürülebilirlik", "Dış Ticaret", "Finans", "Yönetim", "Üretim"])
                konum = st.text_input("Tesis Konumu (İl/İlçe)")
           
            adres = st.text_area("Firma Adresi")
            st.warning("Kaydolarak SMK YATIRIM veri işleme ve gizlilik politikasını kabul etmiş sayılırsınız.")
           
            submit = st.form_submit_button("Hesabı Oluştur ve Verileri Onayla")

            if submit:
                # FORMSPREE BAĞLANTISI BURADA
                formspree_url = "https://formspree.io/f/xreaepjw"
               
                kayit_verileri = {
                    "Mesaj_Tipi": "Yeni Kurumsal Kayit",
                    "Firma_Adi": firma_adi,
                    "E_Posta": email,
                    "Telefon": telefon,
                    "Sektor": sektor,
                    "Departman": departman,
                    "Konum": konum,
                    "Adres": adres
                }
               
                try:
                    resp = requests.post(formspree_url, json=kayit_verileri)
                    if resp.status_code == 200:
                        st.success("Kaydınız başarıyla SMK YATIRIM sistemine iletildi. Artık giriş yapabilirsiniz.")
                        st.balloons()
                    else:
                        st.error("Formspree bağlantı hatası. Lütfen linki kontrol edin.")
                except Exception as e:
                    st.error(f"Sistem Hatası: {e}")

    # --- 2. GİRİŞ EKRANI ---
    elif choice == "Giriş Yap":
        st.title("🔐 Kurumsal Giriş")
        user = st.text_input("E-posta")
        pwd = st.text_input("Şifre", type='password')
       
        if st.button("Sisteme Eriş"):
            if user and pwd:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = user
                st.rerun()
            else:
                st.error("Lütfen bilgileri eksiksiz girin.")

    # --- 3. ANALİZ PANELİ (GİRİŞ YAPILINCA) ---
    if st.session_state['logged_in']:
        st.sidebar.success(f"Aktif Kullanıcı: {st.session_state['user_email']}")
        st.title("🛡️ SMK Analiz Paneli")
       
        st.sidebar.header("📊 Üretim Verileri")
        uretim_ton = st.sidebar.number_input("Yıllık Üretim (Ton)", value=1000)
        kapsam1 = st.sidebar.slider("Kapsam 1 (tCO2/Ton)", 0.0, 10.0, 1.9)
        elektrik_kwh = st.sidebar.number_input("Elektrik Tüketimi (kWh/Ton)", value=450)
       
        toplam_co2 = (uretim_ton * kapsam1) + (uretim_ton * elektrik_kwh * 0.45 / 1000)
        maliyet = toplam_co2 * 85
       
        c1, c2 = st.columns(2)
        c1.metric("Toplam Karbon Yükü", f"{toplam_co2:,.2f} tCO2")
        c2.metric("CBAM Maliyet Riski", f"€ {maliyet:,.2f}")
       
        st.divider()

        st.subheader("📈 Maliyet Projeksiyonu")
        yillar = [2026, 2028, 2030, 2032, 2034]
        vergi_yukselis = [maliyet * oran for oran in [0.025, 0.1, 0.485, 0.735, 1.0]]
        st.line_chart(pd.DataFrame({"Yıl": yillar, "Tahmini Vergi": vergi_yukselis}).set_index("Yıl"))

        if st.sidebar.button("🔴 Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == '__main__':
    main()

