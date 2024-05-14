from myutils.config import globalconfig
import threading, os


class TTSbase:
    def init(self):
        pass

    def getvoicelist(self):
        return []

    def voiceshowmap(self, voice):
        return voice

    def speak(self, content, rate, volume, voice, voiceindex):
        return None  # fname ,若为None则是不需要文件直接朗读

    ####################
    # 一些可能需要的属性
    @property
    def config(self):
        return globalconfig["reader"][self.typename]

    ########################

    def __init__(self, typename, showlistsignal, mp3playsignal) -> None:
        self.typename = typename
        self.showlistsignal = showlistsignal
        self.mp3playsignal = mp3playsignal
        self.loadok = False

        def _():
            self.init()
            self.voicelist = self.getvoicelist()
            self.voiceshowlist = []
            for k in self.voicelist:
                try:
                    _v = self.voiceshowmap(k)
                except:
                    _v = k
                self.voiceshowlist.append(_v)
            if globalconfig["reader"][self.typename]["voice"] not in self.voicelist:
                globalconfig["reader"][self.typename]["voice"] = self.voicelist[0]

            showlistsignal.emit(
                self.voiceshowlist,
                self.voicelist.index(globalconfig["reader"][self.typename]["voice"]),
            )
            self.loadok = True

        threading.Thread(target=_).start()

    def read(self, content, force=False):
        def _(content, force):
            fname = self.syncttstofile(content)
            volume = globalconfig["ttscommon"]["volume"]
            if fname:
                self.mp3playsignal.emit(fname, volume, force)

        threading.Thread(target=_, args=(content, force)).start()

    def syncttstofile(self, content):
        if self.loadok == False:
            return
        if len(content) == 0:
            return
        if len(self.voicelist) == 0:
            return

        rate = globalconfig["ttscommon"]["rate"]
        voice = globalconfig["reader"][self.typename]["voice"]
        voice_index = self.voicelist.index(voice)
        fname = self.speak(content, rate, voice, voice_index)
        return os.path.abspath(fname)
