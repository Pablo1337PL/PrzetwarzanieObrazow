import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QTransform
from PyQt5.QtCore import Qt

class PrzegladarkaObrazow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Włączenie łapania i przesuwania obrazka (Pan)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Ukrycie pasków przewijania dla lepszego wyglądu
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.obecny_pixmap = None
        self.obecny_obraz_numpy = None # Przechowujemy też oryginalną tablicę do zapisu

    def wheelEvent(self, event):
        """Obsługa przybliżania/oddalania (Zoom) rolką myszy."""
        if self.obecny_pixmap is None:
            return

        # Krok powiększenia
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Sprawdzamy, w którą stronę kręci się rolka
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Skalowanie widoku
        self.scale(zoom_factor, zoom_factor)

    def wyswietl_obraz_numpy(self, img_array):
        """Konwertuje tablicę NumPy na QPixmap i wyświetla (zabezpieczone przed błędami pamięci)."""
        # 1. Zabezpieczenie: upewniamy się, że tablica jest w ciągłym bloku pamięci C
        img_array = np.ascontiguousarray(img_array)
        self.obecny_obraz_numpy = img_array
        
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        
        # 2. Tworzymy QImage z pamięci
        q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 3. Zabezpieczenie: Robimy .copy(), aby Qt wzięło pamięć na własność!
        self.obecny_pixmap = QPixmap.fromImage(q_img.copy())
        
        self.scene.clear()
        self.scene.addPixmap(self.obecny_pixmap)
        self.setSceneRect(self.scene.itemsBoundingRect())

    def zapisz_obraz(self, parent_window):
        """Bezpieczny zapis pliku z wymuszaniem poprawnego rozszerzenia."""
        if self.obecny_pixmap is None:
            return

        import os

        # QFileDialog zwraca ścieżkę oraz użyty filtr
        file_path, filtr_str = QFileDialog.getSaveFileName(
            parent_window, 
            "Zapisz obraz", 
            "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )

        if file_path:
            # 1. Sprawdzamy, czy użytkownik wpisał rozszerzenie (np. .jpg)
            _, ext = os.path.splitext(file_path)
            
            # 2. Jeśli nie wpisał, dodajemy je ręcznie na podstawie wybranego filtra!
            if not ext:
                if "PNG" in filtr_str:
                    file_path += ".png"
                elif "JPEG" in filtr_str or "JPG" in filtr_str:
                    file_path += ".jpg"
                elif "BMP" in filtr_str:
                    file_path += ".bmp"

            # 3. Zapisujemy - teraz Qt dokładnie wie, w jakim formacie zapisać
            sukces = self.obecny_pixmap.save(file_path)
            
            if sukces:
                QMessageBox.information(parent_window, "Sukces", f"Zapisano w:\n{file_path}")
            else:
                QMessageBox.critical(parent_window, "Błąd", f"Niestety, nie udało się zapisać pliku w:\n{file_path}")