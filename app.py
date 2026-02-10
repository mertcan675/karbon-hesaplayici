import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="SMK YATIRIM | Karbon Portalı", layout="wide")

# --- ANA PROGRAM ---
def main():
    # Oturum Yönetimi (Giriş yapılıp yapılmadığını kontrol eder)
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Yan Menü Tasarımı
    st.sidebar.title("🏢 SMK YATIRIM")
    st.sidebar.write("Stratejik Karbon Yönetimi")
    st.sidebar.divider()
   
    menu = ["Giriş Yap", "Ücretsiz Kayıt Ol"]
    choice = st.sidebar.selectbox("Hesap Paneli", menu)

    # --- 1. ÜCRETSİZ KAYIT EKRANI (VERİ TOPLAMA) ---
    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 SMK Portalı'na Ücretsiz Kayıt")
        st.write("Analiz sistemine erişmek için kurumsal profilinizi oluşturun.")
       
        with st.form("kayit_formu"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Kurumsal E-posta")
                sifre = st.text_input("Şifre Belirleyin", type='password')
                firma_adi = st.text_input("Firma Tam Adı")
            with col2:
                telefon = st.text_input("Telefon Numarası")
                sektor = st.selectbox("Sektör", ["Demir-Çelik", "Alüminyum", "Gübre", "Çimento", "Hidrojen", "Diğer"])
                konum = st.text_input("Tesis Konumu (İl/İlçe)")
           
            submit = st.form_submit_button("Hesabı Oluştur ve Kaydet")

            if submit:
                # FORMSPREE BAĞLANTISI (Senin Kodunla)
                formspree_url = "https://formspree.io/f/xreaepjw"
               
                veriler = {
                    "Firma_Adi": firma_adi,
                    "E_Posta": email,
                    "Telefon": telefon,
                    "Sektor": sektor,
                    "Konum": konum
                }
               
                try:
                    resp = requests.post(formspree_url, json=veriler)
                    if resp.status_code == 200:
                        st.success("Bilgileriniz SMK YATIRIM veri merkezine iletildi! Şimdi 'Giriş Yap' sekmesinden devam edebilirsiniz.")
                        st.balloons()
                    else:
                        st.error("Bir hata oluştu, lütfen tekrar deneyin.")
                except:
                    st.error("Bağlantı sağlanamadı.")

    # --- 2. GİRİŞ EKRANI ---
    elif choice == "Giriş Yap":
        st.title("🔐 Kurumsal Giriş")
        user = st.sidebar.text_input("E-posta")
        pwd = st.sidebar.text_input("Şifre", type='password')
       
        if st.sidebar.button("Sisteme Giriş"):
            if user and pwd:
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Lütfen e-posta ve şifrenizi girin.")

    # --- 3. ANALİZ PANELİ (GİRİŞ YAPILDIKTAN SONRA) ---
    if st.session_state['logged_in']:
        st.title("🛡️ SMK Analiz Paneli")
        st.subheader("Karbon Risk Projeksiyonu")
       
        # Veri Girişi
        st.sidebar.header("📊 Üretim Verileri")
        uretim = st.sidebar.number_input("Yıllık Üretim (Ton)", value=1000)
       
        # Basit CBAM Hesabı
        emisyon = uretim * 2.5 # Varsayılan katsayı
        maliyet = emisyon * 85  # 85 Euro ETS fiyatı
       
        # Sonuç Kartları
        c1, c2 = st.columns(2)
        c1.metric("Tahmini Karbon Yükü", f"{emisyon:,.2f} tCO2")
        c2.metric("CBAM Maliyet Riski", f"€ {maliyet:,.2f}")
       
        # Grafik
        st.write("**Maliyet Artış Senaryosu (2026-2034)**")
        yillar = [2026, 2030, 2034]
        degerler = [maliyet * 0.025, maliget * 0.485, maliyet]
        st.line_chart(pd.DataFrame({"Yıl": yillar, "Maliyet": degerler}).set_index("Yıl"))
       
        if st.sidebar.button("🔴 Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == '__main__':
    main()
