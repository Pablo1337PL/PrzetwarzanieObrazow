import sys
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')


import matplotlib.image as mpimg

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QFrame,
                             QGridLayout, QCheckBox)
from PyQt5.QtCore import Qt

from przegladarkaobrazow import PrzegladarkaObrazow

from ekspozycja import Ekspozycja
from filtry import Filtry

from histogram import Histogram
from projekcje import ProjekcjaGorna, ProjekcjaBoczna

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
        left_layout.setAlignment(Qt.AlignTop) # Trzyma elementy blisko góry
        
        # 1. Histogram
        self.histogram = Histogram()
        left_layout.addWidget(self.histogram)
        
        # 2. Opcje projekcji
        left_layout.addWidget(QLabel("<b>Sterowanie Projekcjami:</b>"))
        
        self.chk_proj_gora = QCheckBox("Włącz górną projekcję")
        self.chk_proj_gora.setChecked(False)
        self.chk_proj_gora.toggled.connect(self.toggle_projections)
        
        self.chk_proj_lewo = QCheckBox("Włącz boczną projekcję")
        self.chk_proj_lewo.setChecked(False)
        self.chk_proj_lewo.toggled.connect(self.toggle_projections)

        self.chk_proj_rgb = QCheckBox("Projekcje w kolorach RGB")
        self.chk_proj_rgb.setChecked(False)
        # Zmiana trybu RGB odświeża od razu widok
        self.chk_proj_rgb.toggled.connect(self.update_image_pipeline) 

        left_layout.addWidget(self.chk_proj_gora)
        left_layout.addWidget(self.chk_proj_lewo)
        left_layout.addWidget(self.chk_proj_rgb)
        
        frame = QFrame()
        frame.setLayout(left_layout)
        frame.setFrameShape(QFrame.StyledPanel)
        
        self.main_layout.addWidget(frame, stretch=1)
        
        self.main_layout.addWidget(frame, stretch=1)

    def setup_center_panel(self):   
        center_layout = QVBoxLayout()

        # --- SIATKA (GRID) DLA OBRAZU I PROJEKCJI ---
        self.grid = QGridLayout()
        self.grid.setSpacing(0) 

        self.proj_gora = ProjekcjaGorna()
        self.proj_boczna = ProjekcjaBoczna()
        self.przegladarka = PrzegladarkaObrazow()

        self.grid.addWidget(self.proj_gora, 0, 1)   
        self.grid.addWidget(self.proj_boczna, 1, 0) 
        self.grid.addWidget(self.przegladarka, 1, 1)

        self.grid.setColumnStretch(1, 1)
        self.grid.setRowStretch(1, 1)

        # Na starcie aplikujemy stany z checkboxów (ukrywamy projekcje)
        self.toggle_projections()

        center_layout.addLayout(self.grid)

        # --- NASŁUCHIWANIE RUCHU MYSZKĄ ---
        self.przegladarka.pixel_hovered.connect(self.on_pixel_hovered)
        # --- NASŁUCHIWANIE RUCHU I ZMIANY WIDOKU ---
        self.przegladarka.pixel_hovered.connect(self.on_pixel_hovered)
        self.przegladarka.visible_rect_changed.connect(self.update_projections_from_rect)


        # --- PRZYCISKI PLIKÓW ---
        self.btn_load = QPushButton("Wczytaj zdjęcie")
        self.btn_load.clicked.connect(self.load_image_dialog)
        self.btn_save = QPushButton("Zapisz obraz")
        self.btn_save.clicked.connect(lambda: self.przegladarka.zapisz_obraz(self))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_save)
        center_layout.addLayout(btn_layout)

        self.main_layout.addLayout(center_layout, stretch=3)

    
    # NOWA FUNKCJA - Włączanie/wyłączanie wykresów
    def toggle_projections(self):
        """Pokazuje/ukrywa projekcje, dynamicznie zwalniając miejsce na ekranie."""
        self.proj_gora.setVisible(self.chk_proj_gora.isChecked())
        self.proj_boczna.setVisible(self.chk_proj_lewo.isChecked())

    # NOWA FUNKCJA - Przesuwanie linii na wykresach
    def on_pixel_hovered(self, x, y, piksel):
        # Przekazujemy całą tablicę [R, G, B] prosto do histogramu
        self.histogram.set_cursor(piksel) 
        if self.chk_proj_gora.isChecked():
            self.proj_gora.set_cursor(x)
        if self.chk_proj_lewo.isChecked():
            self.proj_boczna.set_cursor(y)

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

        self.current_processed_image = img

        self.przegladarka.wyswietl_obraz_numpy(img)

        self.histogram.update_histogram(img)

    def update_projections_from_rect(self, x, y, w, h):
        """Odbiera koordynaty z przeglądarki i aktualizuje projekcje tylko dla widocznego fragmentu."""
        if not hasattr(self, 'current_processed_image') or self.current_processed_image is None:
            return
            
        # Zapisujemy koordynaty wycięcia, aby poprawić wskaźnik kursora
        self.current_crop_x = x
        self.current_crop_y = y

        # Magia NumPy: wycinamy błyskawicznie tylko widoczny obszar
        widoczny_fragment = self.current_processed_image[y:y+h, x:x+w]
        tryb_rgb = self.chk_proj_rgb.isChecked()

        # Aktualizujemy wykresy (dla optymalizacji - tylko te, które są widoczne)
        if self.chk_proj_gora.isChecked():
            self.proj_gora.update_plot(widoczny_fragment, rgb_mode=tryb_rgb)
        if self.chk_proj_lewo.isChecked():
            self.proj_boczna.update_plot(widoczny_fragment, rgb_mode=tryb_rgb)

    def on_pixel_hovered(self, x, y, piksel):
        self.histogram.set_cursor(piksel)
        
        # Kursor myszki podaje bezwzględną pozycję piksela (np. x=1500)
        # Ale nasz wykres wyświetla tylko wycinek od x=1000. 
        # Zatem dla wykresu kursor jest na pozycji 500.
        rel_x = x - getattr(self, 'current_crop_x', 0)
        rel_y = y - getattr(self, 'current_crop_y', 0)

        if self.chk_proj_gora.isChecked():
            self.proj_gora.set_cursor(rel_x)
        if self.chk_proj_lewo.isChecked():
            self.proj_boczna.set_cursor(rel_y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())