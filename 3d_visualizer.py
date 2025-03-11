import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QWidget, QComboBox, QTabWidget,
    QGroupBox, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt, pyqtSignal
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import (
    glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10
)


# ---------------------------
# Widget para visualização 3D
# (Mantém a mesma lógica de renderização)
# ---------------------------
class Geometry3D(QOpenGLWidget):
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.shape = shape  # "parallelepiped" ou "pyramid"
        self.params = params
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.x_rot = 0
        self.y_rot = 0
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.current_face = None
        self.show_labels = True
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shape_data = self.compute_shape_data()
        self.geometric_properties = self.calculate_geometric_properties()
        glutInit()

    def compute_shape_data(self) -> dict:
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
            faces = {
                "Frente": {"vertices": [4, 5, 6, 7], "normal": [0, 0, 1], "center": [0, 0, d/2]},
                "Trás": {"vertices": [0, 1, 2, 3], "normal": [0, 0, -1], "center": [0, 0, -d/2]},
                "Topo": {"vertices": [3, 2, 6, 7], "normal": [0, 1, 0], "center": [0, h/2, 0]},
                "Base": {"vertices": [0, 1, 5, 4], "normal": [0, -1, 0], "center": [0, -h/2, 0]},
                "Esquerda": {"vertices": [0, 3, 7, 4], "normal": [-1, 0, 0], "center": [-w/2, 0, 0]},
                "Direita": {"vertices": [1, 2, 6, 5], "normal": [1, 0, 0], "center": [w/2, 0, 0]}
            }
            edge_info = {
                "Largura (frente/trás)": {"edges": [(4, 5), (7, 6), (0, 1), (3, 2)], "length": w},
                "Altura (frente/trás)": {"edges": [(4, 7), (5, 6), (0, 3), (1, 2)], "length": h},
                "Profundidade": {"edges": [(0, 4), (1, 5), (2, 6), (3, 7)], "length": d}
            }
            return {"vertices": vertices, "edges": edges, "faces": faces, "edge_info": edge_info}
        elif self.shape == "pyramid":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            vertices = [
                [-w/2, 0, -d/2], [w/2, 0, -d/2],
                [w/2, 0, d/2],   [-w/2, 0, d/2],
                [0, h, 0]
            ]
            edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
            faces = {
                "Base": {"vertices": [0, 1, 2, 3], "normal": [0, -1, 0], "center": [0, 0, 0]},
                "Frente": {"vertices": [3, 2, 4], "normal": [0, d/2, h], "center": [0, h/3, d/4]},
                "Trás": {"vertices": [0, 1, 4], "normal": [0, d/2, -h], "center": [0, h/3, -d/4]},
                "Esquerda": {"vertices": [0, 3, 4], "normal": [-w/2, h, 0], "center": [-w/4, h/3, 0]},
                "Direita": {"vertices": [1, 2, 4], "normal": [w/2, h, 0], "center": [w/4, h/3, 0]}
            }
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
        gluPerspective(45, w/h if h != 0 else 1, 1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        if self.current_face and self.current_face in self.shape_data["faces"]:
            face_data = self.shape_data["faces"][self.current_face]
            normal = face_data["normal"]
            center = face_data["center"]
            camera_dist = 8.0
            camera_pos = [
                center[0] + normal[0] * camera_dist,
                center[1] + normal[1] * camera_dist,
                center[2] + normal[2] * camera_dist
            ]
            gluLookAt(
                camera_pos[0], camera_pos[1], camera_pos[2],
                center[0], center[1], center[2],
                0, 1, 0
            )
        else:
            glTranslatef(self.x_offset, self.y_offset, self.zoom)
            glRotatef(self.x_rot, 1.0, 0.0, 0.0)
            glRotatef(self.y_rot, 0.0, 1.0, 0.0)
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.draw_shape()
        # Se for pirâmide, desenha a linha da altura
        if self.shape == "pyramid":
            self.draw_height_line()
        if self.show_labels:
            self.draw_labels()
        glFlush()

    def draw_shape(self):
        if self.shape == "parallelepiped":
            self.draw_parallelepiped()
        elif self.shape == "pyramid":
            self.draw_pyramid()

    def draw_parallelepiped(self):
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_pyramid(self):
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_height_line(self):
        # Linha tracejada do centro da base (0,0,0) até o vértice (0, h, 0)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x00FF)  # padrão tracejado
        glColor3f(1.0, 0.0, 0.0)  # cor vermelha para a altura
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)  # centro da base
        glVertex3f(0, self.params["height"], 0)  # vértice (bico da pirâmide)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

    def draw_labels(self):
        vertices = self.shape_data.get("vertices", [])
        faces = self.shape_data.get("faces", {})
        edge_info = self.shape_data.get("edge_info", {})
        face_areas = self.geometric_properties.get("face_areas", {})
        glPushMatrix()
        glDisable(GL_LIGHTING)
        for face_name, face_data in faces.items():
            center = face_data["center"]
            glColor3f(1.0, 1.0, 0.0)
            area = self.format_value(face_areas.get(face_name, 0))
            label = f"{face_name}: {area} u²"
            glRasterPos3f(center[0], center[1], center[2])
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
        for edge_name, edge_data in edge_info.items():
            edges = edge_data["edges"]
            length = edge_data["length"]
            if edges:
                edge = edges[0]
                v1 = vertices[edge[0]]
                v2 = vertices[edge[1]]
                mid_x = (v1[0] + v2[0]) / 2
                mid_y = (v1[1] + v2[1]) / 2
                mid_z = (v1[2] + v2[2]) / 2
                glColor3f(0.0, 1.0, 1.0)
                glRasterPos3f(mid_x, mid_y, mid_z)
                length_text = f"{self.format_value(length)}"
                for c in length_text:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def format_value(self, value):
        if value == int(value):
            return str(int(value))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    def focus_on_face(self, face_name):
        self.current_face = face_name
        self.update()

    def reset_view(self):
        self.current_face = None
        self.x_rot = 30
        self.y_rot = 30
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        self.update()

    def mouseMoveEvent(self, event):
        if self.current_face is None:
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
        
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.shape = shape  # "parallelepiped" ou "pyramid"
        self.params = params
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.x_rot = 0
        self.y_rot = 0
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.current_face = None
        self.show_labels = True
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shape_data = self.compute_shape_data()
        self.geometric_properties = self.calculate_geometric_properties()
        glutInit()

    def compute_shape_data(self) -> dict:
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
            faces = {
                "Frente": {"vertices": [4, 5, 6, 7], "normal": [0, 0, 1], "center": [0, 0, d/2]},
                "Trás": {"vertices": [0, 1, 2, 3], "normal": [0, 0, -1], "center": [0, 0, -d/2]},
                "Topo": {"vertices": [3, 2, 6, 7], "normal": [0, 1, 0], "center": [0, h/2, 0]},
                "Base": {"vertices": [0, 1, 5, 4], "normal": [0, -1, 0], "center": [0, -h/2, 0]},
                "Esquerda": {"vertices": [0, 3, 7, 4], "normal": [-1, 0, 0], "center": [-w/2, 0, 0]},
                "Direita": {"vertices": [1, 2, 6, 5], "normal": [1, 0, 0], "center": [w/2, 0, 0]}
            }
            edge_info = {
                "Largura (frente/trás)": {"edges": [(4, 5), (7, 6), (0, 1), (3, 2)], "length": w},
                "Altura (frente/trás)": {"edges": [(4, 7), (5, 6), (0, 3), (1, 2)], "length": h},
                "Profundidade": {"edges": [(0, 4), (1, 5), (2, 6), (3, 7)], "length": d}
            }
            return {"vertices": vertices, "edges": edges, "faces": faces, "edge_info": edge_info}
        elif self.shape == "pyramid":
            w, h, d = self.params["width"], self.params["height"], self.params["depth"]
            vertices = [
                [-w/2, 0, -d/2], [w/2, 0, -d/2],
                [w/2, 0, d/2],   [-w/2, 0, d/2],
                [0, h, 0]
            ]
            edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
            faces = {
                "Base": {"vertices": [0, 1, 2, 3], "normal": [0, -1, 0], "center": [0, 0, 0]},
                "Frente": {"vertices": [3, 2, 4], "normal": [0, d/2, h], "center": [0, h/3, d/4]},
                "Trás": {"vertices": [0, 1, 4], "normal": [0, d/2, -h], "center": [0, h/3, -d/4]},
                "Esquerda": {"vertices": [0, 3, 4], "normal": [-w/2, h, 0], "center": [-w/4, h/3, 0]},
                "Direita": {"vertices": [1, 2, 4], "normal": [w/2, h, 0], "center": [w/4, h/3, 0]}
            }
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
        if self.current_face and self.current_face in self.shape_data["faces"]:
            face_data = self.shape_data["faces"][self.current_face]
            normal = face_data["normal"]
            center = face_data["center"]
            camera_dist = 8.0
            camera_pos = [
                center[0] + normal[0] * camera_dist,
                center[1] + normal[1] * camera_dist,
                center[2] + normal[2] * camera_dist
            ]
            gluLookAt(
                camera_pos[0], camera_pos[1], camera_pos[2],
                center[0], center[1], center[2],
                0, 1, 0
            )
        else:
            glTranslatef(self.x_offset, self.y_offset, self.zoom)
            glRotatef(self.x_rot, 1.0, 0.0, 0.0)
            glRotatef(self.y_rot, 0.0, 1.0, 0.0)
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        self.draw_shape()
        if self.show_labels:
            self.draw_labels()
        glFlush()

    def draw_shape(self):
        if self.shape == "parallelepiped":
            self.draw_parallelepiped()
        elif self.shape == "pyramid":
            self.draw_pyramid()

    def draw_parallelepiped(self):
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_pyramid(self):
        vertices = self.shape_data.get("vertices", [])
        edges = self.shape_data.get("edges", [])
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_labels(self):
        vertices = self.shape_data.get("vertices", [])
        faces = self.shape_data.get("faces", {})
        edge_info = self.shape_data.get("edge_info", {})
        face_areas = self.geometric_properties.get("face_areas", {})
        glPushMatrix()
        glDisable(GL_LIGHTING)
        for face_name, face_data in faces.items():
            center = face_data["center"]
            glColor3f(1.0, 1.0, 0.0)
            area = self.format_value(face_areas.get(face_name, 0))
            label = f"{face_name}: {area} u²"
            glRasterPos3f(center[0], center[1], center[2])
            for c in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
        for edge_name, edge_data in edge_info.items():
            edges = edge_data["edges"]
            length = edge_data["length"]
            if edges:
                edge = edges[0]
                v1 = vertices[edge[0]]
                v2 = vertices[edge[1]]
                mid_x = (v1[0] + v2[0]) / 2
                mid_y = (v1[1] + v2[1]) / 2
                mid_z = (v1[2] + v2[2]) / 2
                glColor3f(0.0, 1.0, 1.0)
                glRasterPos3f(mid_x, mid_y, mid_z)
                length_text = f"{self.format_value(length)}"
                for c in length_text:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def format_value(self, value):
        if value == int(value):
            return str(int(value))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    def focus_on_face(self, face_name):
        self.current_face = face_name
        self.update()

    def reset_view(self):
        self.current_face = None
        self.x_rot = 30
        self.y_rot = 30
        self.zoom = -10.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()
        self.update()

    def mouseMoveEvent(self, event):
        if self.current_face is None:
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


