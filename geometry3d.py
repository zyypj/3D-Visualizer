import math
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10
from geometry_calculator import GeometryCalculator

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
        # Usa GeometryCalculator para calcular as propriedades
        if self.shape == "pyramid":
            self.geometric_properties = GeometryCalculator.calculate_pyramid_properties(self.params)
        else:
            self.geometric_properties = GeometryCalculator.calculate_parallelepiped_properties(self.params)
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
        # Desenha uma linha tracejada (vermelha) do centro da base (0,0,0) até o vértice (0, height, 0)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x00FF)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.params["height"], 0)
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
