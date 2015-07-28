from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil
import time
import socket   #for sockets
import sys  # for exit
import math
from clint.textui import colored, puts

host = 'localhost';
receivePort = 8000;
sendPort = 8001;

api = local_connect() # Get an instance of the API endpoint
vehicle = api.get_vehicles()[0] # Drone vehicle

coordinateList = []
sequenceList = []
sequencePos = 0
vehicleState = 'disarmed'
targetLat = None
targetLon = None
targetAlt = None
lastMsgTime = 0
lastMsg = None


try: # Create socket + port connection between drone + GH
    receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiveSocket.bind((host, receivePort))
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create receiving socket'
    sys.exit()

    
def CheckProximity():
    global targetLat, targetLon
    buffer = 0.4 # waypoint reach threshold in meters
    latInMeters = 111204.722132
    lonInMeters = 73389.384924
    currentLat = float(str(vehicle.location.lat))
    currentLon = float(str(vehicle.location.lon))
    curLatM = currentLat * latInMeters
    curLonM = currentLon * lonInMeters
    tarLatM = targetLat * latInMeters
    tarLonM = targetLon * lonInMeters
    
    distance = math.sqrt( math.pow((curLatM-tarLatM),2) + math.pow((curLonM-tarLonM),2) )
    distance = round(distance,1)
    if curLatM > tarLatM-buffer and curLatM < tarLatM+buffer:
        if curLonM > tarLonM-buffer and curLonM < tarLonM+buffer:
            return True
    else:
        return distance

def PrintMessage(message = None, args = ''):
    global lastMsgTime
    global vehicleState
    global lastMsg
    
    msgDelay = 0.6 #time in seconds between different messages
    
    if time.time() - lastMsgTime > msgDelay or lastMsg != message:
        if message != "print vehicle state":
            print time.strftime("%H:%M:%S"), colored.cyan('     #### '+ message + ' ' + str(args) + ' ####')
        else:
            print time.strftime("%H:%M:%S"), colored.green('#### VEHICLE STATE - '+ str(vehicleState).upper()+ ' ####')
        lastMsgTime = time.time()
        lastMsg = message
    
def Update_vehicle():
    global vehicleState
    global targetLat, targetLon, targetAlt

    # FAIL SAFE - if drone in LOITER, vehicleState = manual
    if vehicle.mode.name == 'LOITER' and vehicleState != 'manual':
        vehicleState = 'manual'

    if vehicleState == 'ready':
        PrintMessage("Basic pre-arm checks...")
        # Don't let the user try to fly autopilot is booting
        if vehicle.mode.name == "INITIALISING":
            PrintMessage("Waiting for vehicle to initialise...")
        else:
            vehicleState = 'initialised'
            PrintMessage("print vehicle state")
        if vehicle.gps_0.fix_type < 2:
            PrintMessage("Waiting for vehicle to initialise...", vehicle.gps_0.fix_type)
            # gps_0.fix_type: #0-1: no fix #2: 2D fix, 3: 3D fix, 4: DGPS, 5: RTK
        else:
            vehicleState = 'gpsfix'
            PrintMessage("print vehicle state")
    
    elif vehicleState == 'gpsfix':
        PrintMessage("Arming motors!")
        # Copter should arm in GUIDED mode
        vehicle.mode    = VehicleMode("GUIDED")
        vehicle.armed   = True
        vehicle.flush()
        vehicleState = 'arming'
        
    elif vehicleState == 'arming':
        #print time.strftime("%H:%M:%S"), " Waiting for arming..."
        PrintMessage("Waiting for arming...")
        if vehicle.armed and not api.exit:
            vehicleState = 'armed'
            PrintMessage("print vehicle state")
            
    elif vehicleState == 'armed':
        
        if targetAlt != None:
            vehicle.commands.takeoff(targetAlt) # Take off to target altitude
            vehicle.flush()
            vehicleState = 'takingoff'
            PrintMessage("Taking off!")

    elif vehicleState == 'takingoff':
        if vehicle.location.alt>=targetAlt*0.95 and not api.exit: 
            vehicleState = 'takeoffcomplete'
            PrintMessage("Reached target altitude!")
            PrintMessage("print vehicle state")
        else:
            PrintMessage("Altitude:", round(vehicle.location.alt,1))
            
    elif vehicleState == 'takeoffcomplete':
        waypoint = Location(targetLat, targetLon, targetAlt, is_relative=True)
        vehicle.commands.goto(waypoint)
        vehicle.flush()
        vehicleState = 'movingtolocation'
        PrintMessage("print vehicle state")
        PrintMessage("Going to location...", str(waypoint))
        
    elif vehicleState == 'movingtolocation':
        #check here if vehicle reached destination waypoint
        if CheckProximity() is True:
            vehicleState = 'reachedlocation'
            PrintMessage("print vehicle state")
        else:
            PrintMessage("Distance to location:", CheckProximity())
            
    elif vehicleState == 'reachedlocation':
        PrintMessage("Setting LAND mode...")
        vehicle.mode = VehicleMode("LAND")
        vehicle.flush()
        vehicleState = 'landing'
        PrintMessage("print vehicle state")
    
    elif vehicleState == 'landing':   
        PrintMessage("Altitude:", round(vehicle.location.alt,1))
        if not vehicle.armed:
            vehicleState = 'disarmed'
            targetLat = None
            targetLon = None
            targetAlt = None
            PrintMessage("print vehicle state")
    
    elif vehicleState == 'disarmed':
        if targetLat != None and targetLon != None and targetAlt != None:
            vehicleState = 'ready'
            PrintMessage("print vehicle state")

    elif vehicleState == 'manual':
        if vehicle.mode.name != 'LOITER':
            vehicle.mode    = VehicleMode("LOITER")
        PrintMessage("print vehicle state")

