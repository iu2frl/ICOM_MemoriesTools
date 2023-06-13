# IC-2820 ICF file
## Frequency encoding and decoding
By checking the input ICF i tried saving multiple memories with different content, example:
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
I got this data from the ICF file:
```
000010 08A9AC9C 000186A0 4351435143512020 -> 0.100000
000010 08A9AC9C 00030D40 4351435143512020 -> 0.200000
000010 08A9AC9C 00186A00 4351435143512020 -> 1.600000
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

## Duplex
To get the duplex mode (positive or negative shift) i got:

```
00201072 00 208300090000415249204D4E2D56 -> No shift
00201072 20 208300090000415249204D4E2D56 -> Negative
00201072 40 208300090000415249204D4E2D56 -> Positive
```

Then we can consider that byte to be the duplex mode