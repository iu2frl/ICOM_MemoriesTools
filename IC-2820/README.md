# IC-2820 ICF file
## Frequency encoding and decoding
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
