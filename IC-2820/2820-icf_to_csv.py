# Import custom packages
import sys
sys.path.append("../")
import functions
from functions import analog_tones_list
from functions import MemoryBank

# Variables specific to this radio
tuning_steps_list: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]
tone_modes: dict = {"00": "None", "04": "Tone", "0C": "TSQL", "10": "TSQL-R", "18": "DTCS", "1C": "DTCR-R"}
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
    tmp_mode = input_bank[2][16:17]
    if tmp_mode == "0":
        return "FM"
    elif tmp_mode == "4":
        return "FM-N"
    elif tmp_mode == "8":
        return "AM"
    elif tmp_mode == "C":
        return "AM-N" 
    else:
        return "Unknown-" + tmp_mode

# Get tone from the current bank
def get_tone(input_bank: list[str]) -> str:
    """Extracts the Tone Mode from the memory bank(s)"""
    return tone_modes.get(input_bank[2][8:10])

# Get the Tone Squelch
def get_tsql(input_bank: list[str]) -> str:
    """Extracts the TSQL information from the memory bank(s)"""
    hex_string = input_bank[2][10:12]
    hex_value = int(hex_string, 16)  # Convert hexadecimal string to integer
    lower_byte = hex_value & 0xFF  # Extract the lower byte (last two characters)
    number = lower_byte // 4  # Divide the lower byte by 4
    return analog_tones_list[number]

def main():
    """Main program process"""
    cli_srguments = functions.get_cli_args(sys.argv[1:])
    if cli_srguments is None:
        return
    input_file_path, output_file_path, first_channel, last_channel = cli_srguments
    with open(input_file_path, "r") as input_stream:
        # Read file content
        input_file_content = input_stream.readlines()
        print("Found memory file by [" + input_file_content[1].rstrip().replace("#", "") + "]")
        print("Reading channels from [" + str(first_channel) + "] to [" + str(last_channel) + "]")
        first_row = (first_channel * 3) + 2
        last_row = (last_channel * 3) + 2
        print("Reading lines from [" + str(first_row) + "] to [" + str(last_row) + "]")
        input_file_content = input_file_content[first_row:last_row]
        print(len(input_file_content))
        # Loop per each memory bank and extract data
        for i in range(int(len(input_file_content)/3)):
            # Read real value from the file
            tmp_bank = input_file_content[(i*3):(i*3)+3]
            memory_bank: list[str] = []
            # Clean the string
            for single_line in tmp_bank:
                memory_bank.append(single_line.strip())
            # Extract frequency from the memory bank
            freq_MHz = str(int(memory_bank[0][6:14], 16))
            if (int(freq_MHz) <= 5000):
                #print("Memory bank [" + str(i) + "] is empty, skipping")
                continue
            # Memory band is valid
            print("Found memory bank [" + str(i) + "]")
            # Extract bank name
            channel_name = str(bytes.fromhex(memory_bank[2][22:])).replace("b\'","").replace("\'","")
            # Extract split
            split = get_split(memory_bank)
            # Extract frequency offset
            freq_offset = str(int(memory_bank[0][14:22], 16))
            # Extract tuning step
            tuning_step = tuning_steps_list[int(memory_bank[2][13:14])]
            # Extract mode
            chan_mode = get_mode(memory_bank)
            # Extract tone mode
            chan_tone = get_tone(memory_bank)
            if chan_tone is None:
                chan_tone = "Unknown"
            # Extract TX analog RPT tone
            try:
                rpt_tone = analog_tones_list[int(memory_bank[2][11:13], 16)]
            except:
                rpt_tone = "None"
            # Extract RX analog RPT tone
            rpt_tsql = get_tsql(memory_bank)
            # Extract YOUR callsign (for DV)
            your_call = str(bytes.fromhex(memory_bank[0][22:34])).replace("b\'","").replace("\'","")
            # Print channel information
            print(memory_bank)
            print(" Channel name: [" + channel_name + "]")
            print(" Frequency: [" + freq_MHz + "] Hz")
            print(" Split: [" + split + "]")
            print(" Offset: [" + freq_offset + "] Hz")
            print(" Tuning step: [" + tuning_step + "]")
            print(" Mode: [" + chan_mode + "]")
            print(" Tone mode: [" + chan_tone + "]")
            print(" Analog RPT tone: [" + rpt_tone + "]")
            print(" Analog TSQL: [" + rpt_tsql + "]")
            print(" Your CALL: [" + your_call + "]")
            
if __name__ == "__main__":
    main()