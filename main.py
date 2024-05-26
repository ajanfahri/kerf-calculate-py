import streamlit as st
import kerf_hesaplama
import veritabani
import pandas as pd

st.title("Kerf ve Offset Hesaplama")

# Otomatik değer seçimi
material = "MildStell"  # Varsayılan malzeme
current = 200  # Varsayılan akım
gases = "O2/AIR"
thickness = 20  # Varsayılan kalınlık

# Material combobox (disabled)
st.selectbox("Material:", veritabani.material_tipleri_al(), index=veritabani.material_tipleri_al().index(material), disabled=True)

# Current combobox (disabled)
current_options = veritabani.current_degerleri_al(material)
if current_options:
    st.selectbox("Current:", current_options, index=current_options.index(current), disabled=True)
else:
    st.warning("Seçilen malzeme için Current değeri bulunamadı.")
    st.stop()

# Gases combobox (disabled)
gases_options = veritabani.gases_degerleri_al(material, current)
if gases_options:
    gases = st.selectbox("Gases:", gases_options, disabled=True)  # Otomatik seçim
else:
    st.warning("Seçilen malzeme ve Current için Gases değeri bulunamadı.")
    st.stop()

# Thickness combobox (disabled)
thickness_options = veritabani.thickness_degerleri_al(material, current, gases)
if thickness_options:
    st.selectbox("Thickness:", thickness_options, index=thickness_options.index(thickness), disabled=True)
else:
    st.warning("Seçilen malzeme, Current ve Gases için Thickness değeri bulunamadı.")
    st.stop()




# Hesaplama butonu
if st.button("Hesapla"):
    results = kerf_hesaplama.kerf_width_bul(material, current, gases, float(thickness))

     # Sonuçları DataFrame'e dönüştürme
    df = pd.DataFrame(results, columns=["Thickness","Angle","Feedrate", "Top Offset", "Bottom Offset","Top Knife","Bottom Knife","Top Land","Bottom Land","Kerf Width"])

    # Negatif açılar için yeni satırlar oluştur
    negative_angle_results = []
    for row in results:
        thickness, angle, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth = row
        negative_angle_results.append([thickness, -angle, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth])

    negative_angle_df = pd.DataFrame(negative_angle_results, columns=df.columns)


    # Sıfır açı için kerf değerlerini ekleyelim
    zero_angle_row = df.iloc[0].copy()  # İlk satırı kopyalayalım
    zero_angle_row["Angle"] = 0
    zero_angle_row[["Top Knife", "Bottom Knife", "Top Land", "Bottom Land"]] = results[0][9]  # Kerf değerini ata
    df = pd.concat([df, pd.DataFrame([zero_angle_row])], ignore_index=True)

    # DataFrameleri birleştir
    df = pd.concat([negative_angle_df, pd.DataFrame([zero_angle_row]), df], ignore_index=True)

    # Açıları -45'ten 45'e sıralayalım
    df["Angle"] = df["Angle"].astype(int)  # Angle sütununu int'e dönüştür
    df = df.sort_values(by="Angle", ascending=True)


   # Feedrate sütunlarını integer olarak formatlama
    format_dict = {
            "Thickness": "{:d}",
            "Angle": "{:d}",
    "Feedrate": "{:d}",
    "Top Offset": "{:.3f}",
    "Bottom Offset": "{:.3f}",
    "Top Knife": "{:.3f}",
    "Bottom Knife": "{:.3f}",
    "Top Land": "{:.3f}",
    "Bottom Land": "{:.3f}",
    "Kerf Width": "{:.3f}"
    }
    styled_df = df.style.format(format_dict)

    # Sonuçları tablo şeklinde gösterme (st.dataframe ile)
    st.subheader("Sonuçlar:")
    st.dataframe(styled_df.data)  # Ondalık sayıları 3 basamağa formatla
    #st.dataframe(df.style.format("{:.3f}"))  # Ondalık sayıları 3 basamağa formatla

    # Dosya oluşturma ve indirme
    def create_and_download_file(df):
        satir_sablonu = "10 :\t\t\t{},\t\t\t{},\t\t\t{},\t\t\t260,\t\t\t150,\t\t{},\t\t\t{:.3f},\t\t\t{:.3f},\t\t\t{:.3f},\t\t\t{:.3f},\t\tLEADTABLE,\t\tLINE2OPEN,\t\t30,\t\t\t8,\t\t\t8,\t\t\t4,\t\t\t4,\t\t\t4,\t\t\t4,\t\t\t,\tLINEOPEN,\t\t\t8,\tLINEOPEN,\t\t\t8,\t\t\t,\tNONE,\t\t\t0,\t\t\t0,\t\t\t,\t\t\t,\t\t\t0,\t\t\t0,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\tVERIFIED,\t\t\t0,\t\t\t-1,\t\t\t0,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,"

        with open('kerf_offset_sonuclari.txt', 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                formatted_row = satir_sablonu.format(
                    int(row["Thickness"]),
                    int(row["Angle"]),
                    int(row["Angle"]),
                    int(row["Feedrate"]),
                    row["Top Knife"], row["Bottom Knife"], row["Top Land"], row["Bottom Land"])
                f.write(formatted_row + "\n")

        with open('kerf_offset_sonuclari.txt', 'rb') as f:  # Dosyayı binary modda aç
            bytes_data = f.read()

        st.download_button(
            label="Sonuçları İndir",
            data=bytes_data,
            file_name='kerf_offset_sonuclari.txt',
            mime='text/plain',
        )

    create_and_download_file(df)


