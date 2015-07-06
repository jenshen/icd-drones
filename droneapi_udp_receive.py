from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  # for exit

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# First get an instance of the API endpoint
api = local_connect()
 
# Variables after processing DroneApi --> GH input
# using udp_process_input.py

# Create socket + port conenction between drone + GH
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
except socket.error:
    print 'Failed to create socket'
    sys.exit()

# Recognize commands
while True:
    data, addr = sock.recvfrom(1024)
    # Protocol --> DroneApi Call
    

