import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PyQt5.QtWidgets import (QVBoxLayout, QCheckBox, QLabel, 
                             QFrame, QSlider, QComboBox, QWidget)
from PyQt5.QtCore import Qt

from zakladka import Zakladka
from ui_helper import UIHelper

class Filtry(Zakladka):
    def __init__(self):
        super().__init__(tytul_modulu="WŁĄCZ MODUŁ FILTRÓW", kolor="#e42b2b")

        self.blur_box = QFrame()
        self.blur_layout = QVBoxLayout(self.blur_box)
        self.blur_layout.setContentsMargins(0, 0, 0, 10) 
        
        self.blur_cb = UIHelper.create_checkbox("Włącz Konwolucję", default_state=False, toggled_func=self.changed.emit)
        
        self.blur_label, self.blur_slider = UIHelper.create_labeled_slider(
            "Siła (iteracje)", 1, 5, 1, release_func=self.changed.emit
        )

        self.blur_combo = UIHelper.create_combo_box(
            [
                "Uśredniający (Zwykły)", 
                "Gaussa (Miękki)", 
                "Płaskorzeźba (Emboss)",
                "Laplasjan (Detekcja Krawędzi)",
                "Własna macierz (Custom)"
            ], 
            changed_func=self.on_blur_mode_changed
        )
        
        self.matrix_grid, self.matrix_inputs = UIHelper.create_3x3_matrix_input(
            [0]*9, text_changed_func=self.on_custom_matrix_edited
        )
        
        self.matrix_widget = QWidget()
        self.matrix_widget.setLayout(self.matrix_grid)
        
        self.blur_layout.addWidget(self.blur_cb)
        self.blur_layout.addWidget(self.blur_combo)
        self.blur_layout.addWidget(self.blur_label)
        self.blur_layout.addWidget(self.blur_slider)
        self.blur_layout.addWidget(self.matrix_widget)
        
        self.sharp_box = QFrame()
        self.sharp_layout = QVBoxLayout(self.sharp_box)
        self.sharp_layout.setContentsMargins(0, 0, 0, 10)
        
        self.sharp_cb = UIHelper.create_checkbox("Filtr Wyostrzający", default_state=False, toggled_func=self.changed.emit)
        self.sharp_label, self.sharp_slider = UIHelper.create_labeled_slider(
            "Waga centralna", 5, 15, 5, release_func=self.changed.emit
        )
        
        self.sharp_layout.addWidget(self.sharp_cb)
        self.sharp_layout.addWidget(self.sharp_label)
        self.sharp_layout.addWidget(self.sharp_slider)

        self.edge_box = QFrame()
        self.edge_layout = QVBoxLayout(self.edge_box)
        self.edge_layout.setContentsMargins(0, 0, 0, 0)

        self.edge_cb = UIHelper.create_checkbox("Wykrywanie krawędzi", default_state=False, toggled_func=self.changed.emit)
        self.edge_gray_cb = UIHelper.create_checkbox("Wymuś odcienie szarości", default_state=True, toggled_func=self.changed.emit)
        self.edge_combo = UIHelper.create_combo_box(
            ["Operator Sobela", "Krzyż Robertsa", "Algorytm Canny'ego"], 
            changed_func=self.changed.emit
        )

        self.edge_layout.addWidget(self.edge_cb)
        self.edge_layout.addWidget(self.edge_gray_cb)
        self.edge_layout.addWidget(self.edge_combo)

        self.layout.addWidget(self.blur_box)
        UIHelper.add_separator(self.layout)
        self.layout.addWidget(self.sharp_box)
        UIHelper.add_separator(self.layout)
        self.layout.addWidget(self.edge_box)

        self.on_blur_mode_changed()

    def set_matrix_values(self, flat_list):
        """Aktualizuje tekst w 9 okienkach na podstawie przekazanej płaskiej listy."""
        for inp in self.matrix_inputs:
            inp.blockSignals(True)
            
        for i, val in enumerate(flat_list):
            formatted_val = f"{val:.3g}"
            self.matrix_inputs[i].setText(formatted_val)
            
        for inp in self.matrix_inputs:
            inp.blockSignals(False)

    def on_blur_mode_changed(self):
        """Ustawia wagi w siatce w zależności od wybranego gotowego filtru."""
        tryb = self.blur_combo.currentText()
        
        if tryb == "Uśredniający (Zwykły)":
            self.set_matrix_values([1/9]*9)
        elif tryb == "Gaussa (Miękki)":
            self.set_matrix_values([1/16, 2/16, 1/16, 2/16, 4/16, 2/16, 1/16, 2/16, 1/16])
        elif tryb == "Płaskorzeźba (Emboss)":
            self.set_matrix_values([-2, -1, 0, -1, 1, 1, 0, 1, 2])
        elif tryb == "Laplasjan (Detekcja Krawędzi)":
            self.set_matrix_values([0, 1, 0, 1, -4, 1, 0, 1, 0])
            
        self.changed.emit()

    def on_custom_matrix_edited(self):
        """Zmienia tryb na Custom, jeśli użytkownik zacznie edytować okienka."""
        if self.blur_combo.currentText() != "Własna macierz (Custom)":
            self.blur_combo.blockSignals(True)
            self.blur_combo.setCurrentIndex(4) 
            self.blur_combo.blockSignals(False)
            
        self.changed.emit()

    def get_custom_kernel(self):
        """Odczytuje wagi z 9 okienek tekstowych i zamienia na macierz 3x3."""
        kernel = []
        for i in range(3):
            row = []
            for j in range(3):
                idx = i * 3 + j
                try:
                    val = float(self.matrix_inputs[idx].text())
                except ValueError:
                    val = 0.0
                row.append(val)
            kernel.append(row)
            
        return kernel

    def convolve(self, img, kernel):
        k = np.array(kernel, dtype=np.float32)
        
        if len(img.shape) == 3:
           pad_width = ((1, 1), (1, 1), (0, 0))
        else:
            pad_width = ((1, 1), (1, 1))
            
        pad_img = np.pad(img, pad_width, mode='edge')
        
        windows = sliding_window_view(pad_img, window_shape=(3, 3), axis=(0, 1))
        output = np.tensordot(windows, k, axes=((-2, -1), (0, 1)))
        return output

    def usrednij(self, img):
        kernel = self.get_custom_kernel()
        kernel_np = np.array(kernel, dtype=np.float32)
        
        suma_wag = np.sum(kernel_np)
        
        if suma_wag != 0:
            kernel_np = kernel_np / suma_wag
        
        for _ in range(self.blur_slider.value()):
            img = self.convolve(img, kernel_np)
            
        return np.clip(img, 0, 255).astype(np.float32)
    

    def process(self, img):
        img_float = img.astype(np.float32)

        if self.blur_cb.isChecked():
            img_float = self.usrednij(img_float)

        if self.sharp_cb.isChecked():
            cw = self.sharp_slider.value()
            kernel_sharp = [[0, -1, 0], [-1, cw, -1], [0, -1, 0]]
            weight_sum = cw - 4
            if weight_sum > 0:
                kernel_sharp = [[val / weight_sum for val in row] for row in kernel_sharp]
            img_float = self.convolve(img_float, kernel_sharp)

        if self.edge_cb.isChecked():
            if self.edge_gray_cb.isChecked() and len(img_float.shape) == 3:
                R, G, B = img_float[:, :, 0], img_float[:, :, 1], img_float[:, :, 2]
                szary = 0.299 * R + 0.587 * G + 0.114 * B
                img_float = np.stack([szary, szary, szary], axis=-1)

            wybrane = self.edge_combo.currentText()

            if wybrane == "Operator Sobela":
                Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
                Gy = [[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]]
                img_x = self.convolve(img_float, Gx)
                img_y = self.convolve(img_float, Gy)
                img_float = np.sqrt(img_x**2 + img_y**2)

            elif wybrane == "Krzyż Robertsa":
                Gx = [[ 0, 0,  0], [ 0, 1,  0], [ 0, 0, -1]]
                Gy = [[ 0,  0, 0], [ 0,  0, 1], [ 0, -1, 0]]
                img_x = self.convolve(img_float, Gx)
                img_y = self.convolve(img_float, Gy)
                #img_float = np.sqrt(img_x**2 + img_y**2)
                img_float = np.hypot(img_x, img_y)
            elif wybrane == "Algorytm Canny'ego":
                gray_2d = img_float[:, :, 0] if len(img_float.shape) == 3 else img_float

                Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
                Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
                Ix = self.convolve(gray_2d, Gx)
                Iy = self.convolve(gray_2d, Gy)
                
                G = np.hypot(Ix, Iy) # <=>  G = sqrt(Ix^2 + Iy^2)
                G = G / G.max() * 255.0 if G.max() > 0 else G
                theta = np.arctan2(Iy, Ix) * 180. / np.pi
                theta[theta < 0] += 180
                
                M, N = G.shape
                Z = np.zeros((M, N), dtype=np.float32)
                
                q_angle = np.zeros((M, N), dtype=np.uint8)
                q_angle[(theta >= 157.5) | (theta < 22.5)] = 0
                q_angle[(theta >= 22.5) & (theta < 67.5)] = 1
                q_angle[(theta >= 67.5) & (theta < 112.5)] = 2
                q_angle[(theta >= 112.5) & (theta < 157.5)] = 3
                
                G_pad = np.pad(G, 1, mode='constant')
                
                m0 = (q_angle == 0); Z[m0] = np.where((G[m0] >= G_pad[1:-1, 2:][m0]) & (G[m0] >= G_pad[1:-1, :-2][m0]), G[m0], 0)
                m1 = (q_angle == 1); Z[m1] = np.where((G[m1] >= G_pad[:-2, :-2][m1]) & (G[m1] >= G_pad[2:, 2:][m1]), G[m1], 0)
                m2 = (q_angle == 2); Z[m2] = np.where((G[m2] >= G_pad[:-2, 1:-1][m2]) & (G[m2] >= G_pad[2:, 1:-1][m2]), G[m2], 0)
                m3 = (q_angle == 3); Z[m3] = np.where((G[m3] >= G_pad[:-2, 2:][m3]) & (G[m3] >= G_pad[2:, :-2][m3]), G[m3], 0)
                
                high_thresh = G.max() * 0.15
                low_thresh = high_thresh * 0.5
                res = np.zeros_like(Z)
                res[Z >= high_thresh] = 255
                res[(Z >= low_thresh) & (Z < high_thresh)] = 50 # Słabe krawędzie
                
                # Jeśli słaba krawędź dotyka mocnej (w promieniu 3x3), staje się mocną krawędzią
                strong = (res == 255).astype(np.float32)
                connected = self.convolve(strong, np.ones((3,3)))
                res = np.where((res == 50) & (connected > 0), 255, res)
                res[res == 50] = 0 # Odrzucamy resztę osamotnionych słabych krawędzi
                
                img_float = np.stack([res, res, res], axis=-1)

        return np.clip(img_float, 0, 255).astype(np.uint8)