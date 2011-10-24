#!/usr/bin/env python

import sys, time
from math import *

import numpy

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

#from OpenGLContext import quaternion
import quaternion

#import objLoader
import bjg.glObj as glObj
from bjg.glOrbiter import Orbiter

#outputFile = 'selectedPoints.csv'
outputFile = ''
if len(sys.argv) > 3:
    outputFile = sys.argv[3]


meshFile = 'example_mesh/simple2.obj'
#meshFile = 'example_mesh/mesh.obj'
textureFile = 'example_mesh/texture.jpg'

centerMesh = False#True 

if len(sys.argv) > 1:
    meshFile = sys.argv[1]
    textureFile = None
if len(sys.argv) > 2:
    textureFile = sys.argv[2]
if len(sys.argv) > 3:
    if sys.argv[3].lower()[0] == 'c':
        centerMesh = True

global obj
obj = 0

winWidth, winHeight = 837, 651

mainWinID = 0
toolWinID = 0
selectWinID = 0
viewWinID = 0

tool = 'Select'
toolButtonIDs = [['Select', 0], ['Rotate', 0], ['Translate', 0], ['Zoom In', 0], ['Zoom Out', 0]]

selectHeader = ['id', 'x', 'y', 'z']
selectColWidths = [55, 55, 55, 55]
selectRowHeight = 13.
selectData = []

viewRadius = 100
trans = [0., 0., 0.]
viewDown = None

rotQuaternion = quaternion.Quaternion()

pointColorMap = [ (1., 0., 0., 1.), (0., 1., 0., 1.), (0., 0., 1., 1.),
                    (1., 1., 0., 1.), (1., 0., 1., 1.), (0., 1., 1., 1.)]

def lookup_id(name, idList):
    for (k,v) in idList:
        if name == k:
            return v

def lookup_name(wid, idList):
    for (k,v) in idList:
        if wid == v:
            return k

def pixel_to_world(px,py,ww,wh):
    return (px - ww / 2.)/(ww/2.), -(py - wh / 2.)/(wh/2.)

def display_text(text,px,py):
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    x = px
    y = py
    for c in text:
        glRasterPos2f(*pixel_to_world(x,y,w,h))
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))
        x += 8

def display_table(data, header, colWidths, rowHeight, x, y, colorMap=None):
    px = x
    py = y
    for (c,h) in zip(colWidths,header):
        display_text(h,px,py)
        px += c
    for (i, datum) in enumerate(data):
        y += rowHeight
        px = x
        if colorMap != None:
            ci = i % len(colorMap)
            glColor(*colorMap[ci])
        for (c,d) in zip(colWidths,datum):
            s = '%.2f' % d
            if len(s) > 5:
                s = s[:6] 
            display_text(s,px,y)
            px += c

def switch_to_tool(newTool):
    global tool, toolButtonIDs
    if newTool == tool:
        return
    oldTool = tool
    tool = newTool
    glutSetWindow(lookup_id(tool, toolButtonIDs))
    glutPostRedisplay()
    glutSetWindow(lookup_id(oldTool, toolButtonIDs))
    glutPostRedisplay()

def keyboard_main(key, x, y):
    #print key, x, y
    global obj
    global viewRadius
    global trans
    global rotQuaternion
    if key == 'z':
        view_zoom_in(None, None, x, y)
    elif key == 'x':
        view_zoom_out(None, None, x, y)
    elif key == 'r': # select rotate mode
        switch_to_tool('Rotate')
    elif key == 't': # select translate mode
        switch_to_tool('Translate')
    elif key == 's': # select select mode
        switch_to_tool('Select')
    elif key == 'm': # toggle mesh
        obj.showMesh = not obj.showMesh
        glutSetWindow(viewWinID)
        glutPostRedisplay()
    elif key == 'p': # toggle point cloud
        obj.showPointCloud = not obj.showPointCloud
        glutSetWindow(viewWinID)
        glutPostRedisplay()
    elif key == 'T': # reset translation
        trans = [0., 0., 0.]
        glutPostRedisplay()
    elif key == 'R': # reset rotation
        rotQuaternion = quaternion.Quaternion()
        glutPostRedisplay()
    elif key == 'Z': # reset zoom
        viewRadius = 100
    elif key == 'q':
        quit_program()

