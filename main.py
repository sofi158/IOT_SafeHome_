#main
import paho.mqtt.client as mqtt
import time
from init import *
from icecream import ic
from datetime import datetime

def time_format():
    return f'{datetime.now()}  Main|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

# Define callback functions
def on_log(client, userdata, level, buf):
    ic("log: " + buf)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        ic("Connected OK")
    else:
        ic("Bad connection. Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    ic("Disconnected result code " + str(rc))

def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    ic("Message from: " + topic, m_decode)

    # Handling different topics based on the incoming messages
    if 'DHT' in topic:
        ic("DHT Data: " + m_decode)
    elif 'Relay' in topic:
        ic("Relay Data: " + m_decode)
    elif 'Button' in topic:
        ic("Button Data: " + m_decode)

def connect_mqtt():
    client = mqtt.Client(clientname, clean_session=True)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    client.username_pw_set(username, password)
    ic("Connecting to broker", broker_ip)
    client.connect(broker_ip, int(broker_port))
    return client

if __name__ == "__main__":
    client = connect_mqtt()
    client.loop_start()  # Start loop
    client.subscribe(comm_topic + "/#")  # Subscribe to all topics under home/safehome
    try:
        while True:
            time.sleep(5)  # Keep running
    except KeyboardInterrupt:
        client.disconnect()
        ic("Disconnected from broker")
    client.loop_stop()


