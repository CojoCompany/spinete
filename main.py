import sys
import time
import socket
from ipaddress import ip_address

import zmq
import yaml
from Qt import QtCore
from Qt import QtGui

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
        self.buffer = {}
        self.splitter()
        refresh = yaml.load(open('config.yaml'))['refresh']
        self.data_period = refresh['data_period']
        self.display_period = refresh['display_period']
        self.data_next_refresh = None
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
        self.barsensor = BarSensor('HUMI', 'Humidity', '%',
                                   color='#add8e6', min_y_range=35)
        self.linesensor = LineSensor('TEMP', 'Temperature', '°C',
                                     color='#dc381f', min_y_range=5)

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

    def update_data(self):
        while True:
            current_time = int(round(time.time() * 1000))
            diff = max(0, self.data_next_refresh - current_time)
            events = dict(self.poller.poll(diff))
            if not events:
                timestamp = self.data_next_refresh / 1000
                self.data_next_refresh += self.data_period
                break
            for socket in events:
                if events[socket] != zmq.POLLIN:
                    continue
                message = socket.recv_pyobj()
                identifier, data = message
                self.buffer[identifier] = data
                #self.vis_3d.update_view(x_angle,y_angle,z_angle)
                #self.beep.beep(x_angle)

        print(self.data_next_refresh)

        self.linesensor.push_data(timestamp, self.buffer['TEMP'])
        self.barsensor.push_data(self.buffer['TEMP'])

    def update_view(self):
        if not self.data_next_refresh:
            current_time = time.time() * 1000
            remaining = self.data_period - current_time % self.data_period
            self.data_next_refresh = int(current_time + remaining)
        while True:
            self.update_data()
            # TODO: update view period should be independent from data period
            #       would it be thread-safe? Otherwise, maybe we should send
            #       the data to plot from one thread to another. Would that
            #       be efficient enough?
            break

        self.barsensor.update_view()
        self.linesensor.update_view()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()

    timer = QtCore.QTimer()
    timer.timeout.connect(main_window.update_view)
    timer.start(1)

    sys.exit(app.exec_())
