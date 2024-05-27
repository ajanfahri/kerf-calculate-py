import math
import veritabani

# kerftipi 0 Ajan Cam
# kerftipi 1 Dos-Cartesia
#
#


def calculate_wdi(current, aci, kerf_tipi):
    """Verilen Current, Açı ve Kerf Tipi değerlerine göre CalculateWDI değerini hesaplar."""

    radyan = math.radians(aci)

    if kerf_tipi in [0, 3]:  # Cartesian Kerf
        if current == 200 or current == 260:
            if aci < 48:
                return math.cos(radyan) * 5.5 - math.sin(radyan) * 3.5
            else:
                return math.cos(radyan) * 17.72 - math.sin(radyan) * 14.46
        elif current == 130:
            if aci < 41.5:
                return math.cos(radyan) * 10 - math.sin(radyan) * 6
            else:
                return math.cos(radyan) * 17.15 - math.sin(radyan) * 14.1
    else:  # Ajan Cam Kerf
        if current == 260:
            if aci < 48:
                return math.cos(radyan) * 5.5 - math.sin(radyan) * 3.5
            else:
                return math.cos(radyan) * 17.72 - math.sin(radyan) * 14.46
        else:  # current 130 veya 200 ise
            if aci < 41.5:
                return math.cos(radyan) * 10 - math.sin(radyan) * 6
            else:
                return math.cos(radyan) * 17.15 - math.sin(radyan) * 14.1

    return None  # Geçerli değerler dışında None döndür
        

#def kerf_width_bul(material="MildStell", current=200, gases="O2/AIR", thickness=15, aci=25,kerf_tipi="Ajan Cam Kerf"):
def kerf_width_bul(material, current, gases, thickness, kerf_tipi):
    """Verilen değerlere göre KerfWidth, Top Angle Offset ve Bottom Angle Offset değerlerini bulan fonksiyon."""

    results = []
    result1 = None  # result1'i başlangıçta None olarak tanımla
    result2 = None
    result_top = None
    result_bottom = None
    bevel_wd = 3
    legal_kerfWidth = veritabani.kerf_width_bul_1(material, current, gases, thickness) 

    kerftipi=0
    
    if kerf_tipi == "Ajan Cam Kerf":
        # Ajan Cam Kerf için özel sorgu
        kerftipi = 1
    elif kerf_tipi == "Dos-Cartesian Kerf":
        # Dos-Cartesian Kerf için özel sorgu
        kerftipi = 0
    else:
        kerftipi = 3


    for aci in [5, 10, 15, 20, 25, 30, 35, 40, 45]:
            yeni_thickness_top    = thickness / math.cos(math.radians(aci))
            top_angle_offset=None
            radyan = math.radians(aci)
            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_top = calculate_wdi(current, aci,kerftipi)

            # SQL sorguları (iki ayrı sorgu)
            #cursor.execute(query2,                 (material, current, gases, yeni_thickness_top))
            result_top = veritabani.kerf_width_bul_2(material, current, gases, yeni_thickness_top)
            feedrate_top =   veritabani.feedrate_bul(material, current, gases, yeni_thickness_top)

            aci_bottom = min(aci * 1.18, 47)  # Açı 47'den büyükse 47 olarak al
            if kerftipi == 1:
                aci_bottom = aci
                
            print(kerf_tipi)
            radyan_bottom = math.radians(aci_bottom)
            yeni_thickness_bottom = thickness / math.cos(radyan_bottom) # Bottom angle için yeni thickness

            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_bottom = calculate_wdi(current, aci_bottom,kerftipi)

                                
            result_bottom = veritabani.kerf_width_bul_2(material, current, gases, yeni_thickness_bottom)
            feedrate_bottom = veritabani.feedrate_bul(material, current, gases, yeni_thickness_bottom)

            # Top Angle Offset hesaplama
            if result_top:
                egimli_kerf_top = result_top
                print(f"\nThickness: {thickness}")
                print(f"\nAçı: {aci}")
                print(f"\nNormal Kerf: {legal_kerfWidth}")
                print(f"\ntemp: {calculate_wdi_top}")
                print(f"\nEğim: {yeni_thickness_top}")
                print(f"\neğimli kerf: {egimli_kerf_top}")
                print(f"\nBevel_WD: {bevel_wd}")
                
                print(f"\nTop Angle Offset Formülü: (TAN({radyan}) * ({thickness} + ({bevel_wd} - {calculate_wdi_top} + ({egimli_kerf_top} / 2) * (COS({radyan}) - 1) / COS({radyan}))) - ({egimli_kerf_top} / 2)) + 1")
                top_angle_offset = (math.tan(radyan) * (thickness + (bevel_wd - calculate_wdi_top + (egimli_kerf_top / 2) * (math.cos(radyan) - 1) / math.cos(radyan))) - (egimli_kerf_top / 2)) + 1
                #if(kerftipi == 1):
                #top_angle_offset = top_angle_offset + (legal_kerfWidth/2)
                top_knife = (thickness/(math.tan(math.radians(90-aci)))) - top_angle_offset
                top_land  = top_knife/2
                print(f"\nTOP ANGLE OFFSET: {top_angle_offset}")

            # Bottom Angle Offset hesaplama
            if result_bottom:
                egimli_kerf_bottom = result_bottom
                #print(f"\nBottom Angle Offset Formülü: (TAN({radyan_bottom}) * (0 + ({bevel_wd} - {calculate_wdi_bottom})) + ({egimli_kerf_bottom} / 2) / COS({radyan_bottom})) + 1")
                bottom_angle_offset = (math.tan(radyan_bottom) * (0 + (bevel_wd - calculate_wdi_bottom)) + (egimli_kerf_bottom / 2) / math.cos(radyan_bottom)) + 1
                bottom_knife = bottom_angle_offset
                bottom_land  = bottom_knife/2

            # Sonuçları listeye ekleme
            if result_top and result_bottom:  # result2 yerine result_bottom kullanıldı
                results.append((int(thickness),
                                int(aci), 
                                current,
                                feedrate_top,
                                top_angle_offset,
                                  bottom_angle_offset,
                                  top_knife,
                                  bottom_knife,
                                  top_land,
                                  bottom_land,
                                  legal_kerfWidth,
                                  material))
    return results

