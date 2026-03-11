import sys
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QFrame)
from PyQt5.QtCore import Qt

from przegladarkaobrazow import PrzegladarkaObrazow

from ekspozycja import Ekspozycja
from filtry import Filtry

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biometria - Projekt 1 (Edytor)")
        self.resize(1200, 700)
        self.original_image = None # Tutaj będziemy trzymać wczytany obraz

        self.main_layout = QHBoxLayout(self)
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        left_layout = QVBoxLayout()
        self.hist_figure = Figure(figsize=(3, 4), dpi=100)
        self.hist_canvas = FigureCanvas(self.hist_figure)
        self.hist_ax = self.hist_figure.add_subplot(111)
        self.hist_ax.set_title("Histogram")
        self.hist_ax.grid(True, alpha=0.3)

        left_layout.addWidget(QLabel("<b>Analiza:</b>"))
        left_layout.addWidget(self.hist_canvas)
        
        frame = QFrame()
        frame.setLayout(left_layout)
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.main_layout.addWidget(frame, stretch=1)

    def setup_center_panel(self):   
        center_layout = QVBoxLayout()

        # Używamy naszej nowej, interaktywnej przeglądarki!
        self.przegladarka = PrzegladarkaObrazow()

        # Przycisk wczytywania
        self.btn_load = QPushButton("Wczytaj zdjęcie z dysku")
        self.btn_load.setMinimumHeight(40)
        self.btn_load.clicked.connect(self.load_image_dialog)

        # NOWOŚĆ: Przycisk Zapisu (na ocenę 4.0)
        self.btn_save = QPushButton("Zapisz przetworzony obraz")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.clicked.connect(lambda: self.przegladarka.zapisz_obraz(self))

        center_layout.addWidget(self.przegladarka)
        
        # Układ poziomy dla przycisków pod obrazkiem
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_save)
        
        center_layout.addLayout(btn_layout)

        self.main_layout.addLayout(center_layout, stretch=3)

    def setup_right_panel(self):
        self.tabs = QTabWidget()
        
        self.tab_ekspozycja = Ekspozycja()
        self.tab_filtry = Filtry()
        
        # Odbieramy sygnały z zakładek i każemy przeliczyć podgląd na żywo
        self.tab_ekspozycja.changed.connect(self.update_image_pipeline)
        self.tab_filtry.changed.connect(self.update_image_pipeline)

        self.tabs.addTab(self.tab_ekspozycja, "Ekspozycja")
        self.tabs.addTab(self.tab_filtry, "Filtry")

        self.main_layout.addWidget(self.tabs, stretch=1)

    def load_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz", "", "Obrazy (*.png *.jpg *.jpeg)")
        if file_path:
            # Wczytanie i standaryzacja do wartości całkowitych 0-255
            img = mpimg.imread(file_path)
            if img.dtype == np.float32: 
                img = (img * 255).astype(np.uint8)
            # Usunięcie kanału alfa jeśli to plik PNG (żeby filtry się nie gubiły)
            if img.shape[-1] == 4:
                img = img[..., :3]

            self.original_image = img
            self.update_image_pipeline() # Odpalenie potoku

    def update_image_pipeline(self):
        """Główny potok, przez który przechodzi obraz."""
        if self.original_image is None:
            return

        # 1. Kopia oryginału
        img = self.original_image.copy()

        # 2. Nakładanie warstw (jak w Photoshopie/RawTherapee)
        img = self.tab_ekspozycja.return_processed_image(img)
        img = self.tab_filtry.return_processed_image(img)


        self.przegladarka.wyswietl_obraz_numpy(img)
        # 3. Wyświetlenie
        # self.image_ax.clear()
        # self.image_ax.imshow(img)
        # self.image_ax.axis('off')
        # self.image_canvas.draw()

        # TODO: Tutaj w przyszłości wywołasz funkcję:
        # self.calculate_and_draw_histogram(self.current_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())