#!/usr/bin/env python

import os
import sys

import numpy
import pylab

import utilities.obj
import utilities.vector


class Scan(object):
    def __init__(self, directory):
        self.directory = directory
        self.scan_to_skull = numpy.loadtxt(
                os.path.join(directory, 'scanToSkull'))
        self.skull_to_hat = numpy.loadtxt(
                os.path.join(directory, 'skullToHat'))
        self.skull = utilities.obj.OBJ(
                os.path.join(directory, 'skull.obj'))
        self.hat = utilities.obj.OBJ(
                os.path.join(directory, 'hat.obj'))
        self.final = utilities.obj.OBJ(
                os.path.join(directory, 'final.obj'))


def find_furthest_point(scan, lookup=True):
    pindex = -1
    mesh = None
    pmax = None
    meshes = (scan.skull, scan.hat, scan.final)
    for m in meshes:
        ds = numpy.sqrt(numpy.sum(m.vertices ** 2., 1))
        cmax = numpy.max(ds)
        if (pmax is None) or (cmax > pmax):
            pindex = ds.argmax()
            pmax = cmax
            mesh = m
    if not lookup:
        return pindex, mesh
    return mesh.vertices[pindex]


def find_max_deviation(a, b):
    amax = numpy.zeros(4)
    bmax = numpy.zeros(4)
    amax[:3] = find_furthest_point(a)
    bmax[:3] = find_furthest_point(b)
    amax = amax * a.skull_to_hat
    bmax = bmax * b.skull_to_hat
    return numpy.sqrt(numpy.sum((amax[:3] - bmax[:3]) ** 2.))


def get_transform_difference(a, b):
    apos, aangle = utilities.vector.decompose_matrix(a.skull_to_hat)
    bpos, bangle = utilities.vector.decompose_matrix(b.skull_to_hat)
    return numpy.array(apos) - numpy.array(bpos), \
            numpy.array(aangle) - numpy.array(bangle)


def compare(a, b):
    r = {}
    r['Maximum Difference'] = find_max_deviation(a, b)
    dpos, dangle = get_transform_difference(a, b)
    r['Delta Position'] = dpos
    r['Delta Angle(degrees)'] = dangle
    return r


def main():
    assert len(sys.argv) == 3
    _, a, b = sys.argv
    r = compare(Scan(a), Scan(b))
    print "---- %s vs %s ----"
    print
    for k, v in r.iteritems():
        print '%s: %s' % (k, v)

if __name__ == '__main__':
    main()
