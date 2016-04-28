import time

def parseSequence(filePath, validate=False):
    print("Parsing sequence at: " + filePath)
    hasHeader = False
    lineNr = 0
    
    with open(filePath, 'r') as f:
        for line in f:
            lineNr += 1
            words = line.split(' ')
            #if(not hasHeader and words[0].lower() != "sequence"):
            #    raise("Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'")
            #else:
            #    hasHeader = True
            #    continue
                
            if(words[0].lower() == "delay"):
                if(len(words) != 2):
                    raise NameError("No argument given for delay at line: " + str(lineNr))
                seconds = float(words[1]) / 1000
                
                if(not validate):
                    print("Will delay " + str(seconds) + " seconds")
                    time.sleep(seconds)
                
            if(words[0].lower().startswith('s:')):
                if(len(words) < 2 or len(words) > 3):
                    raise NameError("Wrong amount of arguments for servo control: " + str(len(words)) + " at line: " + str(lineNr))
                    
                servoID = int(words[0].split(':')[1]);
                coords = words[1].split(',');
                if(len(coords) != 3):
                    raise NameError("Wrong amount of coords: "+str(len(coords))+" at line: " + str(lineNr))
                
                speed = -1
                if(len(words) == 3):
                    speed = int(words[2])

                if(not validate):
                    print("Will control servo {0}, coords: {1}, speed: {2}".format(servoID, coords, speed) )
                    #hier de servocontroller aanroepen met de variabelen wanneer not validate

print("Will validate sequence")
try:
    parseSequence("../sequences/testseqkaput.txt", True)
except NameError as e:
    print(e)
    
parseSequence("../sequences/testseq.txt");
        

