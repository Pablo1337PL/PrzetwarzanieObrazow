import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QLabel, QFrame, QSlider
from PyQt5.QtCore import Qt

# Importujemy klasę abstrakcyjną (upewnij się, że masz ją w pliku zakladka.py)
from zakladka import Zakladka

class Filtry(Zakladka):
    def __init__(self):
        # 1. Wywołanie konstruktora rodzica (ustawia główny przełącznik i layout)
        super().__init__(tytul_modulu="WŁĄCZ MODUŁ FILTRÓW", kolor="#e42b2b")

        # --- 2. FILTR UŚREDNIAJĄCY ---
        self.blur_box = QFrame()
        self.blur_layout = QVBoxLayout(self.blur_box)
        self.blur_layout.setContentsMargins(0, 0, 0, 10) # Drobny margines na dole
        
        self.blur_cb = QCheckBox("Filtr Uśredniający")
        self.blur_cb.toggled.connect(self.changed.emit)
        self.blur_cb.toggled.connect(self.toggle_blur_params) # Aktywacja slidera
        
        self.blur_label = QLabel("Siła rozmycia (iteracje): 1")
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 5) # Od 1 do 5 iteracji
        self.blur_slider.setValue(1)
        self.blur_slider.setEnabled(False) # Zablokowany póki checkbox jest odznaczony
        self.blur_slider.valueChanged.connect(self.update_blur_label)
        
        self.blur_layout.addWidget(self.blur_cb)
        self.blur_layout.addWidget(self.blur_label)
        self.blur_layout.addWidget(self.blur_slider)
        
        # --- 3. FILTR WYOSTRZAJĄCY ---
        self.sharp_box = QFrame()
        self.sharp_layout = QVBoxLayout(self.sharp_box)
        self.sharp_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sharp_cb = QCheckBox("Filtr Wyostrzający")
        self.sharp_cb.toggled.connect(self.changed.emit)
        self.sharp_cb.toggled.connect(self.toggle_sharp_params)
        
        self.sharp_label = QLabel("Waga centralna (łagodność): 5")
        self.sharp_slider = QSlider(Qt.Horizontal)
        self.sharp_slider.setRange(5, 15) # Maska np. od 5 (mocne) do 15 (słabe wyostrzanie)
        self.sharp_slider.setValue(5)
        self.sharp_slider.setEnabled(False)
        self.sharp_slider.valueChanged.connect(self.update_sharp_label)
        
        self.sharp_layout.addWidget(self.sharp_cb)
        self.sharp_layout.addWidget(self.sharp_label)
        self.sharp_layout.addWidget(self.sharp_slider)

        # --- 4. DODANIE DO GŁÓWNEGO LAYOUTU (Z klasy Zakladka) ---
        self.layout.addWidget(self.blur_box)
        
        # Opcjonalna linia rozdzielająca filtry
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #cccccc;")
        self.layout.addWidget(separator)
        
        self.layout.addWidget(self.sharp_box)

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

    # --- LOGIKA PRZETWARZANIA (Wymóg ręcznej implementacji algorytmów) ---
    def manual_convolve_3x3(self, img, kernel):
        """Ręczna implementacja splotu (konwolucji) na tablicach NumPy bez gotowych bibliotek przetwarzania."""
        k = np.array(kernel)
        # Margines, by krawędzie nie wywalały błędów indeksowania
        pad_img = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode='edge')
        output = np.zeros_like(img, dtype=np.float32)

        # Nakładamy maskę pętlą (wymóg implementacji ręcznej projektu)
        for i in range(3):
            for j in range(3):
                output += pad_img[i:i+img.shape[0], j:j+img.shape[1]] * k[i, j]
        return output

    def process(self, img):
        """
        Główna metoda wywoływana przez klasę 'Zakladka'.
        Aplikuje filtry kaskadowo (jeden po drugim), jeśli są zaznaczone.
        """
        img_float = img.astype(np.float32)

        # 1. Aplikacja filtra uśredniającego
        if self.blur_cb.isChecked():
            kernel_blur = [[1/9, 1/9, 1/9], 
                           [1/9, 1/9, 1/9], 
                           [1/9, 1/9, 1/9]]
            # Aplikujemy rozmycie wielokrotnie na podstawie wartości slidera
            iterations = self.blur_slider.value()
            for _ in range(iterations):
                img_float = self.manual_convolve_3x3(img_float, kernel_blur)

        # 2. Aplikacja filtra wyostrzającego
        if self.sharp_cb.isChecked():
            center_weight = self.sharp_slider.value()
            
            # Tworzymy maskę dynamicznie ze slidera
            kernel_sharp = [[ 0, -1,  0], 
                            [-1, center_weight, -1], 
                            [ 0, -1,  0]]
            
            # Normalizujemy maskę (aby zachować stałą jasność obrazu, suma wag powinna = 1)
            weight_sum = center_weight - 4
            if weight_sum > 0:
                kernel_sharp = [[val / weight_sum for val in row] for row in kernel_sharp]
            
            img_float = self.manual_convolve_3x3(img_float, kernel_sharp)

        # Zwracamy przycięte wartości do bezpiecznego zakresu 0-255 dla 8-bitowego obrazu RGB
        return np.clip(img_float, 0, 255).astype(np.uint8)