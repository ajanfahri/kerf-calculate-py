import streamlit as st
import kerf_hesaplama
import veritabani
import pandas as pd

st.title("Kerf ve Offset Hesaplama")

# Otomatik değer seçimi (başlangıç değerleri)
material = "MildStell"
current = 200
gases = "O2/AIR"
thickness = 20

st.subheader("Kerf Tipi Seçimi")
kerf_tipi = st.radio("Kerf Tipi:", ["Ajan Cam Kerf", "Dos-Cartesian Kerf","Düzenlenmiş Kerfler"], key="kerf_tipi_radio")  # Key eklemeyi unutma

# Material combobox
material_options = veritabani.material_tipleri_al()
material = st.selectbox("Material:", material_options, index=material_options.index(material), key="material_selectbox")

# Current combobox
current_options = veritabani.current_degerleri_al(material)
if current_options:
    current = st.selectbox("Current:", current_options, index=current_options.index(current), key="current_selectbox")
else:
    st.warning("Seçilen malzeme için Current değeri bulunamadı.")
    st.stop()

# Gases combobox
gases_options = veritabani.gases_degerleri_al(material, current)
if gases_options:
    gases = st.selectbox("Gases:", gases_options, key="gases_selectbox")
else:
    st.warning("Seçilen malzeme ve Current için Gases değeri bulunamadı.")
    st.stop()

# Thickness combobox
thickness_options = veritabani.thickness_degerleri_al(material, current, gases)
if thickness_options:
    thickness = st.selectbox("Thickness:", thickness_options, index=thickness_options.index(thickness), key="thickness_selectbox")
else:
    st.warning("Seçilen malzeme, Current ve Gases için Thickness değeri bulunamadı.")
    st.stop()


