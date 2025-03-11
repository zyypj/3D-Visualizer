import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QWidget, QComboBox, QTabWidget,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import (
    glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10
)


class Geometry3D(QOpenGLWidget):
    """
    Widget OpenGL para renderização de formas 3D.
    Suporta as formas "parallelepiped" (paralelepípedo) e "pyramid" (pirâmide).
    """
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.shape = shape  # forma interna: "parallelepiped" ou "pyramid"
        self.params = params
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.x_rot = 0
        self.y_rot = 0
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.current_face = None  # face atual em foco
        self.show_labels = True  # exibir os rótulos de área e comprimento
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Pré-computa os vértices e dados geométricos da forma
        self.shape_data = self.compute_shape_data()
        # Calcular propriedades geométricas
        self.geometric_properties = self.calculate_geometric_properties()
        # Inicializar fonte para rótulos
        glutInit()

    def compute_shape_data(self) -> dict:
        """
        Calcula os vértices e arestas ou faces da forma, de acordo com os parâmetros.
        Retorna um dicionário com os dados necessários para o desenho.
        """
        if self.shape == "parallelepiped":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            vertices = [
                [-w/2, -h/2, -d/2], [w/2, -h/2, -d/2],
                [w/2, h/2, -d/2],   [-w/2, h/2, -d/2],
                [-w/2, -h/2, d/2],  [w/2, -h/2, d/2],
                [w/2, h/2, d/2],    [-w/2, h/2, d/2]
            ]
            edges = [
                (0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7)
            ]
            # Define as faces para renderização
            faces = {
                "Frente": {"vertices": [4, 5, 6, 7], "normal": [0, 0, 1], "center": [0, 0, d/2]},
                "Trás": {"vertices": [0, 1, 2, 3], "normal": [0, 0, -1], "center": [0, 0, -d/2]},
                "Topo": {"vertices": [3, 2, 6, 7], "normal": [0, 1, 0], "center": [0, h/2, 0]},
                "Base": {"vertices": [0, 1, 5, 4], "normal": [0, -1, 0], "center": [0, -h/2, 0]},
                "Esquerda": {"vertices": [0, 3, 7, 4], "normal": [-1, 0, 0], "center": [-w/2, 0, 0]},
                "Direita": {"vertices": [1, 2, 6, 5], "normal": [1, 0, 0], "center": [w/2, 0, 0]}
            }
            
            # Informações sobre as arestas (comprimento e posição)
            edge_info = {
                "Largura (frente/trás)": {"edges": [(4, 5), (7, 6), (0, 1), (3, 2)], "length": w},
                "Altura (frente/trás)": {"edges": [(4, 7), (5, 6), (0, 3), (1, 2)], "length": h},
                "Profundidade": {"edges": [(0, 4), (1, 5), (2, 6), (3, 7)], "length": d}
            }
            
            return {"vertices": vertices, "edges": edges, "faces": faces, "edge_info": edge_info}

        elif self.shape == "pyramid":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            # Base retangular e vértice do topo
            vertices = [
                [-w/2, 0, -d/2], [w/2, 0, -d/2],
                [w/2, 0, d/2],   [-w/2, 0, d/2],
                [0, h, 0]
            ]
            # Arestas da base e do topo para a base
            edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
            
            # Distâncias para cálculos de normais e centros das faces
            front_height = math.sqrt(h**2 + (d/2)**2)
            side_height = math.sqrt(h**2 + (w/2)**2)
            
            # Define as faces para renderização
            faces = {
                "Base": {"vertices": [0, 1, 2, 3], "normal": [0, -1, 0], "center": [0, 0, 0]},
                "Frente": {"vertices": [3, 2, 4], "normal": [0, d/2, h], "center": [0, h/3, d/4]},
                "Trás": {"vertices": [0, 1, 4], "normal": [0, d/2, -h], "center": [0, h/3, -d/4]},
                "Esquerda": {"vertices": [0, 3, 4], "normal": [-w/2, h, 0], "center": [-w/4, h/3, 0]},
                "Direita": {"vertices": [1, 2, 4], "normal": [w/2, h, 0], "center": [w/4, h/3, 0]}
            }
            
            # Informações sobre as arestas (comprimento e posição)
            diag_front = math.sqrt(h**2 + (d/2)**2)
            diag_side = math.sqrt(h**2 + (w/2)**2)
            
            edge_info = {
                "Base (largura)": {"edges": [(0, 1), (3, 2)], "length": w},
                "Base (profundidade)": {"edges": [(1, 2), (0, 3)], "length": d},
                "Aresta lateral (frente)": {"edges": [(2, 4), (3, 4)], "length": diag_front},
                "Aresta lateral (trás)": {"edges": [(0, 4), (1, 4)], "length": diag_front},
                "Aresta lateral (lados)": {"edges": [(0, 4), (1, 4), (2, 4), (3, 4)], "length": diag_side}
            }
            
            return {"vertices": vertices, "edges": edges, "faces": faces, "edge_info": edge_info}
        else:
            return {}

    def calculate_geometric_properties(self):
        """Calcula as propriedades geométricas da forma."""
        calculator = GeometryCalculator()
        if self.shape == "parallelepiped":
            return calculator.calculate_parallelepiped_properties(self.params)
        elif self.shape == "pyramid":
            return calculator.calculate_pyramid_properties(self.params)
        return {}

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1, 1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Posicionar a câmera baseado na face atual
        if self.current_face and self.current_face in self.shape_data["faces"]:
            face_data = self.shape_data["faces"][self.current_face]
            normal = face_data["normal"]
            center = face_data["center"]
            
            # Posiciona a câmera na direção da normal da face
            camera_dist = 8.0  # distância da câmera
            camera_pos = [
                center[0] + normal[0] * camera_dist,
                center[1] + normal[1] * camera_dist,
                center[2] + normal[2] * camera_dist
            ]
            
            # Olhar para o centro da face
            gluLookAt(
                camera_pos[0], camera_pos[1], camera_pos[2],  # posição da câmera
                center[0], center[1], center[2],  # ponto para onde olhar
                0, 1, 0  # vetor "up"
            )
        else:
            # Visualização padrão
            glTranslatef(self.x_offset, self.y_offset, self.zoom)
            glRotatef(self.x_rot, 1.0, 0.0, 0.0)
            glRotatef(self.y_rot, 0.0, 1.0, 0.0)
        
        # Exibe o modelo em wireframe
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.draw_shape()
        
        # Desenhar rótulos se ativados
        if self.show_labels:
            self.draw_labels()
            
        glFlush()

    def draw_shape(self):
        """Seleciona e desenha a forma com base nos dados pré-computados."""
        if self.shape == "parallelepiped":
            self.draw_parallelepiped()
        elif self.shape == "pyramid":
            self.draw_pyramid()

    def draw_parallelepiped(self):
        """Desenha um paralelepípedo a partir dos vértices e arestas calculados."""
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_pyramid(self):
        """Desenha uma pirâmide com linhas: as faces laterais e a base."""
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_labels(self):
        """Desenha os rótulos de área e comprimento."""
        vertices = self.shape_data.get("vertices", [])
        faces = self.shape_data.get("faces", {})
        edge_info = self.shape_data.get("edge_info", {})
        face_areas = self.geometric_properties.get("face_areas", {})
        
        # Salvar estado atual da matriz
        glPushMatrix()
        
        # Desabilitar iluminação para os rótulos
        glDisable(GL_LIGHTING)
        
        # Desenhar rótulos de área no centro de cada face
        for face_name, face_data in faces.items():
            # Usar o centro calculado da face
            center = face_data["center"]
            normal = face_data["normal"]
            
            # Verificar se a face está voltada para a câmera
            glColor3f(1.0, 1.0, 0.0)  # Amarelo para área
            
            # Obter área da face
            area = self.format_value(face_areas.get(face_name, 0))
            label = f"{face_name}: {area} u²"
            
            # Desenhar texto no centro da face
            glRasterPos3f(center[0], center[1], center[2])
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
        
        # Desenhar comprimentos nas arestas
        for edge_name, edge_data in edge_info.items():
            edges = edge_data["edges"]
            length = edge_data["length"]
            
            # Escolher primeira aresta para o rótulo
            if edges:
                edge = edges[0]
                v1 = vertices[edge[0]]
                v2 = vertices[edge[1]]
                
                # Posição do rótulo no meio da aresta
                mid_x = (v1[0] + v2[0]) / 2
                mid_y = (v1[1] + v2[1]) / 2
                mid_z = (v1[2] + v2[2]) / 2
                
                # Desenhar o comprimento
                glColor3f(0.0, 1.0, 1.0)  # Ciano para comprimento
                glRasterPos3f(mid_x, mid_y, mid_z)
                length_text = f"{self.format_value(length)}"
                for c in length_text:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))
        
        # Restaurar iluminação e estado da matriz
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def format_value(self, value):
        """Formata um valor para exibição, simplificando valores decimais."""
        if value == int(value):
            return str(int(value))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    def focus_on_face(self, face_name):
        """Define a face atual para foco e atualiza a visualização."""
        self.current_face = face_name
        self.update()

    def reset_view(self):
        """Restaura a visualização padrão."""
        self.current_face = None
        self.x_rot = 30
        self.y_rot = 30
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.update()

    # Eventos de entrada

    def mousePressEvent(self, event):
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        self.update()

    def mouseMoveEvent(self, event):
        if self.current_face is None:  # Só permite rotação quando não estiver focado em uma face
            dx = event.position().x() - self.last_mouse_x
            dy = event.position().y() - self.last_mouse_y
            self.x_rot += dy
            self.y_rot += dx
            self.last_mouse_x = event.position().x()
            self.last_mouse_y = event.position().y()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom += delta / 240.0
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reset_view()
        elif event.key() == Qt.Key.Key_Up:
            self.y_offset -= 0.1
        elif event.key() == Qt.Key.Key_Down:
            self.y_offset += 0.1
        elif event.key() == Qt.Key.Key_Left:
            self.x_offset += 0.1
        elif event.key() == Qt.Key.Key_Right:
            self.x_offset -= 0.1
        elif event.key() == Qt.Key.Key_L:
            self.show_labels = not self.show_labels
        self.update()


