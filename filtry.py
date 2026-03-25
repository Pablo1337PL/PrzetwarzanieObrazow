import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QLabel, QFrame, QSlider, QComboBox
from PyQt5.QtCore import Qt

from zakladka import Zakladka

class Filtry(Zakladka):
    def __init__(self):
        super().__init__(tytul_modulu="WŁĄCZ MODUŁ FILTRÓW", kolor="#e42b2b")

        # --- 2. FILTR UŚREDNIAJĄCY ---
        self.blur_box = QFrame()
        self.blur_layout = QVBoxLayout(self.blur_box)
        self.blur_layout.setContentsMargins(0, 0, 0, 10) 
        
        self.blur_cb = QCheckBox("Filtr Uśredniający")
        self.blur_cb.toggled.connect(self.changed.emit)
        self.blur_cb.toggled.connect(self.toggle_blur_params) 
        
        self.blur_label = QLabel("Siła rozmycia (iteracje): 1")
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 5) 
        self.blur_slider.setValue(1)
        self.blur_slider.setEnabled(False) 
        self.blur_slider.valueChanged.connect(self.update_blur_label)
        
        self.blur_layout.addWidget(self.blur_cb)
        self.blur_layout.addWidget(self.blur_label)
        self.blur_layout.addWidget(self.blur_slider)
        
        # --- 3. FILTR WYOSTRZAJĄCY ---
        self.sharp_box = QFrame()
        self.sharp_layout = QVBoxLayout(self.sharp_box)
        self.sharp_layout.setContentsMargins(0, 0, 0, 10)
        
        self.sharp_cb = QCheckBox("Filtr Wyostrzający")
        self.sharp_cb.toggled.connect(self.changed.emit)
        self.sharp_cb.toggled.connect(self.toggle_sharp_params)
        
        self.sharp_label = QLabel("Waga centralna (łagodność): 5")
        self.sharp_slider = QSlider(Qt.Horizontal)
        self.sharp_slider.setRange(5, 15) 
        self.sharp_slider.setValue(5)
        self.sharp_slider.setEnabled(False)
        self.sharp_slider.valueChanged.connect(self.update_sharp_label)
        
        self.sharp_layout.addWidget(self.sharp_cb)
        self.sharp_layout.addWidget(self.sharp_label)
        self.sharp_layout.addWidget(self.sharp_slider)

        # --- 4. WYKRYWANIE KRAWĘDZI ---
        self.edge_box = QFrame()
        self.edge_layout = QVBoxLayout(self.edge_box)
        self.edge_layout.setContentsMargins(0, 0, 0, 0)

        self.edge_cb = QCheckBox("Wykrywanie krawędzi")
        self.edge_cb.toggled.connect(self.changed.emit)
        self.edge_cb.toggled.connect(self.toggle_edge_params)

        # NOWOŚĆ: Checkbox wymuszający szarość
        self.edge_gray_cb = QCheckBox("Wymuś odcienie szarości")
        self.edge_gray_cb.setChecked(True) # Dobra praktyka: domyślnie włączone
        self.edge_gray_cb.setEnabled(False)
        self.edge_gray_cb.toggled.connect(self.changed.emit)

        self.edge_combo = QComboBox()
        # NOWOŚĆ: Dodany algorytm Canny'ego
        self.edge_combo.addItems(["Operator Sobela", "Krzyż Robertsa", "Algorytm Canny'ego (NumPy)"])
        self.edge_combo.setEnabled(False) 
        self.edge_combo.currentIndexChanged.connect(self.changed.emit)

        self.edge_layout.addWidget(self.edge_cb)
        self.edge_layout.addWidget(self.edge_gray_cb)
        self.edge_layout.addWidget(self.edge_combo)

        # --- DODANIE DO GŁÓWNEGO LAYOUTU ---
        self.layout.addWidget(self.blur_box)
        
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("color: #cccccc;")
        self.layout.addWidget(separator1)
        
        self.layout.addWidget(self.sharp_box)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("color: #cccccc;")
        self.layout.addWidget(separator2)

        self.layout.addWidget(self.edge_box)

    # --- FUNKCJE POMOCNICZE UI ---
    def toggle_blur_params(self, checked):
        self.blur_slider.setEnabled(checked)

    def update_blur_label(self, value):
        self.blur_label.setText(f"Siła rozmycia (iteracje): {value}")
        self.changed.emit()

    def toggle_sharp_params(self, checked):
        self.sharp_slider.setEnabled(checked)

    def update_sharp_label(self, value):
        self.sharp_label.setText(f"Waga centralna (łagodność): {value}")
        self.changed.emit()

    def toggle_edge_params(self, checked):
        self.edge_gray_cb.setEnabled(checked)
        self.edge_combo.setEnabled(checked)

    # --- LOGIKA PRZETWARZANIA (RĘCZNE IMPLEMENTACJE) ---
    def manual_convolve_3x3(self, img, kernel):
        """Ręczna implementacja splotu dla obrazu 3-kanałowego (RGB)."""
        k = np.array(kernel)
        pad_img = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode='edge')
        output = np.zeros_like(img, dtype=np.float32)

        for i in range(3):
            for j in range(3):
                output += pad_img[i:i+img.shape[0], j:j+img.shape[1]] * k[i, j]
        return output

    def convolve_2d(self, img_2d, kernel):
        """Dodatkowa, zoptymalizowana funkcja do konwolucji na 1 kanale (dla Canny'ego)."""
        k = np.array(kernel)
        pad_img = np.pad(img_2d, ((1, 1), (1, 1)), mode='edge')
        output = np.zeros_like(img_2d, dtype=np.float32)
        
        for i in range(3):
            for j in range(3):
                output += pad_img[i:i+img_2d.shape[0], j:j+img_2d.shape[1]] * k[i, j]
        return output

    def process(self, img):
        img_float = img.astype(np.float32)

        # 1. Filtr uśredniający
        if self.blur_cb.isChecked():
            kernel_blur = [[1/9, 1/9, 1/9], [1/9, 1/9, 1/9], [1/9, 1/9, 1/9]]
            for _ in range(self.blur_slider.value()):
                img_float = self.manual_convolve_3x3(img_float, kernel_blur)

        # 2. Filtr wyostrzający
        if self.sharp_cb.isChecked():
            cw = self.sharp_slider.value()
            kernel_sharp = [[0, -1, 0], [-1, cw, -1], [0, -1, 0]]
            weight_sum = cw - 4
            if weight_sum > 0:
                kernel_sharp = [[val / weight_sum for val in row] for row in kernel_sharp]
            img_float = self.manual_convolve_3x3(img_float, kernel_sharp)

        # 3. Wykrywanie Krawędzi
        if self.edge_cb.isChecked():
            
            # Wymuszenie szarości - realizacja Twojego pomysłu
            if self.edge_gray_cb.isChecked() and len(img_float.shape) == 3:
                R, G, B = img_float[:, :, 0], img_float[:, :, 1], img_float[:, :, 2]
                szary = 0.299 * R + 0.587 * G + 0.114 * B
                img_float = np.stack([szary, szary, szary], axis=-1)

            wybrane = self.edge_combo.currentText()

            if wybrane == "Operator Sobela":
                Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
                Gy = [[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]]
                img_x = self.manual_convolve_3x3(img_float, Gx)
                img_y = self.manual_convolve_3x3(img_float, Gy)
                img_float = np.sqrt(img_x**2 + img_y**2)

            elif wybrane == "Krzyż Robertsa":
                Gx = [[ 0, 0,  0], [ 0, 1,  0], [ 0, 0, -1]]
                Gy = [[ 0,  0, 0], [ 0,  0, 1], [ 0, -1, 0]]
                img_x = self.manual_convolve_3x3(img_float, Gx)
                img_y = self.manual_convolve_3x3(img_float, Gy)
                img_float = np.sqrt(img_x**2 + img_y**2)

            elif wybrane == "Algorytm Canny'ego (NumPy)":
                # KROK 1: Wyodrębnienie pojedynczego kanału 2D (dla wydajności)
                gray_2d = img_float[:, :, 0] if len(img_float.shape) == 3 else img_float

                # KROK 2: Gradienty (Sobel)
                Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
                Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
                Ix = self.convolve_2d(gray_2d, Gx)
                Iy = self.convolve_2d(gray_2d, Gy)
                
                # Amplituda i kierunek wektora
                G = np.hypot(Ix, Iy)
                G = G / G.max() * 255.0 if G.max() > 0 else G
                theta = np.arctan2(Iy, Ix) * 180. / np.pi
                theta[theta < 0] += 180
                
                # KROK 3: Wektoryzowane tłumienie niemaksymalne (NMS)
                M, N = G.shape
                Z = np.zeros((M, N), dtype=np.float32)
                
                # Klasyfikujemy kąty do 4 kierunków (0, 45, 90, 135 stopni)
                q_angle = np.zeros((M, N), dtype=np.uint8)
                q_angle[(theta >= 157.5) | (theta < 22.5)] = 0
                q_angle[(theta >= 22.5) & (theta < 67.5)] = 1
                q_angle[(theta >= 67.5) & (theta < 112.5)] = 2
                q_angle[(theta >= 112.5) & (theta < 157.5)] = 3
                
                G_pad = np.pad(G, 1, mode='constant')
                
                # Wektoryzowane maski do sprawdzania sąsiadów - eliminuje powolne pętle for!
                m0 = (q_angle == 0); Z[m0] = np.where((G[m0] >= G_pad[1:-1, 2:][m0]) & (G[m0] >= G_pad[1:-1, :-2][m0]), G[m0], 0)
                m1 = (q_angle == 1); Z[m1] = np.where((G[m1] >= G_pad[:-2, :-2][m1]) & (G[m1] >= G_pad[2:, 2:][m1]), G[m1], 0)
                m2 = (q_angle == 2); Z[m2] = np.where((G[m2] >= G_pad[:-2, 1:-1][m2]) & (G[m2] >= G_pad[2:, 1:-1][m2]), G[m2], 0)
                m3 = (q_angle == 3); Z[m3] = np.where((G[m3] >= G_pad[:-2, 2:][m3]) & (G[m3] >= G_pad[2:, :-2][m3]), G[m3], 0)
                
                # KROK 4: Podwójne progowanie (Double Thresholding)
                high_thresh = G.max() * 0.15
                low_thresh = high_thresh * 0.5
                res = np.zeros_like(Z)
                res[Z >= high_thresh] = 255
                res[(Z >= low_thresh) & (Z < high_thresh)] = 50 # Słabe krawędzie
                
                # KROK 5: Szybka histereza 
                # Jeśli słaba krawędź dotyka mocnej (w promieniu 3x3), staje się mocną krawędzią
                strong = (res == 255).astype(np.float32)
                connected = self.convolve_2d(strong, np.ones((3,3)))
                res = np.where((res == 50) & (connected > 0), 255, res)
                res[res == 50] = 0 # Odrzucamy resztę osamotnionych słabych krawędzi
                
                # Przywracamy format 3-kanałowy na wyjściu
                img_float = np.stack([res, res, res], axis=-1)

        return np.clip(img_float, 0, 255).astype(np.uint8)