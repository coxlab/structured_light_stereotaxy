#!/usr/bin/env python

# import sys
# import logging
#
# # debug
# logging.basicConfig(level=logging.INFO)
#
# from pylab import *
# from scipy.cluster.vq import *
# from scipy.stats import linregress

import logging

from pylab import *

from stairAnalysis import get_clusters, plot_clusters

logging.basicConfig(level=logging.DEBUG)


def calculate_z_deltas(clusters):
    clusterMeans = [mean(c['z']) for c in clusters]
    clusterMeans.sort()  # sorts lowest to highest, but this is ok, z down is +
    measuredDeltas = diff(array(clusterMeans))
    return measuredDeltas


def calculate_z_scale(clusters, actualDeltas):
    """z_scale is the value that the actual values must be multiplied by to get the measured values
    actual * z_scale = measured"""
    measuredDeltas = calculate_z_deltas(clusters)
    zScale = measuredDeltas / actualDeltas
    return zScale

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#                main
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if __name__ == "__main__":
    print logging.getLevelName(logging.getLogger().level)
    l = logging.getLogger()
    l.setLevel(logging.DEBUG)
    print logging.getLevelName(logging.getLogger().level)
    # domino stair delta-z measurements (from high to low)
    domino1 = [0.97, 0.97]
    domino2 = [1.02, 0.94]

    scanDirectory = "/Users/graham/Projects/structuredLight/scans/cleaned_dominos/"
    scanIndexes = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    domino1Files = ["%sd1s%i.obj" % (scanDirectory, i) for i in scanIndexes]
    domino2Files = ["%sd2s%i.obj" % (scanDirectory, i) for i in scanIndexes]
    # domino1Files = ["%sDomino1Scan%i.obj" % (scanDirectory, i+11) for i in xrange(10)]
    # domino2Files = ["%sDomino2Scan%i.obj" % (scanDirectory, i+11) for i in
    # xrange(10)]

    outputFilePrefix = "dominoDeltas"
    # file format:
    # <delta1> <delta2>

    # z1s = []
    # z2s = []
    # err1to2s = []
    # err2to1s = []

    # measure domino 1
    outputFile = open(outputFilePrefix + "1", "w")
    for dfile in domino1Files:
        clusters = get_clusters(dfile)
        plotFile = 'plots/%s%s' % (dfile.split('/')[-1].split('.')[0], '.png')
        plot_clusters(clusters, saveToFile=plotFile)
        close(1)
        mDeltas = calculate_z_deltas(clusters)
        outputFile.write("%.3f\t%.3f\n" % (mDeltas[0], mDeltas[1]))
    outputFile.close()

    # measure domino 2
    outputFile = open(outputFilePrefix + "2", "w")
    for dfile in domino2Files:
        clusters = get_clusters(dfile)
        plotFile = 'plots/%s%s' % (dfile.split('/')[-1].split('.')[0], '.png')
        plot_clusters(clusters, saveToFile=plotFile)
        close(1)
        mDeltas = calculate_z_deltas(clusters)
        outputFile.write("%.3f\t%.3f\n" % (mDeltas[0], mDeltas[1]))
    outputFile.close()
    #
    # for (d1file, d2file) in zip(domino1Files, domino2Files):
    #     logging.debug("processing files: %s, %s" % (d1file, d2file))
    #     logging.debug("\tloading file: %s" % d1file)
    #     c1 = get_clusters(d1file)
    #     logging.debug("\tloading file: %s" % d2file)
    #     c2 = get_clusters(d2file)
    #     logging.debug("\tcalculating z scale")
    #
    #     mDeltas1 = calculate_z_deltas(c1)
    #     mDeltas2 = calculate_z_deltas(c2)
    #
    #     # z1 = calculate_z_scale(c1, domino1)
    #     # z2 = calculate_z_scale(c2, domino2)
    #     #
    #     # # TODO check if I want to just take the mean, max, min, or something else
    #     # z1 = mean(z1)
    #     # z2 = mean(z2)
    #     #
    #     # z1s.append(z1)
    #     # z2s.append(z2)
    #     #
    #     # mDeltas1 = calculate_z_deltas(c1)
    #     # mDeltas2 = calculate_z_deltas(c2)
    #     # err1to2 = domino2 - mDeltas2 / z1
    #     # err2to1 = domino1 - mDeltas1 / z2
    #     #
    #     # # TODO check if I want to just take the mean, max, min, or something else
    #     # err1to2 = mean(err1to2)
    #     # err2to1 = mean(err2to1)
    #     #
    #     # err1to2s.append(err1to2)
    #     # err2to1s.append(err2to1)
    #
    # err1to2s = abs(array(err1to2s))
    # err2to1s = abs(array(err2to1s))
    #
    # print "Error predicting 2 from 1:"
    # print "\tmean:\t%f" % mean(err1to2s)
    # print "\tmedian:\t%f" % median(err1to2s)
    # print "\tmax:\t%f" % max(err1to2s)
    # print "Error predicting 1 from 2:"
    # print "\tmean:\t%f" % mean(err2to1s)
    # print "\tmedian:\t%f" % median(err2to1s)
    # print "\tmax:\t%f" % max(err2to1s)
    #
    # #scatterplot of z1 x z2
    # figure(1)
    # scatter(z1,z2)
    # xlabel('z1')
    # ylabel('z2')
    #
    # figure(2)
    # subplot(221)
    # scatter(err1to2s,err2to1s)
    # xlabel('err1to2')
    # ylabel('err2to1')
    # subplot(222)
    # x = range(len(err1to2s))
    # plot(x,err1to2s,label="err1to2")
    # plot(x,err2to1s,label="err2to1")
    # legend()
    # xlabel("scan index")
    # ylabel("error")
    # subplot(223)
    # hist(err1to2s)
    # ylabel('err1to2')
    # subplot(224)
    # hist(err2to1s)
    # ylabel('err2to1')
    # show()
