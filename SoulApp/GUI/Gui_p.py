import sys
from SoulApp.Scripts import soul
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFrame, \
    QLabel, QPlainTextEdit
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QTimer
import subprocess
import cv2

last_log = ''
cur_state = '停止'


def start_thread():
    global cur_state
    if cur_state != '开始':
        soul.start_thread()
        cur_state = '开始'
        soul.log = '**********程序已开始**********'


def pause_thread():
    global cur_state
    if cur_state == '开始':
        soul.pause_thread()
        cur_state = '暂停'
        soul.log = '**********程序已暂停**********'


def resume_thread():
    global cur_state
    if cur_state == '暂停':
        soul.resume_thread()
        cur_state = '开始'
        soul.log = '**********程序重新开始**********'


def stop_thread():
    global cur_state
    soul.stop_thread()
    cur_state = '停止'


class MainUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口大小和标题
        self.setGeometry(100, 100, 1080, 720)
        self.setWindowTitle('My App')

        # 获取窗口大小
        screen_size = QApplication.desktop().screenGeometry()

        # 创建左侧边栏
        sidebar = QFrame(self)
        sidebar.setStyleSheet("background-color: #D8D8D8")
        sidebar.setFixedWidth(100)
        sidebar.setFixedHeight(screen_size.height())

        # 创建菜单按钮
        btn_monitor = QPushButton('监控', self)
        btn_monitor.setStyleSheet(button_style)
        btn_data = QPushButton('数据', self)
        btn_data.setStyleSheet(button_style)
        btn_settings = QPushButton('设置', self)
        btn_settings.setStyleSheet(button_style)

        # 连接按钮的clicked信号到槽函数
        btn_monitor.clicked.connect(self.on_menu_btn_clicked)
        btn_data.clicked.connect(self.on_menu_btn_clicked)
        btn_settings.clicked.connect(self.on_menu_btn_clicked)

        # 添加菜单按钮到左侧边栏
        vbox = QVBoxLayout(sidebar)
        vbox.addWidget(btn_monitor)
        vbox.addWidget(btn_data)
        vbox.addWidget(btn_settings)
        vbox.addStretch(1)
        vbox.setSpacing(40)
        vbox.setContentsMargins(0, 40, 0, 0)

        # *******************************************************
        # 创建操作按钮区域
        operation = QFrame(self)
        operation.setStyleSheet("background-color: #FFFFFF")
        operation.setFixedWidth(100)
        operation.setFixedHeight(screen_size.height())
        operation.move(400, 0)

        # 创建操作按钮
        btn_start = QPushButton('开始', self)
        btn_start.setStyleSheet(button_style)
        btn_pause = QPushButton('暂停', self)
        btn_pause.setStyleSheet(button_style)
        btn_resume = QPushButton('继续', self)
        btn_resume.setStyleSheet(button_style)
        btn_stop = QPushButton('停止', self)
        btn_stop.setStyleSheet(button_style)

        # 连接按钮的clicked信号到槽函数
        btn_start.clicked.connect(start_thread)
        btn_pause.clicked.connect(pause_thread)
        btn_resume.clicked.connect(resume_thread)
        btn_stop.clicked.connect(stop_thread)

        # 添加操作按钮到操作区域
        vbox = QVBoxLayout(operation)
        vbox.addWidget(btn_start)
        vbox.addWidget(btn_pause)
        vbox.addWidget(btn_resume)
        vbox.addWidget(btn_stop)
        vbox.addStretch(1)
        vbox.setSpacing(40)
        vbox.setContentsMargins(0, 40, 0, 0)

        # *******************************************************
        # 创建中间内容区域
        content = QFrame(self)
        content.setStyleSheet("background-color: #D8D8D8")
        content.setFixedWidth(300)
        content.setFixedHeight(screen_size.height())
        content.move(500, 0)

        # 创建设备ID，设备截屏预览，和实时动态信息
        layout = QtWidgets.QVBoxLayout(content)
        device_id = QLabel('设备ID', content)
        device_id.setAlignment(QtCore.Qt.AlignCenter)
        pixmap = QtGui.QPixmap('screen.png')
        pixmap = pixmap.scaled(pixmap.width() // 4, pixmap.height() // 4)  # 缩小图片
        device_image = QtWidgets.QLabel(self)
        device_image.setPixmap(pixmap)
        device_image.setAlignment(QtCore.Qt.AlignCenter)
        device_image.setContentsMargins(0, 50, 0, 0)
        device_image.setMinimumSize(pixmap.width(), pixmap.height())

        layout.addWidget(device_id)
        layout.addWidget(device_image)
        layout.addStretch(1)

        # *******************************************************
        # 创建右侧日志区域
        log = QFrame(self)
        log.setStyleSheet("background-color: #000000")
        log.setFixedWidth(300)
        log.setFixedHeight(screen_size.height())
        log.move(800, 0)

        # 将QLabel转换为QPlainTextEdit，以便在其中显示文本
        log_text = QPlainTextEdit(log)
        log_text.setReadOnly(True)
        log_text.setStyleSheet("color: white")
        # log_text填充整个窗口
        layout = QVBoxLayout(log)
        layout.addWidget(log_text)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建定时器，定期更新日志文本
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_log(log_text))
        timer.timeout.connect(lambda: self.update_screen(device_image))
        timer.start(100)

    # 槽函数，处理按钮点击事件
    def on_menu_btn_clicked(self):
        btn = self.sender()  # 获取发出信号的对象，即被点击的按钮
        print("按钮标题：", btn.text())  # 获取按钮标题并打印

    # 定义更新日志文本的槽函数
    def update_log(self, log_text):
        global last_log
        if soul.log != last_log:
            log_text.appendPlainText(soul.log)
            last_log = soul.log

    # 定义更新截屏的槽函数
    def update_screen(self, divice_image):
        if soul.changeScreen:
            subprocess.run("adb shell screencap -p /sdcard/screen2.png", shell=True)
            subprocess.run("adb pull /sdcard/screen2.png", shell=True)
            pixmap = QtGui.QPixmap('screen2.png')
            pixmap = pixmap.scaled(pixmap.width() // 4, pixmap.height() // 4)  # 缩小图片
            divice_image.setPixmap(pixmap)
            soul.changeScreen = False


# 设定按钮样式
button_style = "QPushButton { \
                        background-color: #D8D8D8; \
                        color: black; \
                        border-style: outset; \
                        border-width: 0px; \
                        border-radius: 10px; \
                        border-color: #D8D8D8; \
                        font: bold 14px; \
                        padding: 0px; \
                    } \
                    QPushButton:hover { \
                        background-color: #D8D8D8; \
                        color: #3662EC; \
                    } \
                    QPushButton:pressed { \
                        background-color: #696969; \
                        border-style: inset; \
                    }"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    sys.exit(app.exec_())
