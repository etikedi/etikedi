from queue import SimpleQueue


class MockQueue:

    def __init__(self) -> None:
        self.internal = SimpleQueue()

    def put(self, obj, block=True, timeout=None):
        return self.internal.put(obj)

    def get(self, block=True, timeout=None):
        return self.internal.get()

    def empty(self):
        return self.internal.empty()

    def get_nowait(self):
        return self.internal.get()

    def put_nowait(self, obj):
        return self.internal.put(obj)

    def close(self):
        pass

    def qsize(self):
        return self.internal.qsize()