class GeometryCalculator:
    """
    Classe para calcular propriedades geométricas das formas 3D.
    """
    @staticmethod
    def format_value(value):
        """Formata um valor para exibição, incluindo possíveis raízes e números exatos."""
        # Verifica se é valor inteiro
        if value == int(value):
            return str(int(value))
        
        # Tenta identificar raízes quadradas perfeitas em denominadores/numeradores
        # Por exemplo, sqrt(2)/2, 2*sqrt(3), etc.
        
        # Para simplicidade, retorna o valor formatado com 4 casas decimais
        return f"{value:.4f}".rstrip('0').rstrip('.') if '.' in f"{value:.4f}" else f"{value:.4f}"
    
    @staticmethod
    def calculate_parallelepiped_properties(params):
        """Calcula propriedades do paralelepípedo."""
        width, height, depth = params["width"], params["height"], params["depth"]
        
        # Volume
        volume = width * height * depth
        
        # Áreas das faces
        front_back_area = width * height
        top_bottom_area = width * depth
        left_right_area = height * depth
        
        # Área total
        total_area = 2 * (front_back_area + top_bottom_area + left_right_area)
        
        # Faces nomeadas
        face_areas = {
            "Frente": front_back_area,
            "Trás": front_back_area,
            "Topo": top_bottom_area,
            "Base": top_bottom_area,
            "Esquerda": left_right_area,
            "Direita": left_right_area
        }
        
        # Faces agrupadas para a interface
        faces = {
            "Frente/Trás": front_back_area,
            "Topo/Base": top_bottom_area,
            "Esquerda/Direita": left_right_area
        }
        
        return {
            "volume": volume,
            "faces": faces,
            "face_areas": face_areas,
            "total_area": total_area
        }
    
    @staticmethod
    def calculate_pyramid_properties(params):
        """Calcula propriedades da pirâmide de base retangular."""
        width, height, depth = params["width"], params["height"], params["depth"]
        
        # Volume (1/3 da área da base vezes a altura)
        base_area = width * depth
        volume = (1/3) * base_area * height
        
        # Área da base
        base_face_area = base_area
        
        # Áreas das faces laterais
        # Para cada face triangular, calculamos a área usando a fórmula da área do triângulo
        
        # Distância do centro da base ao ponto médio de cada aresta da base
        half_width_center = width / 2
        half_depth_center = depth / 2
        
        # Altura da face triangular (usando o teorema de Pitágoras)
        front_back_triangle_height = math.sqrt(height**2 + half_depth_center**2)
        left_right_triangle_height = math.sqrt(height**2 + half_width_center**2)
        
        # Áreas das faces triangulares
        front_back_face_area = (width * front_back_triangle_height) / 2
        left_right_face_area = (depth * left_right_triangle_height) / 2
        
        # Área total
        total_area = base_face_area + 2 * front_back_face_area + 2 * left_right_face_area
        
        # Faces nomeadas individualmente
        face_areas = {
            "Base": base_face_area,
            "Frente": front_back_face_area,
            "Trás": front_back_face_area,
            "Esquerda": left_right_face_area,
            "Direita": left_right_face_area
        }
        
        # Faces agrupadas para a interface
        faces = {
            "Base": base_face_area,
            "Frente/Trás": front_back_face_area,
            "Esquerda/Direita": left_right_face_area
        }
        
        return {
            "volume": volume,
            "faces": faces,
            "face_areas": face_areas,
            "total_area": total_area
        }


