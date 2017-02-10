from Qt import QtGui
from Qt import QtCore

from spinete.gui import run


def splitter(self):

    hbox = QtGui.QHBoxLayout(self)

    splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
    splitter1.addWidget(self.sensors['position'])
    splitter1.addWidget(self.sensors['humidity'])
    splitter1.setSizes([800, 200])

    splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
    splitter2.addWidget(splitter1)
    splitter2.addWidget(self.sensors['temperature'])
    splitter2.addWidget(self.sensors['light'])
    splitter2.setSizes([400, 200, 200])

    hbox.addWidget(splitter2)
    self.setLayout(hbox)


if __name__ == "__main__":
    run(splitter)
