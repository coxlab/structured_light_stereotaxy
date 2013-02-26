#!/usr/bin/env python

import sys
import os

CfgModule = __name__


def assign_cfg_module(moduleName):
    """
    Assign the name of the glocal cfg file (defaults to __name__ in this module)
    Example (within the cfg file you want to use):
        from cfgBase import *
        assign_cfg_module(__name__)
    """
    global CfgModule
    CfgModule = moduleName


def load_external_cfg(cfgFile):
    """Load an external configuration file into this module
    The values found in the external module will overwrite any
    values defined here. New variables will be created when
    needed.

    Example:

    test.py:
      import cfg.py
      <<point 1>>
      cfg.load_external_cfg('customCfg.py')
      <<point 2>>

    cfg.py:
      foo = '1'

    customCfg.py:
      foo = '2'
      bar = 'hi'

    will result in:
      cfg.foo <<at point 1>> = '1'
      cfg.bar <<at point 1>> does not exist
      cfg.foo <<at point 2>> = '2'
      cfg.bar <<at point 2>> = 'hi'
    """
    mod = sys.modules[CfgModule]

    cfgDir = os.path.abspath(os.path.dirname(cfgFile))
    cfgName = os.path.splitext(os.path.basename(cfgFile))[0]

    # add directory of cfg file to system path
    sys.path.append(cfgDir)
    if cfgName in sys.modules:
        sys.modules.pop(cfgName)

    # move to the directory of the cfg file so that path references within
    # that file will be valid
    oldDir = os.path.abspath(os.curdir)
    os.chdir(cfgDir)

    cfgMod = __import__(cfgName)
    for i in dir(cfgMod):
        if i[0] == '_':
            continue
        if type(i) == type(sys):
            continue
        mod.__setattr__(i, cfgMod.__getattribute__(i))

    # remove directory of cfg file from system path
    sys.path.pop()

    # return to the original directory
    os.chdir(oldDir)


# this is probably a better name
load_cfg = load_external_cfg


def print_cfg():
    mod = sys.modules[CfgModule]
    for i in dir(mod):
        if i[:2] == '__':
            continue
        attr = mod.__getattribute__(i)
        print "%s : %s : %s" % (i, type(attr), repr(attr))


def process_options(options=sys.argv[1:]):
    """Parse a list of options (sys.argv default) in the form of:
    --variable=value
    assigning the new values to the variables within this module,
    creating variables where needed. Do NOT use spaces in the value

    Example:
     python test.py --foo='a' --bar=1 --junk='[1,2,3]'

    where test.py:
      import cfg.py
      cfg.process_options()

    will result in:
      cfg.foo = 'a' (type string)
      cfg.bar = 1 (type int)
      cfg.junk = [1,2,3] (type list)
    """
    # print options
    mod = sys.modules[CfgModule]
    mod.args = []
    for o in options:
        # print "parsing option:" + o
        if o[:2] != '--':
            # print "option:%s invalid, no preceeding --" % o
            # continue
            # print "argument found: %s" % o
            mod.args.append(o)
            continue
        ei = o.find('=')
        if ei == -1:
            # print "option:%s invalid, no value (= not found)" % o
            exec('mod.%s = None' % o[2:])
            continue
        # items = o.split('=')
        # if len(items) != 2:
        #     print "option:%s invalid, len=%i" % (o, len(items))
        #     continue
        arg = o[2:ei]  # items[0][2:]
        val = o[ei + 1:]  # items[1]
        # print "found arg:%s and val:%s" % (arg, val)
        if val[0] == "{":
            ci = val.find("}")
            if ci == -1:
                print "option:%s invalid type (} not found)" % o
                continue
            valType = val[1:ci]
            if valType == 'dict':
                raise ValueError('dicts fail to parse')
            val = val[ci + 1:]
            # print "found val: %s, type: %s" % (val, valType)
            exec('mod.%s = %s("%s")' % (arg, valType, val))
        else:
            exec('mod.%s = %s' % (arg, val))
