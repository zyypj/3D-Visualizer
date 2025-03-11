import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton, QStackedWidget)
from mini_preview_widget import MiniPreviewWidget

class DimensionCalculatorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Seleção da forma
        shape_layout = QHBoxLayout()
        shape_label = QLabel("Selecione a Forma:")
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Paralelepípedo", "Pirâmide"])
        shape_layout.addWidget(shape_label)
        shape_layout.addWidget(self.shape_combo)

        # Seleção da opção de cálculo
        calc_layout = QHBoxLayout()
        calc_label = QLabel("Selecione o Cálculo:")
        self.calc_combo = QComboBox()
        calc_layout.addWidget(calc_label)
        calc_layout.addWidget(self.calc_combo)

        # Área dinâmica para inputs
        self.stack = QStackedWidget()

        layout.addLayout(shape_layout)
        layout.addLayout(calc_layout)
        layout.addWidget(self.stack)

        # Mini preview
        self.preview = MiniPreviewWidget(self.shape_combo.currentText().lower(), {"width":1, "height":1, "depth":1})
        preview_label = QLabel("Pré-visualização:")
        layout.addWidget(preview_label)
        layout.addWidget(self.preview)

        layout.addStretch()
        self.setLayout(layout)

        # Definindo fórmulas
        self.formulas = {
            "Paralelepípedo": {
                "Frente/Trás: Calcular Largura": {
                    "inputs": [("Altura", "float"), ("Área (Frente/Trás)", "float")],
                    "calc": lambda altura, area: area / altura,
                    "result_label": "Largura: {}"
                },
                "Frente/Trás: Calcular Altura": {
                    "inputs": [("Largura", "float"), ("Área (Frente/Trás)", "float")],
                    "calc": lambda largura, area: area / largura,
                    "result_label": "Altura: {}"
                },
                "Topo/Base: Calcular Largura": {
                    "inputs": [("Profundidade", "float"), ("Área (Topo/Base)", "float")],
                    "calc": lambda profundidade, area: area / profundidade,
                    "result_label": "Largura: {}"
                },
                "Topo/Base: Calcular Profundidade": {
                    "inputs": [("Largura", "float"), ("Área (Topo/Base)", "float")],
                    "calc": lambda largura, area: area / largura,
                    "result_label": "Profundidade: {}"
                },
                "Lateral (Esq/Dir): Calcular Altura": {
                    "inputs": [("Profundidade", "float"), ("Área (Lateral)", "float")],
                    "calc": lambda profundidade, area: area / profundidade,
                    "result_label": "Altura: {}"
                },
                "Lateral (Esq/Dir): Calcular Profundidade": {
                    "inputs": [("Altura", "float"), ("Área (Lateral)", "float")],
                    "calc": lambda altura, area: area / altura,
                    "result_label": "Profundidade: {}"
                }
            },
            "Pirâmide": {
                "Base: Calcular Largura": {
                    "inputs": [("Profundidade", "float"), ("Área da Base", "float")],
                    "calc": lambda profundidade, area: area / profundidade,
                    "result_label": "Largura: {}"
                },
                "Base: Calcular Profundidade": {
                    "inputs": [("Largura", "float"), ("Área da Base", "float")],
                    "calc": lambda largura, area: area / largura,
                    "result_label": "Profundidade: {}"
                },
                "Frente: Calcular Altura": {
                    "inputs": [("Largura", "float"), ("Profundidade", "float"), ("Área (Frontal)", "float")],
                    "calc": lambda largura, profundidade, area: math.sqrt((2*area/largura)**2 - (profundidade/2)**2),
                    "result_label": "Altura: {}"
                }
            }
        }

        self.shape_combo.currentTextChanged.connect(self.update_calc_options)
        self.calc_combo.currentTextChanged.connect(self.change_stack_page)
        self.update_calc_options(self.shape_combo.currentText())

    def update_calc_options(self, shape):
        self.calc_combo.clear()
        formulas = self.formulas.get(shape, {})
        for option in formulas.keys():
            self.calc_combo.addItem(option)
        self.build_stack_for_shape(shape)
        self.preview.shape = shape.lower()

    def build_stack_for_shape(self, shape):
        self.clear_stack()
        formulas = self.formulas.get(shape, {})
        for option, data in formulas.items():
            page = QWidget()
            form_layout = QGridLayout()
            inputs = []
            for i, (label_text, _) in enumerate(data["inputs"]):
                label = QLabel(label_text + ":")
                line_edit = QLineEdit()
                form_layout.addWidget(label, i, 0)
                form_layout.addWidget(line_edit, i, 1)
                inputs.append(line_edit)
            btn = QPushButton("Calcular")
            result_label = QLabel("Resultado:")
            form_layout.addWidget(btn, len(data["inputs"]), 0, 1, 2)
            form_layout.addWidget(result_label, len(data["inputs"]) + 1, 0, 1, 2)
            page.setLayout(form_layout)
            page.inputs = inputs
            page.calc_func = data["calc"]
            page.result_label_template = data["result_label"]
            btn.clicked.connect(lambda _, p=page: self.perform_calculation(p))
            self.stack.addWidget(page)
        if self.stack.count() > 0:
            self.stack.setCurrentIndex(0)

    def clear_stack(self):
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def change_stack_page(self, calc_option):
        formulas = self.formulas.get(self.shape_combo.currentText(), {})
        keys = list(formulas.keys())
        index = keys.index(calc_option) if calc_option in keys else 0
        self.stack.setCurrentIndex(index)

    def perform_calculation(self, page):
        try:
            values = [float(inp.text().replace(',', '.')) for inp in page.inputs]
            result = page.calc_func(*values)
            result_text = page.result_label_template.format(f"{result:.2f}")
            result_widget = page.layout().itemAt(page.layout().count()-1).widget()
            result_widget.setText(result_text)
            if (self.shape_combo.currentText() == "Pirâmide" and 
                self.calc_combo.currentText() == "Frente: Calcular Altura"):
                largura = values[0]
                profundidade = values[1]
                new_params = {"width": largura, "depth": profundidade, "height": result}
                self.preview.setParameters(new_params)
        except Exception:
            result_widget = page.layout().itemAt(page.layout().count()-1).widget()
            result_widget.setText("Erro: verifique os valores.")
