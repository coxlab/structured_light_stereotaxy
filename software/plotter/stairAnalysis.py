#!/usr/bin/env python

import sys
import logging

# debug
logging.basicConfig(level=logging.DEBUG)

from pylab import *
from scipy.cluster.vq import *
from scipy.stats import linregress

#filename = '../../../scans/cleaned_stairs/stairs_cleaner_Scene.obj'
filename = '../../../scans/cleaned_stairs/tiltedstair_cleaned_1_Scene.obj'

if len(sys.argv) > 1:
    filename = sys.argv[1]

NClusters = 3
if len(sys.argv) > 2:
    NClusters = int(sys.argv[2])

def get_clusters(filename, NClusters = 3, maxTries = 3, alignZData = True):
    logging.debug("Loading file:%s" % filename)
    data = load_mesh_file(filename)
    
    # center mesh
    data['x'] = array(data['x']) - mean(data['x'])
    data['y'] = array(data['y']) - mean(data['y'])
    data['z'] = array(data['z']) - mean(data['z'])
    
    if alignZData:
        data = align_data_to_z(data)
        data = align_data_to_z(data)
    
    tries = 0
    while (tries < maxTries):
        logging.debug("Entering cluster_points_on_axis")
        clusters = cluster_points_on_axis(data, NClusters)
        if len(clusters) != NClusters:
            tries += 1
            NClusters -= 1
            if NClusters == 1:
                print "Clustering failed, raising exception"
                raise ValueError("process_file could not find >1 cluster in file:%s" % filename)
            print "Clustering failed with N=%i trying %i" % (NClusters+1, NClusters)
        else:
            tries = maxTries
    return clusters

# ===========
def calculate_data_normals(data):
    data['normals'] = []
    for f in data['faces']:
        p1 = array([data['x'][f[0]], data['y'][f[0]], data['z'][f[0]]])
        p2 = array([data['x'][f[1]], data['y'][f[1]], data['z'][f[1]]])
        p3 = array([data['x'][f[2]], data['y'][f[2]], data['z'][f[2]]])
        U = p2 - p1
        V = p3 - p1
        normal = cross(U,V)
        data['normals'] += [normal,]
    
    return data

def load_mesh_file(filename):
    """ 
    argument(s):
        filename: an .obj mesh file
    returns:
        data: dictionary of 'x','y','z' coordinates for each vertex from the obj file"""
    f = open(filename, 'r')
    data = {'x': [], 'y': [], 'z': [], 'faces': [], 'normals': []}
    
    for l in f:
        if l[:2] == 'v ':
            items = l.split(' ')
            data['x'] += [float(items[1]),]
            data['y'] += [float(items[2]),]
            data['z'] += [float(items[3]),]
        if l[:2] == 'f ':
            items = l.split(' ')
            if len(items) == 4:
                # the vertex defs within a face def are 1 indexed (not 0)
                data['faces'] += [[int(items[1].split('/')[0])-1,
                                int(items[2].split('/')[0])-1,
                                int(items[3].split('/')[0])-1],]
    f.close()
    
    return calculate_data_normals(data)

def cluster_points_on_axis(data, NClusters, clusterAxis='z'):
    """
    arguments:
        data:       dictionary containing x,y,z coordinates for points in a mesh
        NClusters:  number of clusters to try
    returns:
        clusters:   """
    
    # mData = transpose(array([data['x'],data['y'],data['z']]))
    # wData = whiten(mData)
    # centers, idx = kmeans2(wData, NClusters, iter=1000)
    
    wz = whiten(data[clusterAxis])
    kInit = linspace(min(wz), max(wz), NClusters)
    logging.debug("-cluster_points_on_axis- Calling kmeans2")
    centers, idx = kmeans2(wz, kInit, iter=1000, minit='matrix')
    
    # split up data
    clusters = [{'x': [], 'y': [], 'z': []} for i in xrange(NClusters)]
    
    for i in xrange(len(idx)):
        clusters[idx[i]]['x'] += [data['x'][i],]
        clusters[idx[i]]['y'] += [data['y'][i],]
        clusters[idx[i]]['z'] += [data['z'][i],]
    
    return clusters

def align_data_to_z(data):
    def get_centroid():
        return {'x': sum(data['x'])/len(data['x']),
                'y': sum(data['y'])/len(data['y']),
                'z': sum(data['z'])/len(data['z'])}
    
    # TODO rotate mesh so when looking up z-axis (down at mesh) you see a rectangle
    # aligned on the x and y axes
    
    data = calculate_data_normals(data)
    meanNormal = median(data['normals'],0)
    normNormal = meanNormal / sqrt(sum(meanNormal**2))
    yAngle = -arctan2(normNormal[0],normNormal[2])
    centroid = get_centroid()
    logging.debug("-align_data_to_z- yAngle:%.3f" % degrees(yAngle))
    data = rotate_about_y(data, yAngle, centroid)
    
    data = calculate_data_normals(data)
    meanNormal = median(data['normals'],0)
    normNormal = meanNormal / sqrt(sum(meanNormal**2))
    xAngle = arctan2(normNormal[1],normNormal[2])
    centroid = get_centroid()
    logging.debug("-align_data_to_z- xAngle:%.3f" % degrees(xAngle))
    data = rotate_about_x(data, xAngle, centroid)
    return data

