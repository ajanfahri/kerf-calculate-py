import sqlite3

def feedrate_bul(material, current, gases, thickness):
        """Verilen değerlere göre Feedrate değerini bulan fonksiyon."""

        with sqlite3.connect('ajandatas.db') as conn:
            cursor = conn.cursor()

            # SQL sorgusu
            query = """
            SELECT Feedrate
            FROM PLASMA
            WHERE Material = ? AND Current = ? AND Gases = ? AND Thickness >= ?
            ORDER BY Thickness ASC
            LIMIT 1;
            """
            cursor.execute(query, (material, current, gases, thickness))
            result = cursor.fetchone()

            if result:
                return result[0]  # Feedrate değerini döndür
            else:
                return None

def kerf_width_bul_1(material, current, gases, thickness):
    try:
        # Veritabanına bağlanma
        conn = sqlite3.connect('ajandatas.db')
        cursor = conn.cursor()

        # SQL sorgusu
        query = """
        SELECT KerfWidth
        FROM PLASMA
        WHERE Material = ? AND Current = ? AND Gases = ? AND Thickness = ?;
        """
        cursor.execute(query, (material, current, gases, thickness))
        result = cursor.fetchone()

        if result:
            return result[0]  # KerfWidth değerini döndür
        else:
            return None
    except sqlite3.Error as e:
        print("Veritabanı hatası:", e)
        return None
    finally:
        # Bağlantıyı kapatma (her durumda)
        if conn:
            conn.close()

def kerf_width_bul_2(material, current, gases, yeni_thickness_top):
    try:
        # Veritabanına bağlanma
        conn = sqlite3.connect('ajandatas.db')
        cursor = conn.cursor()

        # SQL sorgusu
        query = """
        SELECT KerfWidth
        FROM PLASMA
        WHERE Material = ? AND Current = ? AND Gases = ? AND Thickness >= ?
        ORDER BY Thickness ASC
        LIMIT 1;
        """
        cursor.execute(query, (material, current, gases, yeni_thickness_top))
        result = cursor.fetchone()

        if result:
            return result[0]  # KerfWidth değerini döndür
        else:
            return None
    except sqlite3.Error as e:
        print("Veritabanı hatası:", e)
        return None
    finally:
        # Bağlantıyı kapatma (her durumda)
        if conn:
            conn.close()



def baglanti_ac():
    """Veritabanına bağlantı açar ve cursor nesnesi döndürür."""
    conn = sqlite3.connect('ajandatas.db')
    return conn, conn.cursor()

def baglanti_kapat(conn):
    """Veritabanı bağlantısını kapatır."""
    conn.close()

def material_tipleri_al():
    """Veritabanından Material tiplerini çeker."""
    conn, cursor = baglanti_ac()
    cursor.execute("SELECT DISTINCT Material FROM PLASMA")
    tipler = [row[0] for row in cursor.fetchall()]
    baglanti_kapat(conn)
    return tipler

def current_degerleri_al(material):
    """Verilen Material tipine göre Current değerlerini çeker."""
    conn, cursor = baglanti_ac()
    cursor.execute("SELECT DISTINCT Current FROM PLASMA WHERE Material = ?", (material,))
    current_degerleri = [row[0] for row in cursor.fetchall()]
    baglanti_kapat(conn)
    return current_degerleri

    # ... (SQL sorgusu ile Current değerlerini çekme)

def gases_degerleri_al(material, current):
    """Verilen Material ve Current değerlerine göre Gases değerlerini çeker."""
    conn, cursor = baglanti_ac()
    cursor.execute("SELECT DISTINCT Gases FROM PLASMA WHERE Material = ? AND Current = ?", (material,current))
    gases_degerleri = [row[0] for row in cursor.fetchall()]
    baglanti_kapat(conn)
    return gases_degerleri

def thickness_degerleri_al(material, current, gases):
    """Verilen Material, Current ve Gases değerlerine göre Thickness değerlerini çeker."""
    conn, cursor = baglanti_ac()
    cursor.execute("SELECT DISTINCT Thickness FROM PLASMA WHERE Material = ? AND Current = ? AND Gases = ?", (material,current,gases))
    thickness_degerleri = [row[0] for row in cursor.fetchall()]
    baglanti_kapat(conn)
    return thickness_degerleri




# Diğer veritabanı işlemleri için fonksiyonlar (current_degerleri_al, gases_degerleri_al, thickness_degerleri_al)
# ...
