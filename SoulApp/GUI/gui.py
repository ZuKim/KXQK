import tkinter as tk
import tkinter.ttk as ttk
import datetime
import SoulApp
import random

last_log = ''
cur_state = '停止'


def start_thread():
    global cur_state
    if cur_state != '开始':
        SoulApp.start_thread()
        cur_state = '开始'
        console.insert('end', '**********程序已开始**********' + '\n')


def pause_thread():
    global cur_state
    if cur_state == '开始':
        SoulApp.pause_thread()
        cur_state = '暂停'
        console.insert('end', '**********程序已暂停**********' + '\n')


def resume_thread():
    global cur_state
    if cur_state == '暂停':
        SoulApp.resume_thread()
        cur_state = '开始'
        console.insert('end', '**********程序继续运行**********' + '\n')


def stop_thread():
    global cur_state
    SoulApp.stop_thread()
    cur_state = '停止'


def update_label():
    wait_sec_var.set(SoulApp.wait_sec)
    root.after(1000, update_label)  # 每1秒钟更新一次标签文本


def update_settings():
    _min = int(set_min_entry.get())
    if _min < 7200:
        _min = 7200
        wait_sec_min_var.set(str(_min))
    _max = int(set_max_entry.get())
    _start = datetime.datetime.strptime(start_time_var.get(), '%H:%M:%S').time()
    _end = datetime.datetime.strptime(end_time_var.get(), '%H:%M:%S').time()
    SoulApp.wait_sec_min = _min
    SoulApp.wait_sec_max = _max
    SoulApp.start_time = _start
    SoulApp.end_time = _end
    _wait_sec = random.randint(_min, _max)
    SoulApp.wait_sec = _wait_sec

    SoulApp.log = f'*****设置成功！******\n当前加群等待时间为{_wait_sec}\n程序执行时间为{_start}-{_end}'


def quit_program():
    root.destroy()
    SoulApp.stop_thread()


root = tk.Tk()
root.title("SoulApp")

bg = tk.Canvas(root, width=800, height=800, bg="white")
bg.pack()

# 显示加群等待时间
wait_label = tk.Label(bg, text="当前加群等待时间(秒钟)：")
wait_label_window = bg.create_window(360, 20, window=wait_label)

wait_sec_var = tk.StringVar(value=str(SoulApp.wait_sec))
wait_sec_label = tk.Label(bg, width=10, textvariable=wait_sec_var)
wait_sec_label_window = bg.create_window(460, 20, window=wait_sec_label)

# 设置最小等待时间
set_min_label = tk.Label(bg, text="加群最小等待时间(秒钟)：")
set_min_label_window = bg.create_window(600, 200, window=set_min_label)

wait_sec_min_var = tk.StringVar(value=str(SoulApp.wait_sec_min))
set_min_entry = tk.Entry(bg, width=18, textvariable=wait_sec_min_var)
set_min_entry_window = bg.create_window(600, 230, window=set_min_entry)

# 设置最大等待时间
set_max_label = tk.Label(bg, text="加群最大等待时间(秒钟)：")
set_max_label_window = bg.create_window(600, 300, window=set_max_label)

wait_sec_max_var = tk.StringVar(value=str(SoulApp.wait_sec_max))
set_max_entry = tk.Entry(bg, width=18, textvariable=wait_sec_max_var)
set_max_entry_window = bg.create_window(600, 330, window=set_max_entry)

# 设置程序开始时间
set_start_label = tk.Label(bg, text="程序开始时间(几点)：")
set_start_label_window = bg.create_window(600, 400, window=set_start_label)

start_time_var = tk.StringVar(value=str(SoulApp.start_time))
start_time_entry = ttk.Combobox(bg, width=15, textvariable=start_time_var, values=[datetime.time(hour=h, minute=m).strftime('%H:%M:%S') for h in range(24) for m in (0, 15, 30, 45)])
start_time_window = bg.create_window(600, 430, window=start_time_entry)

# 设置程序停止时间
set_end_label = tk.Label(bg, text="程序开始时间(几点)：")
set_end_label_window = bg.create_window(600, 500, window=set_end_label)

end_time_var = tk.StringVar(value=str(SoulApp.end_time))
end_time_entry = ttk.Combobox(bg, width=15, textvariable=end_time_var, values=[datetime.time(hour=h, minute=m).strftime('%H:%M:%S') for h in range(24) for m in (0, 15, 30, 45)])
end_time_window = bg.create_window(600, 530, window=end_time_entry)

# 设置确认按钮
confirm_button = tk.Button(bg, text="确认", command=update_settings, width=10, height=1)
confirm_button_window = bg.create_window(600, 630, window=confirm_button)

# 按钮
start_button = tk.Button(bg, text='开始', command=start_thread, width=10, height=2)
start_button_window = bg.create_window(300, 100, window=start_button)

pause_button = tk.Button(bg, text='暂停', command=pause_thread, width=10, height=2)
pause_button_window = bg.create_window(400, 100, window=pause_button)

continue_button = tk.Button(bg, text='继续', command=resume_thread, width=10, height=2)
continue_button_window = bg.create_window(500, 100, window=continue_button)

# 日志窗口
console = tk.Text(bg, width=60, height=40, bd=1, relief="solid")
console_window = bg.create_window(300, 450, window=console)


# 日志窗口更新
def add_text():
    global last_log
    console.configure(state='normal')
    if SoulApp.log != last_log:
        console.insert('end', SoulApp.log + '\n')
        console.see('end')
        console.configure(state='disabled')
        last_log = SoulApp.log
    root.after(100, add_text)  # 每隔100ms更新一次


add_text()
update_label()
root.mainloop()
