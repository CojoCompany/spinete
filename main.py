import sys
import socket
from ipaddress import ip_address

import zmq
import yaml
from PySide import QtCore
from PySide import QtGui

from spinete.vis_3d import Vis3D
from spinete.line_sensors import LineSensor
from spinete.bar_sensors import BarSensor
from spinete.beepy import Beepy


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Spinete GUI')
        self.resize(1000, 600)
        fullscreen = yaml.load(open('config.yaml'))['gui']['fullscreen']
        if fullscreen:
            self.showFullScreen()
        else:
            self.show()
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)


    def update_view(self):
        self.main_widget.update_view()


class MainWidget(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.splitter()
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        server = yaml.load(open('config.yaml'))['server']
        host = server['host']
        try:
            ip_address(host)
        except ValueError:
            host = socket.gethostbyname(host)
        self.subscriber.connect('tcp://{}:{}'.format(host, server['port']))
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)

        self.beep = Beepy()

    def box(self):

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(pw1)
        layout.addWidget(pw2)

    def splitter(self):

        self.vis_3d = Vis3D()
        self.barsensor = BarSensor('TEMP', 'Temperature', 'ºC',
                                   min_y_range=35)
        self.linesensor = LineSensor('TEMP', 'Temperature', 'ºC',
                                     min_y_range=5)

        hbox = QtGui.QHBoxLayout(self)
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.vis_3d)
        splitter1.addWidget(self.barsensor)
        splitter1.setSizes([800, 200])
        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.linesensor)
        splitter2.setSizes([400, 200])
        hbox.addWidget(splitter2)
        self.setLayout(hbox)

    def update_view(self):
        while True:
            events = dict(self.poller.poll(5))
            if not events:
                break
            for socket in events:
                if events[socket] != zmq.POLLIN:
                    continue
                message = socket.recv_pyobj()
                identifier, timestamp, data = message
                self.linesensor.push_data(timestamp, data)
                self.barsensor.push_data(data)
                #self.vis_3d.update_view(x_angle,y_angle,z_angle)
                #self.beep.beep(x_angle)

        self.barsensor.update_view()
        self.linesensor.update_view()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()

    timer = QtCore.QTimer()
    timer.timeout.connect(main_window.update_view)
    timer.start(30)

    sys.exit(app.exec_())
