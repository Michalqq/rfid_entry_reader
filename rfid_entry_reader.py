import serial
import requests
import threading
import time
from datetime import datetime

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 57600
URL = "http://www.wyniki.online/rfid/addEntry"
SKIP_FIRST_COUNT = 8
SKIP_LAST_COUNT = 4

rfid_data = []
lock = threading.Lock()

def read_serial():
    ser = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            parity = 'N',
            stopbits = 1,
            bytesize = 8,
            timeout=0.01)

    while True:
        rfid = ser.readline()
        if rfid:
            with lock:
                rfid_data.append({"timestamp": datetime.now().isoformat(), "rfid": rfid.hex()[SKIP_FIRST_COUNT:-SKIP_LAST_COUNT]})

def send_data():
    while True:
        time.sleep(10)
        with lock:
            if rfid_data:
                try:
                    response = requests.put(URL, json=rfid_data)
                    if response.status_code == 200:
                        rfid_data.clear()
                    else:
                        print(f"Failed to send data: {response.status_code}, {response.text}")
                except requests.RequestException as e:
                    print(f"Request failed: {e}")

serial_thread = threading.Thread(target=read_serial, daemon=True)
send_thread = threading.Thread(target=send_data, daemon=True)

serial_thread.start()
send_thread.start()

while True:
    time.sleep(1)