class FrameBuffer:
    def __init__(self, max_length):
        self.max_length = max_length
        self.buffer = []

    def add(self, frame):
        self.buffer.append(frame)
        if len(self.buffer) > self.max_length:
            self.buffer.pop(0)

    def is_full(self):
        return len(self.buffer) == self.max_length

    def get(self):
        return self.buffer