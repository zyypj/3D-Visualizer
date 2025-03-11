from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt6.QtGui import QDoubleValidator

class ConfigFormTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Paralelepípedo", "Pirâmide"])
        self.input_width = QLineEdit("2")
        self.input_height = QLineEdit("3")
        self.input_depth = QLineEdit("4")
        validator = QDoubleValidator(0.1, 10.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.input_width.setValidator(validator)
        self.input_height.setValidator(validator)
        self.input_depth.setValidator(validator)
        self.confirm_button = QPushButton("Visualizar")
        layout.addWidget(QLabel("Largura:"))
        layout.addWidget(self.input_width)
        layout.addWidget(QLabel("Altura:"))
        layout.addWidget(self.input_height)
        layout.addWidget(QLabel("Profundidade:"))
        layout.addWidget(self.input_depth)
        layout.addWidget(QLabel("Escolha a forma:"))
        layout.addWidget(self.shape_selector)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)