class GeometryInfoTab(QWidget):
    """
    Aba que exibe informações geométricas da forma.
    """
    face_selected = pyqtSignal(str)  # Sinal para informar seleção de face
    
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.shape = shape
        self.params = params
        self.calculator = GeometryCalculator()
        self.init_ui()
        self.update_calculations()
    
    def init_ui(self):
        """Inicializa a interface da aba de informações geométricas."""
        layout = QVBoxLayout()
        
        # Tabela para exibir as áreas das faces
        self.face_table = QTableWidget()
        self.face_table.setColumnCount(2)
        self.face_table.setHorizontalHeaderLabels(["Face", "Área"])
        self.face_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.face_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.face_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.face_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Conectar sinal de clique na tabela
        self.face_table.cellClicked.connect(self.on_face_selected)
        
        # Labels para exibir o volume e a área total
        self.volume_label = QLabel()
        self.total_area_label = QLabel()
        
        # Instruções
        instructions = QLabel("Clique em uma face para visualizá-la em 3D.\nPressione ESC para voltar à visualização normal.")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        
        # Adiciona os widgets ao layout
        layout.addWidget(QLabel("<h3>Informações Geométricas</h3>"))
        layout.addWidget(self.volume_label)
        layout.addWidget(self.total_area_label)
        layout.addWidget(QLabel("<h4>Áreas das Faces</h4>"))
        layout.addWidget(self.face_table)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
    
    def update_calculations(self):
        """Atualiza os cálculos geométricos com base na forma e parâmetros atuais."""
        if self.shape == "parallelepiped":
            properties = self.calculator.calculate_parallelepiped_properties(self.params)
        elif self.shape == "pyramid":
            properties = self.calculator.calculate_pyramid_properties(self.params)
        else:
            return
        
        # Atualiza volume e área total
        volume = self.calculator.format_value(properties["volume"])
        total_area = self.calculator.format_value(properties["total_area"])
        
        self.volume_label.setText(f"<b>Volume:</b> {volume} unidades³")
        self.total_area_label.setText(f"<b>Área Total:</b> {total_area} unidades²")
        
        # Atualiza tabela de faces
        faces = properties["faces"]
        self.face_table.setRowCount(len(faces))
        
        # Mapeia os nomes das faces na tabela para nomes de faces individuais
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
        """Quando uma face é selecionada na tabela."""
        face_name = self.face_table.item(row, 0).text()
        
        # Se for um par de faces, seleciona a primeira
        if face_name in self.face_mapping and self.face_mapping[face_name]:
            self.face_selected.emit(self.face_mapping[face_name][0])
        else:
            self.face_selected.emit(face_name)


