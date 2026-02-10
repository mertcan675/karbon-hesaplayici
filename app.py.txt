import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="CBAM Analiz ve Danışmanlık Portalı", layout="wide", page_icon="🌍")

# --- PDF OLUŞTURMA FONKSİYONU ---
def generate_pdf(veriler):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "CBAM (SKDM) STRATEJIK ANALIZ RAPORU", ln=True, align="C")
    pdf.ln(10)
   
    pdf.set_font("Arial", "", 12)
    for key, value in veriler.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(90, 10, f"{key}:", border=1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(90, 10, f"{str(value)}", border=1, ln=1)
   
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 10, "Bu rapor varsayilan degerler baz alinarak hazirlanmistir. Resmi beyanname oncesi profesyonel destek alinmasi tavsiye edilir.")
   
    # PDF'i binary formatta döndür (Latin-1 hatasını önlemek için karakter temizliği yapılmıştır)
    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- ANA BAŞLIK ---
st.title("🌍 CBAM (SKDM) Karbon Maliyet Analiz Sistemi")
st.markdown("""
Bu araç, Avrupa Birliği'nin **Sınırda Karbon Düzenleme Mekanizması (CBAM)** kapsamında oluşacak mali yükünüzü hesaplar ve stratejik rapor sunar.
""")

# --- YAN PANEL (GİRDİLER) ---
st.sidebar.header("📊 Üretim ve Emisyon Verileri")
sektor = st.sidebar.selectbox("Sektörünüzü Seçin", ["Demir-Çelik", "Alüminyum", "Gübre", "Çimento", "Hidrojen"])
miktar = st.sidebar.number_input("Yıllık Üretim Miktarı (Ton)", min_value=1.0, value=1000.0)

st.sidebar.subheader("🌱 Emisyon Yoğunluğu")
s1_faktor = st.sidebar.slider("Kapsam 1 (Doğrudan Üretim) - tCO2/Ton", 0.0, 10.0, 1.9)
elektrik_tuketimi = st.sidebar.number_input("Ton Başına Elektrik Tüketimi (kWh/Ton)", value=450)
sebeke_faktoru = st.sidebar.slider("Ülke Şebeke Emisyon Faktörü (kgCO2/kWh)", 0.0, 1.2, 0.45)

st.sidebar.subheader("💰 Finansal Parametreler")
ets_fiyati = st.sidebar.number_input("Güncel AB Karbon Fiyatı (€/Ton)", value=85.0)
yerel_vergi_odendi = st.sidebar.checkbox("Yerel Karbon Vergisi Ödüyorum")
yerel_fiyat = 0.0
if yerel_vergi_odendi:
    yerel_fiyat = st.sidebar.number_input("Ödenen Yerel Karbon Fiyatı (€/Ton)", value=20.0)

# --- HESAPLAMA MANTIĞI ---
s1_toplam = miktar * s1_faktor
s2_toplam = (miktar * elektrik_tuketimi * sebeke_faktoru) / 1000
toplam_co2 = s1_toplam + s2_toplam
fiyat_farki = max(0, ets_fiyati - yerel_fiyat)
net_maliyet = toplam_co2 * fiyat_farki
tasarruf = toplam_co2 * yerel_fiyat if yerel_vergi_odendi else 0

# --- SONUÇ ÖZET KARTLARI ---
st.subheader("📌 Analiz Özeti")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Toplam Karbon Ayak İzi", f"{toplam_co2:,.2f} tCO2")
col2.metric("Brüt CBAM Maliyeti", f"€ {toplam_co2 * ets_fiyati:,.2f}")
col3.metric("Yerel Vergi Mahsubu", f"€ {tasarruf:,.2f}")
col4.metric("Ödenecek Net Tutar", f"€ {net_maliyet:,.2f}", delta="-€ "+f"{tasarruf:,.0f}" if yerel_vergi_odendi else None)

st.divider()

# --- GRAFİKLER ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📋 Emisyon Kaynakları")
    fig1, ax1 = plt.subplots()
    ax1.pie([s1_toplam, s2_toplam], labels=['Kapsam 1', 'Kapsam 2'], autopct='%1.1f%%', colors=['#E63946', '#457B9D'], startangle=140)
    st.pyplot(fig1)

with c2:
    st.subheader("📈 2026-2034 Maliyet Artış Senaryosu")
    takvim = {2026: 0.025, 2028: 0.10, 2030: 0.485, 2032: 0.735, 2034: 1.0}
    yillar = list(takvim.keys())
    maliyetler = [net_maliyet * oran for oran in takvim.values()]
    df_grafik = pd.DataFrame({"Yıl": yillar, "Maliyet (€)": maliyetler})
    st.line_chart(df_grafik.set_index("Yıl"))

# --- PDF VE İLETİŞİM ---
st.divider()
st.subheader("📥 Profesyonel Hizmet Alın")

col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown("**1. Raporunuzu İndirin**")
    rapor_data = {
        "Sektor": sektor,
        "Uretim Miktari": f"{miktar:,.0f} Ton",
        "Kapsam 1 Emisyonu": f"{s1_toplam:,.2f} tCO2",
        "Kapsam 2 Emisyonu": f"{s2_toplam:,.2f} tCO2",
        "Net Birim Karbon Maliyeti": f"{fiyat_farki} EUR/t",
        "Tahmini Toplam Ödeme": f"{net_maliyet:,.2f} EUR"
    }
   
    if st.button("📄 PDF Raporu Oluştur ve İndir"):
        try:
            pdf_bytes = generate_pdf(rapor_data)
            st.download_button(label="📥 Dosyayı Bilgisayara Kaydet", data=pdf_bytes, file_name="CBAM_Analiz_Raporu.pdf", mime="application/pdf")
        except:
            st.error("Rapor oluşturulurken bir hata oluştu. Lütfen teknik destek alın.")

with col_res2:
    st.markdown("**2. Uzman Desteği ve Teklif Alın**")
    # BURAYA KENDI FORMSPREE LINKINI YAZACAKSIN
    FORMSPREE_URL = "https://formspree.io/f/KENDI_KODUNU_BURAYA_YAZ"
   
    with st.expander("📩 Teklif Formunu Aç"):
        with st.form("contact_form"):
            isim = st.text_input("Ad Soyad / Firma")
            email = st.text_input("E-posta")
            msj = st.text_area("İhtiyacınız olan detaylar")
            submit = st.form_submit_button("Teklifi Gönder")
           
            if submit:
                if isim and email:
                    # Gerçek e-posta gönderimi için:
                    # requests.post(FORMSPREE_URL, json={"isim": isim, "email": email, "mesaj": msj})
                    st.success(f"Teşekkürler {isim}, talebiniz başarıyla iletildi!")
                else:
                    st.error("Lütfen tüm alanları doldurun.")

st.caption("© 2026 CBAM Maliyet Analiz Aracı - Tüm hakları saklıdır.")
