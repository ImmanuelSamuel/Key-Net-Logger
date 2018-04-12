
import subprocess as sproc
import numpy as np
import time

### Init
logInterval = 60 # seconds

while True:
    cmd = 'iftop -B -i enp0s25 -t -s {0}'.format(logInterval)
    lines = sproc.getoutput(cmd).split('\n')[6:]
    log = ['Time, {0:1.3f}\n'.format(time.time())]
    for i in range(0,len(lines)-1,2):
        if lines[i][0] == '-':
            break
        toPacket = np.array(lines[i].split())
        fromPacket = np.array(lines[i+1].split())
        if len(toPacket)>2 and len(fromPacket)>2:
            toPacket = toPacket[[1,-1]]
            fromPacket = fromPacket[[0,-1]]
            line = ','.join(list(np.concatenate((toPacket,fromPacket))))
            log.append(line+'\n')

    with open('log.txt', 'a') as f:
        f.writelines(log)