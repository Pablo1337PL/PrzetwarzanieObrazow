import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Histogram(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.uklad_wykresu()
        
        layout.addWidget(QLabel("<b>Histogram (RGB):</b>"))
        layout.addWidget(self.canvas)
        self.cursor_lines = []

    def uklad_wykresu(self):
        self.ax.clear()
        self.ax.set_xlim([0, 255])
        self.ax.grid(True, alpha=0.3)
        self.ax.set_yticks([]) 

    def reczny_histogram(self, data):
        return np.bincount(data.flatten(), minlength=256)

    def set_cursor(self, wartosc_piksela):
        """Ustawia pozycję wskaźników. Przyjmuje 1 wartość (szary) lub 3 (RGB)."""
        if not hasattr(self, 'cursor_lines') or not self.cursor_lines:
            return
            
        # Zamienia pojedynczą liczbę lub listę [R,G,B] na płaską tablicę NumPy
        wartosci = np.atleast_1d(wartosc_piksela)
        
        # Aktualizujemy każdą linię (R, G, B) przypisując jej odpowiednią wartość
        for i, line in enumerate(self.cursor_lines):
            if i < len(wartosci):
                val = wartosci[i]
                line.set_xdata([val, val])
                line.set_alpha(1.0) # Pokazujemy linię
                
        self.canvas.draw_idle()

    def update_histogram(self, img):
        self.uklad_wykresu()
        self.cursor_lines = [] # Resetujemy linie przy nowym obrazie
        
        x = np.arange(256)

        if len(img.shape) == 3 and img.shape[2] >= 3:
            kolory = ['red', 'green', 'blue']
            
            for i, kolor in enumerate(kolory):
                hist = self.reczny_histogram(img[:, :, i])
                self.ax.plot(x, hist, color=kolor, alpha=0.7, linewidth=1.5)
                self.ax.fill_between(x, hist, color=kolor, alpha=0.15)
                
                # Tworzymy 3 krótkie linie na dole (ymax=0.1 -> 10% wysokości)
                line = self.ax.axvline(x=0, color=kolor, ymin=0, ymax=0.1, linewidth=2.5, alpha=0)
                self.cursor_lines.append(line)
        else:
            hist = self.reczny_histogram(img)
            self.ax.plot(x, hist, color='gray', linewidth=2)
            self.ax.fill_between(x, hist, color='gray', alpha=0.3)
            
            # Jedna krótka linia dla obrazu w skali szarości
            line = self.ax.axvline(x=0, color='black', ymin=0, ymax=0.1, linewidth=2.5, alpha=0)
            self.cursor_lines.append(line)

        self.canvas.draw()