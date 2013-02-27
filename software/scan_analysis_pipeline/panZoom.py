#!/usr/bin/env python

import atexit
import math
import sys
from operator import attrgetter

import PIL.Image
from ctypes import c_int
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import numpy as np

# glut does a wonderful thing (this might be apples fault... one of the two)
# when you click File->Quit Python (instead of Shift-Q), python will receive a SIGKILL
# it is impossible to catch this and therefore impossible to clean up prior to exit
# so...
# it's VERY important that this program be exited using Shift-Q and NOTHING ELSE
# sorry :(

# if object coordinates are in opengl, then drawing is dead simple
# however, how do I do zooming and panning?
# I could pass in the necessary to_x and to_y functions, but I would also need to pass in zoom, which is getting sort of complicated
# it would be nice to just be able to change the opengl viewport

# window -> opengl -> texture -> image


class Point:
    def __init__(self, x=0., y=0., color=(1., 1., 1., 1.), size=3):
        self.x = x
        self.y = y
        self.color = color
        self.size = size

    def draw(self):
        """maybe here draw blinking cross-hairs"""
        # glColor(*self.)
        glColor(*self.color)
        glPointSize(self.size)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()


#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#
def perp(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def in_between(val, r1, r2):
    if r1 > r2:
        return (val < r1 and val > r2)
    else:
        return (val < r2 and val > r1)

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return


def seg_intersect(a1, a2, b1, b2):
    a1 = np.array(a1)
    a2 = np.array(a2)
    b1 = np.array(b1)
    b2 = np.array(b2)
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = perp(da)
    denom = np.dot(dap, db)
    num = np.dot(dap, dp)
    ip = (num / denom) * db + b1  # point where lines would intersect
    # test if point is on line
    if all(np.isnan(ip)):
        return [False, ip]
    elif all((in_between(ip[0], a1[0], a2[0]),
              in_between(ip[0], b1[0], b2[0]),
              in_between(ip[1], a1[1], a2[1]),
              in_between(ip[1], b1[1], b2[1]))):
        return [True, ip]
    else:
        return [False, ip]


class Line:
    def __init__(self, points=[]):
        self.points = points

    def test_intersection(self, other):
        a1 = [self.points[0].x, self.points[0].y]
        a2 = [self.points[1].x, self.points[1].y]
        b1 = [other.points[0].x, other.points[0].y]
        b2 = [other.points[1].x, other.points[1].y]
        return seg_intersect(a1, a2, b1, b2)

    def at_t(self, t):
        pass

    def draw(self):
        glLineWidth(2)
        glBegin(GL_LINES)
        glColor(*self.points[0].color)
        glVertex2f(self.points[0].x, self.points[0].y)
        glColor(*self.points[1].color)
        glVertex2f(self.points[1].x, self.points[1].y)
        glEnd()


class Bezier:
    def __init__(self, points=[]):
        self.points = points
        self.resolution = 1000
        self.calculate_polynomial()

    def calculate_polynomial(self):
        self.d = (self.points[0].x, self.points[0].y)
        self.c = (3. * (self.points[1].x - self.points[0].x),
                  3. * (self.points[1].y - self.points[0].y))
        self.b = (3. * (self.points[2].x - self.points[1].x) - self.c[0],
                  3. * (self.points[2].y - self.points[1].y) - self.c[1])
        self.a = (self.points[3].x - self.points[0].x - self.c[0] - self.b[0],
                  self.points[3].y - self.points[0].y - self.c[1] - self.b[1])

    def test_intersection(self, other):
        s1, e1 = (0., 1.)
        s2, e2 = (0., 1.)
        err = np.inf
        prevPoint = np.array([np.inf, np.inf])
        ittr = 0
        while (err > 0.000001):  # if error decreased less than threshold, than return
            # generate 10 line segments for each bezier
            ts1 = np.linspace(s1, e1, 10, True)
            ps1 = [self.at_t(t) for t in ts1]
            ts2 = np.linspace(s2, e2, 10, True)
            ps2 = [other.at_t(t) for t in ts2]
            r = [False, np.array([0., 0.])]
            # test if any of those those segments intersect (using
            # seg_intersect)
            for i in xrange(len(ts1) - 1):
                for j in xrange(len(ts2) - 1):
                    pa1 = np.array(ps1[i])
                    pa2 = np.array(ps1[i + 1])
                    pb1 = np.array(ps2[j])
                    pb2 = np.array(ps2[j + 1])
                    r = seg_intersect(pa1, pa2, pb1, pb2)
                    if r[0]:  # intersection found
                        # find the point of intersection = r[1]
                        # compare this to the previous point of intersection
                        err = np.sqrt(np.sum((prevPoint - r[1]) ** 2))
                        prevPoint = r[1]
                        # update the checking bounds
                        s1 = ts1[i] - 0.0001
                        e1 = ts1[i + 1] + 0.0001
                        s2 = ts2[j] - 0.0001
                        e2 = ts2[j + 1] + 0.0001
                        # print "Intersection found:"
                        # print "Error:", err
                        # print "seg1_t:", s1, e1
                        # print "seg2_t:", s2, e2
                        # print prevPoint
                        # print "Ittr:", ittr, "intersect at", prevPoint
                        break  # ONLY one pair should intersect
                if r[0]:
                    break
            if not r[0]:
                # print "No Intersection was found"
                # print "Error:", err
                # print "seg1_t:", s1, e1
                # print "seg2_t:", s2, e2
                # print "Ittr:", ittr, "no intersection"
                return [False, prevPoint]
        return [True, prevPoint]

    def at_t(self, t):
        return (
            self.a[0] * t ** 3 + self.b[0] * t ** 2 + self.c[
                0] * t + self.d[0],
            self.a[1] * t ** 3 + self.b[1] * t ** 2 + self.c[1] * t + self.d[1])

    def draw(self):
        # [p.draw() for p in self.points]
        # draw bezier
        # cx = 3 (x1 - x0)
        # bx = 3 (x2 - x1) - cx
        # ax = x3 - x0 - cx - bx
        #
        # cy = 3 (y1 - y0)
        # by = 3 (y2 - y1) - cy
        # ay = y3 - y0 - cy - by

        # c = (3. * (self.points[1].x - self.points[0].x),
        #      3. * (self.points[1].y - self.points[0].y))
        # b = (3. * (self.points[2].x - self.points[1].x) - c[0],
        #      3. * (self.points[2].y - self.points[1].y) - c[1])
        # a = (self.points[3].x - self.points[0].x - c[0] - b[0],
        #      self.points[3].y - self.points[0].y - c[1] - b[1])

        self.calculate_polynomial()
        # self.a = a
        # self.b = b
        # self.c = c
        # self.d = (self.points[0].x,self.points[0].y)

        glLineWidth(2)
        c1 = self.points[0].color
        c2 = self.points[3].color
        glBegin(GL_LINE_STRIP)
        for i in xrange(self.resolution):
            t = i / float(self.resolution)
            omt = 1. - t
            glColor(c1[0] * t + c2[0] * omt,
                    c1[1] * t + c2[1] * omt,
                    c1[2] * t + c2[2] * omt,
                    c1[3] * t + c2[3] * omt)
            # x = a[0]*t**3 + b[0]*t**2 + c[0]*t + self.points[0].x
            # y = a[1]*t**3 + b[1]*t**2 + c[1]*t + self.points[0].y
            glVertex2f(*self.at_t(t))
            # glVertex2f(x,y)
        glEnd()


class PanZoom:
    def __init__(self):
        self.offset = [0., 0.]
        self.zoom = 1.
        self.slowPan = 0.01
        self.fastPan = 0.1
        self.texture = None
        self.scale = 1.
        self.contrast = 1.
        self.shader = None

    def process_mouse(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                wx = x
                wy = y
                glx, gly = self._window_to_gl(wx, wy)
                ix, iy = self._gl_to_image(glx, gly)
                # print "w:",wx,wy,"gl:",glx,gly,"im:",ix,iy

    def process_normal_keys(self, key, x, y):
        if key == 'x':
            dx = x / float(glutGet(GLUT_WINDOW_WIDTH))
            dy = y / float(glutGet(GLUT_WINDOW_HEIGHT))
            self.offset[0] -= self.zoom * 0.1 * dx
            self.offset[1] -= self.zoom * 0.1 * dy
            self.zoom *= 1.1
        elif key == 'z':
            dx = x / float(glutGet(GLUT_WINDOW_WIDTH))
            dy = y / float(glutGet(GLUT_WINDOW_HEIGHT))
            self.offset[0] += self.zoom * 0.1 * dx
            self.offset[1] += self.zoom * 0.1 * dy
            self.zoom *= 0.9
        elif key == 'c':
            self.change_contrast(.5)
        elif key == 'C':
            self.change_contrast(-.5)
        elif key == 'r':
            self.contrast = 1.
            self.compile_shader()
        elif key == 'w':
            self.offset[1] -= self.zoom * self.slowPan
        elif key == 'a':
            self.offset[0] -= self.zoom * self.slowPan
        elif key == 's':
            self.offset[1] += self.zoom * self.slowPan
        elif key == 'd':
            self.offset[0] += self.zoom * self.slowPan
        elif key == 'W':
            self.offset[1] -= self.zoom * self.fastPan
        elif key == 'A':
            self.offset[0] -= self.zoom * self.fastPan
        elif key == 'S':
            self.offset[1] += self.zoom * self.fastPan
        elif key == 'D':
            self.offset[0] += self.zoom * self.fastPan

    def process_special_keys(self, key, x, y):
        if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
            scale = self.fastPan
        else:
            scale = self.slowPan
        if key == GLUT_KEY_DOWN:
            self.offset[1] += self.zoom * scale
        elif key == GLUT_KEY_UP:
            self.offset[1] -= self.zoom * scale
        elif key == GLUT_KEY_LEFT:
            self.offset[0] -= self.zoom * scale
        elif key == GLUT_KEY_RIGHT:
            self.offset[0] += self.zoom * scale
        # print self.offset

    def setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            self.offset[0], self.zoom + self.offset[
                0], self.offset[1] + self.zoom,
            self.offset[1], 0, 1)  # so gl agrees with texture coords
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)

    def draw(self):
        self.setup_projection()
        if self.texture == None:
            self.draw_test_quad()
        else:
            self.draw_texture()

    def draw_test_quad(self):
        # test quad
        glBegin(GL_QUADS)
        glColor(1., 0., 0., 1.)
        glVertex2f(0., 1.)
        glColor(0., 1., 0., 1.)
        glVertex2f(1., 1.)
        glColor(0., 0., 1., 1.)
        glVertex2f(1., 0.)
        glVertex2f(0., 0.)
        glEnd()

    # ---- texture -----
    def load_image(self, imageFilename, scale_window=False):
        glEnable(GL_TEXTURE_2D)
        if self.texture != None:
            glDeleteTextures(self.texture)
        self.texture = glGenTextures(1)

        # load image (as color)
        image = PIL.Image.open(imageFilename).convert("RGB")
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.imageSize = image.size

        glutSize = (glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_WIDTH))
        if scale_window:
            if self.imageSize[0] <= glutSize[0] and self.imageSize[1] <= glutSize[1]:
                self.scale = 1.
                glutReshapeWindow(*self.imageSize)
            else:
                self.scale = max(glutSize[0] / float(
                    self.imageSize[0]), glutSize[1] / float(self.imageSize[1]))
                glutReshapeWindow(int(math.ceil(self.imageSize[0] *
                                  self.scale)), int(math.ceil(self.imageSize[1] * self.scale)))
        else:
            if self.imageSize[0] <= glutSize[0] and self.imageSize[1] <= glutSize[1]:
                self.scale = min(glutSize[0] / float(
                    self.imageSize[0]), glutSize[1] / float(self.imageSize[1]))
                glutReshapeWindow(int(math.ceil(self.imageSize[0] *
                                  self.scale)), int(math.ceil(self.imageSize[1] * self.scale)))
            else:
                self.scale = max(glutSize[0] / float(
                    self.imageSize[0]), glutSize[1] / float(self.imageSize[1]))
                glutReshapeWindow(int(math.ceil(self.imageSize[0] *
                                  self.scale)), int(math.ceil(self.imageSize[1] * self.scale)))

        glColor4f(1., 1., 1., 1.)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, image.size[0], image.size[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, image.tostring("raw", "RGB", 0, -1))  # RADAR GL_UNSIGNED_BYTE may be wrong
        glBindTexture(GL_TEXTURE_2D, 0)
        self.imageData = image.tostring()

    def change_contrast(self, deltaContrast):
        self.contrast += deltaContrast
        self.contrast = max(self.contrast, 0.)
        self.compile_shader()

    def compile_shader(self):
        vShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vShader, """
        varying vec2 texture_coordinate;
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            texture_coordinate = vec2(gl_MultiTexCoord0);
        }""")
        glCompileShader(vShader)

        fShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fShader, """
        vec4 contrast = vec4(%f,%f,%f,1.0);
        uniform sampler2D my_color_texture;
        varying vec2 texture_coordinate;
        void main() {
            gl_FragColor = texture2D(my_color_texture, texture_coordinate);
            gl_FragColor = pow(gl_FragColor, contrast);
        }""" % (self.contrast, self.contrast, self.contrast))
        glCompileShader(fShader)

        program = glCreateProgram()
        glAttachShader(program, vShader)
        glAttachShader(program, fShader)
        glLinkProgram(program)
        self.shader = program

    def draw_texture(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        if self.shader != None:
            glUseProgram(self.shader)
        glBegin(GL_QUADS)
        glTexCoord2f(0., 0.)
        glVertex2f(0., 0.,)
        glTexCoord2f(1., 0.)
        glVertex2f(1., 0.)
        glTexCoord2f(1., 1.)
        glVertex2f(1., 1.)
        glTexCoord2f(0., 1.)
        glVertex2f(0., 1.)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    # --- conversion ---
    def _window_to_gl(self, x, y):
        return self.offset[0] + self.zoom * x / float(glutGet(GLUT_WINDOW_WIDTH)), self.offset[1] + self.zoom * y / float(glutGet(GLUT_WINDOW_HEIGHT))

    def _gl_to_window(self, x, y):
        return (x - self.offset[0]) / self.zoom * float(glutGet(GLUT_WINDOW_WIDTH)), (self.offset[1] - y) / self.zoom * float(glutGet(GLUT_WINDOW_HEIGHT))

    def _gl_to_image(self, x, y):
        return x * float(self.imageSize[0]), y * float(self.imageSize[1])

    def _image_to_gl(self, x, y):
        return x / float(self.imageSize[0]), y / float(self.imageSize[1])

    def _window_to_image(self, x, y):
        return self._gl_to_image(*self._window_to_gl(x, y))

    def _image_to_window(self, x, y):
        return self._gl_to_window(*self._image_to_gl(x, y))


def test_pan_zoom(imageFilename=None):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(800, 600)
    glutCreateWindow("Pan Zoom Test")
    glClearColor(0., 0., 0., 1.)

    pz = PanZoom()
    global points
    global beziers
    global lines
    points = []
    beziers = []
    lines = []

    _defaultColors = [(1., 0., 0., 0.5),
                      (0., 1., 0., 0.5),
                      (0., 0., 1., 0.5),
                      (1., 1., 0., 0.5),
                      (1., 0., 1., 0.5),
                      (0., 1., 1., 0.5)]

    if imageFilename != None:
        pz.load_image(imageFilename)

    global selectedPoint
    selectedPoint = None

    # mouse
    def process_mouse(button, state, x, y):
        global selectedPoint
        pz.process_mouse(button, state, x, y)
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_UP:
                glx, gly = pz._window_to_gl(x, y)
                c = _defaultColors[len(points) % len(_defaultColors)]
                points.append(Point(glx, gly, c))

        if button == GLUT_RIGHT_BUTTON:
            if state == GLUT_UP:
                glx, gly = pz._window_to_gl(x, y)
                dist = 1.0
                for p in points[:]:
                    if abs(p.x - glx) < pz.zoom * 0.01:
                        if abs(p.y - gly) < pz.zoom * 0.01:
                            points.remove(p)

        if button == GLUT_MIDDLE_BUTTON:
            if state == GLUT_DOWN:
                # select point
                for p in points[:]:
                    glx, gly = pz._window_to_gl(x, y)
                    if abs(p.x - glx) < pz.zoom * 0.01:
                        if abs(p.y - gly) < pz.zoom * 0.01:
                            global selectedPoint
                            selectedPoint = p
                            selectedPoint.x, selectedPoint.y = (glx, gly)
                            break
            if state == GLUT_UP:
                selectedPoint = None

        glutPostRedisplay()
    glutMouseFunc(process_mouse)

    # active mouse
    def process_active_mouse_motion(x, y):
        global selectedPoint
        if selectedPoint != None:
            selectedPoint.x, selectedPoint.y = pz._window_to_gl(x, y)
            glutPostRedisplay()
    glutMotionFunc(process_active_mouse_motion)

    # normal
    def process_normal_keys(key, x, y):
        global points
        global beziers
        global lines
        if key == 'Q':
            # print out location of points, sorted by y axis?
            print "# Image: %s" % imageFilename
            print "# Size :", pz.imageSize
            print "#"
            print "# subpixel locations"
            print "# x y"
            for p in sorted(points, key=attrgetter('y'), reverse=True):  # sort by -y to get the right order
                print "%f %f" % pz._gl_to_image(p.x, p.y)
            sys.exit(0)
        elif key == 'b':  # add a bezier using the most recent 4 points
            if len(points) > 3:
                beziers.append(Bezier(points[-4:]))
        elif key == 'B':  # delete last bezier
            if len(beziers):
                beziers.pop()
        elif key == 'i':  # test intersection of 'adjacent' bezier curves
            intersections = []
            if len(beziers) > 1:
                for i in xrange(len(beziers) - 1):
                    for j in xrange(len(beziers) - i - 1):
                        # print i,j
                        b1 = beziers[i]
                        b2 = beziers[i + j + 1]
                        intersections.append(b1.test_intersection(b2))
                beziers = []
            if len(lines) > 1:
                intersections = []
                for i in xrange(len(lines) - 1):
                    for j in xrange(len(lines) - i - 1):
                        intersections.append(
                            lines[i].test_intersection(lines[i + j + 1]))
                lines = []
            points = []
            for i in intersections:
                if i[0]:
                    c = _defaultColors[len(points) % len(_defaultColors)]
                    # add intersection to items, maybe make these crosses NOT
                    # points
                    points.append(Point(i[1][0], i[1][1], c))
        elif key == 'l':  # add a line with most recent 2 points
            if len(points) > 1:
                lines.append(Line(points[-2:]))
        elif key == 'L':  # delete last line
            if len(lines):
                lines.pop()
        pz.process_normal_keys(key, x, y)
        glutPostRedisplay()
    glutKeyboardFunc(process_normal_keys)

    # special
    def process_special_keys(key, x, y):
        pz.process_special_keys(key, x, y)
        glutPostRedisplay()
    glutSpecialFunc(process_special_keys)

    def draw_help():
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1, 1, 0, 0, 1)
        glBegin(GL_QUADS)
        glColor(0., 0., 0., 0.1)
        glVertex2f(0, 0)
        glVertex2f(0.25, 0)
        glVertex2f(0.25, 0.25)
        glVertex2f(0, 0.25)
        glEnd()
        px = 0
        py = 13
        w = float(glutGet(GLUT_WINDOW_WIDTH))
        h = float(glutGet(GLUT_WINDOW_HEIGHT))
        p2gl = lambda px, py: (px / w, py / h)
        glColor(1., 1., 1., 1.)
        helptxt = """--Keys--\nwasd(arrows) : pan\nzx : zoom\nl : add line\nL : delete line\nb : add bezier\nB : delete bezier\ni : intersect lines/beziers\nQ : quit\n"""
        helptxt += """--Mouse--\nleft : add point\nmiddle : move point\nright : delete point"""
        for c in helptxt:
            if c == '\n':
                py += 13
                px = 0
                continue
            glRasterPos2f(*p2gl(px, py))
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))
            px += 8
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

    # draw
    def display():
        glClear(GL_COLOR_BUFFER_BIT)
        pz.draw()
        # draw help
        draw_help()
        [p.draw() for p in points]
        [l.draw() for l in lines]
        [b.draw() for b in beziers]
        glutSwapBuffers()
    glutDisplayFunc(display)

    glutMainLoop()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        fn = sys.argv[1]
    else:
        fn = "tests/H1_skull_2.jpg"
    test_pan_zoom(fn)
