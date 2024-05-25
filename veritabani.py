import sqlite3

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
