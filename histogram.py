import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg

class Histogram(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        #self.setMaximumHeight(180)
        

        # Opcjonalnie: ustawienie białego tła i czarnych osi, 
        # aby wyglądało identycznie jak domyślny Matplotlib
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True) # Wygładzanie krawędzi

        # Tworzymy główny widżet wykresu
        self.plot_widget = pg.PlotWidget()
        
        # Wyłączamy interakcje myszką (przybliżanie/przesuwanie) na samym histogramie
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('left') # Ukrywamy liczby na osi Y
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setXRange(0, 255, padding=0)
        
        layout.addWidget(QLabel("<b>Histogram (RGB):</b>"))
        layout.addWidget(self.plot_widget)
        
        self.cursor_lines = []
        self.max_y = 1 # Przechowuje max wysokość, by wskaźniki miały zawsze 10%

    def reczny_histogram(self, data):
        return np.bincount(data.flatten(), minlength=256)

    def set_cursor(self, wartosc_piksela):
        """Ustawia pozycję wskaźników. Zaktualizowane pod PyQtGraph."""
        if not self.cursor_lines:
            return
            
        wartosci = np.atleast_1d(wartosc_piksela)
        
        # Wskaźnik ma mieć 10% całkowitej wysokości wykresu
        wysokosc_wskaznika = self.max_y * 0.05
        
        for i, line in enumerate(self.cursor_lines):
            if i < len(wartosci):
                val = wartosci[i]
                # W PyQtGraph po prostu zmieniamy dane linii
                line.setData([val, val], [-wysokosc_wskaznika, wysokosc_wskaznika])
                line.show() # Pokazujemy linię (domyślnie po resecie są ukryte)

    def update_histogram(self, img):
        # Czyścimy wykres ze wszystkich linii i wypełnień
        self.plot_widget.clear() 
        self.cursor_lines = []
        self.max_y = 1 
        
        x = np.arange(256)

        if len(img.shape) == 3 and img.shape[2] >= 3:
            # Definiujemy kolory w formacie RGB (PyQtGraph używa krotek)
            kolory = [(255, 0, 0), (0, 255, 0), (0, 0, 255)] 
            
            for i, kolor in enumerate(kolory):
                hist = self.reczny_histogram(img[:, :, i])
                self.max_y = max(self.max_y, hist.max())
                
                # Rysowanie linii i wypełnienia w PyQtGraph
                pen = pg.mkPen(color=kolor, width=1.5)
                # alpha 50 (z 255) dla przezroczystości wypełnienia
                brush = pg.mkBrush(*kolor, 50) 
                
                self.plot_widget.plot(x, hist, pen=pen, fillLevel=0, fillBrush=brush)
                
                # Tworzymy wskaźnik kursora (początkowo ukryty i wyzerowany)
                cursor_pen = pg.mkPen(color=kolor, width=2.5)
                cursor_line = self.plot_widget.plot([0, 0], [0, 0], pen=cursor_pen)
                cursor_line.hide()
                self.cursor_lines.append(cursor_line)
        else:
            hist = self.reczny_histogram(img)
            self.max_y = max(self.max_y, hist.max())
            
            szary = (100, 100, 100)
            pen = pg.mkPen(color=szary, width=2)
            brush = pg.mkBrush(*szary, 80)
            
            self.plot_widget.plot(x, hist, pen=pen, fillLevel=0, fillBrush=brush)
            
            # Wskaźnik dla skali szarości (czerwony lub czarny)
            cursor_pen = pg.mkPen(color=(255, 0, 0), width=2.5)
            cursor_line = self.plot_widget.plot([0, 0], [0, 0], pen=cursor_pen)
            cursor_line.hide()
            self.cursor_lines.append(cursor_line)

        # Dopasowujemy oś Y z lekkim marginesem na górze (5%)
        self.plot_widget.setYRange(-1, self.max_y * 1.05, padding=0)