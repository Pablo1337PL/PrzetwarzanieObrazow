from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from PIL import Image


class ProcessWorker(QThread):
    finished_signal = pyqtSignal(object)

    def __init__(self, img, process_func):
        super().__init__()
        self.img = img
        self.process_func = process_func
        self.is_cancelled = False

    def run(self):
        try:
            processed_img = self.process_func(self.img)

            if not self.is_cancelled:
                self.finished_signal.emit(processed_img)
                
        except Exception as e:
            print(f"Błąd w wątku przetwarzania: {e}")



class LoadWorker(QThread):
    success = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Ten kod wykonuje się w tle, nie blokując interfejsu."""
        try:
            pil_img = Image.open(self.file_path)
            pil_img = pil_img.convert('RGB')
            img = np.array(pil_img)

            # 720×480 = 345_600
            # 1280×720 = 921_600
            docelowe_piksele = 921_600
            obecne_piksele = img.shape[1] * img.shape[0]

            if obecne_piksele > docelowe_piksele:
                stosunek = obecne_piksele / docelowe_piksele
                skala = max(2, int(np.round(np.sqrt(stosunek))))
                img = img[::skala, ::skala, :]

            self.success.emit(img)

        except Exception as e:
            self.error.emit(str(e))



class SaveWorker(QThread):
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_path, save_path, process_func):
        super().__init__()
        self.file_path = file_path
        self.save_path = save_path
        self.process_func = process_func 

    def run(self):
        """Ta metoda uruchamia się w tle, gdy wywołamy .start()"""
        try:
            pil_img = Image.open(self.file_path)
            pil_img = pil_img.convert('RGB')
            img = np.array(pil_img)
            
            img = self.process_func(img) 
            
            Image.fromarray(img).save(self.save_path)
            
            self.success.emit()
            
        except Exception as e:
            self.error.emit(str(e))