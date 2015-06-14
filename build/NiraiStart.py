from panda3d.core import *
import rc4

import niraidata

# Config
prc = niraidata.CONFIG
key, prc = prc[:16], prc[16:]
rc4.rc4_setkey(key)
prc = rc4.rc4(prc)

for line in prc.split('\n'):
    line = line.strip()
    if line:
        loadPrcFileData('nirai config', line)

# Mount models.mf
vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount('models.mf', '.', 0)

# Run
try:
    import main

except SystemExit:
    pass
    
except:
    raise