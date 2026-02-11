import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from fpdf import FPDF
import datetime

# --- AB STANDARTLARI VE KATSAYILAR ---
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

# --- PDF RAPORLAMA SINIFI ---
class SMK_Report(FPDF):
    def header(self):
        # Üst Kurumsal Bant
        self.set_fill_color(20, 40, 65) # SMK Laciverti
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 15, "SMK YATIRIM | STRATEJIK ANALIZ BIRIMI", ln=True, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, "CBAM (SKDM) Karbon Risk Projeksiyon Raporu", ln=True, align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Rapor Tarihi: {datetime.datetime.now().strftime('%d/%m/%Y')} | smkyatirim.com", align="L")
        self.cell(0, 10, f"Sayfa {self.page_no()}", align="R")

def create_pdf(veriler):
    pdf = SMK_Report()
    pdf.add_page()
    pdf.set_text_color(40, 40, 40)
   
    # Firma Bilgileri
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "KURUMSAL PROFIL", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Analiz Edilen Firma: {veriler['firma']}", ln=True)
    pdf.cell(0, 7, f"Sektor: {veriler['sektor']}", ln=True)
    pdf.ln(5)

    # Analiz Sonuçları Tablosu
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 10, "Parametre", 1, 0, "L", True)
    pdf.cell(90, 10, "Deger", 1, 1, "L", True)
   
    pdf.set_font("Arial", "", 10)
    sonuclar = [
        ("Uretim Miktari", f"{veriler['prod']} Ton"),
        ("Kullanilan Yakit", veriler['fuel_type']),
        ("Toplam Emisyon (Kapsam 1+2)", f"{veriler['total_co2']:.2f} tCO2"),
        ("Karbon Yogunlugu", f"{veriler['intensity']:.2f} tCO2/Ton"),
        ("Tahmini CBAM Vergi Yuklu (Yillik)", f"EUR {veriler['cost']:.2f}")
    ]
   
    for p, v in sonuclar:
        pdf.cell(100, 10, p, 1)
        pdf.cell(90, 10, v, 1, 1)
   
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "STRATEJIK TAVSIYE", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, "AB Sinirda Karbon Duzenleme Mekanizmasi (CBAM) kapsaminda hesaplanan maliyet yuksek risk grubundadir. Enerji verimliligi yatirimlari ve yenilenebilir enerji sertifikalari ile bu maliyetin %30'a kadar dusurulmesi mumkundur. Detayli yol haritasi icin SMK YATIRIM danismanlariyla iletisime geciniz.")
   
    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- ANA UYGULAMA ---
st.set_page_config(page_title="SMK YATIRIM | Analytics", layout="wide")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    st.sidebar.title("🏢 SMK YATIRIM")
    st.sidebar.caption("Sürdürülebilirlik Portalı")
    st.sidebar.divider()
   
    choice = st.sidebar.radio("Menü", ["Giriş Yap", "Ücretsiz Kayıt Ol"])

    if choice == "Ücretsiz Kayıt Ol":
        st.title("📝 Kayıt ve Erişim Paneli")
        with st.form("kayit"):
            c1, c2 = st.columns(2)
            with c1:
                email = st.text_input("E-posta")
                firma = st.text_input("Firma Adı")
            with c2:
                tel = st.text_input("Telefon")
                sektor = st.selectbox("Sektör", list(AB_FACTORS["Sektör"].keys()))
           
            if st.form_submit_button("Analiz Sistemini Aktif Et"):
                requests.post("https://formspree.io/f/xreaepjw", json={"Firma": firma, "Email": email, "Tel": tel})
                st.success("Kaydınız SMK sistemine iletildi. Giriş yapabilirsiniz.")

    elif choice == "Giriş Yap":
        st.title("🔐 Üye Girişi")
        user = st.sidebar.text_input("E-posta")
        pwd = st.sidebar.text_input("Şifre", type='password')
        if st.sidebar.button("Giriş"):
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = {"email": user}
            st.rerun()

    if st.session_state['logged_in']:
        st.title("🛡️ Stratejik Karbon Dashboard")
       
        with st.container():
            col_v1, col_v2, col_v3 = st.columns(3)
            prod = col_v1.number_input("Üretim (Ton)", value=1000)
            f_type = col_v2.selectbox("Yakıt Tipi", list(AB_FACTORS["Yakıt"].keys()))
            f_amt = col_v3.number_input("Tüketim Miktarı", value=500)
            elec = st.number_input("Elektrik (kWh)", value=150000)

        # Hesaplama
        f_emi = f_amt * AB_FACTORS["Yakıt"][f_type]
        e_emi = (elec * 0.45) / 1000
        total_co2 = f_emi + e_emi
        cost = total_co2 * 85
        intensity = total_co2 / prod

        # Metrikler
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Emisyon", f"{total_co2:,.1f} tCO2")
        m2.metric("CBAM Maliyeti", f"€ {cost:,.0f}")
        m3.metric("Yoğunluk Skoru", f"{intensity:,.2f}")

        # Görseller
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(values=[f_emi, e_emi], names=['Kapsam 1', 'Kapsam 2'],
                             hole=0.4, color_discrete_sequence=['#142841', '#FFC000'])
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            st.info("### 📥 Profesyonel Rapor Hazırla")
            st.write("Verileriniz SMK YATIRIM standartlarında resmi PDF raporuna dönüştürülür.")
           
            report_data = {
                "firma": "Değerli Paydaşımız",
                "sektor": "Endüstriyel Üretim",
                "prod": prod,
                "fuel_type": f_type,
                "total_co2": total_co2,
                "intensity": intensity,
                "cost": cost
            }
           
            if st.button("📄 PDF Raporu Oluştur"):
                pdf_bytes = create_pdf(report_data)
                st.download_button("📥 Raporu İndir", data=pdf_bytes, file_name="SMK_Karbon_Analiz.pdf", mime="application/pdf")

        if st.sidebar.button("🔴 Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == '__main__':
    main()
