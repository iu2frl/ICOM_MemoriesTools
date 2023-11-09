"""Module providing common features for import/export of memories"""

# Import native packages
import os
import sys
import getopt
import ntpath
import logging
from decimal import Decimal
import binascii

# List of repeater tones
analog_tones_list = ["67.0", "69.3", "71.9", "74.4", "77.0", "79.7", "82.5", "85.4", "88.5", "91.5", "94.8", "97.4", "100.0", "103.5", "107.2", "110.9", "114.8", "118.8", "123.0", "127.3", "131.8", "136.5", "141.3", "146.2", "151.4", "156.7", "159.8", "162.2", "165.5", "167.9", "171.3", "173.8", "177.9", "179.9", "183,5", "186.2", "189.9", "192.8", "196.6", "199.5", "203.5", "206.5", "210.7", "218.1", "225.7", "229.1", "233.6", "241.8", "250.3", "254.1"]
digital_tones_list = ["023", "025", "026", "031", "032", "036", "043", "047", "051", "053", "054", "065", "071", "072", "073", "074", "114", "115", "116", "122", "125", "131", "132", "134", "143", "145", "152", "155", "156", "162", "165", "172", "174", "205", "212", "223", "225", "226", "243", "244", "245", "246", "251", "252", "255", "261", "263", "265", "266", "271", "274", "306", "311", "315", "325", "331", "332", "343", "346", "351", "356", "364", "365", "371", "411", "412", "413", "423", "431", "432", "445", "446", "452", "454", "455", "462", "464", "465", "466", "503", "506", "516", "523", "526", "532", "546", "565", "606", "612", "624", "627", "631", "632", "654", "662", "664", "703", "712", "723", "731", "732", "734", "743", "754"]
tone_modes_dict = {1: "Analog Tone", 2: "Digital Tone", -1: "Analog Reverse", -2: "Digital Reverse"}
dig_tone_modes_dict = {0: "Both Normal", 1: "Tx Normal - Rx Reverse", 2: "Tx Reverse - Rx Normal", 3: "Both Reverse"}
chirp_tone_modes_dict = {0: "NN", 1: "NR", 2: "RN", 3: "RR"}
chirp_ch_modes = ['WFM', 'FM', 'NFM', 'AM', 'NAM', 'DV', 'USB', 'LSB', 'CW', 'RTTY', 'DIG', 'PKT', 'NCW', 'NCWR', 'CWR', 'P25', 'Auto', 'RTTYR', 'FSK', 'FSKR', 'DMR', 'FSK-R', 'CW-R', 'Data+LSB', 'Data+USB', 'Data+FM', 'USER-L', 'USER-U', 'LSB+CW', 'USB+CW', 'RTTY-L', 'RTTY-U', 'N/A']

