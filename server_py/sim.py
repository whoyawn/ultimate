import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import pika
import threading
import json

def setColor(label, color):
    label.setStyleSheet('background-color: rgba{};'.format(str(color)))

class HoverLabel(QLabel):
    mouseHover = pyqtSignal(bool)

    def __init__(self, x, y, parent=None):
        self.x_pos = x
        self.y_pos = y
        QLabel.__init__(self, '{},{}'.format(x, y), parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.mouseHover.emit(True)

    def leaveEvent(self, event):
        self.mouseHover.emit(False)

    def pos(self):
        return (self.x_pos, self.y_pos)

class Simulator(QWidget):
    colors_received = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.w = 6
        self.h = 7
        self.s = 100

        self.initUI()

        self.colors_received.connect(self.update_colors)

        pika_thread = threading.Thread(target=self.run_pika)
        pika_thread.start()

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.sensor_channel = connection.channel()
        self.sensor_channel.queue_declare(queue='matrix-sensor')

    def initUI(self):
        self.labels = []
        for y in range(self.h):
            self.labels += [[]]
            for x in range(self.w):
                self.labels[y] += [HoverLabel(x, y, self)]
                self.labels[y][x].setFixedSize(self.s, self.s)
                self.labels[y][x].setAlignment(Qt.AlignCenter)
                self.labels[y][x].move(x * self.s, y * self.s)
                setColor(self.labels[y][x], (25 * x + 75, 25 * y + 75, 0, 255))
                self.labels[y][x].mouseHover.connect(self.hovered)

        self.setStyleSheet("background-color: rgba(255, 255, 255, 100)")
        self.setGeometry(300, 300, 600, 700)
        self.setWindowTitle('Fancy LED Matrix Ultimate Simulation')
        self.show()

    def update_colors(self, colors):
        for y in range(len(colors)):
            for x in range(len(colors[y])):
                setColor(self.labels[y][x], tuple(colors[y][x]))

    def hovered(self, hovered):
        sensors = [[0 for x in range(self.w)] for y in range(self.h)]

        if hovered:
            (x, y) = self.sender().pos()
            sensors[y][x] = 1

        self.sensor_channel.basic_publish(exchange='',
                              routing_key='matrix-sensor',
                              body=json.dumps(sensors))

    def run_pika(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='matrix-color')

        def callback(ch, method, properties, body):
            colors = json.loads(body.decode('utf-8'))
            self.colors_received.emit(colors)

        channel.basic_consume(callback,
                              queue='matrix-color',
                              no_ack=True)

        channel.start_consuming()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sim = Simulator()
    sys.exit(app.exec_())