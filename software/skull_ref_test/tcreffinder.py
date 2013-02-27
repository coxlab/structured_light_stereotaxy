#!/usr/bin/env python

import subprocess

from pylab import *


def find_tc_refs(textureImage):
    pass


if __name__ == '__main__':
    testImageFile = 'scans/H7/Scan02/skull_cropped.png'
    testImage = imread(testImageFile)

    # find them automatically
    autoRefs = find_tc_refs(textureImage)

    # find them manually
    so = file('tcRefs', 'w')
    subprocess.Popen(
        "python %s %s/%s" % ('/Users/graham/Projects/glZoomView/zoomView.py',
                             testImageFile), shell=True, stdout=so).wait()
    so.close()
    manualRefs = loadtxt('tcRefsXY')
