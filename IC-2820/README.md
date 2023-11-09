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

### Memories

So, we know the memories are composed of three lines

#### First line

```
000 010 08A9AC9C 000927C0 435143514351 2020
```
- Bytes 0 to 2 are the lines counter for the file, starting from `000` and stopping at ACB
- Bytes 3 to 5 are always fixed at `010`
- Bytes 6 to 14 are the frequency encoding as described below
- Bytes 14 to 22 are the frequency offset
- Bytes 22 to 34 are the YOUR CALL for DV data
- Bytes 34 to 38 are unknown

#### Second line

```
001 010 20202020202020202020202020202020
```
- Bytes 0 to 2 are the lines counter for the file, starting from `000` and stopping at ACB
- Bytes 3 to 5 are always fixed at `010`

### Third line

```
002 010 72 0 02 08 3 00 0 90000 415249204D4E2D56
```
- Bytes 0 to 2 are the lines counter for the file, starting from `000` and stopping at ACB
- Bytes 3 to 5 are always fixed at `010`
- Byte 8 is the split mode index (None, Pos or Neg)
- Bytes 10 and 11 are the tone squelch index
- Byte 13 is the tuning step
- Bytes 16 is the mode (FM, AM, etc)
- Bytes from 22 to the end are the channel name (8 characters)

# Decoding data

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
## Frequency offset

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
00201072 0 0208300090000415249204D4E2D56 -> No shift
00201072 2 0208300090000415249204D4E2D56 -> Negative
00201072 4 0208300090000415249204D4E2D56 -> Positive
```

## Tuning step

For the tuning steps we have in each 3rd line:

```
0020107200208 0 000000002020202020202020 -> 5k
0050107200208 1 000000002020202020202020 -> 6.25k
0080107200208 2 000000002020202020202020 -> 10k
00B0107200208 3 000000002020202020202020 -> 12.5k
00E0107200208 4 000000002020202020202020 -> 15k
0110107200208 5 000000002020202020202020 -> 20k
0140107200208 6 000000002020202020202020 -> 25k
0170107200208 7 000000002020202020202020 -> 30k
01A0107200208 8 000000002020202020202020 -> 50k
```

So we can extract the right step:
```python
# List of tuning steps in Hz
tuningStepsAry: list[str] = ["5000", "6250", "10000", "12500", "15000", "20000", "25000", "30000", "50000"]
# Extract tuning step
tuningStep = tuningStepsAry[int(hex_value[2][13:14])]
print(" Tuning step: [" + tuningStep + "]")
```

## Mode

For the different modes i found per each 3rd line:

```
0020107200208000 0 000002020202020202020 -> FM
0050107200208000 4 000002020202020202020 -> FM-N
0080107200208000 8 000002020202020202020 -> AM
00B0107200208000 C 000002020202020202020 -> AM-N
```

## Skip mode

Skip can be set as Skip or PSkip, here is the output:

```
0000 1008A48640000000004351435143512020  0010 1020202020202020202020202020202020  0020 1072002080000000002020202020202020 -> Skip
0030 1008A48640000000004351435143512020  0040 1020202020202020202020202020202020  0050 1072002080000000002020202020202020 -> PSkip
0060 1008A48640000000004351435143512020  0070 1020202020202020202020202020202020  0080 1072002080000000002020202020202020 -> None
0090 1008A48640000000004351435143512020  00A0 1020202020202020202020202020202020  00B0 1072002080000000002020202020202020 -> Skip
00C0 1008A48640000000004351435143512020  00D0 1020202020202020202020202020202020  00E0 1072002080000000002020202020202020 -> PSkip
00F0 1008A48640000000004351435143512020  0100 1020202020202020202020202020202020  0110 1072002080000000002020202020202020 -> PSkip
```

I could not find any pattern here, any help is appreciated

## Tone mode

Having this input per each 3rd line:

```
00201072 04 2080000000002020202020202020 -> Tone
00501072 0C 2080000000002020202020202020 -> TSQL
00801072 10 2080000000002020202020202020 -> TSQL-R
00B01072 18 2080000000002020202020202020 -> DTCS
00E01072 1C 2080000000002020202020202020 -> DTCS-R
01401072 00 2080000000002020202020202020 -> None
56301072 44 20A600000000525533312D56454E -> Tone

