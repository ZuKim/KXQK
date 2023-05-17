from PySide2.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide2.QtCore import QTimer, QThread, Signal
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPixmap, QImage
from SoulApp.Scripts import soul
import subprocess

last_log = ''
cur_state = '停止'


def start_thread():
    global cur_state
    soul.start_thread()
    cur_state = '开始'
    soul.log = '**********程序已开始**********'


def pause_thread():
    global cur_state
    soul.pause_thread()
    cur_state = '暂停'
    soul.log = '**********程序已暂停**********'


def resume_thread():
    global cur_state
    soul.resume_thread()
    cur_state = '开始'
    soul.log = '**********程序重新开始**********'


def stop_thread():
    global cur_state
    soul.stop_thread()
    cur_state = '停止'


def get_android_screen():
    cmd = ['adb', 'exec-out', 'screencap', '-p']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    pixmap = QPixmap()
    pixmap.loadFromData(output)
    return pixmap


class UpdateScreenThread(QThread):
    update_screen_signal = Signal(QPixmap)

    def run(self):
        while True:
            pixmap = get_android_screen()
            self.update_screen_signal.emit(pixmap)
            self.msleep(500)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口大小和标题
        self.setGeometry(100, 100, 1080, 720)
        self.setWindowTitle('My App')
        self.main_menu = QUiLoader().load('MainMenu.ui')
        self.display = QUiLoader().load('Display.ui')
        self.log = QUiLoader().load('Log.ui')
        self.init_ui()

    def init_ui(self):
        splitter = QSplitter(self)
        splitter.addWidget(self.main_menu)
        splitter.addWidget(self.display)
        splitter.addWidget(self.log)
        splitter.setSizes([50, 100, 100])
        self.setCentralWidget(splitter)

        self.display.DeviceID.setText(str(soul.get_device_id()))
        self.display.Start_btn.clicked.connect(start_thread)
        self.display.Pause_btn.clicked.connect(pause_thread)

        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_log(self.log.LogText))
        timer.start(100)

        self.update_screen_thread = UpdateScreenThread()
        self.update_screen_thread.update_screen_signal.connect(self.update_screen)
        self.update_screen_thread.start()

    def update_log(self, log_text):
        global last_log
        if soul.log != last_log:
            log_text.appendPlainText(soul.log)
            last_log = soul.log

    def update_screen(self, pixmap):
        scaled_width = pixmap.width() // 5
        scaled_height = pixmap.height() // 5
        scaled_pixmap = pixmap.scaled(scaled_width, scaled_height)
        self.display.ScreenLabel.setPixmap(scaled_pixmap)

    def stop_update_screen_thread(self):
        self.update_screen_thread.terminate()

    def closeEvent(self, event):
        self.stop_update_screen_thread()
        super().closeEvent(event)


app = QApplication([])
main_window = MainWindow()
main_window.show()
app.exec_()