def align_clustered_data_to_z(clusters, xAngle=None, yAngle=None):
    def weighted_slope(axis1, axis2):
        slope = 0.0
        NPoints = 0
        for i in xrange(len(clusters)):
            r = linregress(clusters[i][axis1], clusters[i][axis2])
            slope += r[0] * len(clusters[i]['x'])
            NPoints += len(clusters[i]['x'])
        return slope / NPoints
    
    def get_centroid():
        sx = 0.
        sy = 0.
        sz = 0.
        nx = 0
        ny = 0
        nz = 0
        for i in xrange(len(clusters)):
            sx += sum(clusters[i]['x'])
            sy += sum(clusters[i]['y'])
            sz += sum(clusters[i]['z'])
            nx += len(clusters[i]['x'])
            ny += len(clusters[i]['y'])
            nz += len(clusters[i]['z'])
        return {'x':sx/nx, 'y':sy/ny, 'z':sz/nz}
    
    #xCentroid = get_centroid('y', 'z')
    #yCentroid = get_centroid('x', 'z')
    centroid = get_centroid()
    
    #if yAngle == None:
    #    yAngle = arctan2(weighted_slope('x', 'z'), 1.0) # subplot 2
    logging.debug("-align_clustered_data_to_z- yAngle:%.3f" % degrees(yAngle))
    for i in xrange(len(clusters)):
        clusters[i] = rotate_about_y(clusters[i], yAngle, centroid)
    
    #if xAngle == None:
    #    xAngle = -arctan2(weighted_slope('y','z'), 1.0) # subplot 3
    logging.debug("-align_clustered_data_to_z- xAngle:%.3f" % degrees(xAngle))
    for i in xrange(len(clusters)):
        clusters[i] = rotate_about_x(clusters[i], xAngle, centroid)
    #return clusters
    
    # zAngle = -arctan2(weighted_slope('x','y'), 1.0) # subplot 1
    # logging.debug("-align_clustered_data_to_z- zAngle:%.3f" % degrees(zAngle))
    # for i in xrange(len(clusters)):
    #     clusters[i] = rotate_about_z(clusters[i], zAngle)
    
    return clusters

# def align_clustered_data_to_z(clusters):
#     wXSlopes = []
#     wYSlopes = []
#     for i in xrange(len(clusters)):
#         xr = linregress(clusters[i]['x'], clusters[i]['z'])
#         yr = linregress(clusters[i]['y'], clusters[i]['z'])
#         wXSlopes += [xr[0] * len(clusters[i]['x']),]
#         wYSlopes += [yr[0] * len(clusters[i]['y']),]
#     NPoints = sum([len(cluster['x']) for cluster in clusters])
#     xSlope = sum(wXSlopes)/NPoints
#     ySlope = sum(wYSlopes)/NPoints
# 
#     xAngle = arctan2(xSlope,1.0)
#     yAngle = -arctan2(ySlope,1.0)
#     logging.debug("-align_clustered_data_to_z- xAngle:%.3f yAngle:%.3f"
#                     % (degrees(xAngle), degrees(yAngle)))
# 
#     for c in xrange(len(clusters)):
#         for i in xrange(len(clusters[c]['x'])):
#             x, y, z = (clusters[c]['x'][i], clusters[c]['y'][i], clusters[c]['z'][i])
#             # rotate xAngle about y
#             
#             # rotate yAngle about x
#             nx = x*cos(xSlope) + z*sin(xSlope)
#             ny = x*sin(xSlope)*sin(ySlope) + y*cos(ySlope) + z*cos(xSlope)*sin(ySlope)
#             nz = -x*sin(xSlope)*cos(ySlope) + y*sin(ySlope) + z*cos(xSlope)*cos(ySlope)
#             clusters[c]['x'][i], clusters[c]['y'][i], clusters[c]['z'][i] = (nx, ny, nz)
#     return clusters

def print_clusters(clusters):
    clusterMeans = [mean(c['z']) for c in clusters]
    clusterMeans.sort()
    
    print "\t",
    for i in xrange(len(clusterMeans)):
        print "%.3f\t" % clusterMeans[i],
    print
    for i in xrange(len(clusterMeans)):
        print "%.3f\t" % clusterMeans[i],
        for i2 in xrange(len(clusterMeans)):
            print "%.3f\t" % abs(clusterMeans[i] - clusterMeans[i2]),
        print

def plot_clusters(clusters, saveToFile=None):
    colors = ['b', 'r', 'g', 'c', 'm']
    for i in xrange(len(clusters)):
        subplot(221)
        scatter(clusters[i]['x'], clusters[i]['y'], c=colors[i])
        subplot(222)
        scatter(clusters[i]['x'], clusters[i]['z'], c=colors[i])
        subplot(223)
        scatter(clusters[i]['y'], clusters[i]['z'], c=colors[i])
        subplot(224)
        hist(clusters[i]['z'], color=colors[i])
    
    subplot(221); xlabel("X"); ylabel("Y")
    subplot(222); xlabel("X"); ylabel("Z")
    subplot(223); xlabel("Y"); ylabel("Z")
    subplot(224); xlabel("Z");
    if saveToFile != None:
        savefig(saveToFile)
    else:
        show()

