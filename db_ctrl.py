import threading


class DbCtl(object):
    def __init__(self, buf):
        # a buf used for data from serial
        self.buf = buf
        self.cache = []
        self._hook = None

    def save(self):
        while True:
            data = self.buf.get()
            if self._hook is not None:
                self._hook(data)
            self.cache.append(data)
            if len(self.cache) > 9:
                self.write()
                self.cache = []

    def write(self):
        pass

    def set_hook(self, hook):
        self._hook = hook

    def loop_save(self):
        print('db listening')
        t = threading.Thread(target=self.save)
        t.start()
