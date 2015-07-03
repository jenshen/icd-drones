from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  #for exit

# First get an instance of the API endpoint
api = local_connect()
# Get the connected vehicle (currently only one vehicle can be returned).
v = api.get_vehicles()[0]

# Get vehicle attributes (state)


 
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
 
host = 'localhost';
port = 8888;
 
while(1) :
    data = str(v.location)  
    try :
        #Set the whole string
        s.sendto(data, (host, port))
        print "Hello, success"
         
        # receive data from client (data, addr)
        #d = s.recvfrom(1024)
        #reply = d[0]
        # addr = d[1]
         
        # print 'Server reply : ' + reply
     
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()