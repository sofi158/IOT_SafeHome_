import paho.mqtt.client as mqtt
import time
import random
from init import *
import data_acq as da
from icecream import ic
from datetime import datetime 

def time_format():
    return f'{datetime.now()}  Manager| '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

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
    insert_DB(topic, m_decode)

def insert_DB(topic, m_decode):
    if 'DHT' in m_decode: 
        value = parse_data(m_decode)
        if value != 'NA':
            da.add_IOT_data(m_decode.split('From: ')[1].split(' Temperature: ')[0], da.timestamp(), value)
    elif 'Meter' in m_decode:
        da.add_IOT_data('ElectricityMeter', da.timestamp(), m_decode.split(' Electricity: ')[1].split(' Sensitivity: ')[0])
        da.add_IOT_data('SensitivityMeter', da.timestamp(), m_decode.split(' Sensitivity: ')[1])

def parse_data(m_decode):
    value = m_decode.split(' Temperature: ')[1].split(' Humidity: ')[0]
    return value

def client_init(cname):
    r = random.randrange(1, 10000000)
    ID = str(cname + str(r))
    client = mqtt.Client(ID, clean_session=True)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    if username != "":
        client.username_pw_set(username, password)
    ic("Connecting to broker ", broker_ip)
    client.connect(broker_ip, int(port))
    return client

def check_DB_for_change(client):
    df = da.fetch_data(db_name, 'data', 'SensitivityMeter')
    if len(df.value) == 0: return
    if float(df.value[-1]) > sensitivity_max:
        msg = 'Current Sensitivity consumption exceeds normal! ' + df.value[-1]
        ic(msg)
        client.publish(comm_topic + 'alarm', msg)

    df = da.fetch_data(db_name, 'data', 'ElectricityMeter')
    if len(df.value) == 0: return
    if float(df.value[-1]) > elec_max:
        msg = 'Current electricity consumption exceeds normal! ' + df.value[-1]
        ic(msg)
        client.publish(comm_topic + 'alarm', msg)

def check_Data(client):
    try:
        rrows = da.check_changes('iot_devices')
        for row in rrows:
            topic = row[17]
            if row[10] == 'alarm':
                msg = 'Set temperature to: ' + str(row[15])
                client.publish(topic, msg)
                da.update_IOT_status(int(row[0]))
            else:
                msg = 'actuated'
                client.publish(topic, msg)
    except Exception as e:
        ic("Error in checking data: ", e)

def main():
    cname = "Manager-"
    client = client_init(cname)
    client.loop_start()
    
    print(f"Value of comm_topic: {comm_topic}")  # Print comm_topic before subscribing
    print(f"Subscribing to topic: {comm_topic}#")  # Print the subscription topic

    try:
        client.subscribe(comm_topic + '#')  # Subscribe to all topics under the comm_topic
        while True:
            check_DB_for_change(client)
            time.sleep(1)  # Adjust this as needed
            check_Data(client)
            time.sleep(3)
    except KeyboardInterrupt:
        client.disconnect()
        ic("Interrupted by keyboard")
    client.loop_stop()
    client.disconnect()
    ic("End manager run script")

if __name__ == "__main__":
    main()
