import pyqtgraph as pg


class BarSensor(pg.PlotWidget):
    def __init__(self, name, magnitude, unit, color='y',
                 hide_bottom_axis=True, min_y_range=None):
        super().__init__()
        self.setLimits(minYRange=min_y_range)
        if hide_bottom_axis:
            self.hideAxis('bottom')
        self.setLabel('left', magnitude, unit)
        self.legend = self.addLegend(offset=(-50, 20))
        self.value = self.plot(pen=color, name=name)
        self.bg1 = pg.BarGraphItem(x=[0], height=0, width=1.,
                                   brush=color)
        self.addItem(self.bg1)
        self.data = 0

    def push_data(self, data):
        self.data = data

    def update_view(self):
        self.clear()
        self.bg1.opts['height'] = self.data
        self.bg1.drawPicture()
        self.addItem(self.bg1)
