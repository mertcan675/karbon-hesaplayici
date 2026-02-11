import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# --- AB STANDARTLARI VERİLERİ ---
AB_FACTORS = {
    "Yakıt": {
        "Doğalgaz (MWh)": 0.202,
        "Linyit Kömürü (Ton)": 1.012,
        "İthal Kömür (Ton)": 2.420,
        "Motorin (Litre)": 0.00268,
        "Fuel-Oil (Ton)": 3.120
    },
    "Sektör": {
        "Demir-Çelik": 1.9, "Alüminyum": 4.5, "Çimento": 0.9, "Gübre": 2.1, "Hidrojen": 11.0
    }
}

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="SMK YATIRIM | Premium Analytics", layout="wide")

# --- ANA PROGRAM ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Sol Panel - Görsel Hatalar Düzeltildi
    st.sidebar.title("🏢 SMK YATIRIM")
    st.sidebar.caption("STRATEJİK KARBON ANALİZ PORTALI")
    st.sidebar.divider()
   
    choice = st.sidebar.radio("Ana Menü", ["Giriş Yap", "Ücretsiz Kayıt Ol"])

    # --- 1. KAYIT EKRANI ---
    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 Kurumsal Kayıt Paneli")
        with st.form("kayit_formu"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Kurumsal E-posta")
                firma = st.text_input("Firma Tam Adı")
                tel = st.text_input("İletişim Numarası")
            with col2:
                sektor = st.selectbox("Faaliyet Sektörü", list(AB_FACTORS["Sektör"].keys()))
                konum = st.text_input("Tesis Konumu (Şehir)")
                sifre = st.text_input("Şifre Belirleyin", type='password')
           
            if st.form_submit_button("Hesabı Oluştur"):
                # Formspree Bağlantısı (Senin ID'n aktif)
                requests.post("https://formspree.io/f/xreaepjw",
                             json={"Firma": firma, "Email": email, "Tel": tel, "Sektor": sektor, "Konum": konum})
                st.success("Kaydınız başarıyla SMK veri merkezine iletildi. Şimdi giriş yapabilirsiniz.")

    # --- 2. GİRİŞ EKRANI ---
    elif choice == "Giriş Yap":
        st.title("🔐 Üye Girişi")
        user = st.sidebar.text_input("Kullanıcı Adı (E-posta)")
        pwd = st.sidebar.text_input("Şifre", type='password')
        if st.sidebar.button("Sisteme Eriş"):
            st.session_state['logged_in'] = True
            st.rerun()

    # --- 3. ANALİZ PANELİ (GİRİŞ YAPILINCA) ---
    if st.session_state['logged_in']:
        st.title("🛡️ Stratejik Karbon Dashboard")
       
        # Veri Giriş Alanı
        with st.container():
            st.subheader("⚙️ Operasyonel Veriler")
            v1, v2, v3, v4 = st.columns(4)
            prod = v1.number_input("Üretim (Ton)", min_value=1, value=1000)
            f_type = v2.selectbox("Yakıt Tipi", list(AB_FACTORS["Yakıt"].keys()))
            f_amt = v3.number_input("Yakıt Tüketimi", min_value=1, value=500)
            elec = v4.number_input("Elektrik (kWh)", min_value=1, value=150000)

        # Profesyonel Hesaplama
        fuel_emi = f_amt * AB_FACTORS["Yakıt"][f_type]
        elec_emi = (elec * 0.45) / 1000 # TR Ortalama Faktörü
        total_co2 = fuel_emi + elec_emi
        cost = total_co2 * 85 # Varsayılan ETS Fiyatı

        # --- GÖRSEL METRİKLER ---
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Emisyon", f"{total_co2:,.1f} tCO2")
        m2.metric("CBAM Maliyet Riski", f"€ {cost:,.0f}")
        m3.metric("Birim Yoğunluk", f"{total_co2/prod:,.2f} tCO2/Ton")

        # --- ETKİLEŞİMLİ GRAFİKLER ---
        st.divider()
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("### 🎯 Kaynak Dağılımı")
            fig_pie = px.pie(
                values=[fuel_emi, elec_emi],
                names=['Yakıt (Kapsam 1)', 'Elektrik (Kapsam 2)'],
                hole=0.4,
                color_discrete_sequence=['#142841', '#FFC000']
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with g2:
            st.markdown("### 📈 Vergi Yükü Projeksiyonu")
            years = [2026, 2028, 2030, 2032, 2034]
            tax_vals = [cost * r for r in [0.025, 0.1, 0.48, 0.75, 1.0]]
            fig_area = px.area(x=years, y=tax_vals, labels={'x':'Yıl', 'y':'Maliyet (€)'})
            fig_area.update_traces(line_color='#142841')
            st.plotly_chart(fig_area, use_container_width=True)

        if st.sidebar.button("🔴 Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == '__main__':
    main()


