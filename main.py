import streamlit as st
import kerf_hesaplama
import veritabani
import pandas as pd

st.title("Kerf ve Offset Hesaplama")

# Material combobox
material = st.selectbox("Material:", veritabani.material_tipleri_al())

# Current combobox
current_options = veritabani.current_degerleri_al(material)
if current_options:
    current = st.selectbox("Current:", current_options)
else:
    st.warning("Seçilen malzeme için Current değeri bulunamadı.")
    st.stop()  # Uygulamayı durdur

# Gases combobox
gases_options = veritabani.gases_degerleri_al(material, current)
if gases_options:
    gases = st.selectbox("Gases:", gases_options)
else:
    st.warning("Seçilen malzeme ve Current için Gases değeri bulunamadı.")
    st.stop()

# Thickness combobox
thickness_options = veritabani.thickness_degerleri_al(material, current, gases)
if thickness_options:
    thickness = st.selectbox("Thickness:", thickness_options)
else:
    st.warning("Seçilen malzeme, Current ve Gases için Thickness değeri bulunamadı.")
    st.stop()

# Hesaplama butonu
if st.button("Hesapla"):
    results = kerf_hesaplama.kerf_width_bul(material, current, gases, float(thickness))

     # Sonuçları DataFrame'e dönüştürme
    df = pd.DataFrame(results, columns=["Açı", "Top Offset", "Bottom Offset","Top Knife","Bottom Knife","Top Land","Bottom Land"])

    # Sonuçları tablo şeklinde gösterme (st.dataframe ile)
    st.subheader("Sonuçlar:")
    st.dataframe(df.style.format("{:.3f}"))  # Ondalık sayıları 3 basamağa formatla