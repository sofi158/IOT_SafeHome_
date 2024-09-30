import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QFormLayout, QWidget, QApplication, QCheckBox
from PyQt5.QtGui import QIntValidator
from init import *
from mqtt_client import Mqtt_client
from icecream import ic
from datetime import datetime
import logging
import data_acq as da
import time

# Logger setup
logger = logging.getLogger(__name__)  
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logfile_gui.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def time_format():
    return f'{datetime.now()}  GUI|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

# Prefix for GUI client
clientname_prefix = "SafeHome_GUI_"
clientname = clientname_prefix + str(random.randint(1, 10000))

# Main MQTT Client class for the GUI
class MC(Mqtt_client):
    def __init__(self):
        super().__init__()

    def on_message(self, client, userdata, msg):
        topic = msg.topic            
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("Message from:" + topic, m_decode)

# Connection dock for the GUI
class ConnectionDock(QDockWidget):
    """Connection Dock Widget"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        self.topic = comm_topic + '#'        
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

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("Click to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")

        formLayout = QFormLayout()
        formLayout.addRow("Host", self.eHostInput)
        formLayout.addRow("Port", self.ePort)
        formLayout.addRow("Client ID", self.eClientID)
        formLayout.addRow("Username", self.eUserName)
        formLayout.addRow("Password", self.ePassword)
        formLayout.addRow("Keep Alive", self.eKeepAlive)
        formLayout.addRow("SSL", self.eSSL)
        formLayout.addRow("Clean Session", self.eCleanSession)
        formLayout.addRow("", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
        self.eConnectbtn.setText('Connected')

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())           
        self.mc.connect_to()        
        self.mc.start_listening()
        time.sleep(1)
        if not self.mc.subscribed:
            self.mc.subscribe_to(self.topic)

# Main window class for the GUI
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.mc = MC()  # Instantiate MQTT Client
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('System GUI')
        # Adding Dock Widgets
        self.connectionDock = ConnectionDock(self.mc)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.connectionDock)  # Use QtCore for the enum

# Entry point for the application
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except Exception as e:
        logger.exception("GUI Crash: " + str(e))