# ---------------------------
# Calculadora de Propriedades Geométricas
# (Mesma lógica para paralelepípedo e pirâmide)
# ---------------------------
class GeometryCalculator:
    @staticmethod
    def format_value(value):
        if value == int(value):
            return str(int(value))
        return f"{value:.4f}".rstrip('0').rstrip('.') if '.' in f"{value:.4f}" else f"{value:.4f}"
    
    @staticmethod
    def calculate_parallelepiped_properties(params):
        width, height, depth = params["width"], params["height"], params["depth"]
        volume = width * height * depth
        front_back_area = width * height
        top_bottom_area = width * depth
        left_right_area = height * depth
        total_area = 2 * (front_back_area + top_bottom_area + left_right_area)
        face_areas = {
            "Frente": front_back_area,
            "Trás": front_back_area,
            "Topo": top_bottom_area,
            "Base": top_bottom_area,
            "Esquerda": left_right_area,
            "Direita": left_right_area
        }
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
        width, height, depth = params["width"], params["height"], params["depth"]
        base_area = width * depth
        volume = (1/3) * base_area * height
        base_face_area = base_area
        half_width_center = width / 2
        half_depth_center = depth / 2
        front_back_triangle_height = math.sqrt(height**2 + half_depth_center**2)
        left_right_triangle_height = math.sqrt(height**2 + half_width_center**2)
        front_back_face_area = (width * front_back_triangle_height) / 2
        left_right_face_area = (depth * left_right_triangle_height) / 2
        total_area = base_face_area + 2 * front_back_face_area + 2 * left_right_face_area
        face_areas = {
            "Base": base_face_area,
            "Frente": front_back_face_area,
            "Trás": front_back_face_area,
            "Esquerda": left_right_face_area,
            "Direita": left_right_face_area
        }
        faces = {
            "Base": base_face_area,
            "Frente/Trás": front_back_face_area,
            "Esquerda/Direita": left_right_face_area
        }
        # Adiciona a altura como propriedade para exibição
        return {
            "volume": volume,
            "faces": faces,
            "face_areas": face_areas,
            "total_area": total_area,
            "height": height
        }


