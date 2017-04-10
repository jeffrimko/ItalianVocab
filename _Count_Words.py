##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import qprompt
import os

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    total = 0
    for i in os.listdir("."):
        if not i.endswith(".txt"): continue
        if i.startswith("__temp"): continue
        num = len(open(i).readlines())
        total += num
        qprompt.echo("%u\t%s" % (num, i))
    qprompt.hrule()
    qprompt.echo("Total = %u" % (total))
    qprompt.pause()
