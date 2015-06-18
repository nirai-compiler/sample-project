'''
Use this script to invoke Nirai builder and compile the game.
This process consists of 3 step:

1. Pack models into a models.mf.
2. Compile src/sample.cxx and generate sample.exe using NiraiCompiler.
3. Generate sample.nri, which contains the Python modules.
'''

import argparse
import sys
import os

if not os.path.exists('built'):
    os.mkdir('built')

sys.path.append('../../src')

from niraitools import *

parser = argparse.ArgumentParser()
parser.add_argument('--compile-cxx', '-c', action='store_true',
                    help='Compile the CXX codes and generate sample.exe into built.')
parser.add_argument('--make-nri', '-n', action='store_true',
                    help='Generate sample.nri.')
parser.add_argument('--models', '-m', action='store_true',
                    help='Pack models.mf.')
args = parser.parse_args()

def niraicall_obfuscate(code):
    # We'll obfuscate if len(code) % 4 == 0
    # This way we make sure both obfuscated and non-obfuscated code work.
    if len(code) % 4:
        return False, None

    # There are several ways to obfuscate it
    # For this example, we'll invert the string
    return True, code[::-1]

niraimarshal.niraicall_obfuscate = niraicall_obfuscate

class SamplePackager(NiraiPackager):
    HEADER = 'SAMPLE'
    BASEDIR = '..' + os.sep

    def __init__(self, outfile):
        NiraiPackager.__init__(self, outfile)
        self.__manglebase = self.get_mangle_base(self.BASEDIR)

        self.add_panda3d_dirs()
        self.add_default_lib()
        self.add_directory(self.BASEDIR, mangler=self.__mangler)

    def __mangler(self, name):
        # N.B. Mangler can be used to strip certain files from the build.
        # The file is not included if it returns an empty string.

        return name[self.__manglebase:].strip('.')

    def generate_niraidata(self):
        print 'Generating niraidata'

        config = self.get_file_contents('config.prc', True)
        niraidata = 'CONFIG = %r' % config
        self.add_module('niraidata', niraidata, compile=True)

    def process_modules(self):
        '''
        This method is called when it's time to write the output.

        For sample.nri, we use an encrypted datagram.
        The datagram is read by sample.cxx, which populates Python frozen array.

        Datagram format:

        uint32 numModules
        for each module:
            string name
            int32 size *
            data(abs(size))

        * Negative size means the file was an __init__
        '''

        dg = Datagram()
        dg.addUint32(len(self.modules))

        for moduleName in self.modules:
            data, size = self.modules[moduleName]

            dg.addString(moduleName)
            dg.addInt32(size)
            dg.appendData(data)

        data = dg.getMessage()

        iv = '\0' * 16
        key = 'ExampleKey123456'
        return aes.encrypt(data, key, iv)

if args.compile_cxx:
    compiler = NiraiCompiler('sample.exe')
    compiler.add_nirai_files()
    compiler.add_source('src/sample.cxx')
    compiler.run()

if args.make_nri:
    pkg = SamplePackager('built/sample.nri')
    pkg.add_file('NiraiStart.py')
    pkg.generate_niraidata()
    pkg.write_out()

if args.models:
    os.chdir('..')
    cmd = 'multify -cf build/built/models.mf models'
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    v = p.wait()

    if v != 0:
        print 'The following command returned non-zero value (%d): %s' % (v, cmd[:100] + '...')
        sys.exit(1)
