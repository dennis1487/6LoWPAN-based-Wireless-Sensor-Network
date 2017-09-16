import socket, sys, time, select, struct, threading, Queue
import paho.mqtt.client as mqtt
import Adafruit_DHT

# Sensor

humidity, temperature = Adafruit_DHT.read_retry(11, 4)

class Mysensor(threading.Thread):
    def run(self):
        number = 1

        while True:
            node = 1
            payload = struct.pack('ddii', temperature, humidity, node, number)
            q.put(payload)
            print "No.", number
            print "Temperature:", temperature, " Humidity:", humidity, "\n"
            number+=1
            time.sleep(5)

q = Queue.Queue()
Mysensor().start()

# UDP

address = ('fdfb:b737:a075:2::8', 31500)
s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

counter_a = 1
counter_b = 1

while True:

    print "Counter:", counter_a, ", Please wait for 5 seconds"
    s.sendto("Hi! I am Sensor_Node_1.", address)
    timeout = 1
    s.setblocking(0)
    ready = select.select([s], [], [], timeout)

    if ready[0]:
        data, addr = s.recvfrom(2048)
        print "Received message:", data, "from", addr, "\n"
        s.close()
        mode = 1
        break

    elif counter_a < 6:
        counter_a+=1

    elif counter_a == 6 and counter_b < 4:
        counter_a = 1
        counter_b+=1
        print "Please wait for 30 seconds"
        time.sleep(1)

    elif counter_b == 4:
        print "Wait for drone"
        mode = 2
        break

# MQTT

def mode_A():

    def on_connect(client, userdata, flags, rc):
        print "Connected with result code:", rc, "\n"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("fdfb:b737:a075:2::8", 1883, 60)
    client.loop_start()

    number = 1
    while True:
        try:
#            thetime = time.strftime("%d/%m/%Y %H:%M:%S")
#            payload = struct.pack('19sddii', thetime, temperature, humidity, node, number)
            payload = q.get()
            result, mid = client.publish("drone", payload, qos = 2, retain = False)
            print "Publish_return: result =", result, " mid =", mid, "\n"
#            print "SensorTime:", thetime

        except KeyboardInterrupt:
            print("EXIT")
            sys.exit(0)

def mode_B():

    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.bind(("", 31500))
    data, addr = s.recvfrom(2048)
    print "Received message:", data, "from", addr, "\n"
    s.sendto("Hi! I am Sensor_node_1.", addr)
    s.close()

    def on_connect(client, userdata, flags, rc):
        print "Connected with result code:", rc, "\n"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("fdfb:b737:a075:2::9", 1883, 60)
    client.loop_start()

    while True:
        try:
#            thetime = time.strftime("%d/%m/%Y %H:%M:%S")
#            payload = struct.pack('19sddii', thetime, temperature, humidity, node, number)
            payload = q.get()
            result, mid = client.publish("drone", payload, qos = 2, retain = False)
            print "Publish_return: result =", result, " mid =", mid, "\n"
#            print "SensorTime:", thetime

        except KeyboardInterrupt:
            print("EXIT")
            sys.exit(0)


if mode == 1:
    mode_A()

elif mode == 2:
    mode_B()