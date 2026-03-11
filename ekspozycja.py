import numpy as np
from PyQt5.QtWidgets import QSlider, QLabel, QCheckBox
from PyQt5.QtCore import Qt

# Importujemy naszą klasę bazową
from zakladka import Zakladka

class Ekspozycja(Zakladka):
    def __init__(self):
        # 1. Wywołujemy konstruktor rodzica, ustawiając własny tekst i kolor
        super().__init__(tytul_modulu="WŁĄCZ MODUŁ EKSPOZYCJI", kolor="#2b78e4")

        # 2. Tworzymy nasze specyficzne widżety
        self.negatyw_cb = QCheckBox("Odwróć kolory (Negatyw)") # Wymóg na ocenę 3.0
        self.negatyw_cb.toggled.connect(self.changed.emit)

        self.jasnosc_label = QLabel("Korekta jasności: 0") # Wymóg na ocenę 3.0
        self.jasnosc_slider = QSlider(Qt.Horizontal)
        self.jasnosc_slider.setRange(-100, 100)
        self.jasnosc_slider.setValue(0)
        self.jasnosc_slider.valueChanged.connect(self.on_slider_change)

        # 3. Dodajemy je do layoutu odziedziczonego po klasie Zakladka
        self.layout.addWidget(self.negatyw_cb)
        self.layout.addWidget(self.jasnosc_label)
        self.layout.addWidget(self.jasnosc_slider)

    def on_slider_change(self):
        self.jasnosc_label.setText(f"Korekta jasności: {self.jasnosc_slider.value()}")
        self.changed.emit()

    def process(self, img):
        img_float = img.astype(np.float32)

        # Operacja: Negatyw [cite: 14]
        if self.negatyw_cb.isChecked():
            img_float = 255.0 - img_float

        # Operacja: Korekta jasności [cite: 12]
        jasnosc = self.jasnosc_slider.value()
        if jasnosc != 0:
            img_float += jasnosc

        return np.clip(img_float, 0, 255).astype(np.uint8)