```

## Repeater tones

Having this input per each 3rd line:

```
00201072 0 4 20 00 000000002020202020202020 -> 67.0 (0)
00501072 0 4 20 10 000000002020202020202020 -> 69.3 (1)
00801072 0 4 20 20 000000002020202020202020 -> 71.9 (2)
00B01072 0 4 20 20 000000002020202020202020 -> 71.9 (2)
01101072 0 4 22 70 000000002020202020202020 -> 199.5 (39)
01701072 0 0 04 05 000000002020202020202020 -> Simplex + NoTone + Tone 67.0 + TSQL 69.3
01A01072 2 4 00 05 000000002020202020202020 -> Dup- + TONE + Tone 67.0 + TSQL 67.0
01D01072 4 4 04 05 000000002020202020202020 -> Dup+ + TONE + Tone 67.0 + TSQL 69.3
02001072 4 4 03 15 000000002020202020202020 -> Dup+ + TONE + Tone 254.1 + TSQL 67.0
02301072 4 C 03 15 000000002020202020202020 -> Dup+ + TSQL + Tone 254.1 + TSQL 67.0
02601072 5 0 03 15 000000002020202020202020 -> Dup+ + TSQL-R + Tone 254.1 + TSQL 67.0
02901072 5 8 03 15 000000002020202020202020 -> Dup+ + DTCS + Tone 254.1 + TSQL 67.0
02C01072 5 C 03 15 000000002020202020202020 -> Dup+ + DTCS-R + Tone 254.1 + TSQL 67.0

00201072 0 4 00 05 000000002020202020202020 -> TONE + Tone 67.0 + TSQL 67.0
00501072 0 4 04 05 000000002020202020202020 -> TONE + Tone 67.0 + TSQL 69.3
00801072 0 C 00 05 000000002020202020202020 -> TSQL + Tone 67.0 + TSQL 67.0
00B01072 0 C 04 05 000000002020202020202020 -> TSQL + Tone 67.0 + TSQL 69.3
00E01072 1 0 00 05 000000002020202020202020 -> TSQLR + Tone 67.0 + TSQL 67.0
01101072 1 0 04 05 000000002020202020202020 -> TSQLR + Tone 67.0 + TSQL 69.3
01401072 0 0 00 05 000000002020202020202020 -> None + Tone 67.0 + TSQL 67.0
01701072 0 0 04 05 000000002020202020202020 -> None + Tone 67.0 + TSQL 69.3
56301072 4 4 20 A6 00000000525533312D56454E -> TONE + Tone 94.8 + TSQL 88.5
25D01072 2 4 20 26 000900005230412D4C4F4D20 -> TONE + Tone 71.9 + TSQL 88.5
01A01072 2 4 00 05 000000002020202020202020 -> DUP- + Tone 67.0 + TSQL 67.0
01D01072 4 4 04 05 000000002020202020202020 -> DUP+ + Tone 67.0 + TSQL 69.3
```

## DTCS Tone

Having this input per each 3rd line:

```
023 01072182085 02 0000002020202020202020 -> 025 - 1
026 010721C2085 04 0000002020202020202020 -> 026 - 2
029 01072182085 02 0000102020202020202020 -> 025 - 1
02C 010721C2085 04 0000102020202020202020 -> 026 - 2
02F 01072182085 02 0000202020202020202020 -> 025 - 1
032 010721C2085 00 0000202020202020202020 -> 023 - 0
035 01072182085 02 0000302020202020202020 -> 025 - 1
038 010721C2085 04 0000302020202020202020 -> 026 - 2
03B 01072182085 CE 0000002020202020202020 -> 754 - 103
03E 01072182085 CC 0000002020202020202020 -> 743 - 102
```

## Channel name

Channel name is encoded in the 3rd line of the channel:

```
563010724420A600000000 525533312D56454E -> RU31-VEN
```

## DV Data

### YOUR CALL

The destination callsign is easy to get and comes from the 1st line:

```
00001008A9AC9C000927C0 435143514351 2020 -> CQCQCQ
```