# Import custom packages
import sys
import logging
sys.path.append("../")
import functions
from functions import analog_tones_list
from functions import MemoryBank
from functions import RawData
import binascii
import re

# Variables specific to this radio
tuning_steps_list: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]
# These dictionaries must map to the ones in functions.py
tone_modes: dict = {"0000": "None",
                    "0010": "Tone",
                    "0110": "TSQL",
                    "1000": "TSQL-R",
                    "1100": "DTCS",
                    "1110": "DTCR-R"}
ch_modes: dict = {"000": "FM",
                  "001": "NFM",
                  "010": "AM",
                  "011": "NAM",
                  "100": "DV"}
# List of decoded channels
channels_list: list[MemoryBank] = []

# Get shift from the current bank
def get_split(input_bank: list[str]) -> str:
    """Extracts the Split info from the memory bank(s)"""
    # Extract split
    tmp_split = str(input_bank[2][8:9])
    if tmp_split == "0":
        return "0"
    elif tmp_split == "2":
        return "-"
    elif tmp_split == "4":
        return "+"
    else:
        return "ERR-" + tmp_split

# Get mode from the current bank
def get_mode(input_bank: list[str]) -> str:
    """Extracts the TX Mode from the memory bank(s)"""
    # if re.compile('[^01]').search(input_bank[2]):
    #     raise(Exception("Get_mode function expects binary data!"))
    tmp_mode = functions.hex_str_to_bin_str(input_bank[2][15:17])[3:6]
    #print(tmp_mode)
    channel_mode = ch_modes.get(tmp_mode)
    if channel_mode is None:
        logging.error("Cannot detect mode: [%s]", tmp_mode)
        return "FM"
    else:
        return channel_mode

# Get tone from the current bank
def get_tone_mode(input_bank: list[str]) -> str:
    """Extracts the Tone Mode from the memory bank(s)"""
    tmp_tone_mode = functions.hex_str_to_bin_str(input_bank[2][8:10])[2:-2]
    return tone_modes.get(tmp_tone_mode)

# Get the Tone Squelch
def get_tsql(input_bank: list[str]) -> int:
    """Extracts the TSQL information from the memory bank(s)"""
    hex_string = input_bank[2][10:12]
    hex_value = int(hex_string, 16)  # Convert hexadecimal string to integer
    lower_byte = hex_value & 0xFF  # Extract the lower byte (last two characters)
    number = lower_byte // 4  # Divide the lower byte by 4
    return int(number)

# Get the DTCS mode
def get_dtcs_polarity(input_bank: list[str]) -> int:
    """Extracts the DTCS polarity from the memory bank(s)"""
    hex_string = input_bank[2][20:21]
    return int(hex_string)

# Get DTCS tone
def get_dtcs_tone(input_bank: list[str]) -> int:
    """Extract DTCS Tone index from memories"""
    hex_string = input_bank[2][14:16]
    int_value = int(hex_string, 16)
    return int(int_value/2)

# Process ICF to CSV
def icf_to_csv(input_file_path: str, output_file_path: str, first_channel: int, last_channel: int):
    """Converts an ICF file to a CSV"""
    
    with open(input_file_path, "r", encoding="UTF-8") as input_stream:
        # Read file content
        input_file_content = input_stream.readlines()
        my_call = input_file_content[1].rstrip().replace("#", "")
        logging.info("Found memory file by [%s]", my_call)
        logging.info("Reading channels from [%s] to [%s]", first_channel, last_channel)
        first_row = (first_channel * 3) + 2
        last_row = ((last_channel + 1) * 3) + 2
        logging.debug("Reading lines from [%s] to [%s]", first_row, last_row)
        input_file_content = input_file_content[first_row:last_row]
        logging.debug("File length: [%s]", len(input_file_content))
        
        # Loop per each memory bank and extract data
        for i in range(int(len(input_file_content)/3)):
            # Read real value from the file
            banks_from_file: list[str] = input_file_content[(i*3):(i*3)+3]
            memory_bank = RawData(banks_from_file)
                
            # Extract frequency from the memory bank
            rx_freq =int(memory_bank.hex_string[0][6:14], 16)
            if (rx_freq <= 5000):
                #print("Memory bank [" + str(i) + "] is empty, skipping")
                continue
            
            # Memory band is valid
            logging.debug("Found memory bank [%s]", i)
            # Extract bank name
            channel_name = str(bytes.fromhex(memory_bank.hex_string[2][22:])).replace("b\'","").replace("\'","")
            # Extract split
            split = get_split(memory_bank.hex_string)
            # Extract frequency offset
            freq_offset = int(memory_bank.hex_string[0][14:22], 16)
            # Extract tuning step
            tuning_step = int(tuning_steps_list[int(memory_bank.hex_string[2][13:14])])
            # Extract mode
            chan_mode = get_mode(memory_bank.hex_string)
            # Extract tone mode
            chan_tone = get_tone_mode(memory_bank.hex_string)
            if chan_tone is None:
                chan_tone = -1
            # Extract TX analog RPT tone
            try:
                rpt_tone = int(memory_bank.hex_string[2][11:13], 16)
            except:
                rpt_tone = -1
            # Extract RX analog RPT tone
            rpt_tsql = get_tsql(memory_bank.hex_string)
            # Extract YOUR callsign (for DV)
            your_call = str(bytes.fromhex(memory_bank.hex_string[0][22:34])).replace("b\'","").replace("\'","")
            # Create generic split mode
            if split == "+":
                tx_freq = rx_freq + freq_offset
            elif split == "-":
                tx_freq = rx_freq - freq_offset
            else:
                tx_freq = rx_freq
            # Create generic tone mode
            if chan_tone == "Tone":
                tx_tone = 1
                rx_tone = 0
            elif chan_tone == "TSQL":
                tx_tone = 1
                rx_tone = 1
            elif chan_tone == "TSQL-R":
                tx_tone = -1
                rx_tone = -1
            elif chan_tone == "DTCS":
                tx_tone = 2
                rx_tone = 0
            elif chan_tone == "DTCS-R":
                tx_tone = -2
                rx_tone = -2
            else:
                tx_tone = 0
                rx_tone = 0
            # Get DCS Tone
            dig_tone = get_dtcs_tone(memory_bank.hex_string)
            dig_polarity = get_dtcs_polarity(memory_bank.hex_string)
            # Create channel class
            new_channel = MemoryBank(i, channel_name, rx_freq, tx_freq, tuning_step, chan_mode, rpt_tone, rpt_tsql, dig_tone, dig_tone, my_call, your_call, tx_tone, rx_tone, dig_polarity)
            channels_list.append(new_channel)
            
            # Print for debug
            logging.debug(memory_bank.hex_string)
            
    for single_bank in channels_list:
        # Print channel information
        print()
        single_bank.print_bank()
    functions.write_chirp_csv(output_file_path, channels_list)

# Process CSV to ICF
def csv_to_icf(input_file_path: str, output_file_path: str, first_channel: int, last_channel: int):
    """Process a Chirp CSV file into an ICF format"""
    return NotImplementedError

def main():
    """Main program process"""
    # Check CLI arguments
    input_file_path, output_file_path, first_channel, last_channel = functions.get_cli_args(sys.argv[1:])
    # Check max value
    if last_channel == 0 or last_channel > 499:
        last_channel = 499
    # Check which program to begin
    if ".icf" in input_file_path:
        icf_to_csv(input_file_path, output_file_path, first_channel, last_channel)
    elif ".csv" in input_file_path:
        csv_to_icf(input_file_path, output_file_path, first_channel, last_channel)
    else:
        return

if __name__ == "__main__":
    main()
