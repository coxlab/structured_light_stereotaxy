#!/usr/bin/env python

import sys
import logging

# debug
logging.basicConfig(level=logging.DEBUG)

from pylab import *
#from scipy.cluster.vq import *
#from scipy.stats import linregress

d1file = 'dominoDeltas1'
d2file = 'dominoDeltas2'

# load the delta-zs for each domino for each scan
d1 = loadtxt(d1file)
d2 = loadtxt(d2file)

# actual deltas of the dominos (from lowest, 'highest z-value', to highest, 'lowest z-value')
d1a = [0.97, 0.97]
d2a = [0.94, 1.02]

# z is the value that the actual delta must be multiplied by to get the measured delta
z1 = d1 / d1a
z2 = d2 / d2a

# calculate errors of each measurement
e1 = d1 - d1a
e2 = d2 - d2a

# calculate prediction errors (e.g. use z1 to predict d2 given d2a, subtract actual d2)
pe1 = z2 * d1a - d1
pe2 = z1 * d2a - d2

# ==================== plotting =======================
def number_scatter(x, y, c, xOffset=0., yOffset=0., **kwargs):
    if len(x) != len(y):
        raise ValueError("length of x and y must be the same")
    for i in xrange(len(x)):
        s = str(i)
        text(x[i]+xOffset, y[i]+yOffset, s, color=c, **kwargs)

figure(1)
subplot(111)
title("blue = domino1, green = domino2")

subplot(221)
scatter(z1[:,0], z1[:,1], color='b', s=5)
scatter(z2[:,0], z2[:,1], color='g', s=5)
number_scatter(z1[:,0], z1[:,1], 'b')
number_scatter(z2[:,0], z2[:,1], 'g')
xlabel('z-gain for step 1')
ylabel('z-gain for step 2')
xlim([0.5,1.])
ylim([0.5,1.])

subplot(222)
scatter(e1[:,0], e1[:,1], color='b', s=5)
scatter(e2[:,0], e2[:,1], color='g', s=5)
number_scatter(e1[:,0], e1[:,1], 'b')
number_scatter(e2[:,0], e2[:,1], 'g')
xlabel('z-error for step 1')
ylabel('z-error for step 2')

subplot(223)
scatter(pe1[:,0], pe1[:,1], color='b', s=5)
scatter(pe2[:,0], pe2[:,1], color='g', s=5)
number_scatter(pe1[:,0], pe1[:,1], 'b')
number_scatter(pe2[:,0], pe2[:,1], 'g')
xlabel('prediction error for step 1')
ylabel('prediction error for step 2')

subplots_adjust(wspace=0.35, hspace=0.25)