def view_select(button, state, x, y):
    global obj
    if state != GLUT_UP:
        return
    #print "view_select", button, state, x, y
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    y = h - y
    global obj
    # save old obj settings
    oldShowPointCloud = obj.showPointCloud
    oldShowMesh = obj.showMesh
    obj.showPointCloud = True
    obj.showMesh = False
    
    selectBuffer = glSelectBuffer(10000)
    glRenderMode(GL_SELECT)
    
    # render scene
    global trans
    global viewRadius
    global rotQuaternion
    glEnable(GL_DEPTH_TEST)
    glClearColor(0., 0., 0., 1.)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPickMatrix(x,y,10,10,glGetIntegerv(GL_VIEWPORT))
    gluPerspective(10.,1.,0.1,1000.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(trans[0],trans[1],viewRadius,trans[0],trans[1],trans[2], 0,1,0)
    #gluLookAt(0.,0.,viewRadius, trans[0], trans[1], trans[2], 0,1,0)
    #gluLookAt(0.,0.,viewRadius, 0.,0.,0., 0,1,0)
    glMultMatrixd(rotQuaternion.matrix())
    
    obj.display()
    
    
    # get hits
    hits = glRenderMode(GL_RENDER)
    global selectData
    if not glutGetModifiers() & GLUT_ACTIVE_SHIFT:
        selectData = []
    for hit in hits:
        #selectHeader = ['id', 'x', 'y', 'z']
        hid = hit.names[0]
        # check if this point is already in the 
        found = -1
        for (i,p) in enumerate(selectData):
            if p[0] == hid:
                found = i
                break
        if found != -1:
            selectData.pop(found)
        else:
            v = obj.vertices[hid]
            selectData.append([hid, v[0], v[1], v[2]])
        #print hit.names[0]
    
    # restore
    obj.showPointCloud = oldShowPointCloud
    obj.showMesh = oldShowMesh
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(10.,1.,0.1,1000.0)
    glutPostRedisplay()
    
    # update selection
    global selectWinID
    glutSetWindow(selectWinID)
    glutPostRedisplay()

def view_select_motion(x, y):
    pass

def view_rotate(button, state, x, y):
    global viewDown
    if state == GLUT_DOWN:
        viewDown = (x,y)
    elif state == GLUT_UP:
        viewDown = None

def view_rotate_motion(x, y):
    global viewDown
    if viewDown == None:
        return
    
    # global viewAzimuth, viewElevation
    # viewElevation += (y - viewDown[1])
    # if viewElevation >= 90.:
    #     viewElevation -= 180.
    # elif viewElevation <= -90.:
    #     viewElevation += 180.
    # viewAzimuth -= (x - viewDown[0])
    # if viewAzimuth > 180.:
    #     viewAzimuth -= 360.
    # elif viewAzimuth < -180.:
    #     viewAzimuth += 360.
    
    global rotQuaternion
    rotQuaternion = quaternion.fromEuler((y-viewDown[1])*0.01,(x-viewDown[0])*0.01,0.) * rotQuaternion
    #print rotQuaternion.matrix()
    viewDown = (x,y)
    glutPostRedisplay()

def view_translate(button, state, x, y):
    global viewDown
    if state == GLUT_DOWN:
        viewDown = (x,y)
    elif state == GLUT_UP:
        viewDown = None

def view_translate_motion(x, y):
    global viewDown
    dx = x - viewDown[0]
    dy = y - viewDown[1]
    global trans
    global viewRaidus
    trans[0] = trans[0] + dx * -viewRadius/5000.
    trans[1] = trans[1] + dy * viewRadius/5000.
    viewDown = (x,y)
    #print trans
    glutPostRedisplay()

def view_zoom_in(button, state, x, y):
    global viewRadius
    viewRadius -= 5
    glutPostRedisplay()

def view_zoom_out(button, state, x, y):
    global viewRadius
    viewRadius += 5
    glutPostRedisplay()

def view_motion(x, y):
    global tool
    if tool == 'Select':
        view_select_motion(x, y)
    elif tool == 'Rotate':
        view_rotate_motion(x, y)
    elif tool == 'Translate':
        view_translate_motion(x, y)

def view_clicked(button, state, x, y):
    global tool
    if tool == 'Select':
        view_select(button, state, x, y)
    elif tool == 'Rotate':
        view_rotate(button, state, x, y)
    elif tool == 'Translate':
        view_translate(button, state, x, y)
    elif tool == 'Zoom In':
        view_zoom_in(button, state, x, y)
    elif tool == 'Zoom Out':
        view_zoom_out(button, state, x, y)

def select_clicked(button, state, x, y):
    pass

def tool_button_clicked(button, state, x, y):
    wid = glutGetWindow()
    wname = lookup_name(wid, toolButtonIDs)
    global tool
    if wname == tool:
        return
    switch_to_tool(wname)

def display_tool_button():
    wid = glutGetWindow()
    wname = lookup_name(wid, toolButtonIDs)
    if wname == tool:
        glClearColor(0., 0., 0., 1.)
        glColor(1., 1., 1., 1.)
    else:
        glClearColor(1., 1., 1., 1.)
        glColor(0., 0., 0., 1.)
    glClear(GL_COLOR_BUFFER_BIT)
    labelWidth = len(wname) * 8
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    x = (w - labelWidth)/2.
    y = (h + 13.)/2.
    display_text(wname,x,y)
    
    glutSwapBuffers()

def display_main():
    glClearColor(1., 1., 1., 1.)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glutSwapBuffers()

def display_tool():
    glClearColor(0.2, 0.2, 0.2, 1.)
    glClear(GL_COLOR_BUFFER_BIT)
    glutSwapBuffers()

def display_select():
    global selectData, selectHeader, selectColWidths, selectRowHeight
    if len(selectData) == 3:
        points = numpy.array(selectData)
        points = points[:,1:]
        points.sort(0)
        dists = [sqrt(sum((points[i-1]-points[i])**2)) for i in xrange(len(points))]
        r1 = numpy.product(dists) / sqrt(2*dists[0]**2*dists[1]**2 + 2*dists[1]**2*dists[2]**2 + 2*dists[2]**2*dists[0]**2 - dists[0]**4 - dists[1]**4 - dists[2]**4)    
        print "Radius of arc:", r1
    glClearColor(0.2, 0.2, 0.2, 1.)
    glClear(GL_COLOR_BUFFER_BIT)
    glColor(1., 1., 1., 1.)
    display_table(selectData, selectHeader, selectColWidths, selectRowHeight, 8, 26, pointColorMap)
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)
    glColor(1., 1., 1., 1.)
    glBegin(GL_LINES)
    glVertex2f(*pixel_to_world(7,27,w,h))
    glVertex2f(*pixel_to_world(8+sum(selectColWidths),27,w,h))
    glEnd()
    glutSwapBuffers()

