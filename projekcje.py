import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ProjekcjaGorna(QWidget):
    """Projekcja po kolumnach (oś X), kładziona NAD obrazkiem."""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(120) 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)
        self.cursor_line = None

    def update_plot(self, img, rgb_mode=False):
        self.ax.clear()
        
        # Oś X ma odpowiadać szerokości obrazka
        szerokosc = img.shape[1]

        if rgb_mode and len(img.shape) == 3 and img.shape[2] >= 3:
            kolory = ['red', 'green', 'blue']
            for i, kolor in enumerate(kolory):
                proj = np.sum(img[:, :, i], axis=0) # Suma w kolumnach dla danego kanału
                self.ax.plot(proj, color=kolor, linewidth=1, alpha=0.7)
                self.ax.fill_between(range(len(proj)), proj, color=kolor, alpha=0.15)
        else:
            gray = np.mean(img, axis=2) if len(img.shape) == 3 else img
            proj = np.sum(gray, axis=0)
            self.ax.plot(proj, color='#884499', linewidth=1)
            self.ax.fill_between(range(len(proj)), proj, color='#884499', alpha=0.3)
        
        self.ax.set_xlim([0, szerokosc])
        self.ax.set_yticks([]) 
        self.ax.margins(x=0)
        self.figure.tight_layout(pad=0.2)
        
        self.cursor_line = self.ax.axvline(x=0, color='red', linestyle='--', alpha=0)
        self.canvas.draw()

    def set_cursor(self, x):
        if self.cursor_line:
            self.cursor_line.set_xdata([x, x])
            self.cursor_line.set_alpha(0.8)
            self.canvas.draw_idle()


class ProjekcjaBoczna(QWidget):
    """Projekcja po wierszach (oś Y), kładziona PO LEWEJ stronie obrazka."""
    def __init__(self):
        super().__init__()
        self.setFixedWidth(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)
        self.cursor_line = None

    def update_plot(self, img, rgb_mode=False):
        self.ax.clear()
        
        wysokosc = img.shape[0]

        if rgb_mode and len(img.shape) == 3 and img.shape[2] >= 3:
            kolory = ['red', 'green', 'blue']
            for i, kolor in enumerate(kolory):
                proj = np.sum(img[:, :, i], axis=1) # Suma w wierszach
                y_vals = np.arange(len(proj))
                self.ax.plot(proj, y_vals, color=kolor, linewidth=1, alpha=0.7)
                self.ax.fill_betweenx(y_vals, 0, proj, color=kolor, alpha=0.15)
        else:
            gray = np.mean(img, axis=2) if len(img.shape) == 3 else img
            proj = np.sum(gray, axis=1) 
            y_vals = np.arange(len(proj))
            self.ax.plot(proj, y_vals, color='#449988', linewidth=1)
            self.ax.fill_betweenx(y_vals, 0, proj, color='#449988', alpha=0.3)
        
        self.ax.set_ylim([wysokosc, 0]) # Oś Y odwrócona!
        self.ax.set_xticks([])
        self.ax.margins(y=0)
        self.figure.tight_layout(pad=0.2)
        
        self.cursor_line = self.ax.axhline(y=0, color='red', linestyle='--', alpha=0)
        self.canvas.draw()

    def set_cursor(self, y):
        if self.cursor_line:
            self.cursor_line.set_ydata([y, y])
            self.cursor_line.set_alpha(0.8)
            self.canvas.draw_idle()