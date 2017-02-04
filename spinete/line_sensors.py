import pyqtgraph as pg
from .array import Array


class LineSensor(pg.PlotWidget):
    def __init__(self, identifier, magnitude, unit, color='y', array_size=200,
                 hide_bottom_axis=True, min_y_range=None, y_range=None):
        super().__init__()
        self.setLimits(minYRange=min_y_range)
        if y_range:
            self.setRange(yRange=y_range)
        if hide_bottom_axis:
            self.hideAxis('bottom')
        self.setLabel('right', magnitude, unit)
        self.legend = self.addLegend(offset=(50, 20))
        self.value = self.plot(pen=color, name=identifier)
        self.array = Array(2, max_size=array_size)

    def push_data(self, timestamp, data):
        self.array.push_data([timestamp, data])

    def update_view(self):
        self.value.setData(self.array.view)


class XYZSensor(pg.PlotWidget):
    def __init__(self):
        super().__init__()

        self.setRange(yRange=(-100, 100))
        self.hideAxis('bottom')
        self.setLabel('left', 'Rotation', 'deg')
        self.legend = self.addLegend(offset=(-50, 20))
        self.x_angle = self.plot(pen='y', name='x_angle')
        self.y_angle = self.plot(pen='r', name='y_angle')
        self.z_angle = self.plot(pen='g', name='z_angle')
        self.array = Array(4)

    def push_data(self, timestamp, angles):
        self.array.push_data([timestamp, angles[0], angles[1], angles[2]])

    def update_view(self):
        self.x_angle.setData(self.array.view[:, 1])
        self.y_angle.setData(self.array.view[:, 2])
        self.z_angle.setData(self.array.view[:, 3])
