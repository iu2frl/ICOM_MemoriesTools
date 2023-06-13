# IC-2820 ICF file
ICF files are HEX streams that contains information for each memory bank, structure is something similar to:
```
1. Some number (not decoded yet, maybe radio ID or region?)
2. Callsign
3. First line of first memory channel
4. Second line of first memory channel
5. Third line of first memory channel
6. First line of second memory channel
...
```
So, excluding first two lines we can assume each memory is split into three lines, considering we have 500 memories, we know that memories starts from line 2 up to 1502 (500 memories * 3 lines)

## Frequency encoding and decoding
By checking the input ICF i tried saving multiple memories with different content, example each 1st line:
```
000010 08A9AC9C 000927C04351435143512020 -> 145.337500
000010 089A6A5C 000927C04351435143512020 -> 144.337500
000010 088B281C 000927C04351435143512020 -> 143.337500
000010 05F5E100 000927C04351435143512020 -> 100.000000
000010 06052340 000927C04351435143512020 -> 101.000000
000010 0BEBC200 000927C04351435143512020 -> 200.000000
000010 0BFB0440 000927C04351435143512020 -> 201.000000
```
Then i started reverse engineering and i discovered a pattern

### Encoding Process
1. Take the decimal value you want to encode.
2. Multiply the decimal value by 2^24 (16777216).
3. Convert the result to a hexadecimal representation.

```python
def encode_decimal_to_hex(decimal_value):
    hex_value = hex(int(decimal_value * 2**24))[2:].upper()
    return hex_value

# Example usage
decimal_value = 145.337500
encoded_hex = encode_decimal_to_hex(decimal_value)
print(encoded_hex)
```
### Decoding Process
1. Take the hexadecimal value you want to decode.
2. Convert the hexadecimal value to a decimal representation.
3. Divide the decimal value by 2^24 (16777216).

```python
def decode_hex_to_decimal(hex_value):
    decimal_value = int(hex_value, 16) / 2**24
    return decimal_value

# Example usage
hex_value = "08A9AC9C"
decoded_decimal = decode_hex_to_decimal(hex_value)
print(decoded_decimal)
```
## Frequency offset and shift
I got this data from the ICF file at every 1st line:
```
00001008A9AC9C 000186A0 4351435143512020 -> 0.100000
00001008A9AC9C 00030D40 4351435143512020 -> 0.200000
00001008A9AC9C 00186A00 4351435143512020 -> 1.600000
```

So we can use this approach:

```python
def encode_decimal_to_hex(decimal_value):
    hex_value = hex(int(decimal_value * 2**24))[2:].upper()
    return hex_value

def decode_hex_to_decimal(hex_value):
    decimal_value = int(hex_value, 16) / 2**24
    return decimal_value

# Example usage - Encoding
decimal_value = 0.1
encoded_hex = encode_decimal_to_hex(decimal_value)
print(f"Decimal: {decimal_value} -> Hexadecimal: {encoded_hex}")

# Example usage - Decoding
hex_value = "000186A0"
decoded_decimal = decode_hex_to_decimal(hex_value)
print(f"Hexadecimal: {hex_value} -> Decimal: {decoded_decimal}")
```

## Duplex mode
To get the duplex mode (positive or negative shift) i got from each 3rd line:
```
00201072 00 208300090000415249204D4E2D56 -> No shift
00201072 20 208300090000415249204D4E2D56 -> Negative
00201072 40 208300090000415249204D4E2D56 -> Positive
```

## Tuning step
For the tuning steps we have in each 3rd line:
```
002010720020 80 000000002020202020202020 -> 5k
005010720020 81 000000002020202020202020 -> 6.25k
008010720020 82 000000002020202020202020 -> 10k
00B010720020 83 000000002020202020202020 -> 12.5k
00E010720020 84 000000002020202020202020 -> 15k
011010720020 85 000000002020202020202020 -> 20k
014010720020 86 000000002020202020202020 -> 25k
017010720020 87 000000002020202020202020 -> 30k
01A010720020 88 000000002020202020202020 -> 50k
```

So we can extract the right step:
```python
# List of tuning steps in Hz
tuningStepsAry: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]
# Extract tuning step
tuningStep = tuningStepsAry[int(hex_value[2][13:14])]
print(" Tuning step: [" + tuningStep + "]")
```