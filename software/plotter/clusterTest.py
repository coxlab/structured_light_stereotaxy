#!/usr/bin/env python

import sys

from pylab import *
from scipy.cluster.vq import *
from scipy.stats import linregress

filename = 'stairs_cleaner_Scene.obj'
if len(sys.argv) > 1:
    filename = sys.argv[1]

NClusters = 2
if len(sys.argv) > 2:
    NClusters = int(sys.argv[2])

# read file
f = open(filename,'r')

l = f.readline()
while l[0] != 'v':
	l = f.readline()

x = []
y = []
z = []

while l[:2] == 'v ':
	items = l.split(' ')
	#print l
	x += [float(items[1]),]
	y += [float(items[2]),]
	z += [float(items[3]),]
	l = f.readline()

f.close()

# cluster based on z measurements
wz = whiten(z)
#res, idx = kmeans2(wz,NClusters,iter=100,minit='points') # look for N steps
res, idx = kmeans2(array(z),NClusters,iter=100,minit='points') # look for N steps

# split clusters
xs = [[] for i in range(NClusters)]
ys = [[] for i in range(NClusters)]
zs = [[] for i in range(NClusters)]

for i in range(len(idx)):
    xs[idx[i]] += [x[i],]
    ys[idx[i]] += [y[i],]
    zs[idx[i]] += [z[i],]

#print "raw(non-aligned) z-difference:",mean(zs[1]) - mean(zs[0])
print "raw(non-aligned) z-difference:",[abs(mean(zs[i]) - mean(zs[i-1])) for i in range(NClusters)]

print "aligning..."
# calculate x and y tilt of stairs
weighted_x_slopes = []
weighted_y_slopes = []
for i in range(NClusters):
    xr = linregress(xs[i],zs[i])
    yr = linregress(ys[i],zs[i])
    weighted_x_slopes += [xr[0]*len(xs[i]),]
    weighted_y_slopes += [yr[0]*len(ys[i]),]

x_slope = sum(weighted_x_slopes)/len(x)
y_slope = sum(weighted_y_slopes)/len(y)

for g in range(NClusters):
    for i in range(len(zs[g])):
        zs[g][i] -= ys[g][i] * y_slope + xs[g][i] * x_slope

print "aligned z-difference:",[abs(mean(zs[i]) - mean(zs[i-1])) for i in range(NClusters)]
colors = ['b', 'r', 'g']
for i in range(NClusters):
    subplot(221)
    scatter(xs[i],ys[i],c=colors[i])
    subplot(222)
    scatter(xs[i],zs[i],c=colors[i])
    subplot(223)
    scatter(ys[i],zs[i],c=colors[i])
    subplot(224)
    hist(zs[i],color=colors[i])

show()
