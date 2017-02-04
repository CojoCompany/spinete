import numpy


class Array():
    def __init__(self, width, max_size=200, buffer_size_factor=10):
        self.width = width
        self.buffer_size = int(round(buffer_size_factor * max_size))
        self.max_size = max_size
        self.size = 0
        self.base = numpy.ndarray((self.buffer_size, self.width))
        self.head = self.buffer_size - 1
        self.view = self.base[self.head:self.head + self.size]

    def push_data(self, data):
        if self.head < 0:
            self.base[-self.size:] = self.base[:self.size]
            self.head = self.buffer_size - self.size - 1
        self.base[self.head] = data
        if self.size < self.max_size:
            self.size += 1
        self.view = self.base[self.head:self.head + self.size]
        self.head -= 1
