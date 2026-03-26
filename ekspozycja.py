import numpy as np
from PyQt5.QtWidgets import QSlider, QLabel, QCheckBox, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

from zakladka import Zakladka

class Ekspozycja(Zakladka):
    def __init__(self):
        super().__init__(tytul_modulu="WŁĄCZ MODUŁ EKSPOZYCJI", kolor="#2b78e4")

        # --- 1. KONWERSJA DO SZAROŚCI ---
        self.szarosc_cb = QCheckBox("Odcienie szarości")
        self.szarosc_cb.toggled.connect(self.changed.emit)
        self.layout.addWidget(self.szarosc_cb)

        # --- 2. NEGATYW ---
        self.negatyw_cb = QCheckBox("Negatyw")
        self.negatyw_cb.toggled.connect(self.changed.emit)
        self.layout.addWidget(self.negatyw_cb)

        self.add_separator()

        # --- 3. KOREKTA JASNOŚCI ---
        self.jasnosc_cb = QCheckBox("Włącz korektę jasności")
        self.jasnosc_cb.setChecked(True)
        self.jasnosc_cb.toggled.connect(self.changed.emit)
        self.jasnosc_label = QLabel("Wartość: 0")
        self.jasnosc_slider = self.create_slider(-100, 100, 0, self.update_jasnosc)
        self.layout.addWidget(self.jasnosc_cb)
        self.layout.addWidget(self.jasnosc_label)
        self.layout.addWidget(self.jasnosc_slider)

        # --- 4. KOREKTA KONTRASTU ---
        self.kontrast_cb = QCheckBox("Włącz korektę kontrastu")
        self.kontrast_cb.setChecked(True)
        self.kontrast_cb.toggled.connect(self.changed.emit)
        self.kontrast_label = QLabel("Wartość: 0")
        self.kontrast_slider = self.create_slider(-100, 100, 0, self.update_kontrast)
        self.layout.addWidget(self.kontrast_cb)
        self.layout.addWidget(self.kontrast_label)
        self.layout.addWidget(self.kontrast_slider)

        # --- 5. SATURACJA ---
        self.saturacja_cb = QCheckBox("Włącz saturację")
        self.saturacja_cb.setChecked(True)
        self.saturacja_cb.toggled.connect(self.changed.emit)
        self.saturacja_label = QLabel("Wartość: 0")
        self.saturacja_slider = self.create_slider(-100, 100, 0, self.update_saturacja)
        self.layout.addWidget(self.saturacja_cb)
        self.layout.addWidget(self.saturacja_label)
        self.layout.addWidget(self.saturacja_slider)

        # --- 6. WINIETA ---
        self.winieta_cb = QCheckBox("Winieta")
        self.winieta_cb.toggled.connect(self.changed.emit)
        self.winieta_label = QLabel("Siła winiety: 50%")
        self.winieta_slider = self.create_slider(0, 100, 50, self.update_winieta)
        self.layout.addWidget(self.winieta_cb)
        self.layout.addWidget(self.winieta_label)
        self.layout.addWidget(self.winieta_slider)

        # --- 7. BINARYZACJA ---
        self.bin_cb = QCheckBox("Binaryzacja")
        self.bin_cb.toggled.connect(self.changed.emit)
        self.bin_label = QLabel("Próg odcięcia: 128")
        self.bin_slider = self.create_slider(0, 255, 128, self.update_bin)
        self.layout.addWidget(self.bin_cb)
        self.layout.addWidget(self.bin_label)
        self.layout.addWidget(self.bin_slider)

    def create_slider(self, min_val, max_val, default, connect_func):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(connect_func)
        slider.sliderReleased.connect(self.changed.emit)
        
        return slider

    def add_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #cccccc;")
        self.layout.addWidget(line)

    def update_jasnosc(self):
        self.jasnosc_label.setText(f"Wartość: {self.jasnosc_slider.value()}")
        #self.changed.emit()

    def update_kontrast(self):
        self.kontrast_label.setText(f"Wartość: {self.kontrast_slider.value()}")
        #self.changed.emit()

    def update_saturacja(self):
        self.saturacja_label.setText(f"Wartość: {self.saturacja_slider.value()}")
        #self.changed.emit()

    def update_winieta(self):
        self.winieta_label.setText(f"Siła winiety: {self.winieta_slider.value()}%")
        #self.changed.emit()

    def update_bin(self):
        self.bin_label.setText(f"Próg odcięcia: {self.bin_slider.value()}")
        #self.changed.emit()

    def process(self, img):
        img_float = img.astype(np.float32)

        # 1. Odcienie szarości
        if self.szarosc_cb.isChecked():
            gray = np.dot(img_float[..., :3], [0.299, 0.587, 0.114])
            img_float = np.stack([gray, gray, gray], axis=-1)

        # 2. Negatyw
        if self.negatyw_cb.isChecked():
            img_float = 255.0 - img_float

        # 3. Jasność
        jasnosc = self.jasnosc_slider.value()
        if self.jasnosc_cb.isChecked() and jasnosc != 0:
            img_float += jasnosc

        # 4. Kontrast
        kontrast = self.kontrast_slider.value()
        if self.kontrast_cb.isChecked() and kontrast != 0:
            wspolczynnik = (kontrast + 100) / 100.0
            if wspolczynnik < 0.1: wspolczynnik = 0.1
            
            img_float = (img_float - 128.0) * wspolczynnik + 128.0

        # 5. Saturacja
        saturacja = self.saturacja_slider.value()
        if self.saturacja_cb.isChecked() and saturacja != 0 and not self.szarosc_cb.isChecked():
            wsp_sat = (saturacja + 100) / 100.0
            gray = np.dot(img_float[..., :3], [0.299, 0.587, 0.114])
            gray_3d = np.stack([gray, gray, gray], axis=-1)
            img_float = gray_3d + (img_float - gray_3d) * wsp_sat

        # 6. Winieta
        if self.winieta_cb.isChecked():
            sila = (self.winieta_slider.value() / 100.0) * 1.5 
            h, w = img_float.shape[:2]
            y, x = np.ogrid[:h, :w]
            cy, cx = h / 2, w / 2
            
            max_dist = np.sqrt(cx**2 + cy**2)
            dist = np.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
            
            mask = 1.0 - (dist**4 * sila)
            mask = np.clip(mask, 0, 1)
            
            if len(img_float.shape) == 3:
                mask = mask[..., np.newaxis]
            
            img_float *= mask

        # 7. Binaryzacja
        if self.bin_cb.isChecked():
            prog = self.bin_slider.value()
            jasnosc_piksela = np.mean(img_float, axis=2, keepdims=True)
            img_float = np.where(jasnosc_piksela > prog, 255.0, 0.0)
            if len(img.shape) == 3:
                img_float = np.broadcast_to(img_float, img.shape)

        return np.clip(img_float, 0, 255).astype(np.uint8)
    