##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os
import random
import unicodedata

import auxly.filesys as fsys
import qprompt as q

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

MISSED_VOCAB = "__temp-vocab_to_review.txt"

RANDOM_VOCAB = "__temp-random_vocab.txt"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

stridxrep = lambda s, i, r: "".join([(s[x] if x != i else r) for x in range(len(s))])

def ask_file(msg="File to review"):
    path = q.ask_str(msg, blk=True)
    if not path or not os.path.isfile(path):
        vfiles = [f for f in os.listdir(".") if f.endswith(".txt")]
        path = q.enum_menu(vfiles).show(returns="desc", limit=20)
    return path

def make_random_file(num=20):
    vocabs = []
    vfiles = [f for f in os.listdir(".") if f.endswith(".txt")]
    while len(vocabs) != num:
        random.shuffle(vfiles)
        filenum = random.randrange(len(vfiles))
        lines = [line.strip() for line in open(vfiles[filenum]).readlines() if line]
        linenum = random.randrange(len(lines))
        vocab = lines[linenum]
        if vocab not in vocabs:
            vocabs.append(vocab)
    with open(RANDOM_VOCAB, "w") as fo:
        fo.write("\n".join(vocabs))
    return RANDOM_VOCAB

def get_file():
    menu = q.Menu()
    menu.add("f", "Select file")
    menu.add("r", "Random vocab")
    choice = menu.show()
    if "f" == choice:
        return ask_file()
    else:
        return make_random_file()

def practice_it2en():
    path = get_file()
    redo = q.ask_yesno("Redo missed answers?")
    lines = [line.strip() for line in open(path).readlines() if line]
    random.shuffle(lines)
    for line in lines:
        line = unicodedata.normalize('NFKD', line).encode('ascii','ignore').decode("utf-8").strip()
        if not line: continue
        en,it = line.split(";")
        while True:
            ans = q.ask_str(it).lower().strip()
            ok = [x.lower().strip() for x in en.split("(")[0].split("/")]
            if ans in ok:
                q.echo("CORRECT! " + en)
                break
            else:
                q.error("%s" % (en))
                fmiss.write(line + "\n", "a")
                if not redo:
                    break

def practice_en2it():
    path = get_file()
    hint = q.ask_int("Number of hints letters", dft=0)
    redo = q.ask_yesno("Redo missed answers?")
    lines = [line.strip() for line in open(path).readlines() if line]
    random.shuffle(lines)
    for line in lines:
        line = unicodedata.normalize('NFKD', line).encode('ascii','ignore').decode("utf-8").strip()
        if not line: continue
        en,it = line.split(";")
        msg = en
        if hint > 0:
            msg += " (%s)" % hint_vocab(it, hint)
        while True:
            ans = q.ask_str(msg).lower().strip()
            ok = [x.lower().strip() for x in it.split("(")[0].split("/")]
            if ans in ok:
                q.echo("CORRECT! " + it)
                break
            else:
                q.error("%s" % (it))
                fmiss.write(line + "\n", "a")
                if not redo:
                    break

def hint_vocab(vocab, hintnum):
    letters = []
    for lnum,char in enumerate(vocab):
        if char != " ":
            letters.append(lnum)
    random.shuffle(letters)
    hint = vocab
    hints = len(vocab) - hintnum
    if hints <= 0:
        hints = 1
    for lnum in letters[:hints]:
        hint = stridxrep(hint, lnum, "*")
    return hint

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    fmiss = fsys.File(MISSED_VOCAB)
    menu = q.Menu()
    menu.add("1", "English to Italian", practice_en2it)
    menu.add("2", "Italian to English", practice_it2en)
    menu.add("d", "Delete missed words to review", fsys.delete, [MISSED_VOCAB])
    menu.main(loop=True)
