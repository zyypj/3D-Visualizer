from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QPushButton, QWidget
from geometry3d import Geometry3D
from geometry_info_tab import GeometryInfoTab

class View3D(QMainWindow):
    def __init__(self, shape: str, params: dict, calculator):
        super().__init__()
        self.setWindowTitle("Visualização 3D")
        self.setGeometry(100, 100, 800, 600)
        self.tabs = QTabWidget()
        self.view_tab = QWidget()
        self.gl_widget = Geometry3D(shape, params)
        view_layout = QVBoxLayout()
        view_layout.addWidget(self.gl_widget)
        self.view_tab.setLayout(view_layout)
        self.info_tab = GeometryInfoTab(shape, params, calculator)
        self.info_tab.face_selected.connect(self.focus_on_face)
        self.tabs.addTab(self.view_tab, "Visualização")
        self.tabs.addTab(self.info_tab, "Informações Geométricas")
        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.go_back)
        self.reset_view_button = QPushButton("Restaurar Visualização")
        self.reset_view_button.clicked.connect(self.reset_view)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.reset_view_button)
        button_layout.addWidget(self.back_button)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addLayout(button_layout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def focus_on_face(self, face_name):
        self.gl_widget.focus_on_face(face_name)
        self.tabs.setCurrentIndex(0)

    def reset_view(self):
        self.gl_widget.reset_view()

    def go_back(self):
        from main import MainApp
        self.main_app = MainApp()
        self.main_app.show()
        self.close()
