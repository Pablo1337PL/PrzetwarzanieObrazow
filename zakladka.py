import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

class Zakladka(QWidget):
    # Sygnał musi być zdefiniowany na poziomie klasy
    changed = pyqtSignal()

    def __init__(self, tytul_modulu="WŁĄCZ MODUŁ", kolor="#2b78e4"):
        super().__init__()
        
        # Zapisujemy layout jako 'self.layout', aby dzieci miały do niego dostęp
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # GŁÓWNY WŁĄCZNIK ZAKŁADKI (teraz tytuł i kolor można przekazać w parametrze)
        self.master_switch = QCheckBox(tytul_modulu)
        self.master_switch.setChecked(True)
        self.master_switch.setStyleSheet(f"font-weight: bold; color: {kolor};")
        self.master_switch.toggled.connect(self.changed.emit)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        # DODANIE BAZOWYCH WIDŻETÓW DO LAYOUTU (tego brakowało)
        self.layout.addWidget(self.master_switch)
        self.layout.addWidget(line)

    def return_processed_image(self, img):
        """Główna metoda wywoływana z zewnątrz. Zarządza włącznikiem."""
        # Jeśli moduł jest wyłączony, zwracamy nietknięty obraz
        if not self.master_switch.isChecked():
            return img
        
        # Jeśli włączony, wywołujemy logikę specyficzną dla danej zakładki
        return self.process(img)

    def process(self, img):
        """
        Metoda 'abstrakcyjna'. 
        Wymusza na programiście dopisanie jej w każdej nowej zakładce.
        """
        raise NotImplementedError("Musisz zaimplementować metodę 'przetwarzaj_piksele' w klasie dziedziczącej!")