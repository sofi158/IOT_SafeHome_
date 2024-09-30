# Configuration file for the SafeHome project

import socket
import random

# Index for the broker - 0 for local, 1 for public, etc.
nb = 1  

# Broker details (IP addresses and ports)
brokers = [
    "127.0.0.1",  # Local broker
    "broker.hivemq.com",  # Public broker
    "18.194.176.210"  # Custom broker
]

# Ports for each broker
ports = ['1883', '1883', '1883']
port = ports[nb]

# Usernames and passwords (if required)
usernames = ['user1', 'user2', 'user3']
passwords = ['pass1', 'pass2', 'pass3']

# Assigning the current broker and port
broker_ip = brokers[nb]
broker_port = ports[nb]
username = usernames[nb]
password = passwords[nb]

comm_topic = 'home/safehome'


# General MQTT connection settings
conn_time = 0  # 0 stands for endless loop

# Variables for FFT and DSP modules (used for sensor data processing)
isplot = False
issave = False
percen_thr = 0.05
Fs = 2048.0
deviation_percentage = 10
max_eucl = 0.5 

# Database details (if using SQLite)
db_name = 'data/safehome.db'
db_init = False

# Sensitivity and Electricity limits (adjust for alarms)
sensitivity_max = 0.02
elec_max = 1.8

manag_time = 5

# Generate a unique client name for each instance
clientname_prefix = "SafeHome_Client_"
clientname = clientname_prefix + str(random.randint(1, 10000))
