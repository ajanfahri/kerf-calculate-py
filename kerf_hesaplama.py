import sqlite3
import math
import sqlite3
import math

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

    try:
        # Veritabanına bağlanma
        conn = sqlite3.connect('ajandatas.db')
        cursor = conn.cursor()

        # Yeni thickness değerini hesaplama (top angle için)
        yeni_thickness_top = thickness / math.cos(math.radians(aci))

        # SQL sorguları (iki ayrı sorgu)
        query1 = """
        SELECT KerfWidth
        FROM PLASMA
        WHERE Material = ? AND Current = ? AND Gases = ? AND Thickness = ?;
        """
        query2 = """
        SELECT KerfWidth
        FROM PLASMA
        WHERE Material = ? AND Current = ? AND Gases = ? AND Thickness >= ?
        ORDER BY Thickness ASC
        LIMIT 1;
        """
        # İlk sorguyu çalıştırma (15mm için)
        cursor.execute(query1, (material, current, gases, thickness))
        result1 = cursor.fetchone()

        # İkinci sorguyu çalıştırma (formülden sonraki kalınlık için)
        cursor.execute(query2, (material, current, gases, yeni_thickness_top))
        result2 = cursor.fetchone()



        for aci in [5, 10, 15, 20, 25, 30, 35, 40, 45]:
            yeni_thickness_top    = thickness / math.cos(math.radians(aci))
            top_angle_offset=None
            radyan = math.radians(aci)
            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_top = calculate_wdi(current, aci)

            # SQL sorguları (iki ayrı sorgu)
            cursor.execute(query2, (material, current, gases, yeni_thickness_top))
            result_top = cursor.fetchone()

            aci_bottom = min(aci * 1.18, 47)  # Açı 47'den büyükse 47 olarak al
            radyan_bottom = math.radians(aci_bottom)
            yeni_thickness_bottom = thickness / math.cos(radyan_bottom) # Bottom angle için yeni thickness

            # CalculateWDI hesaplama (fonksiyon kullanarak)
            calculate_wdi_bottom = calculate_wdi(current, aci_bottom)

            cursor.execute(query2, (material, current, gases, yeni_thickness_bottom))
            result_bottom = cursor.fetchone()

            # Top Angle Offset hesaplama
            if result_top:
                egimli_kerf_top = result_top[0]
                print(f"\nTop Angle Offset Formülü: (TAN({radyan}) * ({thickness} + ({bevel_wd} - {calculate_wdi_top} + ({egimli_kerf_top} / 2) * (COS({radyan}) - 1) / COS({radyan}))) - ({egimli_kerf_top} / 2)) + 1")
                top_angle_offset = (math.tan(radyan) * (thickness + (bevel_wd - calculate_wdi_top + (egimli_kerf_top / 2) * (math.cos(radyan) - 1) / math.cos(radyan))) - (egimli_kerf_top / 2)) + 1

            # Bottom Angle Offset hesaplama
            if result_bottom:
                egimli_kerf_bottom = result_bottom[0]
                print(f"\nBottom Angle Offset Formülü: (TAN({radyan_bottom}) * (0 + ({bevel_wd} - {calculate_wdi_bottom})) + ({egimli_kerf_bottom} / 2) / COS({radyan_bottom})) + 1")
                bottom_angle_offset = (math.tan(radyan_bottom) * (0 + (bevel_wd - calculate_wdi_bottom)) + (egimli_kerf_bottom / 2) / math.cos(radyan_bottom)) + 1

            # Sonuçları listeye ekleme
            if result_top and result_bottom:  # result2 yerine result_bottom kullanıldı
                results.append((aci, top_angle_offset, bottom_angle_offset))
 
    except sqlite3.Error as e:
        print("Veritabanı hatası:", e)

    finally:
        # Bağlantıyı kapatma (her durumda)
        if conn:
            conn.close()
    return results