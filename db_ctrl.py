import threading


class DbCtl(object):
    def __init__(self, buf):
        # a buf used for data from serial
        self.buf = buf
        self.cache = []

    def save(self, hook):
        while True:
            data = self.buf.get()
            self.cache.append(data)
            if hook is not None:
                hook(data)
            if len(self.cache) > 9:
                self.write()
                self.cache = []

    def write(self):
        pass

    def loop_save(self, hook=None):
        t = threading.Thread(target=self.save, args=(hook,))
        t.start()
