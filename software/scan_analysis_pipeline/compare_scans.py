#!/usr/bin/env python

import os
import sys

import numpy
import pylab
import mpl_toolkits.mplot3d as m3d

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

        self.final_im = pylab.imread(
            os.path.join(directory, 'final.png'))
        self.hat_im = pylab.imread(
            os.path.join(directory, 'hat.png'))
        self.skull_im = pylab.imread(
            os.path.join(directory, 'skull.png'))

        self.final_refs_uv = numpy.loadtxt(
            os.path.join(directory, 'finalrefsUV'))
        self.hat_refs_uv = numpy.loadtxt(
            os.path.join(directory, 'hatrefsUV'))
        self.skull_refs_uv = numpy.loadtxt(
            os.path.join(directory, 'skullrefsUV'))

        self.hat_refs_in_skull = numpy.loadtxt(
            os.path.join(directory, 'tcRefsInSkull'))

        # project skull pts to hat
        self.hat_refs_in_hat = utilities.vector.apply_matrix_to_points(
            numpy.matrix(self.skull_to_hat),
            self.hat_refs_in_skull)


class Plot(object):
    def __init__(self, a, b, attr, label=False):
        self.a = a
        self.b = b
        self.attr = attr
        self.apts = getattr(a, attr)
        self.bpts = getattr(b, attr)
        self.figure = None
        self.label = label

    def show(self):
        if self.figure is None:
            self.figure = pylab.figure()
        else:
            self.figure.clf()
        if self.apts.shape[1] == 2:
            assert self.bpts.shape[1] == 2
            self.show_2d()
        elif self.apts.shape[1] > 2:
            assert self.bpts.shape[1] > 2
            self.show_3d()
        else:
            raise ValueError("Don't know how to plot %s and %s" %
                             (self.apts, self.bpts))
        return self.figure

    def show_2d(self):
        self.figure.suptitle(self.attr)

        a_ax = self.figure.add_subplot(121)
        b_ax = self.figure.add_subplot(122)
        for (ax, pts, scan) in ((a_ax, self.apts, self.a),
                                (b_ax, self.bpts, self.b)):
            ax.scatter(pts[:, 0], pts[:, 1])
            if self.label:
                for (i, p) in enumerate(pts):
                    ax.text(p[0], p[1], str(i))
            mr = 0.
            for l in (ax.get_xlim(), ax.get_ylim()):
                mr = max(mr, l[1] - l[0])
            for l in ('xlim', 'ylim'):
                lim = getattr(ax, 'get_%s' % l)()
                m = (lim[1] + lim[0]) / 2.
                getattr(ax, 'set_%s' % l)(m - mr / 2., m + mr / 2.)
            ax.set_title(scan.directory)

    def show_3d(self):
        self.figure.suptitle(self.attr)

        a_ax = self.figure.add_subplot(121, projection='3d')
        b_ax = self.figure.add_subplot(122, projection='3d')
        for (ax, pts, scan) in ((a_ax, self.apts, self.a),
                                (b_ax, self.bpts, self.b)):
            ax.scatter3D(pts[:, 0], pts[:, 1], pts[:, 2])
            if self.label:
                for (i, p) in enumerate(pts):
                    ax.text3D(p[0], p[1], p[2], str(i))
            mr = 0.
            for l in (ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()):
                mr = max(mr, l[1] - l[0])
            for l in ('xlim3d', 'ylim3d', 'zlim3d'):
                lim = getattr(ax, 'get_%s' % l)()
                m = (lim[1] + lim[0]) / 2.
                getattr(ax, 'set_%s' % l)(m - mr / 2., m + mr / 2.)
            ax.set_title(scan.directory)


class UVPlot(Plot):
    def __init__(self, a, b, imk, uvk):
        self.a = a
        self.b = b
        self.imk = imk
        self.uvk = uvk
        self.ima = getattr(a, imk)
        self.imb = getattr(b, imk)
        self.uva = getattr(a, uvk)
        self.uvb = getattr(b, uvk)
        self.figure = None

    def show(self):
        if self.figure is None:
            self.figure = pylab.figure()
        else:
            self.figure.clf()
        axa = self.figure.add_subplot(121)
        axb = self.figure.add_subplot(122)
        for (ax, im, uv, scan) in ((axa, self.ima, self.uva, self.a),
                                   (axb, self.imb, self.uvb, self.b)):
            ax.imshow(im)
            ax.scatter(uv[:, 0], uv[:, 1])
            ax.set_title(scan.directory)
        self.figure.suptitle('%s & %s' % (self.imk, self.uvk))


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


def find_max_deviation(a, b, transform):
    amax = numpy.zeros(4)
    bmax = numpy.zeros(4)
    amax[:3] = find_furthest_point(a)
    bmax[:3] = find_furthest_point(b)
    amax = amax * getattr(a, transform)
    bmax = bmax * getattr(b, transform)
    return numpy.sqrt(numpy.sum((amax[:3] - bmax[:3]) ** 2.))


def get_transform_difference(a, b, transform):
    apos, aangle = utilities.vector.decompose_matrix(getattr(a, transform))
    bpos, bangle = utilities.vector.decompose_matrix(getattr(b, transform))
    return numpy.array(apos) - numpy.array(bpos), \
        numpy.array(aangle) - numpy.array(bangle)


def compare(a, b):
    r = {}
    for transform in ('scan_to_skull', 'skull_to_hat'):
        dpos, dangle = get_transform_difference(a, b, transform)
        r[transform] = {
            'Maximum Difference': find_max_deviation(a, b, transform),
            'Delta Position': dpos,
            'Delta Angle(degrees)': dangle,
        }
    for pts in ('final_refs_uv', 'hat_refs_uv',
                'skull_refs_uv', 'hat_refs_in_skull',
                'hat_refs_in_hat'):
        r[pts] = Plot(a, b, pts, label=True)

    for (im, uv) in zip(
            ('final_im', 'hat_im', 'skull_im'),
            ('final_refs_uv', 'hat_refs_uv', 'skull_refs_uv')):
        r[im] = UVPlot(a, b, im, uv)

    return r


def pprint_dict(d, prefix=None, indent='  '):
    if prefix is None:
        prefix = ''
    for k in sorted(d.keys()):
        v = d[k]
        if isinstance(v, dict):
            print '%s%s =' % (prefix, k)
            pprint_dict(v, prefix=prefix + indent)
        elif isinstance(v, Plot):
            f = v.show()
            print '%s%s Plot(%s)' % (prefix, k, f)
        else:
            print '%s%s: %s' % (prefix, k, v)


def main():
    assert len(sys.argv) == 3
    _, a, b = sys.argv
    r = compare(Scan(a), Scan(b))
    print "---- %s vs %s ----" % (a, b)
    print
    pprint_dict(r)
    pylab.show()


if __name__ == '__main__':
    main()
