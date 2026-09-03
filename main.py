from flask import Flask, request, jsonify
import socket
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Конфигурация
TARGET_MAC = os.getenv("TARGET_MAC")
DEST_IP = os.getenv("DEST_IP")
DEST_PORT = int(os.getenv("DEST_PORT"))
SECRET_TOKEN = os.getenv("WOL_SECRET_TOKEN")
SERVER_PORT = int(os.getenv("SERVER_PORT"))


def send_magic_packet(mac_address, dest_ip, dest_port):
    #Создание и отправка Magic Packet для Wake-on-LAN
    # Очистка и проверка MAC-адреса
    mac = mac_address.replace(":", "").replace("-", "")
    if len(mac) != 12:
        raise ValueError("Некорректный MAC-адрес")
    
    # Создание Magic Packet: 6 байт 0xFF + 16 повторений MAC
    packet = b'\xff' * 6 + bytes.fromhex(mac) * 16
    
    # Отправка через UDP broadcast
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (dest_ip, dest_port))


@app.route("/wake", methods=["POST"])
def wake():
    #Endpoint для пробуждения компьютера
    # Проверка авторизации
    if request.headers.get("Authorization") != f"Bearer {SECRET_TOKEN}":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        send_magic_packet(TARGET_MAC, DEST_IP, DEST_PORT)
        return jsonify({
            "status": "success",
            "message": "Packet successfully sent",
            "mac": TARGET_MAC,
            "destination": DEST_IP,
            "port": DEST_PORT
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    #Проверка работы сервиса
    return jsonify({
        "status": "ok",
        "message": "Wake-on-LAN service is running"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)