def processDroneCommand(input):
    elements = input.split(' ')
    if len(elements) > 0:
        i_command = elements[0]
        global sequencePos, sequenceList, vehicleState
        global targetLat, targetLon, targetAlt
        if i_command == 'SETUP':
            i_coordinates = elements[1]
            i_sequence = elements[2]
            
            sequencePos = 0 #reset sequence position
            coordinateStringList = i_coordinates.split(';') #get a list of strings 'lat,lon,alt',...
            for coordinateString in coordinateStringList:
                elements = coordinateString.split(',') # get one coordinate as list - lat,lon,alt
                print colored.green('elements' + str(elements))
                coordinateList.append([float(element) for element in elements])
            
            sequenceList = [int(el) for el in i_sequence.split(',')]
            
        elif i_command == 'GOTO_NEXT' and vehicleState == 'disarmed':
            
            if sequencePos < len(sequenceList): #check if not reached the end of the sequence
                vehicleState = 'ready'
                #print "current sequence position: ", sequencePos
                sequenceItem = sequenceList[sequencePos]
                targetLat, targetLon, targetAlt = coordinateList[sequenceItem]

                sequencePos += 1
                print time.strftime("%H:%M:%S"), colored.yellow('     target location index = ' + str(sequenceItem))
            else:
                print time.strftime("%H:%M:%S"), colored.yellow('     Finished sequence.')
        elif i_command == 'MANUAL':
            vehicleState = 'manual'
        else:
            print time.strftime("%H:%M:%S"), colored.red('     Invalid command: ' + str(input))  
    
# MAIN LOOP
while True:
    try:
        recMavData = str(vehicle.location) + ';' + str(vehicle.attitude) + ';' + str(vehicle.mode.name) # Get vehicle attributes
        sendSocket.sendto(recMavData, (host, sendPort)) # send data to Grasshopper
        # Receive commands from Grasshopper
        data, addr = receiveSocket.recvfrom(1024)
        if len(str(data)) > 0:
            print time.strftime("%H:%M:%S"), colored.green(' Received data: ' + str(data))
            processDroneCommand(data)
            
        Update_vehicle()
    except socket.error, msg:
        print time.strftime("%H:%M:%S") ,' Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()