def rotate_about_x(points, angle, centroid):
    for i in xrange(len(points['x'])):
        x, y, z = points['x'][i], points['y'][i]-centroid['y'], points['z'][i]-centroid['z']
        nx = x
        ny = y*cos(angle)-z*sin(angle)
        nz = y*sin(angle)+z*cos(angle)
        points['x'][i], points['y'][i], points['z'][i] = nx, ny, nz
    return points

def rotate_about_y(points, angle, centroid):
    for i in xrange(len(points['x'])):
        x, y, z = points['x'][i]-centroid['x'], points['y'][i], points['z'][i]-centroid['z']
        nx = x*cos(angle)+z*sin(angle)
        ny = y
        nz = -x*sin(angle)+z*cos(angle)
        points['x'][i], points['y'][i], points['z'][i] = nx, ny, nz
    return points

# def rotate_about_z(points, angle):
#     for i in xrange(len(points['x'])):
#         x, y, z = points['x'][i], points['y'][i], points['z'][i]
#         nx = x*cos(angle)-y*sin(angle)
#         ny = x*sin(angle)+y*cos(angle)
#         nz = z
#         points['x'][i], points['y'][i], points['z'][i] = nx, ny, nz
#     return points

if __name__ == "__main__":
    clusters = get_clusters(filename)
    print_clusters(clusters)
    plot_clusters(clusters)
# -=-=-=-=-=- old -=-=-=-=-=-=-=-=-
# 
# # read file
# f = open(filename,'r')
# 
# l = f.readline()
# while l[0] != 'v':
#   l = f.readline()
# 
# x = []
# y = []
# z = []
# 
# while l[:2] == 'v ':
#   items = l.split(' ')
#   #print l
#   x += [float(items[1]),]
#   y += [float(items[2]),]
#   z += [float(items[3]),]
#   l = f.readline()
# 
# f.close()
# 
# def cluster_points(x,y,z,n):
#     wz = whiten(z)
#     kInit = linspace(min(wz), max(wz), n)
#     res, idx = kmeans2(wz, kInit, iter=100,minit='matrix')
#     print res
#     
#     xs = [[] for i in xrange(n)]
#     ys = [[] for i in xrange(n)]
#     zs = [[] for i in xrange(n)]
#     
#     for i in xrange(len(idx)):
#         xs[idx[i]] += [x[i],]
#         ys[idx[i]] += [y[i],]
#         zs[idx[i]] += [z[i],]
#     
#     return xs, ys, zs
# 
# xs, ys, zs = cluster_points(x,y,z,NClusters)
# 
# clusterFailures = 0
# while any([len(c) == 0 for c in xs]):
#     clusterFailures += 1
#     print "kmeans2 failed to find",NClusters,"clusters, trying again with",NClusters-clusterFailures
#     xs, ys, zs = cluster_points(x,y,z,NClusters-clusterFailures)
# 
# NClusters -= clusterFailures
# 
# def align_data(xs, ys, zs):
#     weighted_x_slopes = []
#     weighted_y_slopes = []
#     for i in range(len(xs)):
#         xr = linregress(xs[i], zs[i])
#         yr = linregress(ys[i], zs[i])
#         weighted_x_slopes += [xr[0] * len(xs[i]),]
#         weighted_y_slopes += [yr[0] * len(ys[i]),]
#     
#     NPoints = sum([len(x) for x in xs])
#     x_slope = sum(weighted_x_slopes)/NPoints
#     y_slope = sum(weighted_y_slopes)/NPoints
#     
#     for g in range(len(xs)):
#         for i in range(len(zs[g])):
#             zs[g][i] -= ys[g][i] * y_slope + xs[g][i] * x_slope
#     
#     return xs, ys, zs
# 
# xs, ys, zs = align_data(xs, ys, zs)
# 
# clusterMeans = [mean(zs[i]) for i in range(NClusters)]
# clusterMeans.sort()
# #print "Z-Mean\tZ-Diffs"
# print "\t",
# for i in range(NClusters):
#     print "%.3f\t" % clusterMeans[i],
# print
# for i in range(NClusters):
#     print "%.3f\t" % clusterMeans[i],
#     for i2 in range(NClusters):
#         print "%.3f\t" % abs(clusterMeans[i] - clusterMeans[i2]),
#     print
# 
# colors = ['b', 'r', 'g', 'c', 'm']
# for i in range(NClusters):
#     subplot(221)
#     scatter(xs[i],ys[i],c=colors[i])
#     subplot(222)
#     scatter(xs[i],zs[i],c=colors[i])
#     subplot(223)
#     scatter(ys[i],zs[i],c=colors[i])
#     subplot(224)
#     hist(zs[i],color=colors[i])
# 
# show()
