import streamlit as st

st.set_page_config(page_title="CNC Sihirbazı v1.9.3", layout="centered")
st.title("CNC Dairesel Fırça Tabanı Sihirbazı v1.9.3")
st.caption("-Made by Arapali-")

# 1. Operasyon Seçimleri
st.subheader("Operasyon Seçimi")
col1, col2, col3 = st.columns(3)
ops = {
    "yuzey": col1.checkbox("Yüzey", True),
    "fatura": col2.checkbox("Fatura", True),
    "delik": col3.checkbox("Delik", True)
}

# 2. Makine Ayarları
st.subheader("Makine Ayarları")
col1, col2 = st.columns(2)
s_devir = col1.number_input("Spindle Devri (S)", value=12000)
feed = col2.number_input("İlerleme (F)", value=800)

# 3. Parametreler
st.subheader("Geometri & Detaylar")
with st.expander("Parametreleri Düzenle"):
    dis_cap = st.number_input("Dış Çap (mm)", value=100.0)
    h_mevcut = st.number_input("Ham Kalınlık (mm)", value=20.0)
    h_hedef = st.number_input("Hedef Kalınlık (mm)", value=18.0)
    freze_cap = st.number_input("Freze Çapı (mm)", value=6.0)
    
    f_cap = st.number_input("Fatura Çapı (mm)", value=60.0)
    f_der = st.number_input("Fatura Derinliği (mm)", value=2.0)
    f_tip = st.selectbox("Fatura Tipi", [(-1, "İç (Pocket)"), (1, "Dış (Boss)")])[0]
    
    delik_cap = st.number_input("Delik Çapı (mm)", value=10.0)
    delik_der = st.number_input("Delik Derinliği (mm)", value=5.0)
    boydan_boya = st.checkbox("Boydan Boya Del (Ham Kalınlık Kadar)")
    pcd = st.number_input("Dizilim (PCD)", value=80.0)
    d_sayisi = st.number_input("Delik Sayısı", value=6)
    
    end_x = st.number_input("Bitiş X (mm)", value=0.0)
    end_z = st.number_input("Bitiş Z (mm)", value=50.0)

# G-Code Üretme Mantığı
if st.button("G-Code Üret ve İndir"):
    target_depth = -(h_mevcut - h_hedef)
    curr_a = 0.0
    g = ["; --- CNC G-CODE v1.9.3 (Web/Mobile Optimized) ---", "G21", "G90", f"M3 S{int(s_devir)}", "G0 Z50.00"]
    
    # Yüzey
    if ops["yuzey"]:
        start_x = (dis_cap / 2) + (freze_cap / 2)
        g.append(f"\n; YUZEY\nG0 X{start_x:.2f} A{curr_a:.2f}\nG1 Z{target_depth:.2f} F{feed}")
        while start_x >= 0:
            curr_a = 360.0 if curr_a == 0.0 else 0.0
            g.append(f"G1 X{start_x:.2f} A{curr_a:.2f}")
            start_x -= (freze_cap * 0.7)
            
    # Fatura
    if ops["fatura"]:
        g.append(f"\n; FATURA\nG0 Z{2.0:.2f}")
        f_z = target_depth - abs(f_der)
        r = (f_cap/2) + (f_tip*(freze_cap/2)) if f_tip == 1 else (f_cap/2)-(freze_cap/2)
        limit = ((dis_cap/2)+10) if f_tip == 1 else 0
        g.append(f"G0 X{r:.2f} A{curr_a:.2f}\nG1 Z{f_z:.2f} F{feed}")
        while (r <= limit) if f_tip == 1 else (r >= 0):
            curr_a = 360.0 if curr_a == 0.0 else 0.0
            g.append(f"G1 X{r:.2f} A{curr_a:.2f}")
            r += (freze_cap*0.7) if f_tip == 1 else -(freze_cap*0.7)
            
    # Delik
    if ops["delik"]:
        g.append("\n; DELIK")
        z_baslangic = target_depth - abs(f_der) if pcd < f_cap else 0.0
        d_derinlik = h_mevcut if boydan_boya else abs(delik_der)
        
        for i in range(int(d_sayisi)):
            angle = i * (360.0 / d_sayisi)
            g.append(f"G0 X{pcd/2:.2f} A{angle:.2f}")
            curr_z = z_baslangic
            final_z = z_baslangic - d_derinlik
            while curr_z > final_z:
                curr_z = max(curr_z - 2.0, final_z)
                g.append(f"G1 Z{curr_z:.2f} F{feed/2}\nG0 Z{z_baslangic+0.5:.2f} F{feed}")
            g.append(f"G0 Z{z_baslangic+5.0:.2f}")

    g.append(f"\n; BITIS\nG0 Z{end_z:.2f}\nG0 X{end_x:.2f}\nM5\nM30")
    
    g_code_str = "\n".join(g)
    st.success("G-Code başarıyla üretildi!")
    st.download_button("Dosyayı İndir (.nc)", g_code_str, file_name="program.nc", mime="text/plain")