# Memory bank raw content
class RawData:
    hex_string: list[str]
    bin_string: list[str]
    
    def __init__(self, input_hex: list[str]):
        # Create as many element as we got in input
        self.hex_string = []
        self.bin_string = []
        for single_hex in input_hex:
            # Store HEX string
            self.hex_string.append(single_hex.strip())
            # Convert to binary string
            bytes_data = bytes.fromhex(single_hex.strip())
            binary_data = bin(int(binascii.hexlify(bytes_data), 16))[2:]
            self.bin_string.append(binary_data.zfill((len(binary_data) + 7) // 8 * 8))

# Memory bank definition
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
    comment: str
    rpt1_call: str
    rpt2_call: str
    skip: str
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
                        in_dig_polarity: int = 0,
                        in_comment: str = "",
                        in_rpt1: str = "",
                        in_rpt2: str = ""):
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
        self.comment = in_comment
        self.rpt1_call = in_rpt1
        self.rpt2_call = in_rpt2
        self.skip = ""

    def get_split_offset(self) -> list[int, str]:
        """Returns a list containing the split offset (int) and the direction (int)"""
        freq_offset = self.tx_freq - self.rx_freq
        offset_dir = 0
        if freq_offset > 0:
            offset_dir = 1
        elif freq_offset < 0:
            offset_dir = -1
        else:
            offset_dir = 0
        return abs(freq_offset), offset_dir

    def print_bank(self) -> None:
        """Prints the current channel informations in console"""
        print(f"Channel number: [{self.memory_index}]")
        print(f"Channel name: [{self.memory_name}]")
        print(f"RX Frequency: [{self.rx_freq}] Hz")
        print(f"TX Frequency: [{self.tx_freq}] Hz")
        if self.get_split_offset()[1] != 0:
            print(f"Freq shift: [{self.get_split_offset()[0]}] Hz")
        print(f"Tuning step: [{self.tuning_step}] Hz")
        print(f"Mode: [{self.ch_mode}]")
        #print(f"Skip: [{self.skip}]")
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

    def get_chirp_csv_line(self) -> str:
        """Return a string in the CHIRP format"""
        chirp_offset, offset_dir = self.get_split_offset()
        if offset_dir > 0:
            chirp_offset_dir = "+"
        elif offset_dir < 0:
            chirp_offset_dir = "-"
        else:
            chirp_offset_dir = ""
        # Convert to CHIRP tone
        if self.rx_tone == 1:
            chirp_tone = "TSQL"
        elif self.rx_tone == -1:
            chirp_tone = "TSQL-R"
        elif self.tx_tone == 1:
            chirp_tone = "Tone"
        elif self.tx_tone == 2:
            chirp_tone = "DTCS"
        elif self.tx_tone == -2:
            chirp_tone = "DTCS-R"
        else:
            chirp_tone = ""
        # Read analog tones
        if self.analog_tx_tone_index > 0 and self.analog_tx_tone_index < len(analog_tones_list):
            chirp_analog_tx_tone = analog_tones_list[self.analog_tx_tone_index]
        else:
            chirp_analog_tx_tone = "67.0"
        if self.analog_rx_tone_index > 0 and self.analog_rx_tone_index < len(analog_tones_list):
            chirp_analog_rx_tone = analog_tones_list[self.analog_rx_tone_index]
        else:
            chirp_analog_rx_tone = "67.0"
        # Read digital tones
        if self.digital_tx_tone_index > 0 and self.digital_tx_tone_index < len(digital_tones_list):
            chirp_digital_tx_tone = digital_tones_list[self.digital_tx_tone_index]
        else:
            chirp_digital_tx_tone = "23"
        # Receive frequency
        chirp_rx_freq = f"{str(self.rx_freq)[:3]}.{str(self.rx_freq)[3:-1]}"
        # Format offset
        chirp_offset = str(chirp_offset)[:-1]
        chirp_offset = f"{chirp_offset[:-5]}.{chirp_offset[-5:]}"
        # Format tuning step
        chirp_tuning_step = str(self.tuning_step/1000)
        return f"{str(self.memory_index)},{self.memory_name.strip()},{chirp_rx_freq},{chirp_offset_dir},{chirp_offset},{chirp_tone},{chirp_analog_tx_tone},{chirp_analog_rx_tone},{chirp_digital_tx_tone},{chirp_tone_modes_dict.get(self.dig_polarity)},{self.ch_mode},{chirp_tuning_step},{self.skip},{self.comment},{self.your_call},{self.rpt1_call},{self.rpt2_call},"

# Convert from HEX to ASCII
def hex_to_ascii(input_data: str, start_index: int, stop_index: int) -> str:
    """Converts a list of HEX Bytes to the corresponding string"""
    return str(bytes.fromhex(input_data[start_index:stop_index])).replace("b\'","").replace("\'","")

# Print help lines to console
def print_help_lines() -> None:
    """Print help information"""
    print("Syntax:")
    print("\tpython filename.py -i <inputfile> -o <outputfile>")
    print("\tOptional: -f <firstCh> -l <lastCh>")

# Get arguments from terminal
def get_cli_args(input_args: list[str]) -> list[str, str, int, int]:
    """Returns: name of input file (str), name of output file (str), first channel to read (int), last channel to read (int)"""
    first_channel: str = ""
    last_channel: str = ""
    inputfile: str = ""
    outputfile: str = ""
    opts, arg = getopt.getopt(input_args,"hi:o:f:l:",["ifile=", "ofile=", "first=", "last="])
    for opt, arg in opts:
        if opt == '-h':
            print_help_lines()
            sys.exit(1)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-f", "--first"):
            first_channel = arg
        elif opt in ("-l", "--last"):
            last_channel = arg
    if inputfile.endswith(".icf") or inputfile.endswith(".csv"):
        logging.info("Input file is [%s]", inputfile)
    else:
        print_help_lines()
        sys.exit(1)
    if inputfile.endswith(".csv"):
        logging.info("Output file is [%s]", outputfile)
    else:
        if inputfile.endswith(".icf"):
            outputfile = ntpath.basename(inputfile.replace(".icf", ".csv"))
        else:
            outputfile = ntpath.basename(inputfile.replace(".csv", ".icf"))
        logging.warning("No output file was given, defaulting to [%s]", outputfile)
    if first_channel == "":
        first_channel = "0"
        logging.warning("No starting channel was given, defaulting to 0")
    else:
        first_channel = int(first_channel)
    if last_channel == "":
        last_channel = "0"
        logging.warning("No ending channel was given, defaulting to max")
    return inputfile, outputfile, int(first_channel), int(last_channel)

# Chirp CSV header
def chirp_header() -> str:
    """Return the standard header for CHIRP"""
    return "Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,Mode,TStep,Skip,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE"

# Write CSV file
def write_chirp_csv(output_path: str, memories_list: list[MemoryBank]) -> bool:
    """Export CSV file according to CHIRP specifications"""
    with open(output_path, "w", encoding="UTF-8") as output_content:
        output_content.write(f"{chirp_header()}\n")
        for single_memory in memories_list:
            output_content.write(f"{single_memory.get_chirp_csv_line()}\n")

# Sample CHIRP file
# Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,Mode,TStep,Skip,Comment,URCALL,RPT1CALL,RPT2CALL
# 0,GB3AL,145.7375,-,0.6,Tone,77,77,023,NN,FM,5.00,,,,,x,
# 1,GB3AU,433.1750,+,1.6,Tone,82.5,82.5,023,NN,FM,5.00,,,,,x,
# 2,GB3AV,433.0500,+,1.6,Tone,118.8,118.8,023,NN,FM,5.00,,,,,x,
# 3,GB3AW,433.2500,+,1.6,Tone,71.9,71.9,023,NN,FM,5.00,,,,,x,