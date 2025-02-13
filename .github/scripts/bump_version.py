import os

from datetime import datetime
from packaging.version import parse

VNS = '__version__'
VDS = '__versiondate__'


def bump_version():

    print(os.getcwd())
    fname = os.path.join('rastertools', 'version.py')

    with open(fname) as fid01:
        flines = fid01.readlines()

    with open(fname, 'w') as fid01:
        for lval in flines:
            if (lval.startswith(VDS)):
                dval = datetime.today().strftime('%Y-%m-%d')
                nline = VDS + ' = ' + dval + '\n'
                fid01.write(nline)
            elif (lval.startswith(VNS)):
                ver = parse(lval.split('\'')[1])
                nver = str(ver.major) + '.' + str(ver.minor) + '.'
                nver = nver + str(ver.micro + 1)
                nline = VNS + ' = \'' + nver + '\'\n'
            else:
                fid01.write(lval)

    return None


if __name__ == '__main__':
    bump_version()
