import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

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
    def __init__(self):
        super().__init__()

        self.w = 6
        self.h = 7
        self.s = 100

        self.initUI()

    def initUI(self):
        labels = []
        for y in range(self.h):
            labels += [[]]
            for x in range(self.w):
                labels[y] += [HoverLabel(x, y, self)]
                labels[y][x].setFixedSize(self.s, self.s)
                labels[y][x].setAlignment(Qt.AlignCenter)
                labels[y][x].move(x * self.s, y * self.s)
                setColor(labels[y][x], (25 * x + 75, 25 * y + 75, 0, 255))
                labels[y][x].mouseHover.connect(self.hovered)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Fancy LED Matrix Ultimate Simulation')
        self.show()

    def hovered(self, hovered):
        if hovered:
            (x, y) = self.sender().pos()
            print("hovered {},{}".format(x, y))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sim = Simulator()
    sys.exit(app.exec_())