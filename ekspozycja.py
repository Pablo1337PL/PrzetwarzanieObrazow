import numpy as np
from PyQt5.QtWidgets import QSlider, QLabel, QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QComboBox
from PyQt5.QtCore import Qt

from zakladka import Zakladka

class Ekspozycja(Zakladka):
    def __init__(self):
        super().__init__(tytul_modulu="MODUŁ EKSPOZYCJI", kolor="#2b78e4")

        # --- 0. WYRÓWNYWANIE HISTOGRAMU ---
        self.hist_eq_cb = QCheckBox("Wyrównaj histogram")
        self.hist_eq_cb.toggled.connect(self.changed.emit)
        self.layout.addWidget(self.hist_eq_cb)
        
        self.add_separator()

        # --- 1. KONWERSJA DO SZAROŚCI ---
        self.szarosc_cb = QCheckBox("Odcienie szarości")
        self.szarosc_combo = QComboBox()
        self.szarosc_combo.addItems(["Luminancja", "Średnia", "Maksymalna"])
        
        self.szarosc_cb.toggled.connect(self.changed.emit)
        self.szarosc_combo.currentIndexChanged.connect(self.changed.emit)
        
        self.layout.addWidget(self.szarosc_cb)
        self.layout.addWidget(self.szarosc_combo)

        # --- 2. NEGATYW ---
        self.negatyw_cb = QCheckBox("Negatyw")
        self.negatyw_cb.toggled.connect(self.changed.emit)
        self.layout.addWidget(self.negatyw_cb)

        self.add_separator()

        # --- 3. JASNOŚĆ ---
        self.jasnosc_cb = QCheckBox("Jasność")
        self.jasnosc_cb.toggled.connect(self.changed.emit)
        self.jasnosc_label = QLabel("Wartość: 0")
        self.jasnosc_slider = self.create_slider(-100, 100, 0, self.update_jasnosc)
        self.layout.addWidget(self.jasnosc_cb)
        self.layout.addWidget(self.jasnosc_label)
        self.layout.addWidget(self.jasnosc_slider)

        # --- 4. KONTRAST ---
        self.kontrast_cb = QCheckBox("Kontrast")
        self.kontrast_cb.toggled.connect(self.changed.emit)
        self.kontrast_label = QLabel("Wartość: 0")
        self.kontrast_slider = self.create_slider(-100, 100, 0, self.update_kontrast)
        self.layout.addWidget(self.kontrast_cb)
        self.layout.addWidget(self.kontrast_label)
        self.layout.addWidget(self.kontrast_slider)

        # --- 5. SATURACJA ---
        self.saturacja_cb = QCheckBox("Saturacja")
        self.saturacja_cb.toggled.connect(self.changed.emit)
        self.saturacja_label = QLabel("Wartość: 0")
        self.saturacja_slider = self.create_slider(-100, 100, 0, self.update_saturacja)
        self.layout.addWidget(self.saturacja_cb)
        self.layout.addWidget(self.saturacja_label)
        self.layout.addWidget(self.saturacja_slider)

        # --- 6. WINIETA ---
        self.winieta_cb = QCheckBox("Winieta")
        self.winieta_cb.toggled.connect(self.changed.emit)
        self.winieta_label = QLabel("Siła winiety: 0")
        self.winieta_slider = self.create_slider(-100, 100, 0, self.update_winieta)
        self.layout.addWidget(self.winieta_cb)
        self.layout.addWidget(self.winieta_label)
        self.layout.addWidget(self.winieta_slider)
        
        self.add_separator()

        # --- 7. BINARYZACJA ---
        self.bin_layout = QHBoxLayout() 
        
        self.bin_cb = QCheckBox("Binaryzacja")
        self.bin_cb.toggled.connect(self.changed.emit)
        
        self.bin_otsu_cb = QCheckBox("Otsu")
        self.bin_otsu_cb.toggled.connect(self.changed.emit)
        
        self.bin_layout.addWidget(self.bin_cb)
        self.bin_layout.addWidget(self.bin_otsu_cb)
        self.bin_layout.setAlignment(Qt.AlignLeft)
        
        self.bin_label = QLabel("Próg odcięcia: 128")
        self.bin_slider = self.create_slider(0, 255, 128, self.update_bin)
        
        self.layout.addLayout(self.bin_layout)
        self.layout.addWidget(self.bin_label)
        self.layout.addWidget(self.bin_slider)

    # --- FUNKCJE POMOCNICZE UI ---
    
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

    def update_kontrast(self):
        self.kontrast_label.setText(f"Wartość: {self.kontrast_slider.value()}")

    def update_saturacja(self):
        self.saturacja_label.setText(f"Wartość: {self.saturacja_slider.value()}")

    def update_winieta(self):
        self.winieta_label.setText(f"Siła winiety: {self.winieta_slider.value()}")

    def update_bin(self):
        # TUTAJ JEST ZMIANA:
        # Kiedy użytkownik rusz suwakiem, sprawdzamy, czy Otsu jest zaznaczone.
        # Jeśli tak - odznaczamy je automatycznie.
        if self.bin_otsu_cb.isChecked():
            self.bin_otsu_cb.setChecked(False)
            
        self.bin_label.setText(f"Próg odcięcia: {self.bin_slider.value()}")

    # --- GŁÓWNA FUNKCJA PRZETWARZANIA ---

    def process(self, img):
        img_float = img.astype(np.float32)

        # 0. Wyrównywanie histogramu
        if self.hist_eq_cb.isChecked():
            img_clipped = np.clip(img_float, 0, 255).astype(np.uint8)
            is_color = len(img_float.shape) == 3
            
            if is_color:
                Y = 0.299 * img_float[..., 0] + 0.587 * img_float[..., 1] + 0.114 * img_float[..., 2]
                Y_uint = np.clip(Y, 0, 255).astype(np.uint8)
                
                hist, _ = np.histogram(Y_uint.flatten(), 256, [0, 256])
                cdf = hist.cumsum()
                cdf_masked = np.ma.masked_equal(cdf, 0)
                cdf_m = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
                cdf_m = np.ma.filled(cdf_m, 0).astype(np.float32)
                
                Y_eq = cdf_m[Y_uint]
                Y_safe = np.where(Y == 0, 1.0, Y)
                ratio = Y_eq / Y_safe
                
                for i in range(3):
                    img_float[..., i] = np.clip(img_float[..., i] * ratio, 0, 255)
            else:
                hist, _ = np.histogram(img_clipped.flatten(), 256, [0, 256])
                cdf = hist.cumsum()
                cdf_masked = np.ma.masked_equal(cdf, 0)
                cdf_m = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
                cdf_m = np.ma.filled(cdf_m, 0).astype(np.float32)
                img_float = cdf_m[img_clipped]

        # 1. Odcienie szarości
        if self.szarosc_cb.isChecked():
            tryb = self.szarosc_combo.currentText()
            
            if tryb == "Luminancja":
                gray = np.dot(img_float[..., :3], [0.299, 0.587, 0.114])
            elif tryb == "Średnia":
                gray = np.mean(img_float[..., :3], axis=2)
            else: # Maksymalna
                gray = np.max(img_float[..., :3], axis=2)
                
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
            wartosc_suwaka = self.winieta_slider.value()
            
            if wartosc_suwaka != 0:
                sila = abs(wartosc_suwaka) / 100.0 * 2
                h, w = img_float.shape[:2]
                y, x = np.ogrid[:h, :w]
                cy, cx = h / 2, w / 2
                
                max_dist = np.sqrt(cx**2 + cy**2)
                dist = np.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
                
                efekt = (dist**3) * sila
                efekt = np.clip(efekt, 0, 1)
                
                if len(img_float.shape) == 3:
                    efekt = efekt[..., np.newaxis]
                
                if wartosc_suwaka > 0:
                    img_float = img_float * (1.0 - efekt)
                else:
                    img_float = img_float * (1.0 - efekt) + 255.0 * efekt

        # 7. Binaryzacja
        if self.bin_cb.isChecked():
            jasnosc_piksela = np.dot(img_float[..., :3], [0.299, 0.587, 0.114]) if len(img_float.shape) == 3 else img_float
            
            if self.bin_otsu_cb.isChecked():
                jasnosc_uint = np.clip(jasnosc_piksela, 0, 255).astype(np.uint8)
                hist, _ = np.histogram(jasnosc_uint.flatten(), 256, [0, 256])
                
                p = hist / hist.sum()
                omega = np.cumsum(p)
                mu = np.cumsum(p * np.arange(256))
                mu_t = mu[-1]
                
                omega_safe = np.where(omega == 0, 1e-6, omega)
                omega_safe_inv = np.where(1-omega == 0, 1e-6, 1-omega)
                
                sigma_b_squared = (mu_t * omega - mu)**2 / (omega_safe * omega_safe_inv)
                prog = np.argmax(sigma_b_squared)
                
                self.bin_label.setText(f"Próg odcięcia: {prog}")
            else:
                prog = self.bin_slider.value()
                self.bin_label.setText(f"Próg odcięcia: {prog}")
            
            img_float_2d = np.where(jasnosc_piksela > prog, 255.0, 0.0)
            
            if len(img.shape) == 3:
                img_float = np.stack([img_float_2d, img_float_2d, img_float_2d], axis=-1)
            else:
                img_float = img_float_2d

        return np.clip(img_float, 0, 255).astype(np.uint8)
    