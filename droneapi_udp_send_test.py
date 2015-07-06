from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  #for exit

startTime = time.strftime("%H:%M:%S")
host = '127.0.1.1';
receivePort = 8000;
sendPort = 8001;

# First get an instance of the API endpoint
api = local_connect()
# Get the connected vehicle (currently only one vehicle can be returned).
v = api.get_vehicles()[0]


# create dgram udp socket
try:
    receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

 # Bind socket to local host and port 
try:
    receiveSocket.bind((host, receivePort))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
    


while(1) :
    # Get vehicle attributes
    recMavData = str(v.location) + ';' + str(v.attitude)
 
    try :
        d = receiveSocket.recvfrom(1024)
        receivedData = d[0]
        print time.strftime("%H:%M:%S"), ' message: ', receivedData
        sendSocket.sendto(recMavData, (host, sendPort))
       
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    
    time.sleep(0.05)
