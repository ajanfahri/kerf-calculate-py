
import kerf_hesaplama
import veritabani

def material_degisti(event):
    """Material seçimi değiştiğinde Current combobox'ını günceller."""
    current_combobox.config(values=veritabani.current_degerleri_al(material_combobox.get()))
    current_combobox.set("")  # Seçimi temizle

def current_degisti(event):
    """Current seçimi değiştiğinde Gases combobox'ını günceller."""
    gases_combobox.config(values=veritabani.gases_degerleri_al(material_combobox.get(), current_combobox.get()))
    gases_combobox.set("")  # Seçimi temizle

def gases_degisti(event):
    """Gases seçimi değiştiğinde Thickness combobox'ını günceller."""
    thickness_combobox.config(values=veritabani.thickness_degerleri_al(material_combobox.get(), current_combobox.get(), gases_combobox.get()))
    thickness_combobox.set("")  # Seçimi temizle

def hesapla_ve_goster():
    """Hesaplamaları yapar ve sonuçları tabloya ekler."""
    material = material_combobox.get()
    current = float(current_combobox.get())
    gases = gases_combobox.get()
    thickness = float(thickness_combobox.get())

    results = kerf_hesaplama.kerf_width_bul(material, current, gases, thickness)

    # Tabloyu temizle
    for i in tree.get_children():
        tree.delete(i)

    # Sonuçları tabloya ekle
    for aci, top_offset, bottom_offset in results:
        if top_offset is not None and bottom_offset is not None:
            tree.insert("", "end", values=(aci, top_offset, bottom_offset))
        else:
            tree.insert("", "end", values=(aci, "Veri Yok", "Veri Yok"))

# Pencere oluşturma
window = tk.Tk()
window.title("Kerf Hesaplama")
# Material combobox
material_label = tk.Label(window, text="Material:")
material_label.grid(row=0, column=0, padx=5, pady=5)
material_combobox = ttk.Combobox(window, values=veritabani.material_tipleri_al())
material_combobox.grid(row=0, column=1, padx=5, pady=5)
material_combobox.bind("<<ComboboxSelected>>", material_degisti)

# Current combobox
current_label = tk.Label(window, text="Current:")
current_label.grid(row=1, column=0, padx=5, pady=5)
current_combobox = ttk.Combobox(window)  # Başlangıçta boş
current_combobox.grid(row=1, column=1, padx=5, pady=5)
current_combobox.bind("<<ComboboxSelected>>", current_degisti)

# Gases combobox
gases_label = tk.Label(window, text="Gases:")
gases_label.grid(row=2, column=0, padx=5, pady=5)
gases_combobox = ttk.Combobox(window)  # Başlangıçta boş
gases_combobox.grid(row=2, column=1, padx=5, pady=5)
gases_combobox.bind("<<ComboboxSelected>>", gases_degisti)

# Thickness combobox
thickness_label = tk.Label(window, text="Thickness:")
thickness_label.grid(row=3, column=0, padx=5, pady=5)
thickness_combobox = ttk.Combobox(window)  # Başlangıçta boş
thickness_combobox.grid(row=3, column=1, padx=5, pady=5)
# Hesaplama ve gösterme düğmesi
hesapla_button = tk.Button(window, text="Hesapla ve Göster", command=hesapla_ve_goster)
hesapla_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)





# Tablo oluşturma
tree = ttk.Treeview(window, columns=("Açı", "Top Offset", "Bottom Offset"), show="headings")
tree.heading("Açı", text="Açı")
tree.heading("Top Offset", text="Top Offset")
tree.heading("Bottom Offset", text="Bottom Offset")
tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

window.mainloop()