# Hesaplama butonu
if st.button("Hesapla"):
    # Seçilen değerleri al (combobox'ların güncel değerleri)
    material = st.session_state.material_selectbox
    current = st.session_state.current_selectbox
    gases = st.session_state.gases_selectbox
    thickness = st.session_state.thickness_selectbox
    kerf_tipi = st.session_state.kerf_tipi_radio

    results = kerf_hesaplama.kerf_width_bul(material, current, gases,float(thickness),kerf_tipi)
    ilk_kayit=1
    baslik_yaz=1
     # Sonuçları DataFrame'e dönüştürme
    df = pd.DataFrame(results, columns=["Thickness","Angle","Current","Feedrate", "Top Offset", "Bottom Offset","Top Knife","Bottom Knife","Top Land","Bottom Land","Kerf Width","Material"])
    st.write(results[0][2])
    # Negatif açılar için yeni satırlar oluştur
    negative_angle_results = []
    for row in results:
        thickness, angle,current, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth,material = row
        negative_angle_results.append([thickness, -angle,current, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth,material])

    negative_angle_df = pd.DataFrame(negative_angle_results, columns=df.columns)


    # Sıfır açı için kerf değerlerini ekleyelim
    zero_angle_row = df.iloc[0].copy()  # İlk satırı kopyalayalım
    zero_angle_row["Angle"] = 0
    zero_angle_row[["Top Knife", "Bottom Knife", "Top Land", "Bottom Land"]] = results[0][9]  # Kerf değerini ata
    df = pd.concat([df, pd.DataFrame([zero_angle_row])], ignore_index=True)

    # DataFrameleri birleştir
    df = pd.concat([negative_angle_df,  df], ignore_index=True)

    # Açıları -45'ten 45'e sıralayalım
    df["Angle"] = df["Angle"].astype(int)  # Angle sütununu int'e dönüştür
    df = df.sort_values(by="Angle", ascending=True)

    #df.drop(columns=["Material", "Kerf Width"], inplace=True)
   # Feedrate sütunlarını integer olarak formatlama
    format_dict = {
            "Thickness": "{:d}",
            "Angle": "{:d}",
            "Current": "{:d}",
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
    bytes_data=kerf_hesaplama.create_and_download_file(df, results, baslik_yaz,ilk_kayit)
    st.write(thickness)
    st.download_button(
        label=f"Sonuçları İndir ({thickness}mm)",  # Dosya adına kalınlık bilgisi ekle
        data=bytes_data,
        file_name=f'kerf_offset_sonuclari_{thickness}mm.txt',  # Dosya adına kalınlık bilgisi ekle
        mime='text/plain',
    )
        
    

# MildStell 200 Amper Kerf Hesapla butonu
if st.button("MildStell Tüm Kerfleri Hesapla"):
    material = "MildStell"
    current = 200
    gases = "O2/AIR"

    amper_degerleri = [130, 200, 260]  # Hesaplama yapılacak amper değerleri
    ilk_kayit=1
    for current in amper_degerleri:
        thickness_options = veritabani.thickness_degerleri_al(material, current, gases)  # Kalınlıkları amper değerine göre al
        baslik_yaz=1
        all_results = []
        for thickness in thickness_options:
            if 7 < thickness <= 26:  # 0'dan büyük ve 25'e eşit veya küçük kalınlıklar için hesapla
                results = kerf_hesaplama.kerf_width_bul(material, current, gases, float(thickness),kerf_tipi)
                # Sonuçları DataFrame'e dönüştürme
                df = pd.DataFrame(results, columns=["Thickness","Angle","Current","Feedrate", "Top Offset", "Bottom Offset","Top Knife","Bottom Knife","Top Land","Bottom Land","Kerf Width","Material"])

                # Negatif açılar için yeni satırlar oluştur
                negative_angle_results = []
                for row in results:
                    thickness, angle,current, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth,material = row
                    negative_angle_results.append([thickness, -angle,current, feedrate, top_offset, bottom_offset, top_knife, bottom_knife, top_land, bottom_land,kerfwidth,material])

                negative_angle_df = pd.DataFrame(negative_angle_results, columns=df.columns)


                # Sıfır açı için kerf değerlerini ekleyelim
                zero_angle_row = df.iloc[0].copy()  # İlk satırı kopyalayalım
                zero_angle_row["Angle"] = 0
                zero_angle_row[["Top Knife", "Bottom Knife", "Top Land", "Bottom Land"]] = (results[0][10])/2  # Kerf değerini ata
                df = pd.concat([df, pd.DataFrame([zero_angle_row])], ignore_index=True)

                # DataFrameleri birleştir
                df = pd.concat([negative_angle_df, df], ignore_index=True)

                # Açıları -45'ten 45'e sıralayalım
                df["Angle"] = df["Angle"].astype(int)  # Angle sütununu int'e dönüştür
                df = df.sort_values(by="Angle", ascending=True)
                
                
                df.drop(columns=["Material", "Kerf Width"], inplace=True)

                all_results.append(df)  # Sıralanmış DataFrame'i all_results listesine ekle

        #st.write(all_results)
        # Tüm DataFrame'leri birleştir
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Feedrate sütunlarını integer olarak formatlama
        format_dict = {
                "Thickness": "{:d}",
                "Angle": "{:d}",
                "Current": "{:d}",
                "Feedrate": "{:d}",
                "Top Offset": "{:.3f}",
                "Bottom Offset": "{:.3f}",
                "Top Knife": "{:.3f}",
                "Bottom Knife": "{:.3f}",
                "Top Land": "{:.3f}",
                "Bottom Land": "{:.3f}",
                "Kerf Width": "{:.3f}"
            }
        styled_df = final_df.style.format(format_dict)

    
        # ... (Mevcut kodundaki diğer işlemler - negatif açılar, sıfır açı, sıralama)

        # Sonuçları tablo şeklinde gösterme
        st.subheader(f"MildStell {current} Amper - Tüm Kalınlıklar Sonuçlar:")
        st.dataframe(styled_df.data)

            # Dosya oluşturma ve indirme
        bytes_data = kerf_hesaplama.create_and_download_file(final_df, results, baslik_yaz,ilk_kayit)  # Fonksiyonu tüm sonuçlarla çağır   
        ilk_kayit=0
        baslik_yaz=0
    st.download_button(
                #label=f"Sonuçları İndir ({thickness}mm)",  # Dosya adına kalınlık bilgisi ekle
                label=f"Ajan_Precision_Plasma_Bevel_MM.TEC",  # Dosya adına kalınlık bilgisi ekle
                data=bytes_data,
                #file_name=f'kerf_offset_sonuclari_{thickness}mm.txt',  # Dosya adına kalınlık bilgisi ekle
                file_name='Ajan_Precision_Plasma_Bevel_MM.TEC',  # Dosya adına kalınlık bilgisi ekle
                mime='text/plain',
            )