import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

from zakladka import Zakladka
from ui_helper import UIHelper

class Morfologia(Zakladka):
    def __init__(self):
        super().__init__(tytul_modulu="MODUŁ MORFOLOGII", kolor="#2ca02c")

        # --- 1. WYBÓR OPERACJI ---
        self.operacja_cb = UIHelper.create_checkbox("Morfologia", default_state=False, toggled_func=self.changed.emit)
        
        self.operacja_combo = UIHelper.create_combo_box(
            ["Dylatacja", "Erozja", "Otwarcie (Erozja + Dylatacja)", "Zamknięcie (Dylatacja + Erozja)"], 
            changed_func=self.changed.emit
        )

        self.layout.addWidget(self.operacja_cb)
        self.layout.addWidget(self.operacja_combo)

        UIHelper.add_separator(self.layout)

        # --- 2. ROZMIAR MASKI ---
        self.rozmiar_label, self.rozmiar_slider = UIHelper.create_labeled_slider(
            "Rozmiar maski", 3, 15, 3, release_func=self.changed.emit
        )
        
        # Wymuszamy nieparzystość
        self.rozmiar_slider.valueChanged.connect(self.fix_slider_step)
        
        self.layout.addWidget(self.rozmiar_label)
        self.layout.addWidget(self.rozmiar_slider)

        # --- 3. LICZBA ITERACJI ---
        self.iteracje_label, self.iteracje_slider = UIHelper.create_labeled_slider(
            "Liczba powtórzeń", 1, 5, 1, release_func=self.changed.emit
        )
        
        self.layout.addWidget(self.iteracje_label)
        self.layout.addWidget(self.iteracje_slider)

    def fix_slider_step(self, value):
        """Wymusza zatrzymywanie się suwaka tylko na liczbach nieparzystych."""
        if value % 2 == 0:
            self.rozmiar_slider.setValue(value + 1)

    def filtr_min_max(self, img, size, mode='dilation'):
        """Główny silnik morfologiczny oparty na oknach NumPy."""
        pad_w = size // 2
        
        if len(img.shape) == 3:
            pad_width = ((pad_w, pad_w), (pad_w, pad_w), (0, 0))
            axis = (0, 1)
        else:
            pad_width = ((pad_w, pad_w), (pad_w, pad_w))
            axis = (0, 1)

        pad_img = np.pad(img, pad_width, mode='edge')
        windows = sliding_window_view(pad_img, window_shape=(size, size), axis=axis)

        if mode == 'dilation':
            return np.max(windows, axis=(-2, -1))
        else: # erosion
            return np.min(windows, axis=(-2, -1))

    def process(self, img):
        if not self.operacja_cb.isChecked():
            return img

        size = self.rozmiar_slider.value()
        if size % 2 == 0:
            size += 1
            
        iters = self.iteracje_slider.value()
        op = self.operacja_combo.currentText()

        img_float = img.copy()

        for _ in range(iters):
            if op == "Dylatacja":
                img_float = self.filtr_min_max(img_float, size, 'dilation')
                
            elif op == "Erozja":
                img_float = self.filtr_min_max(img_float, size, 'erosion')
                
            elif "Otwarcie" in op:
                img_float = self.filtr_min_max(img_float, size, 'erosion')
                img_float = self.filtr_min_max(img_float, size, 'dilation')
                
            elif "Zamknięcie" in op:
                img_float = self.filtr_min_max(img_float, size, 'dilation')
                img_float = self.filtr_min_max(img_float, size, 'erosion')

        return img_float.astype(np.uint8)
    