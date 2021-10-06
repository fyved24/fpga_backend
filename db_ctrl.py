import threading


class DbCtl(object):
    def __init__(self, buf):
        # a buf used for data from serial
        self.buf = buf
        self.cache = []

    def save(self, hook):
        while True:
            if len(self.cache) > 9:
                self.write()
                if hook is not None:
                    hook(self.cache)
                self.cache = []
            else:
                print(self.cache)
                self.cache.append(self.buf.get())

    def write(self):
        print(self.cache)

    def loop_save(self, hook=None):
        t = threading.Thread(target=self.save, args=(hook,))
        t.start()
