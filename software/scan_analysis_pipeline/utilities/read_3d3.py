#!/usr/bin/env python

import struct


up = struct.unpack
pint = lambda f: up('i', f.read(4))[0]
pfloat = lambda f: up('f', f.read(4))[0]
pdouble = lambda f: up('d', f.read(8))[0]
p3double = lambda f: up('ddd', f.read(24))
p3int = lambda f: up('iii', f.read(12))
p2int = lambda f: up('ii', f.read(8))
p2float = lambda f: up('ff', f.read(8))


def read_header(f):
    info = {}
    info['version'] = pint(f)
    if info['version'] == 1:
        info.update(read_header_v1(f))
        return info
    raise ValueError('Unknown version: %s' % info['version'])


def read_header_v1(f):
    info = {}
    info['grid_height'] = pint(f)
    info['grid_width'] = pint(f)
    # info['tex_height'] = pint(f)
    # info['tex_width'] = pint(f)
    info['tex_step_h'] = pint(f)
    info['tex_step_w'] = pint(f)
    info['cam_dist'] = pdouble(f)
    info['n_verts'] = pint(f)
    # info['n_faces'] = pint(f)
    info['n_grid'] = pint(f)
    info['n_faces'] = pint(f)
    # info['n_uvs'] = pint(f)
    if info['n_grid'] != info['n_verts']:
        raise ValueError('n_grid[%s] != n_verts[%s]' %
                        (info['n_grid'], info['n_verts']))
    return info


def read_list(f, n, fn):
    return [fn(f) for i in xrange(n)]


def read_verts(f, n):
    return read_list(f, n, p3double)


def read_faces(f, n):
    return read_list(f, n, p3int)


def read_grid(f, n):
    return read_list(f, n, p2int)


def read_uvs(f, n):
    return read_list(f, n, p2float)


def read_3d3(fn):
    f = open(fn, 'rb')
    fd = {}
    fd['info'] = read_header(f)
    # verts are x, y, z, positions
    fd['verts'] = read_verts(f, fd['info']['n_verts'])
    # grid are y, x pixel coordinates
    fd['grid'] = read_grid(f, fd['info']['n_grid'])
    # faces are v0, v1, v2 vertex indice
    fd['faces'] = read_faces(f, fd['info']['n_faces'])
    # uvs = read_uvs(f, info['n_uvs'])
    # print len(verts)
    p = f.tell()
    f.seek(0, 2)
    e = f.tell()
    if p != e:
        raise IOError("Failed to read entire file: final position=%s, end=%s"
                      % (p, e))
    return fd


if __name__ == '__main__':
    fn = 'Scan03.3d3'
    read_3d3(fn)
