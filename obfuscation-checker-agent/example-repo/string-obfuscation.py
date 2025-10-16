# STRING OBFUSCATION TECHNIQUES

import base64

# 1. Base64 encoding
encoded = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
decoded = base64.b64decode(encoded).decode()
print(decoded)

# 2. Hex encoding
hex_string = "\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64"  # "Hello World" in hex
print(hex_string)

# 3. Unicode escapes
unicode_str = "\u0048\u0065\u006c\u006c\u006f\u0020\u0057\u006f\u0072\u006c\u0064"
print(unicode_str)

# 4. String concatenation
part1 = "Hell"
part2 = "o Wo"
part3 = "rld"
print(part1 + part2 + part3)

# 5. String from char codes
chars = [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100]
result = ''.join(chr(c) for c in chars)
print(result)

# 6. F-string obfuscation
a = "Wor"
b = "ld"
print(f"Hell{'o'} {a + b}")

# 7. Format string obfuscation
template = "Hell{} {}{}"
print(template.format("o", "Wor", "ld"))

# 8. Rot13 encoding
def rot13(text):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + 13) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)

print(rot13("Uryyb Jbeyq"))

# 9. XOR encoding
def xor_encode(text, key):
    return ''.join(chr(ord(c) ^ key) for c in text)

xor_str = xor_encode("Hello World", 42)
print(xor_encode(xor_str, 42))  # decode

# 10. Byte string manipulation
byte_str = b"Hello World"
encoded_bytes = bytes([x ^ 42 for x in byte_str])
decoded_bytes = bytes([x ^ 42 for x in encoded_bytes])
print(decoded_bytes.decode())
