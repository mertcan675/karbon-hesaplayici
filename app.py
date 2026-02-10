import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# --- AB STANDARTLARI VE GÖRSEL TEMA ---
AB_STANDARDS = {
    "Yakıt Tipleri": {
        "Doğalgaz (MWh)": 0.202,
        "Linyit Kömürü (Ton)": 1.012,
        "İthal Kömür (Ton)": 2.420,
        "Motorin (Litre)": 0.00268,
        "Fuel-Oil (Ton)": 3.120
    },
    "Sektörel Katsayılar": {
        "Demir-Çelik": 1.9, "Alüminyum": 4.5, "Çimento": 0.9, "Gübre": 2.1, "Hidrojen": 11.0
    }
}

st.set_page_config(page_title="SMK YATIRIM | Premium Analytics", layout="wide")

# --- CUSTOM CSS (Daha şık görünüm için) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #142841; color: white; }
    </style>
    """, unsafe_content_allowed=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Sol Panel
    st.sidebar.markdown(f"<h1 style='text-align: center; color: #142841;'>SMK YATIRIM</h1>", unsafe_content_allowed=True)
    st.sidebar.markdown("<p style='text-align: center; font-size: 0.8em;'>STRATEJİK ANALİZ PORTALI</p>", unsafe_content_allowed=True)
    st.sidebar.divider()
   
    choice = st.sidebar.radio("Menü", ["Giriş Yap", "Ücretsiz Kayıt Ol"])

    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 Kurumsal Kayıt Paneli")
        with st.container():
            with st.form("kayit"):
                c1, c2 = st.columns(2)
                with c1:
                    email = st.text_input("E-posta")
                    firma = st.text_input("Firma Adı")
                with c2:
                    tel = st.text_input("Telefon")
                    sektor = st.selectbox("Sektör", list(AB_STANDARDS["Sektörel Katsayılar"].keys()))
               
                if st.form_submit_button("Kayıt Ol ve Analizi Başlat"):
                    requests.post("https://formspree.io/f/xreaepjw", json={"Firma": firma, "Email": email, "Tel": tel})
                    st.success("Kaydınız alındı. Giriş sekmesine geçebilirsiniz.")

    elif choice == "Giriş Yap":
        st.title("🔐 Üye Portalı")
        user = st.sidebar.text_input("Kullanıcı")
        pwd = st.sidebar.text_input("Şifre", type='password')
        if st.sidebar.button("Sisteme Eriş"):
            st.session_state['logged_in'] = True
            st.rerun()

    if st.session_state['logged_in']:
        st.title("🛡️ Stratejik Karbon Dashboard")
       
        # Üst Veri Girişi
        with st.expander("⚙️ Veri Giriş Parametreleri", expanded=True):
            v1, v2, v3, v4 = st.columns(4)
            prod = v1.number_input("Yıllık Üretim (Ton)", value=1000)
            fuel_t = v2.selectbox("Yakıt Tipi", list(AB_STANDARDS["Yakıt Tipleri"].keys()))
            fuel_a = v3.number_input("Yakıt Miktarı", value=500)
            elec = v4.number_input("Elektrik (kWh)", value=150000)

        # Hesaplamalar
        fuel_emi = fuel_a * AB_STANDARDS["Yakıt Tipleri"][fuel_t]
        elec_emi = (elec * 0.45) / 1000
        total_co2 = fuel_emi + elec_emi
        cost = total_co2 * 85

        # --- GÖRSEL KARTLAR ---
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Emisyon", f"{total_co2:,.1f} tCO2")
        m2.metric("CBAM Vergi Riski", f"€ {cost:,.0f}")
        m3.metric("Karbon Yoğunluğu", f"{total_co2/prod:,.2f}")
        m4.metric("ETS Tahmini", "€ 85.00", "+5.2%")

        # --- PROFESYONEL GRAFİKLER ---
        st.divider()
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("### 🎯 Emisyon Kaynakları")
            fig_pie = px.pie(
                values=[fuel_emi, elec_emi],
                names=['Yakıt (Kapsam 1)', 'Elektrik (Kapsam 2)'],
                hole=0.4,
                color_discrete_sequence=['#142841', '#FFC000']
            )
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with g2:
            st.markdown("### 📈 2026-2034 Maliyet Projeksiyonu")
            years = [2026, 2028, 2030, 2032, 2034]
            costs = [cost * r for r in [0.025, 0.1, 0.485, 0.75, 1.0]]
            fig_line = px.area(x=years, y=costs, labels={'x':'Yıl', 'y':'Maliyet (€)'})
            fig_line.update_traces(line_color='#142841', fillcolor='rgba(20, 40, 65, 0.2)')
            st.plotly_chart(fig_line, use_container_width=True)

        if st.sidebar.button("🔴 Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == '__main__':
    main()

