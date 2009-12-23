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

def cluster_points(x,y,z,n):
    wz = whiten(z)
    kInit = linspace(min(wz), max(wz), n)
    res, idx = kmeans2(wz, kInit, iter=100,minit='matrix')
    
    xs = [[] for i in xrange(n)]
    ys = [[] for i in xrange(n)]
    zs = [[] for i in xrange(n)]
    
    for i in xrange(len(idx)):
        xs[idx[i]] += [x[i],]
        ys[idx[i]] += [y[i],]
        zs[idx[i]] += [z[i],]
    
    return xs, ys, zs

xs, ys, zs = cluster_points(x,y,z,NClusters)

# calculate 'fit'
stDev = 0.0
for i in xrange(NClusters):
    stDev += std(xs[i])
    stDev += std(ys[i])
    stDev += std(zs[i])
stDev /= 3
print stDev

clusterFailures = 0
while any([len(c) == 0 for c in xs]):
    clusterFailures += 1
    print "kmeans2 failed to find",NClusters,"clusters, trying again with",NClusters-clusterFailures
    xs, ys, zs = cluster_points(x,y,z,NClusters-clusterFailures)

NClusters -= clusterFailures

# # cluster based on z measurements
# wz = whiten(z)
# kInit = linspace(min(wz),max(wz),NClusters)
# #res, idx = kmeans2(wz,NClusters,iter=100,minit='points') # look for N steps
# res, idx = kmeans2(wz,kInit,iter=100,minit='matrix') # look for N steps
# 
# # split clusters
# xs = [[] for i in range(NClusters)]
# ys = [[] for i in range(NClusters)]
# zs = [[] for i in range(NClusters)]
# 
# for i in range(len(idx)):
#     xs[idx[i]] += [x[i],]
#     ys[idx[i]] += [y[i],]
#     zs[idx[i]] += [z[i],]
# 
# #print "raw(non-aligned) z-difference:",mean(zs[1]) - mean(zs[0])
# #print "raw(non-aligned) z-difference:",[abs(mean(zs[i]) - mean(zs[i-1])) for i in range(NClusters)]

def align_data(xs, ys, zs):
    weighted_x_slopes = []
    weighted_y_slopes = []
    for i in range(len(xs)):
        xr = linregress(xs[i], zs[i])
        yr = linregress(ys[i], zs[i])
        weighted_x_slopes += [xr[0] * len(xs[i]),]
        weighted_y_slopes += [yr[0] * len(ys[i]),]
    
    NPoints = sum([len(x) for x in xs])
    x_slope = sum(weighted_x_slopes)/NPoints
    y_slope = sum(weighted_y_slopes)/NPoints
    
    for g in range(len(xs)):
        for i in range(len(zs[g])):
            zs[g][i] -= ys[g][i] * y_slope + xs[g][i] * x_slope
    
    return xs, ys, zs

xs, ys, zs = align_data(xs, ys, zs)
# #print "aligning..."
# # calculate x and y tilt of stairs
# weighted_x_slopes = []
# weighted_y_slopes = []
# for i in range(NClusters):
#     xr = linregress(xs[i],zs[i])
#     yr = linregress(ys[i],zs[i])
#     weighted_x_slopes += [xr[0]*len(xs[i]),]
#     weighted_y_slopes += [yr[0]*len(ys[i]),]
# 
# x_slope = sum(weighted_x_slopes)/len(x)
# y_slope = sum(weighted_y_slopes)/len(y)
# 
# for g in range(NClusters):
#     for i in range(len(zs[g])):
#         zs[g][i] -= ys[g][i] * y_slope + xs[g][i] * x_slope

#print "aligned z-difference:",[abs(mean(zs[i]) - mean(zs[i-1])) for i in range(NClusters)]
clusterMeans = [mean(zs[i]) for i in range(NClusters)]
clusterMeans.sort()
#print "Z-Mean\tZ-Diffs"
print "\t",
for i in range(NClusters):
    print "%.3f\t" % clusterMeans[i],
print
for i in range(NClusters):
    print "%.3f\t" % clusterMeans[i],
    for i2 in range(NClusters):
        print "%.3f\t" % abs(clusterMeans[i] - clusterMeans[i2]),
    print

colors = ['b', 'r', 'g', 'c', 'm']
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
