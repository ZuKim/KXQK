import cv2
import numpy as np
import subprocess
import datetime
import time
import random
import threading
import adbutils
import pytesseract

update_sec = 10
wait_sec_min = 7000
wait_sec_max = 9000
wait_sec = random.randint(wait_sec_min, wait_sec_max)
last_join_time = datetime.datetime.now() - datetime.timedelta(seconds=wait_sec)
start_time = datetime.time(9, 0)
end_time = datetime.time(22, 0)
log = ''
changeScreen = False
device_id = ''

page_dict = {
    "主屏幕页面": "../ImgSrc/p_home.png",
    "星球页面": "../ImgSrc/soul/p_xingqiu.png",
    "兴趣群组页面": "../ImgSrc/soul/p_xingqiu_group.png",
    "聊天页面": "../ImgSrc/soul/p_xingqiu_group_chat.png",
    "弹窗页面": "../ImgSrc/soul/p_anchuang.png",
    "其他主页面": "../ImgSrc/soul/p_main.png",
    "群预览页面": "../ImgSrc/soul/p_group_view.png",
}

btn_dict = {
    "app_soul按钮": "../ImgSrc/soul/app.png",
    "兴趣群组按钮": "../ImgSrc/soul/b_xingqiu_group.png",
    "加入按钮": "../ImgSrc/soul/b_xingqiu_group_join.png",
    "知道按钮": "../ImgSrc/soul/b_tanchuang_zd.png",
    "星球按钮": "../ImgSrc/soul/b_main_xingqiu.png",
    "表情选择按钮": "../ImgSrc/soul/b_xingqiu_group_chat_face.png",
}


def get_device_id():
    adb = adbutils.AdbClient()
    devices = adb.device_list()
    return devices[0].serial


print(get_device_id())


def current_page():
    global changeScreen
    # 截取当前屏幕截图，并加载为 OpenCV 图像对象
    subprocess.run("adb shell screencap -p /sdcard/screen.png", shell=True)
    subprocess.run("adb pull /sdcard/screen.png", shell=True)
    screen = cv2.imread("screen.png")
    changeScreen = True
    # 遍历 page_dict 中的每个页面，并进行模板匹配
    max_similarity = 0.8
    max_page_name = ""
    for page_name, template_path in page_dict.items():
        template = cv2.imread(template_path)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        similarity = result.max()
        if similarity > max_similarity:
            max_similarity = similarity
            max_page_name = page_name
    return max_page_name


def find_btn_and_point(btn_name):
    global log
    # 使用ADB命令截取屏幕截图
    subprocess.run("adb shell screencap -p /sdcard/screen.png", shell=True)
    subprocess.run("adb pull /sdcard/screen.png", shell=True)

    # 加载截图并查找特定图像
    screen = cv2.imread("screen.png")
    template = cv2.imread(btn_dict[btn_name])
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    y, x = np.unravel_index(result.argmax(), result.shape)
    print(result[y, x])

    # 如果找到了特定图像，使用ADB命令模拟点击操作
    if result[y, x] > 0.8:
        subprocess.run("adb shell input tap {} {}".format(x, y), shell=True)
        log = f'执行操作：点击{str(btn_name)}'
    else:
        log = f'未能找到相应按钮，{str(update_sec)}秒钟后重新执行脚本'


def join_group():
    global last_join_time
    global log
    global wait_sec
    find_btn_and_point("加入按钮")
    last_join_time = datetime.datetime.now()
    log = f"{last_join_time.replace(microsecond=0)}加入了一个群"
    wait_sec = random.randint(7200, 9000)


def try_join_group():
    global log
    global update_sec
    current_time = datetime.datetime.now().time()
    if start_time <= current_time <= end_time:
        if datetime.datetime.now() > last_join_time + datetime.timedelta(seconds=wait_sec):
            cur_page = current_page()
            log = f'当前手机页面为：{cur_page}'
            print(log)
            if cur_page == "主屏幕页面":
                find_btn_and_point("app_soul按钮")
            elif cur_page == "星球页面":
                find_btn_and_point("兴趣群组按钮")
            elif cur_page == "兴趣群组页面":
                join_group()
            elif cur_page == "聊天页面" or cur_page == "群预览页面":
                chat()
                # subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_BACK"], capture_output=True)
                # log = '返回'
            elif cur_page == "弹窗页面":
                find_btn_and_point("知道按钮")
            elif cur_page == "其他主页面":
                find_btn_and_point("星球按钮")
            else:
                log = f'{datetime.datetime.now().replace(microsecond=0)}\n未能识别当前手机页面，{str(update_sec)}秒钟后重新执行脚本'
        # else:
        #     log = f'{datetime.datetime.now().replace(microsecond=0)}晚些再进群'
    else:
        log = f'{datetime.datetime.now().replace(microsecond=0)}休息时间'


def chat():
    text = "Hello"
    adb_command = f'adb shell input text "{text}"'
    subprocess.call(adb_command, shell=True)
    subprocess.run("adb shell input keyevent 66", shell=True)

stop_event = threading.Event()


def t_join_group():
    global log
    while not stop_event.is_set():
        try_join_group()
        time.sleep(update_sec)


def start_thread():
    global thread
    thread = threading.Thread(target=t_join_group)
    thread.start()


def stop_thread():
    stop_event.set()
    thread.join()


def pause_thread():
    stop_event.set()


def resume_thread():
    stop_event.clear()
    start_thread()
