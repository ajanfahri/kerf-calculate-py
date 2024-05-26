import math
import veritabani

def calculate_wdi(current, aci):
    """Verilen Current ve Açı değerlerine göre CalculateWDI değerini hesaplar."""

    radyan = math.radians(aci)
    if (current == 200) and (aci < 48):
        return math.cos(radyan) * 5.5 - math.sin(radyan) * 3.5
    elif (current == 200) and (aci >= 48):
        return math.cos(radyan) * 17.72 - math.sin(radyan) * 14.46
    elif (current == 260) and (aci < 48):
        return math.cos(radyan) * 5.5 - math.sin(radyan) * 3.5
    elif (current == 260) and (aci >= 48):
        return math.cos(radyan) * 17.72 - math.sin(radyan) * 14.46
    elif (current == 130) and (aci < 41.5):
        return math.cos(radyan) * 10 - math.sin(radyan) * 6
    elif (current == 130) and (aci >= 41.5):
        return math.cos(radyan) * 17.15 - math.sin(radyan) * 14.1
    else:
        return None

def kerf_width_bul(material="MildStell", current=200, gases="O2/AIR", thickness=15, aci=25):
    """Verilen değerlere göre KerfWidth, Top Angle Offset ve Bottom Angle Offset değerlerini bulan fonksiyon."""

    results = []
    result1 = None  # result1'i başlangıçta None olarak tanımla
    result2 = None
    result_top = None
    result_bottom = None
    bevel_wd = 3
    legal_kerfWidth = veritabani.kerf_width_bul_1(material, current, gases, thickness) 
    for aci in [5, 10, 15, 20, 25, 30, 35, 40, 45]:
            yeni_thickness_top    = thickness / math.cos(math.radians(aci))
            top_angle_offset=None
            radyan = math.radians(aci)
            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_top = calculate_wdi(current, aci)

            # SQL sorguları (iki ayrı sorgu)
            #cursor.execute(query2,                 (material, current, gases, yeni_thickness_top))
            result_top = veritabani.kerf_width_bul_2(material, current, gases, yeni_thickness_top)
            feedrate_top =   veritabani.feedrate_bul(material, current, gases, yeni_thickness_top)

            aci_bottom = min(aci * 1.18, 47)  # Açı 47'den büyükse 47 olarak al
            radyan_bottom = math.radians(aci_bottom)
            yeni_thickness_bottom = thickness / math.cos(radyan_bottom) # Bottom angle için yeni thickness

            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_bottom = calculate_wdi(current, aci_bottom)

                                
            result_bottom = veritabani.kerf_width_bul_2(material, current, gases, yeni_thickness_bottom)
            feedrate_bottom = veritabani.feedrate_bul(material, current, gases, yeni_thickness_bottom)

            # Top Angle Offset hesaplama
            if result_top:
                egimli_kerf_top = result_top
                #print(f"\nTop Angle Offset Formülü: (TAN({radyan}) * ({thickness} + ({bevel_wd} - {calculate_wdi_top} + ({egimli_kerf_top} / 2) * (COS({radyan}) - 1) / COS({radyan}))) - ({egimli_kerf_top} / 2)) + 1")
                top_angle_offset = (math.tan(radyan) * (thickness + (bevel_wd - calculate_wdi_top + (egimli_kerf_top / 2) * (math.cos(radyan) - 1) / math.cos(radyan))) - (egimli_kerf_top / 2)) + 1
                top_knife = (thickness/(math.tan(math.radians(90-aci)))) - top_angle_offset
                top_land  = top_knife/2

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
                                feedrate_top,
                                top_angle_offset,
                                  bottom_angle_offset,
                                  top_knife,
                                  bottom_knife,
                                  top_land,
                                  bottom_land,
                                  legal_kerfWidth))
    return results
