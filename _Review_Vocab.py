##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os
import random; random.seed()
import string
import unicodedata
from collections import namedtuple
from threading import Thread, Lock

import qprompt as q
import related
from auxly.filesys import File, delete
from gtts import gTTS
from playsound import playsound

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

MISSED_VOCAB = "__temp-vocab_to_review.txt"

RANDOM_VOCAB = "__temp-random_vocab.txt"

TALK_LOCK = Lock()

Setting = namedtuple('Setting', 'name func conf')

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

@related.immutable
class LanguageName(object):
    short = related.StringField(default="en")
    full = related.StringField(default="English")

@related.mutable
class LanguageInfo(object):
    name = related.ChildField(LanguageName)
    talk = related.BooleanField(default=False)
    hint = related.IntegerField(default=0)

@related.mutable
class TextInfo(object):
    text = related.StringField()
    lang = related.ChildField(LanguageInfo)

@related.mutable
class PracticeConfig(object):
    lang1 = related.ChildField(LanguageInfo)
    lang2 = related.ChildField(LanguageInfo)
    num = related.IntegerField(default=10)
    path = related.StringField(default="")
    redo = related.BooleanField(default=False)
    swap = related.BooleanField(default=False)

@related.mutable
class UtilConfig(object):
    lang1 = related.ChildField(LanguageInfo)
    lang2 = related.ChildField(LanguageInfo)
    redo = related.BooleanField(default=False)
    path = related.StringField(default=".")
    num = related.IntegerField(default=10)

class Practice(object):
    def __init__(self, config):
        self.config = config
        self.miss = set()
        self.okay = set()

    def start(self):
        self.miss = set()
        self.okay = set()
        path = get_file(self.config.path)
        lines = [line.strip() for line in File(path).readlines() if line][:self.config.num]
        random.shuffle(lines)
        for (num, line) in enumerate(lines):
            q.hrule()
            q.echo("%s of %s" % (num+1, len(lines)))
            self._ask(line)
        fmiss = File(MISSED_VOCAB)
        for miss in self.miss:
            fmiss.append(miss + "\n")

    def _ask(self, line):
        line = unicodedata.normalize('NFKD', line).encode('ascii','replace').decode("utf-8").strip()
        if not line: return
        qst = TextInfo(line.split(";")[0], self.config.lang1)
        ans = TextInfo(line.split(";")[1], self.config.lang2)
        if self.config.swap:
            ans,qst = qst,ans
        msg = qst.text
        if ans.lang.hint:
            msg += " (%s)" % hint(ans.text, ans.lang.hint)
        talk_qst = run_once(talk)
        while True:
            q.alert(msg)
            if qst.lang.talk:
                talk_qst(qst.text, qst.lang.name.short)
            rsp = q.ask_str("").lower().strip()
            ok = [x.lower().strip() for x in ans.text.split("(")[0].split("/")]
            if rsp in ok:
                q.echo("[CORRECT] " + ans.text)
                self.okay.add(line)
            else:
                q.error(ans.text)
                self.miss.add(line)
                if self.config.redo:
                    continue
            if ans.lang.talk:
                talk(ans.text, ans.lang.name.short, wait=True)
            return

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

stridxrep = lambda s, i, r: "".join([(s[x] if x != i else r) for x in range(len(s))])

randstr = lambda length: "".join(random.choice(string.ascii_lowercase) for _ in range(length))

#: from https://stackoverflow.com/questions/4103773/efficient-way-of-having-a-function-only-execute-once-in-a-loop
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def try_catch(f, oncatch=None, rethrow=False):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            print()
            if oncatch != None:
                oncatch()
            if rethrow:
                raise
    return wrapper

def get_file(path="."):
    menu = q.Menu()
    menu.add("f", "Select file")
    menu.add("r", "Random vocab")
    choice = menu.show()
    if "f" == choice:
        return ask_file(path)
    else:
        return make_random_file()

def ask_file(dpath, msg="File to review (blank to list)"):
    """Prompts user for a file to review. Returns the file name."""
    path = q.ask_str(msg, blk=True)
    if not path or not os.path.isfile(path):
        vfiles = [f for f in os.listdir(dpath) if f.endswith(".txt")]
        path = q.enum_menu(vfiles).show(returns="desc", limit=20)
    return path

def talk(text, lang, slow=False, wait=False):
    def _talk():
        """Pronouces the given text in Italian."""
        with TALK_LOCK:
            fpath = f"__temp-talk-{randstr(6)}.mp3"
            gTTS(text=text, lang=lang, slow=slow).save(fpath)
            playsound(fpath)
            delete(fpath)
    try:
        t = Thread(target=_talk)
        t.start()
        if wait:
            t.join()
    except:
        q.warn("Could not talk at this time.")

def make_random_file(num=20):
    vocabs = []
    vfiles = [f for f in os.listdir(".") if (f.endswith(".txt") and not f.startswith("__"))]
    while len(vocabs) != num:
        random.shuffle(vfiles)
        filenum = random.randrange(len(vfiles))
        lines = [line.strip() for line in File(vfiles[filenum]).readlines() if line]
        linenum = random.randrange(len(lines))
        vocab = lines[linenum]
        if vocab not in vocabs:
            vocabs.append(vocab)
    File(RANDOM_VOCAB, del_at_exit=True).write("\n".join(vocabs))
    return RANDOM_VOCAB

def hint(vocab, hintnum, skipchars=" /'"):
    """Returns the given string with all characters expect the given hint
    number replaced with an asterisk. The given skip characters will be
    excluded."""
    random.seed()
    idx = []
    if len(vocab) <= hintnum:
        hintnum -= 1
    if hintnum < 1:
        hintnum = 1
    while len(idx) < hintnum:
        cidx = random.randrange(0, len(vocab))
        if vocab[cidx] not in skipchars and cidx not in idx:
            idx.append(cidx)
    hint = vocab
    for i,c in enumerate(vocab):
        if c in skipchars:
            continue
        if i not in idx:
            hint = stridxrep(hint, i, "*")
    return hint

def main():
    config = related.to_model(UtilConfig, related.from_yaml(File("config.yaml").read()))
    util = Util(config)
    try_catch(util.main_menu)()

class Util(object):
    def __init__(self, config):
        self.config = config

    def main_menu(self):
        def start(swap=False):
            p = PracticeConfig(swap=swap, **related.to_dict(self.config))
            try_catch(Practice(p).start)()
        menu = q.Menu()
        menu.add("1", f"{self.config.lang1.name.full} to {self.config.lang2.name.full}", start, [False])
        menu.add("2", f"{self.config.lang2.name.full} to {self.config.lang1.name.full}", start, [True])
        menu.add("d", "Delete missed words to review", delete, [MISSED_VOCAB])
        menu.add("s", "Settings", try_catch(self.settings_menu))
        menu.main(loop=True)

    def settings_menu(self):
        def change(s):
            default = getattr(s.conf, s.name)
            setattr(s.conf, s.name, s.func(f"{s.name.capitalize()}", default=default))
        settings = [
                Setting("redo", q.ask_yesno, self.config),
                Setting("num", q.ask_int, self.config),
                Setting("hint", q.ask_int, self.config.lang2),
                Setting("talk", q.ask_yesno, self.config.lang2)]
        menu = q.Menu()
        for s in settings:
            menu.add(s.name[0], s.name.capitalize(), change, [s])
        menu.add("p", "Print", print, [self.config])
        menu.main(loop=True)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