class View3D(QMainWindow):
    """
    Janela para exibição da forma 3D.
    Contém o widget OpenGL e um botão para voltar.
    """
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.setWindowTitle("Visualização 3D")
        self.setGeometry(100, 100, 800, 600)
        
        # Cria o widget para abas
        self.tabs = QTabWidget()
        
        # Aba de visualização 3D
        self.view_tab = QWidget()
        self.gl_widget = Geometry3D(shape, params)
        view_layout = QVBoxLayout()
        view_layout.addWidget(self.gl_widget)
        self.view_tab.setLayout(view_layout)
        
        # Aba de informações geométricas
        self.info_tab = GeometryInfoTab(shape, params)
        
        # Conectar sinal de seleção de face ao visualizador 3D
        self.info_tab.face_selected.connect(self.focus_on_face)
        
        # Adiciona as abas
        self.tabs.addTab(self.view_tab, "Visualização")
        self.tabs.addTab(self.info_tab, "Informações Geométricas")
        
        # Botão para voltar
        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.go_back)
        
        # Botão para restaurar a visualização
        self.reset_view_button = QPushButton("Restaurar Visualização")
        self.reset_view_button.clicked.connect(self.reset_view)
        
        # Layout dos botões
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.reset_view_button)
        button_layout.addWidget(self.back_button)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addLayout(button_layout)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def focus_on_face(self, face_name):
        """Foca a visualização em uma face específica."""
        self.gl_widget.focus_on_face(face_name)
        # Alternar para a aba de visualização
        self.tabs.setCurrentIndex(0)

    def reset_view(self):
        """Restaura a visualização padrão."""
        self.gl_widget.reset_view()

    def go_back(self):
        """Retorna para a tela de configuração."""
        self.main_app = MainApp()
        self.main_app.show()
        self.close()