# Dosya oluşturma ve indirme
def create_and_download_file(df,results, baslik_yaz,ilk_kayit):
        mat="SS"
        if results[0][11] == "MildStell":
            mat="MS"
        else:
            mat="SS"

        baslik_satirlari = [
            "",
            "",
        f"800 : Sheet Name = {mat} {results[0][2]}AMP",
        "999 : Process = 2",
        "1000: Material = MS,PMSTEEL",
        "1001: Cut Quality = 1,2,3,4,5",
        f"1002: Cutting Conditions = {results[0][2]}AMP",
        "",
        "5\t:\t\tThick-, \t\tAngle, \t\tProg, \t\tCurrent, \t\tVolts, \t\tFeed, \t\tKerf, \t\tKerf, \t\tKerf, \t\tKerf, \tLEADTABLE, \t\tConer, \t\tConer, \t\tConer, \t\tConer, \t\tLeadin, \t\tLeadin, \t\tLeadOut, \t\tLeadout, \t\t\t, \tBlindBevel, \tBlindBevel, \tBlindBevel, \tBlindBevel, \t\t\t, \t\tBevel, \t\tPreCut, \t\tPre Cut, \t\t\t, \t\t\t, \tArc Radius, \tArc Radius, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \tDO NOT MODIFY, \tVerified1, \t\tBevType, \tVerified2, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t,",
        "5\t:\t\tness, \t\t(Deg), \t\tAngle, \t\t(amps), \t(not used), \t\trate, \tTop Knife, \tBottom Knife, \tTop Land, \tBottom Land, \t[DELIMITER], \t\tLoop, \t\tLoop, \t\tLoop, \t\tLoop, \t\tLength, \tLength 2, \t\tLength, \tLength 2, \t\t\t, \tLoopType, \t\tSize, \t\tType, \t\tSize, \t\t\t, \t\tPreCut, \t\tSize 1, \t\tSize 2, \t\t\t, \t\t\t, \t\tLeadin, \t\tLeadout, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t , \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t,",
        "5\t:\t\t(in), \t\t\t, \t\t(Deg), \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\tType, \t\tAngle, \t\tSize 1, \t\tSize 2, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\tIN, \t\tIN, \t\tOUT, \t\tOUT, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \tInternal, \tInternal, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t , \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t, \t\t\t,"
        ]
         
         # Başlık satırlarını yaz
        

        satir_sablonu = "10 :\t\t\t{},\t\t\t{},\t\t\t{},\t\t\t{},\t\t\t{},\t\t{},\t\t\t{:.3f},\t\t\t{:.3f},\t\t\t{:.3f},\t\t\t{:.3f},\t\tLEADTABLE,\t\tLINE2OPEN,\t\t30,\t\t\t8,\t\t\t8,\t\t\t4,\t\t\t4,\t\t\t4,\t\t\t4,\t\t\t,\tLINEOPEN,\t\t\t8,\tLINEOPEN,\t\t\t8,\t\t\t,\tNONE,\t\t\t0,\t\t\t0,\t\t\t,\t\t\t,\t\t\t0,\t\t\t0,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\tVERIFIED,\t\t\t0,\t\t\t-1,\t\t\t0,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,\t\t\t,"
        # Dosya açma modu: ilk hesaplamada 'w' (write), sonraki hesaplamalarda 'a' (append)
        dosya_modu = 'w' if ilk_kayit else 'a'
        # Dosya açma modu: 'a' (append) ile dosya sonuna ekleme yapılacak
        with open('Ajan_Precision_Plasma_Bevel_MM.TEC', dosya_modu, encoding='utf-8') as f:
            if baslik_yaz:  # Başlık yazdırma parametresi True ise başlıkları yaz
                for satir in baslik_satirlari:
                    f.write(satir + "\n")

            for _, row in df.iterrows():
                formatted_row = satir_sablonu.format(
                    int(row["Thickness"]),
                    int(row["Angle"]),
                    int(row["Angle"]),
                    int(row["Current"]),
                    int(row["Current"]),
                    int(row["Feedrate"]),
                    row["Top Knife"], row["Bottom Knife"], row["Top Land"], row["Bottom Land"])
                f.write(formatted_row + "\n")

        with open('Ajan_Precision_Plasma_Bevel_MM.TEC', 'rb') as f:  # Dosyayı binary modda aç
            bytes_data = f.read()

        return bytes_data  # Dosyanın içeriğini döndür
        