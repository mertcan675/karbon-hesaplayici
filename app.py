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

# --- ANA PROGRAM ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # HATA BURADAYDI - DÜZELTİLDİ
    st.sidebar.markdown("<h1 style='color: #142841; text-align: center;'>SMK YATIRIM</h1>", unsafe_content_allowed=True)
    st.sidebar.markdown("<p style='text-align: center;'>Stratejik Karbon Yönetimi</p>", unsafe_content_allowed=True)
   
    menu = ["Giriş Yap", "Ücretsiz Kayıt Ol"]
    choice = st.sidebar.selectbox("Hesap Paneli", menu)

    # --- 1. ÜCRETSİZ KAYIT EKRANI ---
    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 SMK Portalı'na Ücretsiz Kayıt")
        st.info("Sisteme erişmek için kurumsal profilinizi oluşturun.")
       
        with st.form("kayit_formu"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Kurumsal E-posta")
                sifre = st.text_input("Şifre", type='password')
                firma_adi = st.text_input("Firma Tam Adı")
            with col2:
                sektor = st.selectbox("Sektör", ["Demir-Çelik", "Alüminyum", "Gübre", "Çimento", "Hidrojen", "Diğer"])
                telefon = st.text_input("Telefon")
                konum = st.text_input("Tesis Konumu")
           
            submit = st.form_submit_button("Hesabı Oluştur")

            if submit:
                # BURAYA KENDİ FORMSPREE LİNKİNİ YAPIŞTIR
                formspree_url = "https://formspree.io/f/xreaepjw"
               
                kayit_verileri = {
                    "Firma": firma_adi,
                    "Eposta": email,
                    "Sektor": sektor,
                    "Telefon": telefon
                }
               
                try:
                    resp = requests.post(formspree_url, json=kayit_verileri)
                    if resp.status_code == 200:
                        st.success("Kaydınız SMK sistemine iletildi!")
                        st.balloons()
                except:
                    st.error("Bağlantı hatası!")

    # --- 2. GİRİŞ VE ANALİZ ---
    elif choice == "Giriş Yap":
        user = st.sidebar.text_input("E-posta")
        pwd = st.sidebar.text_input("Şifre", type='password')
        if st.sidebar.button("Giriş"):
            st.session_state['logged_in'] = True
            st.rerun()

    if st.session_state['logged_in']:
        st.title("🛡️ SMK Analiz Paneli")
        uretim = st.sidebar.number_input("Yıllık Üretim (Ton)", value=1000)
        maliyet = uretim * 85 # Basit hesap
        st.metric("Tahmini CBAM Riski", f"€ {maliyet:,.2f}")

if __name__ == '__main__':
    main()