def draw_origin():
    #glMatrixMode(GL_MODELVIEW)
    #glPushMatrix()
    #glLoadIdentity()
    
    # glColor(1.,0.,0.,0.)
    # glBegin(GL_POINTS)
    # glVertex3f(-1.,0.,0.)
    # glVertex3f(0.,-1.,0.)
    # glVertex3f(0.,0.,-1.)
    # glEnd()
    
    glPushMatrix() # X
    glRotatef(90,0,1,0)
    glColor(1.,0.,0.,1.)
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.5, 10, 3)
    glTranslate(0.,0.,0.5)
    glutSolidCone(0.1, 0.2, 10, 3)
    glPopMatrix()
    
    #glTranslate(0.,0.,-1.)
    glPushMatrix() # Y
    glRotatef(-90,1,0,0)
    glColor(0.,0.,1.,1.)
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.5, 10, 3)
    glTranslate(0.,0.,0.5)
    glutSolidCone(0.1, 0.2, 10, 3)
    glPopMatrix()
    
    glColor(0.,1.,0.,1.) # Z
    glPushMatrix()
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.5, 10, 3)
    glTranslate(0.,0.,0.5)
    glutSolidCone(0.1, 0.2, 10, 3)
    glPopMatrix()
    #glTranslate(0.,0.,-1.)
    
    #glTranslate(0.,0.,-1.)
    # glColor(1.,1.,1.,1.)
    # glutSolidSphere(0.2,10,10)
    #glPopMatrix()

