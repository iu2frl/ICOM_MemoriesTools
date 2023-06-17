import sys, getopt, os
import ntpath

# List of tuning steps in Hz
tuningStepsAry: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]
# List of repeater tones
rptTonesAry = ["67.0", "69.3", "71.9", "74.4", "77.0", "79.7", "82.5", "85.4", "88.5", "91.5", "94.8", "97.4", "100.0", "103.5", "107.2", "110.9", "114.8", "118.8", "123.0", "127.3", "131.8", "136.5", "141.3", "146.2", "151.4", "156.7", "159.8", "162.2", "165.5", "167.9", "171.3", "173.8", "177.9", "179.9", "183,5", "186.2", "189.9", "192.8", "196.6", "199.5", "203.5", "206.5", "210.7", "218.1", "225.7", "229.1", "233.6", "241.8", "250.3", "254.1"]

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
        return
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
        if lastCh > 499:
            lastCh = 499
    return inputfile, outputfile, firstCh, lastCh

# Get shift from the current bank
def GetSplit(inputBank: list[str]) -> str:
    # Extract split
    tmpSplit = str(inputBank[2][8:9])
    if tmpSplit == "0":
        return "0"
    elif tmpSplit == "2":
        return "-"
    elif tmpSplit == "4":
        return "+"
    else:
        return "ERR-" + tmpSplit

# Get mode from the current bank
def GetMode(inputBank: list[str]) -> str:
    tmpMode = inputBank[2][16:17]
    if tmpMode == "0":
        return "FM"
    elif tmpMode == "4":
        return "FM-N"
    elif tmpMode == "8":
        return "AM"
    elif tmpMode == "C":
        return "AM-N" 
    else:
        return "Unknown-" + tmpMode

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
        return "Unknown-" + tmpTone

# Get the Tone Squelch
def GetTsql(inputBank: list[str]) -> str:
    hex_string = inputBank[2][10:12]
    hex_value = int(hex_string, 16)  # Convert hexadecimal string to integer
    lower_byte = hex_value & 0xFF  # Extract the lower byte (last two characters)
    number = lower_byte // 4  # Divide the lower byte by 4
    return rptTonesAry[number]

def main():
    inputFilePath, outputFilePath, firstCh, lastCh = GetArgs()
    with open(inputFilePath, "r") as inputStream:
        # Read file content
        inputFileContent = inputStream.readlines()
        print("Found memory file by [" + inputFileContent[1].rstrip().replace("#", "") + "]")
        print("Reading channels from [" + str(firstCh) + "] to [" + str(lastCh) + "]")
        firstRow = (firstCh * 3) + 2
        lastRow = (lastCh * 3) + 2
        print("Reading lines from [" + str(firstRow) + "] to [" + str(lastRow) + "]")
        inputFileContent = inputFileContent[firstRow:lastRow]
        print(len(inputFileContent))
        # Loop per each memory bank and extract data
        for i in range(int(len(inputFileContent)/3)):
            # Read real value from the file
            tmpBank = inputFileContent[(i*3):(i*3)+3]
            memoryBank: list[str] = []
            # Clean the string
            for singleLine in tmpBank:
                memoryBank.append(singleLine.strip())
            # Extract frequency from the memory bank
            freqMhz = str(int(memoryBank[0][6:14], 16))
            if (int(freqMhz) <= 5000):
                #print("Memory bank [" + str(i) + "] is empty, skipping")
                continue
            # Memory band is valid
            print("Found memory bank [" + str(i) + "]")
            # Extract bank name
            channelName = str(bytes.fromhex(memoryBank[2][22:])).replace("b\'","").replace("\'","")
            # Extract split
            split = GetSplit(memoryBank)
            # Extract frequency offset
            freqOffset = str(int(memoryBank[0][14:22], 16))
            # Extract tuning step
            tuningStep = tuningStepsAry[int(memoryBank[2][13:14])]
            # Extract mode
            chanMode = GetMode(memoryBank)
            # Extract tone mode
            chanTone = GetTone(memoryBank)
            # Extract TX analog RPT tone
            try:
                rptTone = rptTonesAry[int(memoryBank[2][11:13], 16)]
            except:
                rptTone = "None"
            # Extract RX analog RPT tone
            rptTsql = GetTsql(memoryBank)
            # Extract YOUR callsign (for DV)
            yourCall = str(bytes.fromhex(memoryBank[0][22:34])).replace("b\'","").replace("\'","")
            # Print channel information
            print(memoryBank)
            print(" Channel name: [" + channelName + "]")
            print(" Frequency: [" + freqMhz + "] Hz")
            print(" Split: [" + split + "]")
            print(" Offset: [" + freqOffset + "] Hz")
            print(" Tuning step: [" + tuningStep + "]")
            print(" Mode: [" + chanMode + "]")
            print(" Tone mode: [" + chanTone + "]")
            print(" Analog RPT tone: [" + rptTone + "]")
            print(" Analog TSQL: [" + rptTsql + "]")
            print(" Your CALL: [" + yourCall + "]")
            
if __name__ == "__main__":
   main()