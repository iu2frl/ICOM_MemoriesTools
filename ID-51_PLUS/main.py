import sys, getopt, os
import ntpath
import sys
sys.path.append('..')  # Add the parent folder to the system path
import functions

# Get arguments from terminal
def GetArgs() -> list[str, str, int, int]:
    firstCh = ""
    lastCh = ""
    opts, arg = getopt.getopt(sys.argv[1:],"hi:o:f:l:",["ifile=", "ofile=", "first=", "last="])
    for opt, arg in opts:
        if opt == '-h':
            print(os.path.basename(__file__) + ' -i <inputfile> -o <outputfile>')
            print("Optional: -f <firstCh> -l <lastCh>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-f", "--first"):
            firstCh = arg
        elif opt in ("-l", "--last"):
            lastCh = arg
    if (inputfile.endswith(".icf")):
        print ('Input file is ', inputfile)
    else:
        print("No ICF file was given as input!")
        exit()
    if (inputfile.endswith(".csv")):
        print ('Output file is ', outputfile)
    else:
        outputfile = ntpath.basename(inputfile.replace(".icf", ".csv"))
        print("No output file was given, defaulting to " + outputfile)
    if firstCh == "":
        firstCh = 0
    else:
        firstCh = int(firstCh)
    if lastCh == "":
        lastCh = 499
    else:
        lastCh = int(lastCh)
    return inputfile, outputfile, firstCh, lastCh

# Get duplex mode
def GetDuplex(inputData) -> str:
    inputStr = str(inputData)
    if inputStr == "8":
        return "DUP+"
    elif inputStr == "0":
        return "OFF"
    elif inputStr == "4":
        return "DUP-"
    else:
        return f"UNKNOWN - {inputStr}"
    
def GetMode(inputData) -> str:
    inputStr = str(inputData)
    if inputStr == "0":
        return "FM"
    elif inputStr == "1":
        return "FM-N"
    elif inputStr == "3":
        return "AM"
    elif inputStr == "5":
        return "DV"
    else:
        return f"UNKNOWN - {inputStr}"
    
def GetToneMode(inputData) -> str:
    inputStr = str(inputData)
    if inputStr == "0":
        return "None"
    elif inputStr == "1":
        return "Tone"
    elif inputStr == "3":
        return "TSQL"
    elif inputStr == "5":
        return "DTCS"
    else:
        return f"UNKNOWN - {inputStr}"

def GetStep(inputData) -> str:
    inputStr = str(inputData)
    if inputStr == "1":
        return "6,25"
    elif inputStr == "2":
        return "8,33"
    elif inputStr == "8":
        return "25"
    else:
        return f"UNKNOWN - {inputStr}"

def main():
    inputFilePath, outputFilePath, firstCh, lastCh = GetArgs()
    with open(inputFilePath, "r") as inputStream:
        # Read file content
        print("Reading channels from [" + str(firstCh) + "] to [" + str(lastCh) + "]")
        # Each memory is 119 characters long so we need a special approach
        # Start by reading the whole file as a list of lines
        inputList = inputStream.readlines()[4:]
        tmpStream: list[str] = []
        for i in range(len(inputList)):
            # Remove the lines count
            tmpStream.append(inputList[i][10:].strip())
        # Create the single string
        singleString = ''.join(tmpStream[:-1])
        # Set length of each memory
        memoryLength = 98
        # Create list of all memories
        memoriesList: list[str] = []
        for i in range(500):
            memoriesList.append(singleString[i*memoryLength:(i*memoryLength)+memoryLength])
        bankCnt = 0
        for singleMemory in memoriesList[firstCh:lastCh]:
            print(f"Channel: [{bankCnt}]")
            print(f" Name: [{functions.HexToAscii(singleMemory, 22, 54)}]")
            #print(" Your call: [" + functions.HexToAscii(singleMemory, ))
            #print(str(int(singleMemory[2:10], 16)))
            print(f" Duplex: [{GetDuplex(singleMemory[21:22])}]")
            print(f" Mode: [{GetMode(singleMemory[13:14])}]")
            print(f" Tone: [{GetToneMode(singleMemory[20:21])}] Hz")
            print(f" Step: [{GetStep(singleMemory[16:17])}] KHz")
            print(f" Raw: [{singleMemory}]")
            bankCnt += 1
            
if __name__ == "__main__":
   main()