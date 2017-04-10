##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os
import sys
import unicodedata

import auxly as ax
import qprompt as q

sys.dont_write_bytecode = True
from _Review_Vocab import ask_file

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def sort_all():
    for f in os.listdir("."):
        if f.endswith(".txt"):
            q.status("Sorting `%s`..." % f, sort_file, [f])

def sort_file(path=None):
    if not path:
        path = ask_file("File to sort")
    if not path.endswith(".txt"):
        q.error("Can only sort `.txt` files!")
        return
    with open(path) as fi:
        lines = fi.readlines()
    sorts = []
    for num,line in enumerate(lines):
        line = line.strip()
        try:
            if not line: continue
            en,it = line.split(";")
            enx = ""
            itx = ""
            if en.find("(") > -1:
                en,enx = en.split("(")
                en = en.strip()
                enx = " (" + enx
            if it.find("(") > -1:
                it,itx = it.split("(")
                it = it.strip()
                itx = " (" + itx
            en = "/".join(sorted(en.split("/")))
            it = "/".join(sorted(it.split("/")))
            sorts.append("%s%s;%s%s" % (en,enx,it,itx))
        except:
            temp = unicodedata.normalize('NFKD', line.decode("utf-8")).encode('ascii','ignore').strip()
            q.warn("Issue splitting `%s` line %u: %s" % (path, num, temp))
            sorts.append(line)
    with open(path, "w") as fo:
        for line in sorted(sorts):
            fo.write(line + "\n")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    menu = q.Menu()
    menu.add("s", "Sort single file", sort_file)
    menu.add("a", "Sort all files", sort_all)
    menu.main(loop=True)
