from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import pyqtSignal
from geometry_calculator import GeometryCalculator
import math

class GeometryInfoTab(QWidget):
    face_selected = pyqtSignal(str)
    
    def __init__(self, shape: str, params: dict, calculator: GeometryCalculator):
        super().__init__()
        self.shape = shape
        self.params = params
        self.calculator = calculator
        self.init_ui()
        self.update_calculations()
    
    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("<h3>Informações Geométricas</h3>")
        layout.addWidget(header)
        self.volume_label = QLabel()
        layout.addWidget(self.volume_label)
        self.height_label = QLabel()
        layout.addWidget(self.height_label)
        self.generatriz_label = QLabel()
        layout.addWidget(self.generatriz_label)
        self.total_area_label = QLabel()
        layout.addWidget(self.total_area_label)
        layout.addWidget(QLabel("<h4>Áreas das Faces</h4>"))
        self.face_table = QTableWidget()
        self.face_table.setColumnCount(2)
        self.face_table.setHorizontalHeaderLabels(["Face", "Área"])
        self.face_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.face_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.face_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.face_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.face_table.cellClicked.connect(self.on_face_selected)
        layout.addWidget(self.face_table)
        instructions = QLabel("Clique em uma face para visualizá-la em 3D.\nPressione ESC para voltar à visualização normal.")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)
        self.setLayout(layout)

    
    def update_calculations(self):
        if self.shape == "parallelepiped":
            properties = self.calculator.calculate_parallelepiped_properties(self.params)
            self.height_label.setText("")  # Não exibe altura para paralelepípedo
            self.generatriz_label.setText("")  # Sem geratriz para paralelepípedo
        elif self.shape == "pyramid":
            properties = self.calculator.calculate_pyramid_properties(self.params)
            height_val = self.params.get("height", 0)
            self.height_label.setText(f"<b>Altura:</b> {self.calculator.format_value(height_val)} unidades")
            geratriz_front = properties.get("geratriz_front_back", 0)
            geratriz_side = properties.get("geratriz_left_right", 0)
            # Se as duas geratrizes forem iguais (pirâmide quadrada), exibe uma única geratriz.
            if math.isclose(geratriz_front, geratriz_side, rel_tol=1e-9):
                self.generatriz_label.setText(f"<b>Geratriz:</b> {self.calculator.format_value(geratriz_front)} unidades")
            else:
                self.generatriz_label.setText(f"<b>Geratriz Frente/Trás:</b> {self.calculator.format_value(geratriz_front)} unidades, "
                                            f"<b>Geratriz Lados:</b> {self.calculator.format_value(geratriz_side)} unidades")
        else:
            return

        volume = self.calculator.format_value(properties["volume"])
        total_area = self.calculator.format_value(properties["total_area"])
        self.volume_label.setText(f"<b>Volume:</b> {volume} unidades³")
        self.total_area_label.setText(f"<b>Área Total:</b> {total_area} unidades²")
        
        faces = properties["faces"]
        self.face_table.setRowCount(len(faces))
        # Mapeamento para seleção de face na visualização 3D
        self.face_mapping = {}
        if self.shape == "parallelepiped":
            self.face_mapping = {
                "Frente/Trás": ["Frente", "Trás"],
                "Topo/Base": ["Topo", "Base"],
                "Esquerda/Direita": ["Esquerda", "Direita"]
            }
        elif self.shape == "pyramid":
            self.face_mapping = {
                "Base": ["Base"],
                "Frente/Trás": ["Frente", "Trás"],
                "Esquerda/Direita": ["Esquerda", "Direita"]
            }
        
        for i, (face_name, face_area) in enumerate(faces.items()):
            face_item = QTableWidgetItem(face_name)
            face_item.setToolTip("Clique para visualizar esta face")
            area_item = QTableWidgetItem(self.calculator.format_value(face_area) + " unidades²")
            self.face_table.setItem(i, 0, face_item)
            self.face_table.setItem(i, 1, area_item)

    
    def on_face_selected(self, row, column):
        face_name = self.face_table.item(row, 0).text()
        if face_name in self.face_mapping and self.face_mapping[face_name]:
            self.face_selected.emit(self.face_mapping[face_name][0])
        else:
            self.face_selected.emit(face_name)
