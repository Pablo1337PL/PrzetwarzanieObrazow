import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PIL import Image
from PIL.ExifTags import TAGS

class Metadane(QWidget):
    def __init__(self):
        super().__init__()
        # Ustalamy stałą, niewielką wysokość, żeby nie zabrać miejsca wykresom
        #self.setFixedHeight(160) 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("<b>Metadane pliku i EXIF:</b>"))

        # Zwykłe pole tekstowe (Tylko do odczytu)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-size: 11px; background-color: #f8f9fa; color: #333;")
        layout.addWidget(self.text_edit)

    def wczytaj_dane(self, file_path):
        """Wczytuje informacje bezpośrednio z pliku, omijając macierz NumPy."""
        self.text_edit.clear()
        if not file_path or not os.path.exists(file_path):
            self.text_edit.setText("Brak pliku.")
            return

        try:
            # Używamy PIL tylko do odczytania nagłówków (bardzo szybka operacja)
            img = Image.open(file_path)
            info = []
            
            # --- 1. Podstawowe informacje o pliku ---
            rozmiar_kb = os.path.getsize(file_path) / 1024
            info.append(f"<b>Nazwa:</b> {os.path.basename(file_path)}")
            info.append(f"<b>Format:</b> {img.format} ({img.mode})")
            info.append(f"<b>Waga:</b> {rozmiar_kb:.2f} KB")
            info.append(f"<b>Rozdzielczość (Oryginał):</b> {img.width} x {img.height} px")

            # --- 2. Metadane z aparatu (EXIF) ---
            exif_data = img.getexif()
            if exif_data:
                info.append("<br><b>Dane z aparatu:</b>")
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    # Omijamy nieczytelne, binarne tagi (np. miniaturki zdjęć zapisane w bajtach)
                    if isinstance(value, bytes):
                        continue
                    info.append(f"<i>{tag_name}:</i> {value}")
            else:
                info.append("<br><i>Plik nie zawiera danych EXIF.</i>")

            # Ustawiamy tekst używając prostego formatowania HTML
            self.text_edit.setHtml("<br>".join(info))
            
            # Zamykamy plik, żeby nie blokować go w systemie
            img.close()

        except Exception as e:
            self.text_edit.setText(f"Błąd odczytu metadanych:<br>{e}")