def draw_selected_points():
    global selectData
    global obj
    
    # for (i, d) in enumerate(selectData):
    #     pid = d[0]
    #     ci = i % len(pointColorMap)
    #     glColor(*pointColorMap[ci])
    #     glPushMatrix()
    #     glTranslate(*obj.vertices[pid])
    #     glutSolidSphere(0.1, 10, 10)
    #     glPopMatrix()
    
    glPointSize(4.0)
    glBegin(GL_POINTS)
    for (i,d) in enumerate(selectData):
        pid = d[0]
        ci = i % len(pointColorMap)
        glColor(*pointColorMap[ci])
        glVertex3f(*obj.vertices[pid])
    glEnd()

def display_view():
    global obj
    global viewRadius
    global trans
    global rotQuaternion
    glEnable(GL_DEPTH_TEST)
    glClearDepth(1.0)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0., 0., 0., 1.)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    #gluLookAt(0.,0.,viewRadius, 0.,0.,0., 0,1,0)
    # maybe try:
    gluLookAt(trans[0],trans[1],viewRadius,trans[0],trans[1],trans[2], 0,1,0)
    #gluLookAt(0.,0.,viewRadius, trans[0], trans[1], trans[2], 0,1,0)
    glMultMatrixd(rotQuaternion.matrix())
    obj.display()
    draw_selected_points()
    draw_origin()
    glutSwapBuffers()

def quit_program():
    # print points to file
    if outputFile == '':
        print "#id  x      y      z\n"
        for d in selectData:
            #print '%i, %.3f, %.3f, %.3f\n' % (d[0], d[1], d[2], d[3])
            print '%i' % d[0]
    else:
        outFile = open(outputFile, 'w')
        outFile.write('#id  x      y      z\n')
        for d in selectData:
            #outFile.write('%i, %.3f, %.3f, %.3f\n' % (d[0], d[1], d[2], d[3]))
            outFile.write('%i\n' % d[0])
        outFile.close()
    sys.exit(0)

# ============================
# ======== Main ==============
# ============================

# - init -
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
glutInitWindowSize(winWidth, winHeight)
mainWinID = glutCreateWindow('3d point picker')

# - bind -
glutDisplayFunc(display_main)
glutKeyboardFunc(keyboard_main)

# - subwindows -
# tools
toolWinID = glutCreateSubWindow(mainWinID,0,0,winWidth,50)
glutDisplayFunc(display_tool)
dW, dH = 88, 30
x, y = 10, 10
for i in range(len(toolButtonIDs)):
    toolButtonIDs[i] = [toolButtonIDs[i][0], glutCreateSubWindow(toolWinID,x,y,dW,dH)]
    x += dW + 10
    glutDisplayFunc(display_tool_button)
    glutMouseFunc(tool_button_clicked)
    glutKeyboardFunc(keyboard_main)

# selection info
selectWinID = glutCreateSubWindow(mainWinID,winWidth-236,51,236,winHeight-51)
glutDisplayFunc(display_select)
glutMouseFunc(select_clicked)
glutKeyboardFunc(keyboard_main)

# point display
viewWinID = glutCreateSubWindow(mainWinID,0,51,winWidth-237,winHeight-51)
glutDisplayFunc(display_view)
glutMouseFunc(view_clicked)
glutMotionFunc(view_motion)
glutKeyboardFunc(keyboard_main)
glMatrixMode(GL_PROJECTION)
gluPerspective(10.,1.,0.1,1000.0)
#glMatrixMode(GL_MODELVIEW)
#gluLookAt(0,0,50, 0,0,0, 0,1,0)

# load mesh
#print "Loading mesh..."
#obj = objLoader.OBJ(meshFile, textureFile)
obj = glObj.GLOBJ()
obj.load(meshFile, textureFile)

#obj.vertices = obj.vertices - (150, -10, -600)

if centerMesh:
    obj.center_mean()
# if centerMesh:
#     # center mesh
#     v = numpy.array(obj.vertices)
#     v = v - numpy.mean(v,0)
#     obj.vertices = v.tolist()
#print "Prepping display..."
obj.prep_lists()
#print "Running"

glutMainLoop()
