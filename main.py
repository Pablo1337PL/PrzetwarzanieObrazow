import sys
import matplotlib
# Ważne: wymuszamy backend Qt5Agg, bo taką mamy bibliotekę w systemie
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Importujemy backend dla Qt5 (zgodnie z zainstalowaną biblioteką)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ZMIANA: Importujemy z PyQt5 zamiast PyQt6
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QFrame)
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biometria - Projekt 1 (Edytor)")
        self.resize(1200, 700)

        # Główny układ poziomy (3 kolumny)
        self.main_layout = QHBoxLayout(self)

        # --- 1. LEWA KOLUMNA (Histogram) ---
        self.setup_left_panel()

        # --- 2. ŚRODKOWA KOLUMNA (Obraz + Toolbar) ---
        self.setup_center_panel()

        # --- 3. PRAWA KOLUMNA (Zakładki) ---
        self.setup_right_panel()

    def setup_left_panel(self):
        """Tworzy lewy panel z miejscem na histogram."""
        left_layout = QVBoxLayout()
        
        # Tworzymy figurę dla histogramu
        self.hist_figure = Figure(figsize=(3, 4), dpi=100)
        self.hist_canvas = FigureCanvas(self.hist_figure)
        self.hist_ax = self.hist_figure.add_subplot(111)
        self.hist_ax.set_title("Histogram")
        self.hist_ax.set_xlabel("Wartość piksela")
        self.hist_ax.set_ylabel("Liczba")
        self.hist_ax.grid(True, alpha=0.3)

        # Dodajemy do layoutu
        left_layout.addWidget(QLabel("<b>Analiza:</b>"))
        left_layout.addWidget(self.hist_canvas)
        
        # Ramka oddzielająca
        frame = QFrame()
        frame.setLayout(left_layout)
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Stretch=1 oznacza, że zajmie 1 część szerokości
        self.main_layout.addWidget(frame, stretch=1)

    def setup_center_panel(self):
        """Tworzy środkowy panel z obrazem i przyciskiem wczytywania."""
        center_layout = QVBoxLayout()

        # Figura dla głównego obrazu
        self.image_figure = Figure(figsize=(6, 6), dpi=100)
        self.image_canvas = FigureCanvas(self.image_figure)
        self.image_ax = self.image_figure.add_subplot(111)
        self.image_ax.axis('off')  # Ukrywamy osie na start
        self.image_ax.set_title("Brak obrazu")

        # Pasek narzędzi Matplotlib (Zoom, Pan, Save)
        self.toolbar = NavigationToolbar(self.image_canvas, self)

        # Przycisk wczytywania
        self.btn_load = QPushButton("📂 Wczytaj zdjęcie z dysku")
        self.btn_load.setMinimumHeight(40)
        self.btn_load.clicked.connect(self.load_image_dialog)

        center_layout.addWidget(self.toolbar)
        center_layout.addWidget(self.image_canvas)
        center_layout.addWidget(self.btn_load)

        # Stretch=3 - ten panel będzie najszerszy
        self.main_layout.addLayout(center_layout, stretch=3)

    def setup_right_panel(self):
        """Tworzy prawy panel z zakładkami."""
        self.tabs = QTabWidget()
        
        # Przykładowe zakładki (tu dodasz swoje suwaki później)
        tab1 = QWidget()
        tab2 = QWidget()
        
        self.tabs.addTab(tab1, "Ekspozycja")
        self.tabs.addTab(tab2, "Filtry")

        # Stretch=1
        self.main_layout.addWidget(self.tabs, stretch=1)

    def load_image_dialog(self):
        """Otwiera okno dialogowe i wczytuje wybrany plik."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Wybierz obraz", 
            "", 
            "Obrazy (*.png *.jpg *.jpeg *.bmp *.tif)"
        )

        if file_path:
            self.display_image(file_path)

    def display_image(self, path):
        """Wyświetla obraz na środkowym wykresie."""
        # 1. Wczytanie obrazu przez Matplotlib (zwraca tablicę NumPy!)
        self.current_image = mpimg.imread(path)

        # 2. Wyczyszczenie osi i wyświetlenie
        self.image_ax.clear()
        self.image_ax.imshow(self.current_image)
        self.image_ax.axis('off') # Ukrycie osi X/Y dla estetyki
        self.image_ax.set_title("Podgląd")

        # 3. Odświeżenie płótna (canvasu)
        self.image_canvas.draw()

        # TODO: Tutaj w przyszłości wywołasz funkcję:
        # self.calculate_and_draw_histogram(self.current_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ustawienie stylu Fusion (wygląda lepiej niż standardowy Windows/Linux)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())