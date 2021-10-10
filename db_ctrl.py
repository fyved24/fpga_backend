import threading


class DbCtl(object):
    def __init__(self, buf):
        # a buf used for data from serial
        self.buf = buf
        self.cache = []

    def save(self):
        while True:
            data = self.buf.get()
            self.cache.append(data)
            if len(self.cache) > 9:
                self.write()
                self.cache = []

    def write(self):
        pass

    def loop_save(self):
        print('db listening')
        t = threading.Thread(target=self.save)
        t.start()
