import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QWidget, QComboBox
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QIntValidator, QPainter, QFont
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *

class Geometry3D(QOpenGLWidget):
    def __init__(self, shape, params):
        super().__init__()
        self.shape = shape
        self.params = params
        print(f"[DEBUG] Geometry3D init: shape = {self.shape}, params = {self.params}")
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.x_rot = 0
        self.y_rot = 0
        self.zoom = -6.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initializeGL(self):
        print("[DEBUG] initializeGL: Inicializando OpenGL")
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

    def resizeGL(self, w, h):
        print(f"[DEBUG] resizeGL: width = {w}, height = {h}")
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h else 1, 1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        print("[DEBUG] paintGL: Iniciando desenho")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.x_offset, self.y_offset, self.zoom)
        glRotatef(self.x_rot, 1.0, 0.0, 0.0)
        glRotatef(self.y_rot, 0.0, 1.0, 0.0)
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.draw_shape(filled=False)
        glFlush()
        self.draw_edge_labels()

    def draw_shape(self, filled):
        print(f"[DEBUG] draw_shape: filled = {filled}, shape = {self.shape}")
        if self.shape == "paralelepípedo":
            self.draw_parallelepiped(filled)
        elif self.shape == "pirâmide":
            self.draw_pyramid(filled)
        else:
            print("[DEBUG] draw_shape: Forma desconhecida!")

    def draw_parallelepiped(self, filled):
        print(f"[DEBUG] draw_parallelepiped: Desenhando paralelepípedo, filled = {filled}")
        w, h, d = self.params["width"], self.params["height"], self.params["depth"]
        vertices = [
            [-w/2, -h/2, -d/2], [w/2, -h/2, -d/2], [w/2, h/2, -d/2], [-w/2, h/2, -d/2],
            [-w/2, -h/2, d/2], [w/2, -h/2, d/2], [w/2, h/2, d/2], [-w/2, h/2, d/2]
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_pyramid(self, filled):
        print(f"[DEBUG] draw_pyramid: Desenhando pirâmide, filled = {filled}")
        w, h, d = self.params["width"], self.params["height"], self.params["depth"]
        vertices = [
            [-w/2, 0, -d/2], [w/2, 0, -d/2],
            [w/2, 0, d/2], [-w/2, 0, d/2], [0, h, 0]
        ]
        glBegin(GL_LINES)
        faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        for edge in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def draw_edge_labels(self):
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 12))
        if self.shape == "paralelepípedo":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            vertices = [
                (-w/2, -h/2, -d/2), (w/2, -h/2, -d/2),
                (w/2, h/2, -d/2), (-w/2, h/2, -d/2),
                (-w/2, -h/2, d/2), (w/2, -h/2, d/2),
                (w/2, h/2, d/2), (-w/2, h/2, d/2)
            ]
            edges = [
                (0, 1, str(w)), (1, 2, str(h)),
                (2, 3, str(w)), (3, 0, str(h)),
                (4, 5, str(w)), (5, 6, str(h)),
                (6, 7, str(w)), (7, 4, str(h)),
                (0, 4, str(d)), (1, 5, str(d)),
                (2, 6, str(d)), (3, 7, str(d))
            ]
        elif self.shape == "pirâmide":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            vertices = [
                (-w/2, 0, -d/2), (w/2, 0, -d/2),
                (w/2, 0, d/2), (-w/2, 0, d/2),
                (0, h, 0)
            ]
            edges = [
                (0, 1, str(w)), (1, 2, str(d)),
                (2, 3, str(w)), (3, 0, str(d))
            ]
            lateral_length = math.sqrt((w/2)**2 + h**2 + (d/2)**2)
            lateral_str = f"{lateral_length:.2f}"
            edges.extend([
                (0, 4, lateral_str), (1, 4, lateral_str),
                (2, 4, lateral_str), (3, 4, lateral_str)
            ])
        else:
            painter.end()
            return
        for edge in edges:
            i, j, label = edge
            v1 = vertices[i]
            v2 = vertices[j]
            mid = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2, (v1[2] + v2[2]) / 2)
            win = gluProject(mid[0], mid[1], mid[2], model, proj, viewport)
            if win is not None:
                winX, winY, winZ = win
                qt_y = viewport[3] - winY
                painter.drawText(int(winX), int(qt_y), label)
        painter.end()

    def mousePressEvent(self, event):
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        print(f"[DEBUG] mousePressEvent: x = {self.last_mouse_x}, y = {self.last_mouse_y}")

    def mouseMoveEvent(self, event):
        dx = event.position().x() - self.last_mouse_x
        dy = event.position().y() - self.last_mouse_y
        self.x_rot += dy
        self.y_rot += dx
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        print(f"[DEBUG] mouseMoveEvent: dx = {dx}, dy = {dy}, x_rot = {self.x_rot}, y_rot = {self.y_rot}")
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom += delta / 240.0
        print(f"[DEBUG] wheelEvent: angleDelta = {delta}, zoom = {self.zoom}")
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.y_offset += 0.1
            print(f"[DEBUG] keyPressEvent: Up pressed, y_offset = {self.y_offset}")
        elif event.key() == Qt.Key_Down:
            self.y_offset -= 0.1
            print(f"[DEBUG] keyPressEvent: Down pressed, y_offset = {self.y_offset}")
        elif event.key() == Qt.Key_Left:
            self.x_offset -= 0.1
            print(f"[DEBUG] keyPressEvent: Left pressed, x_offset = {self.x_offset}")
        elif event.key() == Qt.Key_Right:
            self.x_offset += 0.1
            print(f"[DEBUG] keyPressEvent: Right pressed, x_offset = {self.x_offset}")
        self.update()

class View3D(QMainWindow):
    def __init__(self, shape, params):
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
        print(f"[DEBUG] View3D: Abrindo visualização para '{shape}' com parâmetros {params}")

    def go_back(self):
        print("[DEBUG] go_back: Retornando à tela principal")
        self.main_app = MainApp()
        self.main_app.show()
        self.close()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Forma")
        self.setGeometry(100, 100, 400, 300)
        self.shape_selector = QComboBox()
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
        print("[DEBUG] MainApp: Interface inicializada")

    def open_3d_view(self):
        shape = self.shape_selector.currentText().lower()
        params = {
            "width": int(self.input_width.text()),
            "height": int(self.input_height.text()),
            "depth": int(self.input_depth.text())
        }
        print(f"[DEBUG] open_3d_view: shape = {shape}, params = {params}")
        self.view3d = View3D(shape, params)
        self.view3d.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())