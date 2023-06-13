import sys, getopt, os
import ntpath

# List of tuning steps in Hz
tuningStepsAry: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]

# Get arguments from terminal
def GetArgs() -> list[str, str]:
    opts, arg = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
    for opt, arg in opts:
        if opt == '-h':
            print (os.path.basename(__file__) + ' -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    if (inputfile.endswith(".icf")):
        print ('Input file is ', inputfile)
    else:
        print("No ICF file was given as input!")
        return
    if (inputfile.endswith(".csv")):
        print ('Output file is ', outputfile)
    else:
        outputfile = ntpath.basename(inputfile.replace(".icf", ".csv"))
        print("No output file was given, defaulting to " + outputfile)
    return inputfile, outputfile

# Get shift from the current bank
def GetShift(inputBank: list[str]) -> str:
    # Extract split
    tmpSplit = str(inputBank[2].rstrip()[8:10])
    if tmpSplit == "00":
        return "0"
    elif tmpSplit == "20":
        return "-"
    elif tmpSplit == "40":
        return "+"
    else:
        return "ERR"

# Get mode from the current bank
def GetMode(inputBank: list[str]) -> str:
    tmpMode = inputBank[2][16:18]
    if tmpMode == "00":
        return "FM"
    elif tmpMode == "40":
        return "FM-N"
    elif tmpMode == "80":
        return "AM"
    elif tmpMode == "C0":
        return "AM-N" 
    else:
        return "Unknown"

# Get tone from the current bank
def GetTone(inputBank: list[str]) -> str:
    tmpTone = inputBank[2][8:10]
    if tmpTone == "00":
        return "None"
    elif tmpTone == "04":
        return "Tone"
    elif tmpTone == "0C":
        return "TSQL"
    elif tmpTone == "10":
        return "TSQL-R"
    elif tmpTone == "18":
        return "DTCS"
    elif tmpTone == "1C":
        return "DTCR-R"
    else:
        return "Unknown"

def main():
    inputFilePath, outputFilePath = GetArgs()
    with open(inputFilePath, "r") as inputStream:
        # Read lines up to memory number 500
        inputFileContent = inputStream.readlines()[0:(500*3)+2]
        print("Found memory file by [" + inputFileContent[1].rstrip().replace("#", "") + "]")
        # Loop per each memory bank and extract data
        for i in range(int((len(inputFileContent)-2)/3)):
            memoryBank = inputFileContent[(i*3)+2:(i*3)+5]
            # Extract frequency from the memory bank
            freqMhz = str(int(memoryBank[0].rstrip()[6:14], 16))
            if (int(freqMhz) <= 5000):
                #print("Memory bank [" + str(i) + "] is empty, skipping")
                continue
            # Memory band is valid
            print("Found memory bank [" + str(i) + "]")
            # Extract bank name
            channelName = str(bytes.fromhex(memoryBank[2].rstrip()[22:])).replace("b\'","").replace("\'","")
            # Extract split
            split = GetShift(memoryBank)
            # Extract frequency offset
            freqOffset = str(int(memoryBank[0].rstrip()[14:22], 16))
            # Extract tuning step
            tuningStep = tuningStepsAry[int(memoryBank[2][13:14])]
            # Extract mode
            chanMode = GetMode(memoryBank)
            # Extract tone mode
            chanTone = GetTone(memoryBank)
            # Print channel information
            print(" Channel name: [" + channelName + "]")
            print(" Frequency: [" + freqMhz + "] Hz")
            print(" Split: [" + split + "]")
            print(" Offset: [" + freqOffset + "] Hz")
            print(" Tuning step: [" + tuningStep + "]")
            print(" Mode: [" + chanMode + "]")
            print(" Tone mode: [" + chanTone + "]")
            
if __name__ == "__main__":
   main()