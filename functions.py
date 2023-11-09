# Import native packages
import os
import sys
import getopt
import ntpath
import logging

####################################################
# Common structures for all the different programs #
####################################################

# List of repeater tones
analog_tones_list = ["67.0", "69.3", "71.9", "74.4", "77.0", "79.7", "82.5", "85.4", "88.5", "91.5", "94.8", "97.4", "100.0", "103.5", "107.2", "110.9", "114.8", "118.8", "123.0", "127.3", "131.8", "136.5", "141.3", "146.2", "151.4", "156.7", "159.8", "162.2", "165.5", "167.9", "171.3", "173.8", "177.9", "179.9", "183,5", "186.2", "189.9", "192.8", "196.6", "199.5", "203.5", "206.5", "210.7", "218.1", "225.7", "229.1", "233.6", "241.8", "250.3", "254.1"]
digital_tones_list = ["023", "025", "026", "031", "032", "036", "043", "047", "051", "053", "054", "065", "071", "072", "073", "074", "114", "115", "116", "122", "125", "131", "132", "134", "143", "145", "152", "155", "156", "162", "165", "172", "174", "205", "212", "223", "225", "226", "243", "244", "245", "246", "251", "252", "255", "261", "263", "265", "266", "271", "274", "306", "311", "315", "325", "331", "332", "343", "346", "351", "356", "364", "365", "371", "411", "412", "413", "423", "431", "432", "445", "446", "452", "454", "455", "462", "464", "465", "466", "503", "506", "516", "523", "526", "532", "546", "565", "606", "612", "624", "627", "631", "632", "654", "662", "664", "703", "712", "723", "731", "732", "734", "743", "754"]
tone_modes_dict = {1: "Analog Tone", 2: "Digital Tone", -1: "Analog Reverse", -2: "Digital Reverse"}
dig_tone_modes_dict = {0: "Both Normal", 1: "Tx Normal - Rx Reverse", 2: "Tx Reverse - Rx Normal", 3: "Both Reverse"}

class MemoryBank:
    """Contains the definition of the memory channel"""
    memory_index: int
    memory_name: str
    tx_freq: int
    rx_freq: int
    tuning_step: int
    ch_mode: str
    analog_rx_tone_index: int
    digital_rx_tone_index: int
    analog_tx_tone_index: int
    digital_tx_tone_index: int
    my_call: str
    your_call: str
    # Tone modes
    # 0: Disabled
    # 1: Analog
    # -1: Analog Reverse
    # 2: Digital
    # -2: Digital Reverse
    tx_tone: int
    rx_tone: int
    # DTCS Polarity
    # 0: Both N
    # 1: TN-RR
    # 2: TR-RN
    # 3: Both R
    dig_polarity: int
    def __init__(self, in_index: int,
                        in_name: str,
                        rx_freq: int,
                        tx_freq: int,
                        in_tuning: int,
                        in_mode: str,
                        in_an_tx_tone_id: int,
                        in_an_rx_tone_id: int,
                        in_dig_tx_tone_id: int,
                        in_dig_rx_tone_id: int,
                        in_my_call: str,
                        in_your_call: str = "",
                        in_tx_tone: int = 0,
                        in_rx_tone: int = 0,
                        in_dig_polarity: int = 0):
        self.memory_index = in_index
        self.memory_name = in_name
        self.tx_freq = tx_freq
        self.rx_freq = rx_freq
        self.tuning_step = in_tuning
        self.ch_mode = in_mode
        self.analog_rx_tone_index = in_an_rx_tone_id
        self.analog_tx_tone_index = in_an_tx_tone_id
        self.digital_rx_tone_index = in_dig_rx_tone_id
        self.digital_tx_tone_index = in_dig_tx_tone_id
        self.my_call = in_my_call
        self.your_call = in_your_call
        self.tx_tone = in_tx_tone
        self.rx_tone = in_rx_tone
        self.dig_polarity = in_dig_polarity
    
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
    
    def print_bank(self) -> None:
        """Prints the current channel informations in console"""
        print(f"Channel number: [{self.memory_index}]")
        print(f"Channel name: [{self.memory_name}]")
        print(f"RX Frequency: [{self.rx_freq}] Hz")
        print(f"TX Frequency: [{self.tx_freq}] Hz")
        print(f"Tuning step: [{self.tuning_step}] Hz")
        print(f"Mode: [{self.ch_mode}]")
        print(f"Skip: [not implemented yet]")
        if self.analog_tx_tone_index >= 0 and self.analog_tx_tone_index < len(analog_tones_list):
            print(f"Analog TX Tone: [{analog_tones_list[self.analog_tx_tone_index]}]")
        if self.analog_rx_tone_index >= 0 and self.analog_rx_tone_index < len(analog_tones_list):
            print(f"Analog RX Tone: [{analog_tones_list[self.analog_rx_tone_index]}]")
        if self.my_call != "":
            print(f"My CALL: [{self.my_call}]")
        if self.your_call != "":
            print(f"Your CALL: [{self.your_call}]")
        if self.tx_tone > 0:
            print(f"TX Tone mode: [{tone_modes_dict.get(self.tx_tone)}]")
        if self.rx_tone > 0:
            print(f"RX Tone mode: [{tone_modes_dict.get(self.rx_tone)}]")
        if self.dig_polarity > 0:
            print(f"DTCS Polarity: [{dig_tone_modes_dict.get(self.dig_polarity)}]")
        if self.digital_rx_tone_index >= 0 and self.digital_rx_tone_index < len(digital_tones_list):
            print(f"Digital RX Tone: [{digital_tones_list[self.digital_rx_tone_index]}]")
        if self.digital_tx_tone_index >= 0 and self.digital_tx_tone_index < len(digital_tones_list):
            print(f"Digital TX Tone: [{digital_tones_list[self.digital_tx_tone_index]}]")

def hex_to_ascii(input_data: str, start_index: int, stop_index: int) -> str:
    """Converts a list of HEX Bytes to the corresponding string"""
    return str(bytes.fromhex(input_data[start_index:stop_index])).replace("b\'","").replace("\'","")

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
        logging.info("Input file is [%s]", inputfile)
    else:
        logging.error("No ICF file was given as input!")
        return None
    if (inputfile.endswith(".csv")):
        logging.info("Output file is [%s]", outputfile)
    else:
        outputfile = ntpath.basename(inputfile.replace(".icf", ".csv"))
        logging.warning("No output file was given, defaulting to [%s]", outputfile)
    if first_channel == "":
        first_channel = 0
        logging.warning("No starting channel was given, defaulting to 0")
    else:
        first_channel = int(first_channel)
    if last_channel == "":
        last_channel = 499
        logging.warning("No ending channel was given, defaulting to 499")
    else:
        last_channel = int(last_channel)
        if last_channel > 499:
            last_channel = 499
            logging.warning("Fefaulting to max 499 channels")
    return inputfile, outputfile, first_channel, last_channel