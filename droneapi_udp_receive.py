from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  # for exit

host = 'localhost';
receivePort = 8000;
sendPort = 8001;

# First get an instance of the API endpoint
api = local_connect()

# Drone vehicle
v = api.get_vehicles()[0]
 
# Variables after processing DroneApi --> GH input
# using udp_process_input.py

# Create socket + port conenction between drone + GH
try:
    receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiveSocket.bind((host, receivePort))
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create receiving socket'
    sys.exit()

# Recognize commands
while True:
    try:
        # Get vehicle attributes
        recMavData = str(v.location) + ';' + str(v.attitude)
        #send to GH
        sendSocket.sendto(recMavData, (host, sendPort))
        
        data, addr = receiveSocket.recvfrom(1024)
        # Protocol --> DroneApi Call
        print "Received data:", data
        processDroneCommand(data)
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
# DRONEAPI_COMMANDS = {
# 	"TAKEOFF": takeoff()
# }

def processDroneCommand(input):
	elements = input.split()
	i_command = elements[0]
	i_params = elements[1:]
    if i_command == 'TAKEOFF':
    	alt = float(i_params[0])
    	v.commands.takeoff(alt)
    elif i_command == 'LAND':
    	pass
    elif i_command == 'GO_TO':
    	lat, lon, alt = [float(p) for p in i_params]
    	new_location = Location(lat, lon, alt)

    	v.commands.goto(new_location)
    elif i_command == 'ARMED':
    	armed_param = i_params[0]

    	is_armed = False
    	if armed_param == 'true':
    		v.armed = True
    	elif armed_param == 'false':
    		v.armed = False
    	else:
    		pass
    elif i_command == 'MODE':
    	mode = i_params[0]
    	v.mode = mode
    elif i_command == 'FLUSH':
    	v.flush()
    else:
    	print 'Invalid command: \"%s\"' % input




    