# ---------------------------
# Aba de Informações Geométricas (já existente)
# ---------------------------
class GeometryInfoTab(QWidget):
    face_selected = pyqtSignal(str)
    
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.shape = shape
        self.params = params
        self.calculator = GeometryCalculator()
        self.init_ui()
        self.update_calculations()
    
    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("<h3>Informações Geométricas</h3>")
        layout.addWidget(header)
        self.volume_label = QLabel()
        layout.addWidget(self.volume_label)
        # Novo rótulo para Altura (apenas para pirâmide)
        self.height_label = QLabel()
        layout.addWidget(self.height_label)
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
            # Para paralelepípedo, não adicionamos o rótulo de altura
            self.height_label.setText("")
        elif self.shape == "pyramid":
            properties = self.calculator.calculate_pyramid_properties(self.params)
            # Exibe a altura (usando o parâmetro)
            height_val = self.params.get("height", 0)
            self.height_label.setText(f"<b>Altura:</b> {self.calculator.format_value(height_val)} unidades")
        else:
            return
        volume = self.calculator.format_value(properties["volume"])
        total_area = self.calculator.format_value(properties["total_area"])
        self.volume_label.setText(f"<b>Volume:</b> {volume} unidades³")
        self.total_area_label.setText(f"<b>Área Total:</b> {total_area} unidades²")
        faces = properties["faces"]
        self.face_table.setRowCount(len(faces))
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

