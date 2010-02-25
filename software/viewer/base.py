#!/usr/bin/env python

import sys

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import objLoader

# simple viewer program that enables:
#  displays objects, meshes etc
#  allows rotation and movement of the camera
#  allows object selection and lassoing

#------------------------------------------------------
#------------------------------------------------------
#--------------------- classes ------------------------
#------------------------------------------------------
#------------------------------------------------------

class MouseRotator:
    def __init__(self, xScale, yScale, button=GLUT_RIGHT_BUTTON):
        self.focused = False
        self.rotating = False
        self.downX = 0
        self.downY = 0
        self.button = button
        self.xScale = xScale
        self.yScale = yScale
        self.xRotation = 0.0
        self.yRotation = 0.0
    
    def process_button(self, button, state, x, y):
        #print button, state
        if (state == GLUT_DOWN) and self.focused and (button == self.button):
            self.downX = x
            self.downY = y
            self.rotating = True
        elif (state == GLUT_UP) and (button == self.button):
            self.rotating = False
        return
    
    def process_entry(self, state):
        if state == GLUT_LEFT:
            self.focused = False
        elif state == GLUT_ENTERED:
            self.focused = True
        return
    
    def process_active_motion(self, x, y):
        if self.focused and self.rotating:
            self.xRotation += (x - self.downX) * self.xScale
            self.yRotation += (y - self.downY) * self.yScale
            #print self.xRotation, self.yRotation
        return
    
    def rotate_display(self):
        glRotatef(self.xRotation, 0.0, 1.0, 0.0)
        glRotatef(self.yRotation, 1.0, 0.0, 0.0)

class KeyboardTranslator:
    def __init__(self, moveIncrement=1.0, shiftScale=10.0):
        self.moveIncrement = moveIncrement
        self.shiftScale = shiftScale
        self.position = [0.0, 0.0, 0.0] # x, y, z
    
    def process_normal_keys(self, key, x, y):
        lowerKey = key.lower()
        inc = self.moveIncrement
        
        # check if shift is pressed
        modifiers = glutGetModifiers()
        if modifiers & GLUT_ACTIVE_SHIFT:
            inc *= self.shiftScale
        
        # check keys
        if lowerKey == 'w':
            self.position[1] += inc
        elif lowerKey == 'a':
            self.position[0] -= inc
        elif lowerKey == 's':
            self.position[1] -= inc
        elif lowerKey == 'd':
            self.position[0] += inc
        elif lowerKey == 'z':
            self.position[2] -= inc
        elif lowerKey == 'x':
            self.position[2] += inc
    
    def translate_display(self):
        glTranslate(*self.position)

# class KeyboardZoomer:
#     def __init__(self, zoomIn=1.1, zoomOut=0.9, shiftScale=10.0):
#         self.zoomIn = zoomIn
#         self.zoomOut = zoomOut
#         self.shiftScale = shiftScale
#         self.zoom = 1.0
# 
#     def process_normal_keys(self, key, x, y):
#         # check keys
#         if key == 'z':
#             self.zoom *= self.zoomIn
#         elif key == 'Z':
#             self.zoom *= self.zoomIn * self.shiftScale
#         elif key == 'x':
#             self.zoom *= self.zoomOut
#         elif key == 'X':
#             self.zoom *= self.zoomOut/self.shiftScale
#     
#     def zoom_display(self):
#         glScalef(self.zoom, self.zoom, self.zoom)

# class MouseZoomer:
#     def __init__(self, ):

def init_viewer(windowSize=(400,400), bgColor=(0.0, 0.0, 0.0, 1.0), name='viewer'):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(*windowSize)
    #windowWidth = glutGet(GLUT_WINDOW_WIDTH);
    #windowHeight = glutGet(GLUT_WINDOW_HEIGHT);
    glutCreateWindow(name)
    glClearColor(*bgColor)
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION, (10.0, 4.0, 10.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.01)
    glLightfv(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.005)
    glEnable(GL_LIGHT0)

def enable_perspective_view(perspective=(40.0, 1.0, 0.01, 10000.0)):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(*perspective)

def look_at(look_at_matrix=(0,0,10, 0,0,0, 0,1,0)):
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(*look_at_matrix)

#def display():
#    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def main():
    init_viewer()
    enable_perspective_view()
    look_at()
    
    obj = objLoader.OBJ(sys.argv[1],sys.argv[2])
    obj.prep_lists()
    
    mouseRotator = MouseRotator(2.0/glutGet(GLUT_WINDOW_WIDTH), 2.0/glutGet(GLUT_WINDOW_HEIGHT))
    keyboardTranslator = KeyboardTranslator()
    keyboardTranslator.position[2] = 100.0
    #keyboardZoomer = KeyboardZoomer()
    
    def process_active_motion(x, y):
        mouseRotator.process_active_motion(x, y)
    def process_mouse_entry(state):
        mouseRotator.process_entry(state)
    def process_mouse_button(button, state, x, y):
        mouseRotator.process_button(button, state, x, y)
    def process_normal_keys(key, x, y):
        keyboardTranslator.process_normal_keys(key, x, y)
        #keyboardZoomer.process_normal_keys(key, x, y)
    
    glutMotionFunc(process_active_motion)
    glutEntryFunc(process_mouse_entry)
    glutMouseFunc(process_mouse_button)
    glutKeyboardFunc(process_normal_keys)
    
    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        #keyboardTranslator.translate_display()
        #mouseRotator.rotate_display()
        #keyboardZoomer.zoom_display()
        gluLookAt(keyboardTranslator.position[0], keyboardTranslator.position[1], keyboardTranslator.position[2],
                keyboardTranslator.position[0],keyboardTranslator.position[1],-1000.0,
                0, 1, 0)
        #print keyboardTranslator.position
        #zoom
        # display objects
        
        glPushMatrix()
        mouseRotator.rotate_display()
        obj.display()
        #glMaterialfv(GL_FRONT,GL_DIFFUSE,(1.0, 1.0, 1.0, 1.0))
        #glutSolidTorus(5.0, 10.0, 20, 20)
        glPopMatrix()
        
        glPopMatrix()
        glutSwapBuffers()
        glutPostRedisplay()
    
    glutDisplayFunc(display)
    
    glutMainLoop()

if __name__ == '__main__': main()