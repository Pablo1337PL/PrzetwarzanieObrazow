import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PIL import Image
from PIL.ExifTags import TAGS

class Metadane(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("<b>Metadane pliku i EXIF:</b>"))

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
            img = Image.open(file_path)
            info = []
            
            rozmiar_kb = os.path.getsize(file_path) / 1024
            info.append(f"<b>Nazwa:</b> {os.path.basename(file_path)}")
            info.append(f"<b>Format:</b> {img.format} ({img.mode})")
            info.append(f"<b>Waga:</b> {rozmiar_kb:.2f} KB")
            info.append(f"<b>Rozdzielczość (Oryginał):</b> {img.width} x {img.height} px")

            exif_data = img.getexif()
            if exif_data:
                info.append("<br><b>Dane z aparatu:</b>")
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        continue
                    info.append(f"<i>{tag_name}:</i> {value}")
            else:
                info.append("<br><i>Plik nie zawiera danych EXIF.</i>")

            self.text_edit.setHtml("<br>".join(info))
            
            img.close()

        except Exception as e:
            self.text_edit.setText(f"Błąd odczytu metadanych:<br>{e}")