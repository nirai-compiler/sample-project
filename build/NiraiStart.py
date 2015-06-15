from panda3d.core import *
import aes

import niraidata

# Config
prc = niraidata.CONFIG
iv, key, prc = prc[:16], prc[16:32], prc[32:]
prc = aes.decrypt(prc, key, iv)

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