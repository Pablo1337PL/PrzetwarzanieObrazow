import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class ProjekcjaGorna(QWidget):
    """Projekcja po kolumnach (oś X), kładziona NAD obrazkiem."""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(120) 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Ustawienia kolorystyki PyQtGraph, aby pasowała do reszty aplikacji
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('left') # Ukrywamy liczby na osi Y
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        layout.addWidget(self.plot_widget)
        
        # Nieskończona pionowa linia kursora (domyślnie ukryta)
        self.cursor_line = pg.InfiniteLine(angle=90, pen=pg.mkPen(color='r', style=Qt.DashLine, width=1.5))
        self.cursor_line.hide()
        self.plot_widget.addItem(self.cursor_line)

    def update_plot(self, img, rgb_mode=False):
        # Czyścimy wykres, ale zachowujemy linię kursora
        self.plot_widget.clear()
        self.plot_widget.addItem(self.cursor_line)
        
        szerokosc = img.shape[1]
        x_vals = np.arange(szerokosc)

        if rgb_mode and len(img.shape) == 3 and img.shape[2] >= 3:
            kolory = [(255, 10, 10), (10, 255, 10), (10, 10, 255)]
            for i, kolor in enumerate(kolory):
                proj = np.sum(img[:, :, i], axis=0)
                pen = pg.mkPen(color=kolor, width=1.5)
                brush = pg.mkBrush(*kolor, 50) # Alpha 50 dla wypełnienia
                self.plot_widget.plot(x_vals, proj, pen=pen, fillLevel=0, fillBrush=brush)
        else:
            gray = np.mean(img, axis=2) if len(img.shape) == 3 else img
            proj = np.sum(gray, axis=0)
            
            # Kolor fioletowy (#884499) dla skali szarości
            fiolet = (136, 68, 153)
            pen = pg.mkPen(color=fiolet, width=1.5)
            brush = pg.mkBrush(*fiolet, 80)
            self.plot_widget.plot(x_vals, proj, pen=pen, fillLevel=0, fillBrush=brush)
        
        self.plot_widget.setXRange(0, szerokosc, padding=0)

    def set_cursor(self, x):
        self.cursor_line.setPos(x)
        self.cursor_line.show()


class ProjekcjaBoczna(QWidget):
    """Projekcja po wierszach (oś Y), kładziona PO LEWEJ stronie obrazka."""
    def __init__(self):
        super().__init__()
        self.setFixedWidth(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom') # Ukrywamy liczby na osi X
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Kluczowe: Odwracamy oś Y, aby punkt 0 był na górze (jak na zdjęciu)
        self.plot_widget.getViewBox().invertY(True)
        
        layout.addWidget(self.plot_widget)
        
        # Pozioma linia kursora (angle=0)
        self.cursor_line = pg.InfiniteLine(angle=0, pen=pg.mkPen(color='r', style=Qt.DashLine, width=1.5))
        self.cursor_line.hide()
        self.plot_widget.addItem(self.cursor_line)

    def update_plot(self, img, rgb_mode=False):
        self.plot_widget.clear()
        self.plot_widget.addItem(self.cursor_line)
        
        wysokosc = img.shape[0]
        y_vals = np.arange(wysokosc)
        
        # Pusta krzywa (zero na osi X) do narysowania horyzontalnego wypełnienia
        zero_curve = pg.PlotCurveItem([0] * wysokosc, y_vals)

        if rgb_mode and len(img.shape) == 3 and img.shape[2] >= 3:
            kolory = [(255, 10, 10), (10, 255, 10), (10, 10, 255)]
            for i, kolor in enumerate(kolory):
                proj = np.sum(img[:, :, i], axis=1)
                
                pen = pg.mkPen(color=kolor, width=1.5)
                brush = pg.mkBrush(*kolor, 50)
                
                # Rysujemy linię (X = wartość, Y = wiersz)
                data_curve = pg.PlotCurveItem(proj, y_vals, pen=pen)
                # Wypełniamy pomiędzy naszą linią a zerem
                fill = pg.FillBetweenItem(data_curve, zero_curve, brush=brush)
                
                self.plot_widget.addItem(data_curve)
                self.plot_widget.addItem(fill)
        else:
            gray = np.mean(img, axis=2) if len(img.shape) == 3 else img
            proj = np.sum(gray, axis=1) 
            
            # Kolor morski (#449988) dla skali szarości
            morski = (68, 153, 136)
            pen = pg.mkPen(color=morski, width=1.5)
            brush = pg.mkBrush(*morski, 80)
            
            data_curve = pg.PlotCurveItem(proj, y_vals, pen=pen)
            fill = pg.FillBetweenItem(data_curve, zero_curve, brush=brush)
            
            self.plot_widget.addItem(data_curve)
            self.plot_widget.addItem(fill)
        
        self.plot_widget.setYRange(0, wysokosc, padding=0)

    def set_cursor(self, y):
        self.cursor_line.setPos(y)
        self.cursor_line.show()