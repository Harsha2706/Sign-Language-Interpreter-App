from collections import deque, Counter

class PredictionSmoother:
    def __init__(self, window_size):
        self.history = deque(maxlen=window_size)

    def add(self, prediction):
        self.history.append(prediction)

    def get(self):
        if not self.history:
            return None
        return Counter(self.history).most_common(1)[0][0]