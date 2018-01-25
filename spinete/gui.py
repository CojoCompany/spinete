import sys
import time
import socket
from ipaddress import ip_address

import zmq
import yaml
from Qt import QtCore
from Qt import QtGui

from spinete.bar_sensors import BarSensor
from spinete.line_sensors import LineSensor
from spinete.euclidean_sensors import EuclideanSensor
from spinete.beepy import Beepy


class MainWindow(QtGui.QMainWindow):
    def __init__(self, splitter):
        super().__init__()
        self.setWindowTitle('Spinete GUI')
        self.resize(1000, 600)
        fullscreen = yaml.load(open('config.yaml'))['gui']['fullscreen']
        if fullscreen:
            self.showFullScreen()
        else:
            self.show()
        self.main_widget = MainWidget(splitter)
        self.setCentralWidget(self.main_widget)

    def update_view(self):
        self.main_widget.update_view()


class MainWidget(QtGui.QWidget):
    def __init__(self, splitter):
        super().__init__()

        self.buffer = {}
        refresh = yaml.load(open('config.yaml'))['refresh']
        self.data_period = refresh['data_period']
        self.display_period = refresh['display_period']
        self.data_next_refresh = None

        self.references = {}
        self.sensors = {}
        self.load_sensors()

        splitter(self)

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

    def load_sensors(self):
        configurations = yaml.load(open('config.yaml'))['sensors']

        for identifier, sensor in configurations.items():

            reference = sensor['reference']
            sensor_type = sensor['type']
            magnitude = sensor.get('magnitude', None)
            unit = sensor.get('unit', None)
            color = sensor.get('color', 'r')
            seconds = sensor.get('seconds', 4)
            min_y_range = sensor.get('min_y_range', None)
            y_range = sensor.get('y_range', None)

            if sensor_type == 'line':
                array_size = int(seconds * 1000) / self.data_period
                sensor = LineSensor(
                    name=reference, magnitude=magnitude,
                    unit=unit, color=color, array_size=array_size,
                    min_y_range=min_y_range, y_range=y_range)
            elif sensor_type == 'bar':
                sensor = BarSensor(
                    name=reference, magnitude=magnitude,
                    unit=unit, color=color,
                    min_y_range=min_y_range, y_range=y_range)
            elif sensor_type == 'euclidean':
                sensor = EuclideanSensor()
            else:
                raise ValueError('Wrong sensor type "%s"' % sensor_type)

            self.sensors[identifier] = sensor
            self.references[identifier] = reference

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
                reference, timestamp, data = message
                self.buffer[reference] = data

        print(self.data_next_refresh)

        for identifier, sensor in self.sensors.items():
            reference = self.references[identifier]
            if reference not in self.buffer:
                continue
            if isinstance(sensor, LineSensor):
                sensor.push_data(timestamp, self.buffer[reference])
            else:
                sensor.push_data(self.buffer[reference])

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

        for sensor in self.sensors.values():
            sensor.update_view()


def run(splitter):
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow(splitter)

    timer = QtCore.QTimer()
    timer.timeout.connect(main_window.update_view)
    timer.start(1)

    sys.exit(app.exec_())
