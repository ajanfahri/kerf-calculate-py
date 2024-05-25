import streamlit as st
import kerf_hesaplama
import veritabani

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

    # Sonuçları tablo şeklinde gösterme
    st.subheader("Sonuçlar:")
    if results:
        st.write(
            f"""
            | Açı | Top Offset | Bottom Offset |
            |---|---|---|
            """
        )
        for aci, top_offset, bottom_offset in results:
            if top_offset is not None and bottom_offset is not None:
                st.write(f"| {aci} | {top_offset:.3f} | {bottom_offset:.3f} |")
            else:
                st.write(f"| {aci} | Veri Yok | Veri Yok |")
    else:
        st.write("Belirtilen değerlere uygun kayıt bulunamadı.")
