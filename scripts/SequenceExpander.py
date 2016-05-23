# Sequencefile expander
# Given a sequence file and a expansion_rate this script wil insert
# expansion_rate interpolated frames between two exsisting frames
#
# usage: python SequenceExpander.py infile outfile expansion_rate(int)
# example: python SequenceExpander.py walk-frame.txt walk-frame-expanded.txt 5

import sys

# Get the arguments list 
argCount = len(sys.argv)
cmdargs = sys.argv

if(argCount != 4):
    sys.exit("Wrong amount of arguments")

infile = cmdargs[1]
outfile = cmdargs[2]
expansion_rate = int(cmdargs[3])

def getFrameLines(frame):
	tmplines = {}
	tmplines[0] = "framebegin\n"
	
	for line in frame:
		tmplines[len(tmplines)] = frame[line] + "\n"
		
	tmplines[len(tmplines)] = "frameend\n"
	
	return tmplines
	
def getCoords(line):
	words = line.strip().split(' ')
	strs = words[1].split(",")
	retval = {}
	retval[0] = float(strs[0])
	retval[1] = float(strs[1])
	retval[2] = float(strs[2])
	return retval

def getIntermediateFrame(framenr, frameA, frameB):
	global expansion_rate, legCoordMap
	ratio = float(framenr)/expansion_rate
	
	newFrame = {}
	
	for i in frameB:
		
		words = frameB[i].strip().split(' ')
		if frameA.get(i, None) is not None:
			startCoords = getCoords(frameA[i])
			destCoords = getCoords(frameB[i])
			
		else:
			startCoords = legCoordMap[i]
			
			destCoords = getCoords(frameB[i])
		
		newCoords = {}
		newCoords[0] = startCoords[0] + ((destCoords[0] - startCoords[0]) * ratio)
		newCoords[1] = startCoords[1] + ((destCoords[1] - startCoords[1]) * ratio)
		newCoords[2] = startCoords[2] + ((destCoords[2] - startCoords[2]) * ratio)
		
		newFrame[i] = i + " " + str(newCoords[0])+ ","+ str(newCoords[1])+","+str(newCoords[2])+ " " + words[2]
	return newFrame


with open(infile) as fo:
	lines = fo.readlines()

newlines = []
linecount = len(lines)
tmpFrame = {}
legCoordMap = {}

frameA = None
frameB = None
inFrame = False

#We run the parser multiple times to be able to interpolate the last frame to the first frame
for runCount in range(0, 3):
	framesRead = 0;
	i = 0
	while(i < linecount):
		line = lines[i]
		
		words = line.strip().split(' ')
		command = words[0]
		
		if(command == "framebegin"):
			tmpFrame = {}
		elif(command == "frameend"):
			if(frameA is None):
				frameA = tmpFrame	
				newFrame = getFrameLines(frameA)
			else:
				frameB = tmpFrame
		elif(command.startswith("l:")):
			tmpFrame[command] = line
			if command not in legCoordMap:
				legCoordMap[command] = getCoords(line)
		else:
			if(runCount == 1):
				newlines.append(line)
			
		if(frameA is not None and frameB is not None):
			#newFrames = []
			for j in range(1, expansion_rate):
				newFrame = getFrameLines(getIntermediateFrame(j, frameA, frameB))
				if(runCount == 1):
					for nline in newFrame: 
						newlines.append(newFrame[nline])			
				
			if((runCount == 1) or (framesRead == 0 and runCount == 3)):
				frameBlines = getFrameLines(frameB)
				for nline in frameBlines: 
					newlines.append(frameBlines[nline])
			
			for leg in frameB:
				legCoordMap[leg] = getCoords(frameB[leg])
			
			frameA = frameB
			frameB = None
			
			framesRead += 1
		i += 1

#Write the output file
with open(outfile, "w+") as fw:
	for line in newlines:
		fw.write(line)
