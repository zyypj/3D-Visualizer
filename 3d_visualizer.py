import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QWidget, QComboBox
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *


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
        self.zoom = -6.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Pré-computa os vértices e dados geométricos da forma
        self.shape_data = self.compute_shape_data()

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
            return {"vertices": vertices, "edges": edges}

        elif self.shape == "pyramid":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            # Base retangular e vértice do topo
            vertices = [
                [-w/2, 0, -d/2], [w/2, 0, -d/2],
                [w/2, 0, d/2],   [-w/2, 0, d/2],
                [0, h, 0]
            ]
            # Faces laterais (triângulos) e aresta da base
            faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
            base_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
            return {"vertices": vertices, "faces": faces, "base_edges": base_edges}
        else:
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
        glTranslatef(self.x_offset, self.y_offset, self.zoom)
        glRotatef(self.x_rot, 1.0, 0.0, 0.0)
        glRotatef(self.y_rot, 0.0, 1.0, 0.0)
        # Exibe o modelo em wireframe
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.draw_shape()
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
        faces = self.shape_data.get("faces", [])
        base_edges = self.shape_data.get("base_edges", [])
        glBegin(GL_LINES)
        # Desenha as faces laterais
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        # Desenha as arestas da base
        for edge in base_edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    # Eventos de entrada

    def mousePressEvent(self, event):
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        self.update()

    def mouseMoveEvent(self, event):
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
        if event.key() == Qt.Key.Key_Up:
            self.y_offset -= 0.1
        elif event.key() == Qt.Key.Key_Down:
            self.y_offset += 0.1
        elif event.key() == Qt.Key.Key_Left:
            self.x_offset += 0.1
        elif event.key() == Qt.Key.Key_Right:
            self.x_offset -= 0.1
        self.update()


class View3D(QMainWindow):
    """
    Janela para exibição da forma 3D.
    Contém o widget OpenGL e um botão para voltar.
    """
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.setWindowTitle("Visualização 3D")
        self.setGeometry(100, 100, 800, 600)
        self.gl_widget = Geometry3D(shape, params)
        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.go_back)
        layout = QVBoxLayout()
        layout.addWidget(self.gl_widget)
        layout.addWidget(self.back_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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
        self.input_width = QLineEdit("2")
        self.input_height = QLineEdit("3")
        self.input_depth = QLineEdit("4")
        validator = QIntValidator(1, 10)
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
        params = {
            "width": int(self.input_width.text()),
            "height": int(self.input_height.text()),
            "depth": int(self.input_depth.text())
        }
        self.view3d = View3D(shape, params)
        self.view3d.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())