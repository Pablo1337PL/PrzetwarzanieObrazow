from PyQt5.QtWidgets import QSlider, QFrame, QCheckBox, QLabel, QComboBox, QVBoxLayout, QGridLayout, QLineEdit, QWidget
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QDoubleValidator

class UIHelper:
    """Klasa narzędziowa do szybkiego generowania powtarzalnych elementów interfejsu."""

    @staticmethod
    def add_separator(layout):
        """Dodaje poziomą linię oddzielającą do wybranego layoutu."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #cccccc; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(line)
        return line

    @staticmethod
    def create_checkbox(text, default_state=False, toggled_func=None):
        """Tworzy gotowego checkboxa z opcjonalnym podpięciem funkcji."""
        cb = QCheckBox(text)
        cb.setChecked(default_state)
        if toggled_func:
            cb.toggled.connect(toggled_func)
        return cb

    @staticmethod
    def create_combo_box(items, default_index=0, changed_func=None):
        """Tworzy rozwijaną listę (QComboBox)."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(default_index)
        if changed_func:
            combo.currentIndexChanged.connect(changed_func)
        return combo

    @staticmethod
    def create_labeled_slider(prefix_text, min_val, max_val, default, release_func=None):
        """
        Generuje etykietę i suwak. 
        Automatycznie łączy je ze sobą, aby etykieta aktualizowała się sama w czasie rzeczywistym!
        Zwraca krotkę: (QLabel, QSlider)
        """
        label = QLabel(f"{prefix_text}: {default}")
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        
        slider.valueChanged.connect(lambda v: label.setText(f"{prefix_text}: {v}"))
        
        if release_func:
            slider.sliderReleased.connect(release_func)
            
        return label, slider
    
    @staticmethod
    def create_combo_box(items, default_index=0, changed_func=None):
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(default_index)
        if changed_func:
            combo.currentIndexChanged.connect(changed_func)
        return combo

    @staticmethod
    def create_3x3_matrix_input(default_values, text_changed_func=None):
        """
        Tworzy wizualną macierz 3x3 z polami QLineEdit do wpisywania wag.
        Zwraca (QGridLayout, Lista 9 obiektów QLineEdit).
        """
        grid = QGridLayout()
        grid.setSpacing(5)
        
        validator = QDoubleValidator()
        validator.setLocale(QLocale(QLocale.C))
        
        inputs = []
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                line_edit = QLineEdit(str(default_values[idx]))
                line_edit.setValidator(validator)
                line_edit.setAlignment(Qt.AlignCenter)
                line_edit.setFixedWidth(40)
                
                if text_changed_func:
                    line_edit.editingFinished.connect(text_changed_func)
                    
                grid.addWidget(line_edit, i, j)
                inputs.append(line_edit)
                
        return grid, inputs