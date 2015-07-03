#
# This example shows how to use DroneKit-Python to get and set vehicle state, parameter and channel-override information. 
# It also demonstrates how to observe vehicle attribute (state) changes. 
# 
# Usage:
# * mavproxy.py
# * module load api
# * api start vehicle-state.py
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket
import sys

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
addr = ('127.0.0.1', '50438')
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
# First get an instance of the API endpoint
api = local_connect()
# Get the connected vehicle (currently only one vehicle can be returned).
v = api.get_vehicles()[0]

while not api.exit:
	# Get all vehicle attributes (state)
	data = v.location #+ v.attitude
	s.sendto(data , addr)
	print data
	
#now keep talking with the client

      
         
    
   # print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
     
s.close()
	



