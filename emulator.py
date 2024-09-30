# emulator.py - Emulates different IoT devices for SafeHome

import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from init import *
from mqtt_client import Mqtt_client  # Custom MQTT client class for handling communication
from icecream import ic
from datetime import datetime
import time  # Import time module for sleep functionality

# Setup logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logfile_emulator.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Prefix for each emulator client
clientname_prefix = "SafeHome_Emulator_"

# Generating a unique client name for each instance
clientname = clientname_prefix + str(random.randint(1, 10000))

# Define the main MQTT Client class
class MC(Mqtt_client):
    def __init__(self):
        super().__init__()

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("Message from:" + topic, m_decode)
        try:
            mainwin.connectionDock.update_btn_state(m_decode)
        except Exception as e:
            ic("Failed to update button state", e)


# Define the connection dock for emulators
class ConnectionDock(QDockWidget):
    """Connection Dock Widget"""
    def __init__(self, mc, name, topic_sub, topic_pub):
        QDockWidget.__init__(self)
        self.name = name
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)

        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()
        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("Click to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        formLayout = QFormLayout()
        formLayout.addRow("Host", self.eHostInput)
        formLayout.addRow("Port", self.ePort)
        formLayout.addRow("Client ID", self.eClientID)
        formLayout.addRow("Username", self.eUserName)
        formLayout.addRow("Password", self.ePassword)
        formLayout.addRow("Keep Alive", self.eKeepAlive)
        formLayout.addRow("SSL", self.eSSL)
        formLayout.addRow("Clean Session", self.eCleanSession)
        formLayout.addRow("Turn On/Off", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle(name)

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()

# Main window for GUI
class MainWindow(QMainWindow):
    def __init__(self, args, parent=None):
        QMainWindow.__init__(self, parent)
        global tmp_upd

        self.name = args[1]
        self.units = args[2]
        self.topic_sub = comm_topic + args[3] + '/sub'
        self.topic_pub = comm_topic + args[3] + '/pub'
        self.update_rate = args[4]

        self.mc = MC()

        self.connectionDock = ConnectionDock(self.mc, self.name, self.topic_sub, self.topic_pub)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

        # Start a timer for publishing data
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.publish_data)
        self.timer.start(int(self.update_rate) * 1000)  # Convert seconds to milliseconds

    def publish_data(self):
        # Example data publishing for DHT sensor
        if self.name == 'DHT':
            temperature = random.uniform(20.0, 30.0)  # Simulate temperature
            humidity = random.uniform(30.0, 70.0)  # Simulate humidity
            message = f"Temperature: {temperature}, Humidity: {humidity}"
            self.mc.publish_to(self.topic_pub, message)
        # Example data publishing for Relay
        elif self.name == 'Relay':
            state = random.choice(['ON', 'OFF'])
            message = f"Relay State: {state}"
            self.mc.publish_to(self.topic_pub, message)
        # Example data publishing for Button
        elif self.name == 'Button':
            button_state = random.choice(['Pressed', 'Released'])
            message = f"Button State: {button_state}"
            self.mc.publish_to(self.topic_pub, message)

# Entry point of the application
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        argv = sys.argv
        if len(sys.argv) == 1:
            argv.append('DHT')  # Change this to 'Relay' or 'Button' for different emulators
            argv.append('Celsius')
            argv.append('air-1')
            argv.append('7')

        mainwin = MainWindow(argv)
        mainwin.show()
        app.exec_()
    except:
        logger.exception("Crash!")


