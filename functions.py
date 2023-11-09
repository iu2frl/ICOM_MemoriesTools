# Import native packages
import os
import sys
import getopt
import ntpath

####################################################
# Common structures for all the different programs #
####################################################

# List of repeater tones
analog_tones_list = ["67.0", "69.3", "71.9", "74.4", "77.0", "79.7", "82.5", "85.4", "88.5", "91.5", "94.8", "97.4", "100.0", "103.5", "107.2", "110.9", "114.8", "118.8", "123.0", "127.3", "131.8", "136.5", "141.3", "146.2", "151.4", "156.7", "159.8", "162.2", "165.5", "167.9", "171.3", "173.8", "177.9", "179.9", "183,5", "186.2", "189.9", "192.8", "196.6", "199.5", "203.5", "206.5", "210.7", "218.1", "225.7", "229.1", "233.6", "241.8", "250.3", "254.1"]

class MemoryBank:
    """Contains the definition of the memory channel"""
    memory_index: int
    memory_name: str
    tx_freq: int
    rx_freq: int
    tuning_step: int
    def __init__(self, in_index: int, in_name: str, tx_freq: int, rx_freq: int, in_tuning: int):
        self.memory_index = in_index
        self.memory_name = in_name
        self.tx_freq = tx_freq
        self.rx_freq = rx_freq
        self.tuning_step = in_tuning
    
    def get_split_offset(self) -> list[int, str]:
        """Returns a list containing the split offset (int) and the direction (int)"""
        freq_offset = self.rx_freq - self.tx_freq
        offset_dir = 0
        if freq_offset > 0:
            offset_dir = 1
        if freq_offset < 0:
            offset_dir = -1
        else:
            offset_dir = 0
        return freq_offset, offset_dir

def hex_to_ascii(inputData: str, startIndex: int, stopIndex: int) -> str:
    """Converts a list of HEX Bytes to the corresponding string"""
    return str(bytes.fromhex(inputData[startIndex:stopIndex])).replace("b\'","").replace("\'","")

# Get arguments from terminal
def get_cli_args(input_args: list[str]) -> list[str, str, int, int]:
    """Returns: name of input file (str), name of output file (str), first channel to read (int), last channel to read (int)"""
    first_channel = ""
    last_channel = ""
    inputfile = ""
    outputfile = ""
    opts, arg = getopt.getopt(input_args,"hi:o:f:l:",["ifile=", "ofile=", "first=", "last="])
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
            first_channel = arg
        elif opt in ("-l", "--last"):
            last_channel = arg
    if (inputfile.endswith(".icf")):
        print ('Input file is ', inputfile)
    else:
        print("No ICF file was given as input!")
        return None
    if (inputfile.endswith(".csv")):
        print ('Output file is ', outputfile)
    else:
        outputfile = ntpath.basename(inputfile.replace(".icf", ".csv"))
        print("No output file was given, defaulting to " + outputfile)
    if first_channel == "":
        first_channel = 0
        print("No starting channel was given, defaulting to 0")
    else:
        first_channel = int(first_channel)
    if last_channel == "":
        last_channel = 499
        print("No ending channel was given, defaulting to 499")
    else:
        last_channel = int(last_channel)
        if last_channel > 499:
            last_channel = 499
            print("Fefaulting to max 499 channels")
    return inputfile, outputfile, first_channel, last_channel