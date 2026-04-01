import sys, os
import numpy as np

from PIL import Image

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QFrame,
                             QGridLayout, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt


from Workers import LoadWorker, SaveWorker, ProcessWorker

from przegladarkaobrazow import PrzegladarkaObrazow

from ekspozycja import Ekspozycja
from filtry import Filtry

from histogram import Histogram
from projekcje import ProjekcjaGorna, ProjekcjaBoczna
from metadane import Metadane
from morfologia import Morfologia

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biometria - Projekt 1 (Edytor)")
        self.resize(1200, 700)
        self.original_image = None # Tutaj będziemy trzymać wczytany obraz
        self.file_path = None
        
        self.main_layout = QHBoxLayout(self)
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

        self.file_path = os.path.join("obrazki", "grzyb.jpg")
        self.btn_load.setEnabled(False)
        self.btn_load.setText("Wczytywanie...")

        self.load_thread = LoadWorker(self.file_path)
        self.load_thread.success.connect(self.on_load_success)
        self.load_thread.error.connect(self.on_load_error)
        
        self.load_thread.start()
    
    def add_separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #cccccc;")
        layout.addWidget(line)

    def setup_left_panel(self):
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Histogram
        self.histogram = Histogram()
        left_layout.addWidget(self.histogram, stretch=1)
        
        self.add_separator(left_layout)
        # 2. Opcje projekcji

        projekcje_layout = QVBoxLayout()
        projekcje_layout.setAlignment(Qt.AlignTop)
        
        projekcje_layout.addWidget(QLabel("<b>Sterowanie Projekcjami:</b>"))
        
        self.chk_proj_gora = QCheckBox("Włącz górną projekcję")
        self.chk_proj_gora.setChecked(False)
        self.chk_proj_gora.toggled.connect(self.toggle_projections)
        
        self.chk_proj_lewo = QCheckBox("Włącz boczną projekcję")
        self.chk_proj_lewo.setChecked(False)
        self.chk_proj_lewo.toggled.connect(self.toggle_projections)

        self.chk_proj_rgb = QCheckBox("Projekcje w kolorach RGB")
        self.chk_proj_rgb.setChecked(False)
        self.chk_proj_rgb.toggled.connect(self.update_image_pipeline) 

        projekcje_layout.addWidget(self.chk_proj_gora)
        projekcje_layout.addWidget(self.chk_proj_lewo)
        projekcje_layout.addWidget(self.chk_proj_rgb)
        
        left_layout.addLayout(projekcje_layout, stretch=1)

        self.add_separator(left_layout)

        self.metadane = Metadane()
        left_layout.addWidget(self.metadane, stretch=2)
        
        frame = QFrame()
        frame.setLayout(left_layout)
        frame.setFrameShape(QFrame.StyledPanel)
        
        self.main_layout.addWidget(frame, stretch=1)

    def setup_center_panel(self):   
        center_layout = QVBoxLayout()

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

        self.toggle_projections()

        center_layout.addLayout(self.grid)

        self.przegladarka.pixel_hovered.connect(self.on_pixel_hovered)
        self.przegladarka.pixel_hovered.connect(self.on_pixel_hovered)
        self.przegladarka.visible_rect_changed.connect(self.update_projections_from_rect)


        self.btn_load = QPushButton("Wczytaj zdjęcie")
        self.btn_load.clicked.connect(self.load_image_dialog)
        self.btn_save = QPushButton("Zapisz obraz")
        self.btn_save.clicked.connect(self.save_image_dialog)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_save)
        center_layout.addLayout(btn_layout)

        self.main_layout.addLayout(center_layout, stretch=6)

    
    def toggle_projections(self):
        """Pokazuje/ukrywa projekcje, dynamicznie zwalniając miejsce na ekranie."""
        self.proj_gora.setVisible(self.chk_proj_gora.isChecked())
        self.proj_boczna.setVisible(self.chk_proj_lewo.isChecked())

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
        self.tab_morfologia = Morfologia()
        
        self.tab_ekspozycja.changed.connect(self.update_image_pipeline)
        self.tab_filtry.changed.connect(self.update_image_pipeline)
        self.tab_morfologia.changed.connect(self.update_image_pipeline)

        self.tabs.addTab(self.tab_ekspozycja, "Ekspozycja")
        self.tabs.addTab(self.tab_filtry, "Filtry")
        self.tabs.addTab(self.tab_morfologia, "Morfologia")
        
        self.main_layout.addWidget(self.tabs, stretch=2)

    def load_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz", "", "Obrazy (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.file_path = file_path

            self.btn_load.setEnabled(False)
            self.btn_load.setText("Wczytywanie...")

            self.load_thread = LoadWorker(self.file_path)
            self.load_thread.success.connect(self.on_load_success)
            self.load_thread.error.connect(self.on_load_error)
            
            self.load_thread.start()

    def on_load_success(self, img_array):
        """Odbiera przeliczoną macierz NumPy i puszcza ją w potok."""
        self.btn_load.setEnabled(True)
        self.btn_load.setText("Wczytaj zdjęcie")

        if hasattr(self, 'metadane'):
            self.metadane.wczytaj_dane(self.file_path)

        self.original_image = img_array
        self.update_image_pipeline()

    def on_load_error(self, error_message):
        """Obsługa błędu przy wczytywaniu."""
        self.btn_load.setEnabled(True)
        self.btn_load.setText("Wczytaj zdjęcie")
        QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać pliku:\n{error_message}")
    
    def save_image_dialog(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            return

        save_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Zapisz obraz jako...", 
            "", 
            "Plik PNG (*.png);;Plik JPEG (*.jpg *.jpeg)"
        )

        if not save_path:
            return

        path_lower = save_path.lower()
        if not (path_lower.endswith('.png') or path_lower.endswith('.jpg') or path_lower.endswith('.jpeg')):
            if "PNG" in selected_filter:
                save_path += ".png"
            elif "JPEG" in selected_filter:
                save_path += ".jpg"

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Zapisywanie...")

        self.save_thread = SaveWorker(self.file_path, save_path, self.process_image)
        
        self.save_thread.success.connect(self.on_save_success)
        self.save_thread.error.connect(self.on_save_error)
        
        self.save_thread.start()

    def on_save_success(self):
        """Wywoływane, gdy wątek zaraportuje sukces."""
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Zapisz obraz")
        QMessageBox.information(self, "Sukces", "Obraz zapisany pomyślnie!")

    def on_save_error(self, error_message):
        """Wywoływane, gdy wątek napotka problem."""
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Zapisz obraz")
        QMessageBox.critical(self, "Błąd", f"Nie można zapisać pliku:\n{error_message}")


    def process_image(self, img):
        img = self.tab_ekspozycja.return_processed_image(img)
        img = self.tab_filtry.return_processed_image(img)
        img = self.tab_morfologia.return_processed_image(img)
        return img

    def update_image_pipeline(self):
        """Rozpoczyna asynchroniczny potok w tle (nie blokuje GUI)."""
        if getattr(self, 'original_image', None) is None:
            return

        if hasattr(self, 'process_thread') and self.process_thread.isRunning():
            self.process_thread.is_cancelled = True
            self.process_thread.wait() # Czekamy ułamek sekundy na zakończenie

        img_copy = self.original_image.copy()

        self.process_thread = ProcessWorker(img_copy, self.process_image)
        self.process_thread.finished_signal.connect(self.on_processing_finished)
        self.process_thread.start()

    def on_processing_finished(self, processed_img):
        """Ta funkcja wywołuje się automatycznie, gdy wątek skończy liczyć."""
        self.current_processed_image = processed_img

        self.przegladarka.wyswietl_obraz_numpy(processed_img)

        self.histogram.update_histogram(processed_img)
        
    def update_projections_from_rect(self, x, y, w, h):
        """Odbiera koordynaty z przeglądarki i aktualizuje projekcje tylko dla widocznego fragmentu."""
        if not hasattr(self, 'current_processed_image') or self.current_processed_image is None:
            return
            
        self.current_crop_x = x
        self.current_crop_y = y

        widoczny_fragment = self.current_processed_image[y:y+h, x:x+w]
        tryb_rgb = self.chk_proj_rgb.isChecked()

        if self.chk_proj_gora.isChecked():
            self.proj_gora.update_plot(widoczny_fragment, rgb_mode=tryb_rgb)
        if self.chk_proj_lewo.isChecked():
            self.proj_boczna.update_plot(widoczny_fragment, rgb_mode=tryb_rgb)

    def on_pixel_hovered(self, x, y, piksel):
        self.histogram.set_cursor(piksel)
        
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