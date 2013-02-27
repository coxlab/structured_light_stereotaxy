#!/usr/bin/env python

import numpy as np
import pylab as pl

import cv

md = 'L2/Scan01/View1/Images/'

if False:
    black = cv.LoadImage(md + 'Z0000.jpg', False)
    white = cv.LoadImage(md + 'A0000.jpg', False)
    bars = [cv.LoadImage(md + 'A000%i.jpg' % i, False) for i in xrange(1, 8)]
    imsize = cv.GetSize(black)

    tempim = cv.CreateImage(imsize, black.depth, black.nChannels)
    threshim = cv.CreateImage(imsize, black.depth, black.nChannels)
    t = 0.5
    dim = cv.CreateImage(imsize, black.depth, black.nChannels)

    # compute threshold image
    cv.Sub(white, black, dim)
    cv.ScaleAdd(dim, t, black, threshim)
    cv.SaveImage('threshim.png', threshim)

    bim = cv.CreateImage(imsize, black.depth, black.nChannels)
    depthim = cv.CreateImage(imsize, black.depth, black.nChannels)
    cv.SetZero(depthim)
    cv.AddS(depthim, 1, depthim)

    for (bi, barim) in enumerate(bars):
        print "bar:", bi
        cv.Cmp(barim, threshim, dim, cv.CV_CMP_GE)
        cv.Scale(dim, bim, (2 ** (bi + 1)) / 255.)
        cv.Add(depthim, bim, depthim)

    cv.SaveImage('depthim.png', depthim)

if True:
    # phaseim = cv.CreateImage(imsize, cv.IPL_DEPTH_32F, 1)
    # cacc = cv.CreateImage(imsize, cv.IPL_DEPTH_32F, 1)
    # sacc = cv.CreateImage(imsize, cv.IPL_DEPTH_32F, 1)
    # phases = [cv.LoadImage(md+'C000%i.jpg' % i, False) for i in xrange(6)]
    phases = [np.mean(pl.imread(md + 'C000%i.jpg' % i), 2) for i in xrange(6)]
    cacc = np.zeros(
        phases[0].shape)  # cv.CreateImage(imsize, cv.IPL_DEPTH_32F, 1)
    sacc = np.zeros(
        phases[0].shape)  # cv.CreateImage(imsize, cv.IPL_DEPTH_32F, 1)
    pvals = [(np.pi * 2.) / 6. * i for i in xrange(6)]

    for (pv, pim) in zip(pvals, phases):
        print "phase:", pv
        c = np.cos(pv)
        s = np.sin(pv)
        cacc += c * pim
        sacc += s * pim

    phaseim = np.arctan2(cacc, sacc)
    pl.gray()
    pl.imsave('phases.png', phaseim[::-1, :])

if True:
    phase = pl.imread('phases.png')
    bar = pl.imread('depthim.png')
