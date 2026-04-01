import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

class Zakladka(QWidget):
    changed = pyqtSignal()

    def __init__(self, tytul_modulu="WŁĄCZ MODUŁ", kolor="#2b78e4"):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        self.master_switch = QCheckBox(tytul_modulu)
        self.master_switch.setChecked(True)
        self.master_switch.setStyleSheet(f"font-weight: bold; color: {kolor};")
        self.master_switch.toggled.connect(self.changed.emit)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        self.layout.addWidget(self.master_switch)
        self.layout.addWidget(line)

    def return_processed_image(self, img):
        """Główna metoda wywoływana z zewnątrz. Zarządza włącznikiem."""
        if not self.master_switch.isChecked():
            return img
        
        return self.process(img)

    def process(self, img):
        """
        Metoda 'abstrakcyjna'. 
        Wymusza na programiście dopisanie jej w każdej nowej zakładce.
        """
        raise NotImplementedError("Musisz zaimplementować metodę 'przetwarzaj_piksele' w klasie dziedziczącej!")