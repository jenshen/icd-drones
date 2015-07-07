from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  # for exit

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# First get an instance of the API endpoint
api = local_connect()

# Drone vehicle
v = api.get_vehicles()[0]
 
# Variables after processing DroneApi --> GH input
# using udp_process_input.py

# Create socket + port conenction between drone + GH
try:
    recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recvSock.bind((UDP_IP, UDP_PORT))
except socket.error:
    print 'Failed to create receiving socket'
    sys.exit()

# Recognize commands
while True:
    data, addr = sock.recvfrom(1024)
    # Protocol --> DroneApi Call
    
	print "Received data:", data
	processDroneCommand(data)

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




    