class MainApp(QMainWindow):
    """
    Janela principal para configuração dos parâmetros da forma.
    Permite escolher a forma e definir os valores de largura, altura e profundidade.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Forma")
        self.setGeometry(100, 100, 400, 300)
        self.shape_selector = QComboBox()
        # Exibe os nomes em português para o usuário
        self.shape_selector.addItems(["Paralelepípedo", "Pirâmide"])
        
        # Usa QDoubleValidator para permitir valores decimais
        self.input_width = QLineEdit("2")
        self.input_height = QLineEdit("3")
        self.input_depth = QLineEdit("4")
        validator = QDoubleValidator(0.1, 10.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        self.input_width.setValidator(validator)
        self.input_height.setValidator(validator)
        self.input_depth.setValidator(validator)
        
        self.confirm_button = QPushButton("Visualizar")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Largura:"))
        layout.addWidget(self.input_width)
        layout.addWidget(QLabel("Altura:"))
        layout.addWidget(self.input_height)
        layout.addWidget(QLabel("Profundidade:"))
        layout.addWidget(self.input_depth)
        layout.addWidget(QLabel("Escolha a forma:"))
        layout.addWidget(self.shape_selector)
        layout.addWidget(self.confirm_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.confirm_button.clicked.connect(self.open_3d_view)

    def open_3d_view(self):
        """Coleta os parâmetros informados e abre a visualização 3D."""
        # Mapeia o nome da forma para a chave interna utilizada
        shape_mapping = {
            "paralelepípedo": "parallelepiped",
            "pirâmide": "pyramid"
        }
        selected = self.shape_selector.currentText().strip().lower()
        shape = shape_mapping.get(selected, selected)
        
        # Converte texto para float para suportar valores decimais
        params = {
            "width": float(self.input_width.text().replace(',', '.')),
            "height": float(self.input_height.text().replace(',', '.')),
            "depth": float(self.input_depth.text().replace(',', '.'))
        }
        
        self.view3d = View3D(shape, params)
        self.view3d.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())