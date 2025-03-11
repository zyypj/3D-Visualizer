from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_10

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
        for i in range(4):
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[(i+1)%4])
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
