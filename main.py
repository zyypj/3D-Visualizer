import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from config_form_tab import ConfigFormTab
from dimension_calculator_tab import DimensionCalculatorTab
from view3d import View3D
from geometry_calculator import GeometryCalculator

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Forma")
        self.setGeometry(100, 100, 400, 300)
        tabs = QTabWidget()
        self.config_tab = ConfigFormTab()
        tabs.addTab(self.config_tab, "Parâmetros da Forma")
        self.calc_tab = DimensionCalculatorTab()
        tabs.addTab(self.calc_tab, "Calculadora de Dimensões")
        self.setCentralWidget(tabs)
        self.config_tab.confirm_button.clicked.connect(self.open_3d_view)

    def open_3d_view(self):
        shape_mapping = {
            "paralelepípedo": "parallelepiped",
            "pirâmide": "pyramid"
        }
        selected = self.config_tab.shape_selector.currentText().strip().lower()
        shape = shape_mapping.get(selected, selected)
        params = {
            "width": float(self.config_tab.input_width.text().replace(',', '.')),
            "height": float(self.config_tab.input_height.text().replace(',', '.')),
            "depth": float(self.config_tab.input_depth.text().replace(',', '.'))
        }
        calculator = GeometryCalculator()
        self.view3d = View3D(shape, params, calculator)
        self.view3d.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
