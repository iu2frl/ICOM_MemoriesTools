import sys, getopt, os
import ntpath

# List of tuning steps in Hz
tuningStepsAry: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]

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

def main():
    inputFilePath, outputFilePath = GetArgs()
    with open(inputFilePath, "r") as inputStream:
        # Read lines up to memory number 500
        #inputFileContent = inputStream.readlines()[0:(500*3)+2]
        inputFileContent = inputStream.readlines()[0:32]
        print("Found memory file by [" + inputFileContent[1].rstrip().replace("#", "") + "]")
        # Loop per each memory bank and extract data
        for i in range(int((len(inputFileContent)-2)/3)):
            memoryBank = inputFileContent[(i*3)+2:(i*3)+5]
            # Extract frequency from the memory bank
            freqMhz = str(int(memoryBank[0].rstrip()[6:14], 16))
            if (freqMhz == "5000"):
                #print("Memory bank [" + str(i) + "] is empty, skipping")
                continue
            # Memory band is valid
            print("Found memory bank [" + str(i) + "]")
            # Extract bank name
            channelName = str(bytes.fromhex(memoryBank[2].rstrip()[22:])).replace("b\'","").replace("\'","")
            # Extract split
            tmpSplit = str(memoryBank[2].rstrip()[8:10])
            if tmpSplit == "00":
                split = "0"
            elif tmpSplit == "20":
                split = "-"
            elif tmpSplit == "40":
                split = "+"
            else:
                split = "ERR"
            # Extract frequency offset
            freqOffset = str(int(memoryBank[0].rstrip()[14:22], 16))
            # Extract tuning step
            tuningStep = tuningStepsAry[int(memoryBank[2][13:14])]
            # Print channel information
            print(" Channel name: [" + channelName + "]")
            print(" Frequency: [" + freqMhz + "] Hz")
            print(" Split: [" + split + "]")
            print(" Offset: [" + freqOffset + "] Hz")
            print(" Tuning step: [" + tuningStep + "]")
            
if __name__ == "__main__":
   main()