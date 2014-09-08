'''
FaceTrack - A visual servoing example using SimpleCV and an Arduino. More info at http://hhj.me/facetrack
'''

print __doc__

import time
from SimpleCV import *
import serial, time

## OpenCV Delaration
display = Display()
cam = Camera()
# We are using a HaarCascade to detect faces
haarcascade = HaarCascade("face")

## Camera Variable Declaration
# We are talking over serial to the arduino. Change these variables to match your system
ser = serial.Serial('COM4', 9600, timeout=1)
# For some reason it takes a little time for the serial link to establish so wait 2 seconds
time.sleep(2.0)

# Default positions for the yaw and pitch servos. Change these numbers to match your setup
yawPos = 100
pitchPos = 107

# Tolerances. Tighter tolerances (smaller) track the face more percisel but result in move movement. If the tolerance is too small the camera might begin to oscillate.
xErrMin = -10;
xErrMax = 10;
yErrMin = -10;
yErrMax = 10;

# Variables used to indicate which direction to move the servos
yawDelta = 0
pitchDelta = 0

# Firmware Variables 
firmVersion = 0.0;
firmState = -1;
firmYawValue = -1;
firmPitchValue = -1;

def setVariable(rawVariableLine):
	global firmVersion, firmState, firmYawValue, firmPitchValue
	temp1 = rawVariableLine.split(':')
	if(len(temp1) == 2):
		#print "[VARIABLE] - " + temp1[0] + " = " + temp1[1]
		if(temp1[0] == "Version"):
			firmVersion = float(temp1[1])
			print "Firmware Version: " + str(firmVersion)
		elif(temp1[0] == "State"):
			firmState = int(temp1[1])
			#print "FState set"
		elif(temp1[0] == "YawValue"):
			firmYawValue = int(temp1[1])
			#print "FYawValue set"
		elif(temp1[0] == "PitchValue"):
			firmPitchValue = int(temp1[1])
			#print "FPitchValue set"
	#else:
		#print "[ERROR] - Bad Variable Length (" + str(len(temp1)) + ")"

## Helper function to send servo commands to the Arduino
def srvUpdate(yawPos, pitchPos, yawDelta, pitchDelta):
	yawPos = yawPos + yawDelta
	pitchPos = pitchPos + pitchDelta
	if (yawPos < 30):
		yawPos = 30
	if (yawPos > 150):
		yawPos = 150
	if (pitchPos < 50):
		pitchPos = 50
	if (pitchPos > 130):
		pitchPos = 130
	yawStr = str(yawPos).zfill(3)
	pitchStr = str(pitchPos).zfill(3);

	#print "[INFO] " + "> FYawValue:" + yawStr + ", FPitchValue:" + str(firmPitchValue) + ", FState:" + pitchStr

	# Custom protocol is fairly straight forward: ">YYYPPP" where YYY and PPP are zero padded numbers representing servo positions
	cmd = '>' + yawStr + pitchStr + '\n'
	ser.write(cmd)

	gotResponse = 0

	while(gotResponse == 0):
		line = ser.readline().rstrip()
		if(line[0] == "!"):
			# Got an event.
			#print "[EVENT] - " + line[1:]
			if(line[1:] == "ACK"):
				gotResponse = 1
			elif (line[1:] == "NAK"):
				gotResponse = 2
			elif (line[1:] == "Timeout"):
				gotResponse = 3
			else:
				gotResponse = -1
				print '[ERROR] - Unknown Event'
		#elif(line[0] == "#"):
			# Got an comment.
			#print "[DEBUG] - " + line[1:]
		elif(line[0] == "$"):
			# Got an variable.
			setVariable(line[1:])

	#print "[INFO] " + "< FYawValue:" + str(firmYawValue).zfill(3) + ", FPitchValue:" + str(firmPitchValue).zfill(3) + ", FState:" + str(firmState)
			
## Main Program Start
# Got to the 'home' position
srvUpdate(yawPos, pitchPos, 0, 0)

# While the display window is still open
while display.isNotDone():
	# Grab the camera image, flip it, and scale it. Scaling helps to speed up the face finding
	image = cam.getImage().flipHorizontal().scale(0.5)

	# Find the faces in the image
	faces = image.findHaarFeatures(haarcascade)

	# If there are faces, grab the first, draw a square around it, and calcualte the movement required to center the camera on it
	if faces:
		# Grab the first face. In images with more than one "face" the "first" face is not persistance and can jump between visible faces. This is one of the reasons for the yawDelta and pitchDelta variables. Instead of jumping between the two+ faces as quickly as possible, which would be hectic given the unstability of the face selection, the algorithm simply moves towards the "first" face so the final result is much smoother even with the face finding persistance problem
		face = faces[-1]
		# Draw a square around the face
		face.show(Color.RED)	

		# Calculate the error between the center of the face and the center of the camera image		 
		xErr = face.x - image.width/2
		yErr = face.y - image.height/2

		# If the error is out of tolerance set the appropriate delta so that the servo moves in the correct direction.
		if (xErr < xErrMin):
			yawDelta = -1
		elif (xErr > xErrMax):
			yawDelta = 1
		else:
			yawDelta = 0

		if (yErr < yErrMin):
			pitchDelta = 1
		elif (yErr > yErrMax):
			pitchDelta = -1
		else:
			pitchDelta = 0

	# Show the image to the user (not really necessary but interesting)
	image.show()
	# Update the servo
	srvUpdate(firmYawValue, firmPitchValue, yawDelta, pitchDelta)

# If the user closes the main window then be good citizens and close the serial connection
ser.close()

