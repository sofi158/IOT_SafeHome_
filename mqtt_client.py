import paho.mqtt.client as mqtt
from icecream import ic
from datetime import datetime

def time_format():
    return f'{datetime.now()}  Agent|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

class Mqtt_client:
    
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = '' 
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''
        self.connected = False
        self.subscribed = False
        
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_broker(self, value):
        self.broker = value         

    def set_port(self, value):
        self.port = value     

    def set_clientName(self, value):
        self.clientname = value        

    def set_username(self, value):
        self.username = value     

    def set_password(self, value):
        self.password = value         
        
    def connect_to(self):
        self.client = mqtt.Client(self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect  
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)        
        ic("Connecting to broker ", self.broker)        
        self.client.connect(self.broker, self.port)
    
    def disconnect_from(self):
        self.client.disconnect()                   
    
    def start_listening(self):        
        self.client.loop_start()        
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):
        if self.connected:
            self.client.subscribe(topic)
            self.subscribed = True
        else:
            ic("Can't subscribe. Connection should be established first.")        
        
    def publish_to(self, topic, message):
        if self.connected:
            self.client.publish(topic, message)
        else:
            ic("Can't publish. Connection should be established first.")

    def on_log(self, client, userdata, level, buf):
        ic("log: "+buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            ic("Connected OK")
            self.connected = True
            self.on_connected_to_form()
        else:
            ic("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.connected = False
        ic("Disconnected result code "+str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("Message from:" + topic, m_decode)
