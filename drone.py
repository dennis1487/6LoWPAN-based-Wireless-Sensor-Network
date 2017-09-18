import socket, sys, time, select, threading, struct, gspread, Queue
import paho.mqtt.client as mqtt
from oauth2client.service_account import ServiceAccountCredentials as SAC

# UDP

address = ('fdfb:b737:a075:2::8', 31500)
s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

while True:
    s.sendto("Hi! I am Subscriber.", address)
    timeout = 5
    s.setblocking(0)
    ready = select.select([s], [], [], timeout)

    if ready[0]:
        data, addr = s.recvfrom(2048)
        print "Received message:", data, "from", addr, "\n"
        s.close()
        break

# Google sheet

json = 'path to json'
scope = ['https://spreadsheets.google.com/feeds']
key = SAC.from_json_keyfile_name(json, scope)
gc = gspread.authorize(key)
spreadsheet = gc.open("datasheet_name")
worksheet = spreadsheet.worksheet("worksheet_name")
delaysheet = spreadsheet.worksheet("worksheet_name")

class Mythread(threading.Thread):
    def run(self):
        a = 1

        while True:
            msg = q.get()
            temperature, humidity, node, number = struct.unpack("ddii", msg)
            print "No.", a
            a+=1
            print "Node ID:", node, "Sequence:", number, "Temperature:", temperature, " Humidity:", humidity
            thetime = time.strftime("%d/%m/%Y %H:%M:%S")
            print "TX time:", thetime
            tx_start = time.time()
            worksheet.append_row((node, number, temperature, humidity))
            tx_end = time.time()
            delay = tx_end - tx_start
            data = struct.pack('ii19sd', node, number, thetime, delay)
            d.put(data)

class Mydelay(threading.Thread):
    def run(self):
        while True:
            rxtime = t.get()
            data = d.get()
            node, number, thetime, delay = struct.unpack('ii19sd', data)
            delaysheet.append_row((node, number, rxtime, thetime, delay))
            print "delay :", delay, "\n"

# Queue

q = Queue.Queue()
t = Queue.Queue()
d = Queue.Queue()
Mythread().start()
Mydelay().start()

# MQTT

def on_connect(client, userdata, flags, rc):
    print"Connected with result code:", rc, "\n"
    client.subscribe("drone",2)

def on_message(client, userdata, msg):
    thetime = time.strftime("%d/%m/%Y %H:%M:%S")
    print "RX time:", thetime
    t.put(thetime)

    if len(msg.payload) > 0:
        q.put(msg.payload)

client = mqtt.Client(client_id = "9", clean_session = False)
client.on_connect = on_connect
client.on_message = on_message
client.connect("fdfb:b737:a075:2::8", 1883, 60)
client.loop_forever()