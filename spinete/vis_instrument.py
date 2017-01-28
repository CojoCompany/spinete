import pyqtgraph as pg
import numpy as np

class VisInstrument(pg.PlotWidget):
	def __init__(self):
		super().__init__()
		self.setRange(yRange=(0,1))
		self.hideAxis('bottom')
		self.setLabel('left', 'Acceleration', 'g')
		self.legend = self.addLegend(offset=(-50, 20))
		self.legend1 = self.plot(pen='y', name='x_accel')
		self.legend2 = self.plot(pen='r', name='y_accel')
		x_ax = np.arange(1)


	def update_view(self, x, y, z):
		self.clear()
		x_ax = np.arange(1)
		bg1 = pg.BarGraphItem(x=x_ax, height=abs(x), width=0.3, brush='y')
		bg2 = pg.BarGraphItem(x=x_ax+0.33, height=abs(y), width=0.3, brush='r')
		self.addItem(bg1)
		self.addItem(bg2)



