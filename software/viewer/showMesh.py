#!/usr/bin/env python

import sys

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import objLoader

name = 'scan viewer'
#dataFile = 'scan_bjg.asc'
#angle = 0.0
xrot = 0.0
yrot = 0.0
zrot = 0.0
xpos = 0.0
ypos = 0.0
zpos = 0.0
scale = 0.01
mouseFocused = False
mouseRotating = False
mouseLassoing = False
lassoPoints = []
sx = 0
sy = 0
#x = []
#y = []
#z = []
#N = 0
obj = None
meshFile = 'example_mesh/mesh.obj'
textureFile = 'example_mesh/texture.jpg'

#------------------------------------------------------
#------------------------------------------------------
#--------------------- classes ------------------------
#------------------------------------------------------
#------------------------------------------------------

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400,400)
    glutCreateWindow(name)
    glClearColor(0.,0.,0.,1.)
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    #glutPassiveMotionFunc(process_passive_mouse_motion)
    glutMotionFunc(process_active_mouse_motion)
    glutEntryFunc(process_mouse_entry)
    glutMouseFunc(process_mouse)
    glutKeyboardFunc(process_normal_keys)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40.,1.,0.1,1000.0)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    #glPushMatrix()
    #f = open(dataFile,'r')
    #l = f.readline()
    #global x,y,z,N
    global obj, meshFile, textureFile
    if len(sys.argv) > 1:
      meshFile = sys.argv[1]
    if len(sys.argv) > 2:
      textureFile = sys.argv[2]
    print "Loading obj file: ", meshFile, " and texture: ", textureFile, "...",
    obj = objLoader.OBJ(meshFile, textureFile)
    print "done"
    print "Preparing gl display list...",
    obj.prep_lists()
    print "done"
    #while (len(l) > 2):
    #    items = l[:-2].split(' ')
    #    x += [float(items[0])*0.02,]
    #    y += [float(items[1])*0.02,]
    #    z += [float(items[2])*0.02,]
    #    l = f.readline()
    #N = len(x)
    print "Entering main loop"
    print " == Usage == "
    print "  wasd : stafe camera"
    print "  zx : zoom camera in/out"
    print "  right click and drag : rotate mesh"
    print "  tpm : toggle texture, point cloud, mesh"
    glutMainLoop()
    return

def process_normal_keys(key, x, y):
    #print key
    global scale, xpos, ypos, obj
    if key == 'z':
        scale *= 1.1
    elif key == 'Z':
        scale *= 11.1
    elif key == 'x':
        scale *= 0.9
    elif key == 'X':
        scale *= 0.09
    elif key == 'w':
        ypos -= 0.1
    elif key == 'W':
        ypos -= 1.0
    elif key == 'a':
        xpos += 0.1
    elif key == 'A':
        xpos += 1.0
    elif key == 's':
        ypos += 0.1
    elif key == 'S':
        ypos += 1.0
    elif key == 'd':
        xpos -= 0.1
    elif key == 'D':
        xpos -= 1.0
    elif key == 't':
        obj.showTexture = not obj.showTexture
        #obj.prep_list()
    elif key == 'm':
        obj.showMesh = not obj.showMesh
        #obj.prep_list()
    elif key == 'p':
        obj.showPointCloud = not obj.showPointCloud
        #obj.prep_list()
    return

def process_mouse(button, state, x, y):
    #print button, state, x, y
    global sx, sy, mouseFocused, mouseRotating, mouseLassoing, lassoPoints
    if (state == GLUT_DOWN) and mouseFocused and (button == GLUT_RIGHT_BUTTON):
        sx = x
        sy = y
        mouseRotating = True
    elif state == GLUT_UP:
        if button == GLUT_RIGHT_BUTTON:
            mouseRotating = False
        # elif button == GLUT_LEFT_BUTTON:
        #     mouseLassoing = False
        #     lassoPoints = []
    # elif (state == GLUT_DOWN) and mouseFocused and (button == GLUT_LEFT_BUTTON):
    #     # start selection lasso
    #     lassoPoints += [(x,y),]
    #     mouseLassoing = True
    return

def process_mouse_entry(state):
    global mouseFocused
    if state == GLUT_LEFT:
        mouseFocused = False
    if state == GLUT_ENTERED:
        mouseFocused = True

# def process_passive_mouse_motion(x, y):
#     global mouseFocused, mouseRotating
#     if (not mouseFocused) or (not mouseRotating):
#         return
#     dx = x/200.0 - 1.0
#     dy = y/200.0 - 1.0
#     global xrot, yrot, angle
#     xrot = dy
#     yrot = dx
#     angle = (dx * dx + dy * dy) ** 0.5 * 20.0
#     return

def process_active_mouse_motion(x, y):
    global mouseFocused, mouseRotating, mouseLassoing
    if mouseFocused:
        if mouseRotating:
            dx = (x - sx)/400.0
            dy = (y - sy)/400.0
            global xrot, yrot, angle
            xrot += dx
            yrot += dy
            #angle += (dx * dx + dy * dy) ** 0.5 * 20.0
        # if mouseLassoing:
        #     global lassoPoints
        #     if lassoPoints[-1] != (x,y):
        #         lassoPoints += [(x,y),]
    return

def display():
    global xpos, ypos, zpos, xrot, yrot, zrot, angle, scale
    global obj
    #zpos += 0.01
    #scale += 0.1
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    #glPointSize(2.0)
    glPushMatrix()
    glTranslatef(xpos,ypos,zpos)
    #glRotatef(angle,xrot,yrot,zrot)
    glRotatef(xrot,0.0,1.0,0.0)
    glRotatef(yrot,1.0,0.0,0.0)
    glScalef(scale,scale,scale)
    #glCallList(obj.gl_list)
    obj.display()
    #glBegin(GL_POINTS)
    #for i in range(N):
    #    #glColor4f(1.0, 0.0, 0.0, 1.0)
    #    glVertex3f(x[i],y[i],z[i])
    #glEnd()
    glPopMatrix()
    
    # draw lasso
    # global lassoPoints
    # if len(lassoPoints) > 0:
    #     print lassoPoints[-1]
    #     glPushMatrix()
    #     glLoadIdentity()
    #     glColor3f(1.0, 0.0, 0.0)
    #     glBegin(GL_LINE_STRIP)
    #     #for point in lassoPoints:
    #     #    glVertex2f(point[0]/400.0-1, 1-point[1]/400.0)
    #     #    #glVertex2f((point[0]-200.0)/50.0, (200.0-point[1])/50.0)
    #     glVertex2f(1.0,1.0)
    #     glVertex2f(1.0,-1.0)
    #     glVertex2f(-1.0,1.0)
    #     glVertex2f(-1.0,-1.0)
    #     glVertex2f(1.0,1.0)
    #     glEnd()
    #     glPopMatrix()
    
    glutSwapBuffers()
    glutPostRedisplay()
    return

if __name__ == '__main__': main()