# ---------------------------
# Janela de Visualização 3D
# ---------------------------
class View3D(QMainWindow):
    def __init__(self, shape: str, params: dict):
        super().__init__()
        self.setWindowTitle("Visualização 3D")
        self.setGeometry(100, 100, 800, 600)
        self.tabs = QTabWidget()
        self.view_tab = QWidget()
        self.gl_widget = Geometry3D(shape, params)
        view_layout = QVBoxLayout()
        view_layout.addWidget(self.gl_widget)
        self.view_tab.setLayout(view_layout)
        self.info_tab = GeometryInfoTab(shape, params)
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
        self.main_app = MainApp()
        self.main_app.show()
        self.close()

# ---------------------------
# Aba de Parâmetros da Forma (entrada dos parâmetros)
# ---------------------------
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


# ---------------------------
# Mini widget de pré-visualização para a Calculadora de Dimensões
# (Segue a mesma lógica do Geometry3D, mas em escala menor e sem interação)
# ---------------------------
class MiniPreviewWidget(QOpenGLWidget):
    def __init__(self, shape, params, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.params = params  # dicionário com os parâmetros
        self.x_rot = 30
        self.y_rot = 30
        self.zoom = -5.0
        glutInit()

    def setParameters(self, params):
        self.params = params
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h != 0 else 1, 1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.x_rot, 1, 0, 0)
        glRotatef(self.y_rot, 0, 1, 0)
        if self.shape == "pyramid":
            self.draw_pyramid()
        elif self.shape == "parallelepiped":
            self.draw_parallelepiped()
        glFlush()

    def draw_pyramid(self):
        w = self.params.get("width", 1)
        h = self.params.get("height", 1)
        d = self.params.get("depth", 1)
        vertices = [
            [-w/2, 0, -d/2],
            [w/2, 0, -d/2],
            [w/2, 0, d/2],
            [-w/2, 0, d/2],
            [0, h, 0]
        ]
        glBegin(GL_LINES)
        # Base
        for i in range(4):
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[(i+1)%4])
        # Lados
        for i in range(4):
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[4])
        glEnd()

    def draw_parallelepiped(self):
        w = self.params.get("width", 1)
        h = self.params.get("height", 1)
        d = self.params.get("depth", 1)
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
        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()


