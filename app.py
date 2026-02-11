import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- TÜRKÇE KARAKTER DÖNÜŞTÜRÜCÜ ---
def tr_fix(text):
    maps = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c"}
    for key, val in maps.items():
        text = str(text).replace(key, val)
    return text

# --- PROFESYONEL RAPOR SINIFI ---
class SMK_Report(FPDF):
    def header(self):
        # Kurumsal Üst Bant
        self.set_fill_color(10, 30, 60) # Koyu Lacivert
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, tr_fix("SMK YATIRIM | YESIL DONUSUM ANALIZI"), ln=True, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, tr_fix("SKDM Risk ve GES Yatirim Fizibilite Raporu"), ln=True, align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        tarih = datetime.datetime.now().strftime('%d/%m/%Y')
        self.cell(0, 10, f"Rapor Tarihi: {tarih} | Sayfa {self.page_no()}", align="C")

def generate_pdf(veriler):
    pdf = SMK_Report()
    pdf.add_page()
    
    # --- 1. KURUMSAL ÖZET ---
    pdf.set_text_color(20, 40, 80)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, tr_fix("1. ANALIZ OZETI"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    # Bilgi Kutusu
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(95, 8, tr_fix(f"Analiz Edilen Firma: {veriler['firma']}"), 0, 0, 'L', True)
    pdf.cell(95, 8, tr_fix(f"Sektor: {veriler['sektor']}"), 0, 1, 'L', True)
    pdf.ln(5)

    # --- 2. KARBON VE VERGI TABLOSU ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, tr_fix("2. KARBON AYAK IZI VE VERGI PROJEKSIYONU"), ln=True)
    
    # Tablo Başlıkları
    pdf.set_fill_color(10, 30, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, "Parametre", 1, 0, 'C', True)
    pdf.cell(90, 10, "Deger", 1, 1, 'C', True)
    
    # Tablo İçeriği
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    data = [
        ("Yillik Toplam Emisyon", f"{veriler['total_co2']:.2f} tCO2"),
        ("GES Kaynakli Karbon Tasarrufu", f"{veriler['co2_saved']:.2f} tCO2"),
        ("SKDM Karbon Vergisi (Yillik)", f"EUR {veriler['tax']:.2f}"),
        ("GES Vergi Avantaji", f"EUR {veriler['tax_saving']:.2f}"),
        ("Yatirim Geri Donus Suresi (ROI)", f"{veriler['roi']:.1f} Yil")
    ]
    
    for row in data:
        pdf.cell(100, 10, tr_fix(row[0]), 1)
        pdf.cell(90, 10, tr_fix(row[1]), 1, 1, 'C')

    # --- 3. STRATEJIK TAVSIYELER ---
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(0, 10, tr_fix("3. STRATEJIK YOL HARITASI"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    tavsiye = (
        f"Yapilan analiz sonucunda, GES yatirimi ile karbon yoğunluğunun %{veriler['reduction_pct']:.1f} oraninda "
        f"dusurulebilecegi gorulmektedir. Mevcut karbon fiyati olan EUR {veriler['c_price']} baz alindiginda, "
        f"yatirimin yillik toplam ekonomik katkisi EUR {veriler['total_gain']:.2f} seviyesindedir. "
        "AB SKDM mevzuati geregi, bu sertifikalandirilmis tasarruf ihracat maliyetlerinizi dogrudan dusurecektir."
    )
    pdf.multi_cell(0, 7, tr_fix(tavsiye))
    
    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- STREAMLIT ARAYÜZÜ (HESAPLAMA DAHİL) ---
st.set_page_config(page_title="SMK YATIRIM", layout="centered")
st.title("🛡️ Profesyonel Karbon Raporlama")

with st.expander("📊 Tesis ve Yatırım Verilerini Girin", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        firma = st.text_input("Firma Adı", "SMK Tekstil A.Ş.")
        sektor = st.selectbox("Sektör", ["Demir-Çelik", "Alüminyum", "Tekstil", "Gübre"])
        elec = st.number_input("Yıllık Elektrik (kWh)", value=500000)
    with c2:
        ges_yield = st.number_input("Yıllık GES Üretimi (kWh)", value=200000)
        ges_cost = st.number_input("GES Yatırım Bedeli (€)", value=120000)
        c_price = st.slider("Karbon Fiyatı (€/Ton)", 60, 150, 85)

# Hesaplamalar
e_emi = (elec * 0.45) / 1000
co2_saved = (ges_yield * 0.45) / 1000
net_co2 = e_emi - co2_saved
tax = net_co2 * c_price
tax_saving = co2_saved * c_price
total_gain = tax_saving + (ges_yield * 0.15) # Enerji tasarrufu dahil
roi = ges_cost / total_gain if total_gain > 0 else 0

st.divider()

# Rapor Hazırlama Verisi
report_payload = {
    "firma": firma, "sektor": sektor, "total_co2": net_co2, 
    "co2_saved": co2_saved, "tax": tax, "tax_saving": tax_saving,
    "roi": roi, "reduction_pct": (co2_saved/e_emi)*100, 
    "total_gain": total_gain, "c_price": c_price
}

if st.button("📄 PROFESYONEL PDF RAPORU OLUSTUR"):
    pdf_out = generate_pdf(report_payload)
    st.download_button(
        label="📥 Raporu İndir (PDF)",
        data=pdf_out,
        file_name=f"SMK_Analiz_{firma}.pdf",
        mime="application/pdf"
    )
    st.success("Rapor başarıyla oluşturuldu!")
