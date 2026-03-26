from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
import numpy as np


class ProcessWorker(QThread):
    finished_signal = pyqtSignal(object)

    def __init__(self, img, process_func):
        super().__init__()
        self.img = img
        self.process_func = process_func
        self.is_cancelled = False

    def run(self):
        try:
            # Wywołujemy Twoją funkcję process_image w tle!
            processed_img = self.process_func(self.img)

            # Jeśli użytkownik nie ruszył znowu suwakiem, wysyłamy wynik
            if not self.is_cancelled:
                self.finished_signal.emit(processed_img)
                
        except Exception as e:
            print(f"Błąd w wątku przetwarzania: {e}")



class LoadWorker(QThread):
    # Sygnały do komunikacji z głównym oknem
    success = pyqtSignal(object) # Przesyła gotową macierz NumPy
    error = pyqtSignal(str)      # Przesyła treść błędu

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Ten kod wykonuje się w tle, nie blokując interfejsu."""
        try:
            # 1. Wczytanie i standaryzacja z PIL
            pil_img = Image.open(self.file_path)
            pil_img = pil_img.convert('RGB')
            img = np.array(pil_img)

            # 2. Błyskawiczna optymalizacja wielkości do ~720p
            docelowe_piksele = 921_600
            obecne_piksele = img.shape[1] * img.shape[0]

            if obecne_piksele > docelowe_piksele:
                stosunek = obecne_piksele / docelowe_piksele
                skala = max(2, int(np.round(np.sqrt(stosunek))))
                img = img[::skala, ::skala, :]

            # 3. Wysyłamy gotowy obraz do interfejsu
            self.success.emit(img)

        except Exception as e:
            self.error.emit(str(e))



class SaveWorker(QThread):
    # Definiujemy sygnały, które wątek wyśle do głównego okna po zakończeniu pracy
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_path, save_path, process_func):
        super().__init__()
        self.file_path = file_path
        self.save_path = save_path
        # Przekazujemy wskaźnik do funkcji process_image z głównej klasy
        self.process_func = process_func 

    def run(self):
        """Ta metoda uruchamia się w tle, gdy wywołamy .start()"""
        try:
            pil_img = Image.open(self.file_path)
            pil_img = pil_img.convert('RGB')
            img = np.array(pil_img)
            
            # Przetwarzanie pełnej rozdzielczości (może zająć kilka sekund)
            img = self.process_func(img) 
            
            # Zapis na dysk
            Image.fromarray(img).save(self.save_path)
            
            # Informujemy główne okno, że wszystko się udało!
            self.success.emit()
            
        except Exception as e:
            # W razie błędu, wysyłamy jego treść do głównego okna
            self.error.emit(str(e))