# ---------------------------
# Aba de Calculadora de Dimensões (extensível)
# ---------------------------
class DimensionCalculatorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Seleção da forma para o cálculo
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
        
        # Área dinâmica para os inputs (usando QStackedWidget)
        self.stack = QStackedWidget()
        
        layout.addLayout(shape_layout)
        layout.addLayout(calc_layout)
        layout.addWidget(self.stack)
        
        # Adiciona o mini preview abaixo dos inputs
        self.preview = MiniPreviewWidget(self.shape_combo.currentText().lower(), {"width":1, "height":1, "depth":1})
        preview_label = QLabel("Pré-visualização:")
        layout.addWidget(preview_label)
        layout.addWidget(self.preview)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Definindo as fórmulas para cada forma
        # Note que para "Pirâmide" foi adicionado "Frente: Calcular Altura"
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
                # Nova opção para calcular a altura da pirâmide
                "Frente: Calcular Altura": {
                    "inputs": [("Largura", "float"), ("Profundidade", "float"), ("Área (Frontal)", "float")],
                    # Fórmula: h = sqrt((2*area / largura)² - (profundidade/2)²)
                    "calc": lambda largura, profundidade, area: math.sqrt((2*area/largura)**2 - (profundidade/2)**2),
                    "result_label": "Altura: {}"
                }
            }
        }
        
        # Atualiza as opções de cálculo conforme a forma selecionada
        self.shape_combo.currentTextChanged.connect(self.update_calc_options)
        self.calc_combo.currentTextChanged.connect(self.change_stack_page)
        self.update_calc_options(self.shape_combo.currentText())
    
    def update_calc_options(self, shape):
        self.calc_combo.clear()
        formulas = self.formulas.get(shape, {})
        for option in formulas.keys():
            self.calc_combo.addItem(option)
        self.build_stack_for_shape(shape)
        # Atualiza o mini preview
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
            # Armazena dados para o cálculo
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
            # Se estivermos calculando a altura de uma pirâmide (opção "Frente: Calcular Altura"),
            # atualizamos o mini preview com os parâmetros calculados.
            if (self.shape_combo.currentText() == "Pirâmide" and 
                self.calc_combo.currentText() == "Frente: Calcular Altura"):
                largura = values[0]
                profundidade = values[1]
                new_params = {"width": largura, "depth": profundidade, "height": result}
                self.preview.setParameters(new_params)
        except Exception:
            result_widget = page.layout().itemAt(page.layout().count()-1).widget()
            result_widget.setText("Erro: verifique os valores.")


# ---------------------------
# Janela Principal com abas de Configuração e Calculadora
# ---------------------------
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração da Forma")
        self.setGeometry(100, 100, 400, 300)
        tabs = QTabWidget()
        self.config_tab = ConfigFormTab()
        tabs.addTab(self.config_tab, "Parâmetros da Forma")
        # Supondo que a classe DimensionCalculatorTab esteja definida conforme o exemplo anterior
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
        self.view3d = View3D(shape, params)
        self.view3d.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())